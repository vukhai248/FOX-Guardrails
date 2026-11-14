const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const Stripe = require('stripe');
const { loader } = require('./load-ts.cjs');
const { userA } = require('./payment-fixture.cjs');
const { paymentDependencies: deps, testStripeClient, shopOrigin } = loader()(path.resolve(__dirname, '../payment-runtime.ts'));

function setup(t) {
  const names = ['STRIPE_SECRET_KEY', 'STRIPE_WEBHOOK_SECRET', 'APP_URL', 'NEXT_PUBLIC_SUPABASE_URL', 'NEXT_PUBLIC_SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_ROLE_KEY'];
  const originals = Object.fromEntries(names.map(name => [name, process.env[name]]));
  const fetch = global.fetch;
  Object.assign(process.env, {
    STRIPE_SECRET_KEY: 'sk_test_offline_fixture', STRIPE_WEBHOOK_SECRET: 'whsec_offline_fixture',
    APP_URL: 'http://localhost:3000', NEXT_PUBLIC_SUPABASE_URL: 'https://offline.supabase.invalid',
    NEXT_PUBLIC_SUPABASE_ANON_KEY: 'offline-anon-key', SUPABASE_SERVICE_ROLE_KEY: 'offline-service-key',
  });
  t.after(() => {
    global.fetch = fetch;
    for (const [name, value] of Object.entries(originals)) {
      if (value === undefined) delete process.env[name]; else process.env[name] = value;
    }
  });
}

test('actual Stripe SDK verifies raw signed event and rejects tampering/stale signatures', t => {
  setup(t);
  const sdk = new Stripe(process.env.STRIPE_SECRET_KEY);
  const payload = JSON.stringify({ id: 'evt_offline', object: 'event', type: 'checkout.session.completed', livemode: false, data: { object: { id: 'cs_test_offline', object: 'checkout.session' } } });
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  const signature = sdk.webhooks.generateTestHeaderString({ payload, secret });
  assert.equal(deps.verifyEvent(payload, signature).id, 'evt_offline');
  assert.throws(() => deps.verifyEvent(`${payload} `, signature));
  assert.throws(() => deps.verifyEvent(payload, sdk.webhooks.generateTestHeaderString({ payload, secret, timestamp: 1 })));
});

test('missing/live Stripe keys fail closed without any network', t => {
  setup(t);
  delete process.env.STRIPE_SECRET_KEY;
  assert.throws(testStripeClient, error => error.code === 'SERVICE_UNAVAILABLE');
  process.env.STRIPE_SECRET_KEY = 'sk_live_offline_fixture_not_a_real_key';
  assert.throws(testStripeClient, error => error.code === 'SERVICE_UNAVAILABLE');
});

test('redirect origin comes from APP_URL, permitting HTTPS or loopback only', t => {
  setup(t);
  process.env.APP_URL = 'https://shop.example/some/path';
  assert.equal(shopOrigin(), 'https://shop.example');
  for (const value of ['http://outside.example', 'https://user:password@shop.example', 'file:///tmp/shop']) {
    process.env.APP_URL = value;
    assert.throws(shopOrigin);
  }
});

test('Supabase auth sends the supplied access token to getUser with anon credentials', async t => {
  setup(t);
  let captured;
  global.fetch = async (url, options) => {
    captured = { url: new URL(url), options };
    return Response.json({ id: userA, aud: 'authenticated', role: 'authenticated', email: 'offline@example.invalid' });
  };
  assert.equal(await deps.authenticate('user-access-token'), userA);
  assert.equal(captured.url.pathname, '/auth/v1/user');
  const headers = new Headers(captured.options.headers);
  assert.equal(headers.get('authorization'), 'Bearer user-access-token');
  assert.equal(headers.get('apikey'), 'offline-anon-key');
  global.fetch = async () => Response.json({ msg: 'Invalid token' }, { status: 401 });
  assert.equal(await deps.authenticate('invalid'), null);
});

test('Supabase detail query includes owner filter and service key', async t => {
  setup(t);
  let captured;
  global.fetch = async (url, options) => { captured = { url: new URL(url), options }; return Response.json({ id: 'order', user_id: userA }); };
  await deps.getOrder('order', userA);
  assert.equal(captured.url.searchParams.get('id'), 'eq.order');
  assert.equal(captured.url.searchParams.get('user_id'), `eq.${userA}`);
  assert.equal(new Headers(captured.options.headers).get('apikey'), 'offline-service-key');
});

test('Supabase note update filters owner and pending in the atomic write', async t => {
  setup(t);
  let captured;
  global.fetch = async (url, options) => { captured = { url: new URL(url), options }; return Response.json({ id: 'order', note: 'unchanged\u200b🦊' }); };
  assert.equal((await deps.updateNote('order', userA, 'unchanged\u200b🦊')).note, 'unchanged\u200b🦊');
  assert.equal(captured.options.method, 'PATCH');
  assert.equal(captured.url.searchParams.get('user_id'), `eq.${userA}`);
  assert.equal(captured.url.searchParams.get('status'), 'eq.pending');
  assert.deepEqual(JSON.parse(captured.options.body), { note: 'unchanged\u200b🦊' });
});

test('Supabase RPC is a server-key POST and RPC errors propagate without logging secrets', async t => {
  setup(t);
  let captured;
  global.fetch = async (url, options) => { captured = { url: new URL(url), options }; return Response.json({ id: 'server-order' }); };
  assert.equal((await deps.rpc('create_shop_order', { p_user_id: userA })).id, 'server-order');
  assert.equal(captured.url.pathname, '/rest/v1/rpc/create_shop_order');
  assert.equal(captured.options.method, 'POST');
  assert.equal(new Headers(captured.options.headers).get('apikey'), 'offline-service-key');
  global.fetch = async () => Response.json({ code: 'P0001', message: 'OUT_OF_STOCK' }, { status: 400 });
  await assert.rejects(deps.rpc('create_shop_order', {}), /OUT_OF_STOCK/);
});
