const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { loader } = require('./load-ts.cjs');
const { userA, userB } = require('./payment-fixture.cjs');
const load = loader();
const { createOrderHandlers } = load(path.resolve(__dirname, '../order-handlers.ts'));
const { parseOrderInput, checkoutParams } = load(path.resolve(__dirname, '../order-core.ts'));
const id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const input = (extra = {}) => ({
  items: [{ product_id: 1, quantity: 2 }], payment_method: 'cod',
  recipient_name: 'Test Recipient', recipient_phone: '0900000000',
  address_line: 'Private address', ward: 'Test ward', province: 'Test province', note: '', ...extra,
});
const order = (extra = {}) => ({
  id, user_id: userA, status: 'pending', payment_status: 'cod_pending', payment_method: 'cod',
  total: 25000, items: [{ product_id: 1, name: 'DB Product', price: 12500, quantity: 2, image: null }],
  recipient_name: 'Test Recipient', recipient_phone: '0900000000', address_line: 'Private address',
  ward: 'Test ward', province: 'Test province', note: '', created_at: '2026-11-03T00:00:00Z',
  stripe_session_id: 'cs_test_order', stock_decremented_at: null, ...extra,
});
function req(body = input(), token = 'token-a', method = 'POST') {
  return new Request('http://localhost/api/orders', {
    method, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    ...(method === 'GET' ? {} : { body: JSON.stringify(body) }),
  });
}
function context(extra = {}) {
  const calls = [];
  const deps = {
    authenticate: async token => token === 'token-a' ? userA : token === 'token-b' ? userB : null,
    rpc: async (name, args) => { calls.push({ name, args }); return order(); },
    getOrder: async (orderId, userId) => orderId === id && userId === userA ? order() : null,
    updateNote: async (orderId, userId, note) => ({ id: orderId, note }),
    createCheckout: async () => ({ id: 'cs_test_order', url: 'https://checkout.stripe.com/test', livemode: false }),
    expireCheckout: async () => {},
    verifyEvent: () => ({ type: 'checkout.session.completed', livemode: false, data: { object: {
      id: 'cs_test_order', livemode: false, mode: 'payment', payment_status: 'paid',
      metadata: { order_id: id }, amount_total: 25000, currency: 'vnd',
    } } }),
    shopOrigin: () => 'http://localhost:3000',
    ...extra,
  };
  return { deps, calls, handlers: createOrderHandlers(deps) };
}

test('missing/invalid bearer authentication cannot create or read an order', async () => {
  for (const token of [null, 'invalid']) {
    const ctx = context();
    const response = await ctx.handlers.create(req(input(), token));
    assert.equal(response.status, 401);
    assert.equal((await response.json()).error.code, 'UNAUTHENTICATED');
    assert.equal(ctx.calls.length, 0);
    assert.equal((await ctx.handlers.detail(req(undefined, token, 'GET'), id)).status, 401);
  }
});

test('invalid JSON and empty cart use the error contract', async () => {
  const { handlers } = context();
  const response = await handlers.create(new Request('http://localhost/api/orders', {
    method: 'POST', headers: { Authorization: 'Bearer token-a' }, body: '{',
  }));
  assert.equal(response.status, 400);
  assert.equal((await response.json()).error.code, 'INVALID_FIELD');
  const empty = await handlers.create(req(input({ items: [] })));
  assert.equal(empty.status, 400);
  assert.equal((await empty.json()).error.code, 'EMPTY_CART');
});

for (const invalid of [null, [], input({ payment_method: 'cash' }), input({ recipient_name: ' ' }),
  input({ note: '🦊'.repeat(501) }), input({ items: [{ product_id: 1, quantity: -1 }] }),
  input({ items: [{ product_id: 1, quantity: 1.5 }] }), input({ items: [{ product_id: '1', quantity: 1 }] }),
  input({ items: [{ product_id: 1, quantity: 10001 }] }), input({ address_line: 'x'.repeat(501) })]) {
  test(`invalid order fields rejected: ${JSON.stringify(invalid).slice(0, 90)}`, async () => {
    const ctx = context();
    const response = await ctx.handlers.create(req(invalid));
    assert.equal(response.status, 400);
    assert.equal((await response.json()).error.code, 'INVALID_FIELD');
    assert.equal(ctx.calls.length, 0);
  });
}

test('duplicate product quantities aggregate; Unicode note is preserved', () => {
  const note = 'Giao\u200b hàng 🦊\u{E0001}';
  const parsed = parseOrderInput(input({ items: [{ product_id: 1, quantity: 1 }, { product_id: 1, quantity: 2 }], note }));
  assert.deepEqual(parsed.items, [{ product_id: 1, quantity: 3 }]);
  assert.equal(parsed.note, note);
  assert.equal(parseOrderInput(input({ note: '🦊'.repeat(500) })).note, '🦊'.repeat(500));
});

test('COD response uses canonical server order and ignores supplied price/user/status', async () => {
  const ctx = context();
  const response = await ctx.handlers.create(req(input({
    items: [{ product_id: 1, quantity: 2, price: 1 }], user_id: userB, total: 1, payment_status: 'paid',
  })));
  assert.equal(response.status, 201);
  assert.deepEqual(await response.json(), { order_id: id, status: 'pending', payment_status: 'cod_pending', total: 25000 });
  assert.equal(ctx.calls[0].args.p_user_id, userA);
  assert.deepEqual(ctx.calls[0].args.p_items, [{ product_id: 1, quantity: 2 }]);
});

for (const code of ['OUT_OF_STOCK', 'INVALID_PRODUCT']) {
  test(`database ${code} is mapped to public 400`, async () => {
    const { handlers } = context({ rpc: async () => { throw new Error(code); } });
    const response = await handlers.create(req());
    assert.equal(response.status, 400);
    assert.equal((await response.json()).error.code, code);
  });
}

test('internal database errors are not leaked', async () => {
  const { handlers } = context({ rpc: async () => { throw new Error('private database/token details'); } });
  const response = await handlers.create(req());
  assert.equal(response.status, 500);
  assert.doesNotMatch(await response.text(), /private|token details/);
});

test('Stripe session uses server snapshot and only order/session identifiers in URLs', async () => {
  let params;
  const ctx = context({
    rpc: async (name, args) => { ctx.calls.push({ name, args }); return order({ payment_method: 'stripe', payment_status: 'unpaid' }); },
    createCheckout: async (p, key) => { params = p; assert.equal(key, `order:${id}`); return { id: 'cs_test_order', url: 'https://checkout.stripe.com/test', livemode: false }; },
  });
  const request = req(input({ payment_method: 'stripe' }));
  request.headers.set('Origin', 'https://untrusted.example');
  const response = await ctx.handlers.create(request);
  assert.equal(response.status, 201);
  assert.equal((await response.json()).checkout_url, 'https://checkout.stripe.com/test');
  assert.equal(params.line_items[0].price_data.unit_amount, 12500);
  assert.equal(params.line_items[0].quantity, 2);
  assert.equal(params.success_url, `http://localhost:3000/checkout-success?order_id=${id}&session_id={CHECKOUT_SESSION_ID}`);
  assert.deepEqual(params.metadata, { order_id: id });
  assert.doesNotMatch(JSON.stringify(params), /Private address|0900000000|untrusted\.example|Test Recipient/);
  assert.equal(ctx.calls[1].name, 'attach_stripe_session');
});

test('checkout failure marks unpaid order failed and never fabricates checkout URL', async () => {
  const ctx = context({ createCheckout: async () => { throw Error('provider secret details'); } });
  const response = await ctx.handlers.create(req(input({ payment_method: 'stripe' })));
  assert.equal(response.status, 503);
  assert.equal(ctx.calls.at(-1).name, 'fail_stripe_order');
  assert.doesNotMatch(await response.text(), /provider secret|checkout_url/);
});

test('session attachment failure expires the external session', async () => {
  let expired;
  const ctx = context({
    rpc: async name => { if (name === 'attach_stripe_session') throw Error('db unavailable'); return order(); },
    expireCheckout: async session => { expired = session; },
  });
  assert.equal((await ctx.handlers.create(req(input({ payment_method: 'stripe' })))).status, 503);
  assert.equal(expired, 'cs_test_order');
});

test('detail gives other users/malformed IDs the same 404 and omits internal fields', async () => {
  const { handlers } = context();
  assert.equal((await handlers.detail(req(undefined, 'token-b', 'GET'), id)).status, 404);
  assert.equal((await handlers.detail(req(undefined, 'token-a', 'GET'), 'bad-id')).status, 404);
  const response = await handlers.detail(req(undefined, 'token-a', 'GET'), id);
  assert.equal(response.status, 200);
  const data = await response.json();
  assert.equal(data.order_id, id);
  assert.equal(data.total, 25000);
  assert.equal(data.user_id, undefined);
  assert.equal(data.stripe_session_id, undefined);
  assert.equal(data.stock_decremented_at, undefined);
});

test('note edits preserve codepoints and enforce ownership, status and update race', async () => {
  const note = 'Note\u200b🦊\u{E0001}';
  assert.deepEqual(await (await context().handlers.note(req({ note }), id)).json(), { order_id: id, note });
  assert.equal((await context().handlers.note(req({ note }, 'token-b'), id)).status, 404);
  assert.equal((await context().handlers.note(req({ note: 'x'.repeat(501) }), id)).status, 400);
  assert.equal((await context({ getOrder: async () => order({ status: 'delivered' }) }).handlers.note(req({ note }), id)).status, 409);
  assert.equal((await context({ updateNote: async () => null }).handlers.note(req({ note }), id)).status, 409);
});

function webhookRequest(signature = 'test-signature') {
  return new Request('http://localhost/api/stripe/webhook', { method: 'POST', headers: signature ? { 'stripe-signature': signature } : {}, body: '{"test":"raw body"}' });
}

test('missing or invalid Stripe signature cannot reach payment RPC', async () => {
  const ctx = context({ verifyEvent: () => { throw Error('invalid signature'); } });
  for (const signature of [null, 'bad-signature']) {
    assert.equal((await ctx.handlers.webhook(webhookRequest(signature))).status, 400);
  }
  assert.equal(ctx.calls.length, 0);
});

test('signed paid event passes only verified session/amount/currency/order to RPC', async () => {
  const ctx = context();
  const response = await ctx.handlers.webhook(webhookRequest());
  assert.equal(response.status, 200);
  assert.deepEqual(ctx.calls, [{ name: 'finalize_stripe_order', args: {
    p_order_id: id, p_session_id: 'cs_test_order', p_amount_total: 25000, p_currency: 'vnd',
  } }]);
});

test('live, wrong-mode and malformed payment events never finalize orders', async () => {
  const template = context().deps.verifyEvent();
  for (const event of [
    { ...template, livemode: true },
    { ...template, data: { object: { ...template.data.object, livemode: true } } },
    { ...template, data: { object: { ...template.data.object, mode: 'subscription' } } },
    { ...template, data: { object: { ...template.data.object, metadata: {} } } },
  ]) {
    const ctx = context({ verifyEvent: () => event });
    assert.equal((await ctx.handlers.webhook(webhookRequest())).status, 400);
    assert.equal(ctx.calls.length, 0);
  }
});

test('unpaid or unrelated events are acknowledged without payment writes', async () => {
  const template = context().deps.verifyEvent();
  for (const event of [{ ...template, type: 'customer.created' }, { ...template, data: { object: { ...template.data.object, payment_status: 'unpaid' } } }]) {
    const ctx = context({ verifyEvent: () => event });
    assert.equal((await ctx.handlers.webhook(webhookRequest())).status, 200);
    assert.equal(ctx.calls.length, 0);
  }
});

test('webhook database/stock failure remains retryable and does not return success', async () => {
  const { handlers } = context({ rpc: async () => { throw Error('OUT_OF_STOCK'); } });
  assert.equal((await handlers.webhook(webhookRequest())).status, 503);
});

for (const code of ['PAYMENT_MISMATCH', 'NOT_FOUND', 'NOT_EDITABLE', 'INVALID_PRODUCT']) {
  test(`permanent webhook failure ${code} is acknowledged with only order ID and code logged`, async t => {
    const logged = [];
    t.mock.method(console, 'error', (...args) => logged.push(args));
    const { handlers } = context({ rpc: async () => { throw Error(code); } });
    const response = await handlers.webhook(webhookRequest());
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { received: true });
    assert.deepEqual(logged, [[{ order_id: id, code }]]);
  });
}

test('unknown database failure stays retryable without logging error details or PII', async t => {
  const logged = [];
  t.mock.method(console, 'error', (...args) => logged.push(args));
  const { handlers } = context({ rpc: async () => { throw Error('connection lost: private address 0912345678'); } });
  const response = await handlers.webhook(webhookRequest());
  assert.equal(response.status, 503);
  assert.deepEqual(logged, []);
  assert.doesNotMatch(JSON.stringify(await response.json()), /0912345678|private address/);
});

test('signed expired Checkout session fails only its bound unpaid order and is replayable', async () => {
  const template=context().deps.verifyEvent();
  const event={...template,type:'checkout.session.expired',data:{object:{...template.data.object,status:'expired',payment_status:'unpaid'}}};
  const ctx=context({verifyEvent:()=>event});
  for(let i=0;i<2;i++)assert.equal((await ctx.handlers.webhook(webhookRequest())).status,200);
  assert.deepEqual(ctx.calls,[0,1].map(()=>({name:'fail_stripe_order',args:{p_order_id:id,p_session_id:'cs_test_order'}})));
  const paid=context({verifyEvent:()=>({...event,data:{object:{...event.data.object,payment_status:'paid'}}})});
  assert.equal((await paid.handlers.webhook(webhookRequest())).status,200);assert.equal(paid.calls.length,0);
});

test('malformed signed session without an ID returns 400 rather than throwing', async () => {
  const template = context().deps.verifyEvent();
  const ctx = context({ verifyEvent: () => ({ ...template, data: { object: { ...template.data.object, id: undefined } } }) });
  assert.equal((await ctx.handlers.webhook(webhookRequest())).status, 400);
  assert.equal(ctx.calls.length, 0);
});

test('uncertain session expiration leaves order unpaid for webhook reconciliation', async () => {
  const ctx = context({
    rpc: async name => { ctx.calls.push(name); if (name === 'attach_stripe_session') throw Error('db outage'); return order(); },
    expireCheckout: async () => { throw Error('provider outage'); },
  });
  assert.equal((await ctx.handlers.create(req(input({ payment_method: 'stripe' })))).status, 503);
  assert.equal(ctx.calls.includes('fail_stripe_order'), false);
});

test('registered create/detail/note/webhook/legacy Stripe routes delegate correctly', async () => {
  const ctx = context();
  const routeLoad = loader({ '@/lib/server/payment-runtime': { paymentDependencies: ctx.deps } });
  const api = path.resolve(__dirname, '../../../app/api');
  const routes = [
    [path.join(api, 'orders/route.ts'), 'POST', req(), 201],
    [path.join(api, 'stripe/route.ts'), 'POST', req(), 201],
    [path.join(api, 'orders/[id]/route.ts'), 'GET', req(undefined, 'token-a', 'GET'), 200],
    [path.join(api, 'orders/[id]/note/route.ts'), 'PATCH', req({ note: 'test' }), 200],
    [path.join(api, 'stripe/webhook/route.ts'), 'POST', webhookRequest(), 200],
  ];
  for (const [file, method, request, expectedStatus] of routes) {
    assert.equal((await routeLoad(file)[method](request, { params: Promise.resolve({ id }) })).status, expectedStatus, file);
  }
});

test('Stripe parameters reject non-integer stored prices rather than trusting malformed snapshot', () => {
  assert.throws(() => checkoutParams(order({ items: [{ name: 'x', price: 1.5, quantity: 1 }] }), 'http://localhost:3000'));
});
