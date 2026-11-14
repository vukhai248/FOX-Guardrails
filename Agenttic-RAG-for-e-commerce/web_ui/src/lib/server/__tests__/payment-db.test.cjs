const { test, before, after, beforeEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { fixture, userA, args, rpc } = require('./payment-fixture.cjs');

// Tool-only dependency, installed outside this repository; no app dependency changes.
const { PGlite } = require(process.env.PGLITE_MODULE_PATH || '@electric-sql/pglite');
const migrationPath = path.resolve(__dirname, '../../../../../database/migrations/2026-11_payment_and_address.sql');
let db;
before(async () => {
  db = new PGlite();
  await db.exec(fixture);
  await db.exec(fs.readFileSync(migrationPath, 'utf8'));
});
after(async () => { if (db) await db.close(); });
beforeEach(async () => {
  await db.exec(`TRUNCATE public.orders, public.products;
    INSERT INTO public.products VALUES (1,'Server Product',12500,5,null),(2,'Second Product',20000,1,null);`);
});

test('COD prices come from DB, duplicate quantities aggregate and stock decreases once', async () => {
  const order = await rpc(db, 'create_shop_order', args('cod', [
    { product_id: 1, quantity: 1, price: 1 }, { product_id: 1, quantity: 2, price: 0 },
  ]));
  assert.equal(Number(order.total), 37500);
  assert.equal(order.payment_status, 'cod_pending');
  assert.equal(order.status, 'pending');
  assert.equal(order.items.length, 1);
  assert.equal(order.items[0].name, 'Server Product');
  assert.equal(order.items[0].quantity, 3);
  assert.equal((await db.query('select stock from products where id=1')).rows[0].stock, 2);
  await rpc(db, 'decrement_stock_for_order', { p_order_id: order.id });
  assert.equal((await db.query('select stock from products where id=1')).rows[0].stock, 2);
});

test('insufficient stock rolls back the entire COD order', async () => {
  await assert.rejects(rpc(db, 'create_shop_order', args('cod', [{ product_id: 1, quantity: 2 }, { product_id: 2, quantity: 2 }])), /OUT_OF_STOCK/);
  assert.equal((await db.query('select count(*)::int as n from orders')).rows[0].n, 0);
  assert.deepEqual((await db.query('select stock from products order by id')).rows.map(row => row.stock), [5, 1]);
});

test('unknown product, empty cart and zero quantity cannot create orders', async () => {
  for (const [items, error] of [[[], /EMPTY_CART/], [[{ product_id: 999, quantity: 1 }], /INVALID_PRODUCT/], [[{ product_id: 1, quantity: 0 }], /INVALID_FIELD/]]) {
    await assert.rejects(rpc(db, 'create_shop_order', args('cod', items)), error);
  }
});

test('unpaid Stripe does not deduct stock and cannot use decrement RPC', async () => {
  const order = await rpc(db, 'create_shop_order', args('stripe'));
  assert.equal(order.payment_status, 'unpaid');
  assert.equal((await db.query('select stock from products where id=1')).rows[0].stock, 5);
  await assert.rejects(rpc(db, 'decrement_stock_for_order', { p_order_id: order.id }), /NOT_PAID/);
});

async function stripeOrder() {
  const order = await rpc(db, 'create_shop_order', args('stripe'));
  await rpc(db, 'attach_stripe_session', { p_order_id: order.id, p_session_id: 'cs_test_order' });
  return order;
}
function payment(order, extra = {}) {
  return { p_order_id: order.id, p_session_id: 'cs_test_order', p_amount_total: 25000, p_currency: 'vnd', ...extra };
}

test('duplicate paid events set processing/paid and deduct inventory exactly once', async () => {
  const order = await stripeOrder();
  for (let i = 0; i < 2; i++) {
    const result = await rpc(db, 'finalize_stripe_order', payment(order));
    assert.equal(result.status, 'processing');
    assert.equal(result.payment_status, 'paid');
    assert.ok(result.paid_at);
  }
  assert.equal((await db.query('select stock from products where id=1')).rows[0].stock, 3);
});

test('signed payment must match stored amount, currency and session', async () => {
  const order = await stripeOrder();
  for (const extra of [{ p_amount_total: 1 }, { p_currency: 'usd' }, { p_session_id: 'cs_test_other' }]) {
    await assert.rejects(rpc(db, 'finalize_stripe_order', payment(order, extra)), /PAYMENT_MISMATCH/);
  }
  const row = (await db.query('select payment_status from orders')).rows[0];
  assert.equal(row.payment_status, 'unpaid');
  assert.equal((await db.query('select stock from products where id=1')).rows[0].stock, 5);
});

test('webhook stock shortage rolls back payment transition and can retry after restock', async () => {
  const order = await stripeOrder();
  await db.exec('update products set stock=0 where id=1');
  await assert.rejects(rpc(db, 'finalize_stripe_order', payment(order)), /OUT_OF_STOCK/);
  assert.equal((await db.query('select payment_status from orders')).rows[0].payment_status, 'unpaid');
  await db.exec('update products set stock=2 where id=1');
  assert.equal((await rpc(db, 'finalize_stripe_order', payment(order))).payment_status, 'paid');
});

test('paid webhook before session attachment binds that session safely', async () => {
  const order = await rpc(db, 'create_shop_order', args('stripe'));
  await rpc(db, 'finalize_stripe_order', payment(order));
  await rpc(db, 'attach_stripe_session', { p_order_id: order.id, p_session_id: 'cs_test_order' });
  assert.equal((await db.query('select stripe_session_id from orders')).rows[0].stripe_session_id, 'cs_test_order');
});

test('failed Checkout marks order failed without touching stock', async () => {
  const order = await rpc(db, 'create_shop_order', args('stripe'));
  await rpc(db, 'fail_stripe_order', { p_order_id: order.id });
  assert.deepEqual((await db.query('select status,payment_status from orders')).rows[0], { status: 'cancelled', payment_status: 'failed' });
  assert.equal((await db.query('select stock from products where id=1')).rows[0].stock, 5);
});

test('authenticated users cannot bypass orders API or call payment RPCs', async () => {
  await db.exec(`SET ROLE authenticated; SET request.jwt.claim.sub = '${userA}';`);
  try {
    await assert.rejects(db.query('insert into orders(user_id,items,total,shipping_address) values($1,$2,0,$3)', [userA, '[]', 'test']), /permission denied/);
    await assert.rejects(rpc(db, 'create_shop_order', args()), /permission denied/);
    await assert.rejects(db.exec('update orders set payment_status=\'paid\''), /permission denied/);
  } finally { await db.exec('RESET ROLE'); }
});

test('service_role can execute RPC and migration can be reapplied preserving data', async () => {
  await db.exec('SET ROLE service_role');
  let order;
  try { order = await rpc(db, 'create_shop_order', args()); }
  finally { await db.exec('RESET ROLE'); }
  await db.exec(fs.readFileSync(migrationPath, 'utf8'));
  assert.equal((await db.query('select id from orders')).rows[0].id, order.id);
});

test('Unicode delivery note is preserved and length is checked by codepoint', async () => {
  const note = 'Giao\u200b hàng 🦊\u{E0001}';
  const order = await rpc(db, 'create_shop_order', { ...args(), p_note: note });
  assert.equal(order.note, note);
  await assert.rejects(rpc(db, 'create_shop_order', { ...args(), p_note: '🦊'.repeat(501) }), /INVALID_FIELD/);
});

test('session binding requires literal cs_test_ prefix', async () => {
  const order = await rpc(db, 'create_shop_order', args('stripe'));
  await assert.rejects(rpc(db, 'attach_stripe_session', { p_order_id: order.id, p_session_id: 'csXtestYother' }), /PAYMENT_MISMATCH/);
  await assert.rejects(rpc(db, 'finalize_stripe_order', payment(order, { p_session_id: 'csXtestYother' })), /PAYMENT_MISMATCH/);
});

test('real handlers plus SQL and signed Stripe SDK event complete payment once', async () => {
  const { loader } = require('./load-ts.cjs');
  const Stripe = require('stripe');
  const { createOrderHandlers } = loader()(path.resolve(__dirname, '../order-handlers.ts'));
  const sdk = new Stripe('sk_test_offline_fixture');
  const secret = 'whsec_offline_fixture';
  const handlers = createOrderHandlers({
    authenticate: async () => userA,
    rpc: (name, params) => rpc(db, name, params),
    shopOrigin: () => 'http://localhost:3000',
    createCheckout: async params => {
      assert.equal(params.line_items[0].price_data.unit_amount, 12500);
      return { id: 'cs_test_integration', url: 'https://checkout.stripe.com/test', livemode: false };
    },
    verifyEvent: (body, signature) => sdk.webhooks.constructEvent(body, signature, secret),
  });
  const response = await handlers.create(new Request('http://localhost/api/orders', {
    method: 'POST', headers: { Authorization: 'Bearer offline-token', 'Content-Type': 'application/json' },
    body: JSON.stringify({ items: [{ product_id: 1, quantity: 2, price: 1 }], payment_method: 'stripe',
      recipient_name: 'Test', recipient_phone: '0900000000', address_line: 'Test', ward: 'Test', province: 'Test' }),
  }));
  assert.equal(response.status, 201);
  const created = await response.json();
  assert.equal(created.total, 25000);
  assert.equal(created.payment_status, 'unpaid');
  const payload = JSON.stringify({ type: 'checkout.session.completed', livemode: false, data: { object: {
    id: 'cs_test_integration', mode: 'payment', livemode: false, payment_status: 'paid',
    metadata: { order_id: created.order_id }, amount_total: 25000, currency: 'vnd',
  } } });
  for (let i = 0; i < 2; i++) {
    const webhook = await handlers.webhook(new Request('http://localhost/api/stripe/webhook', {
      method: 'POST', headers: { 'stripe-signature': sdk.webhooks.generateTestHeaderString({ payload, secret }) }, body: payload,
    }));
    assert.equal(webhook.status, 200);
  }
  assert.deepEqual((await db.query('select status,payment_status from orders')).rows[0], { status: 'processing', payment_status: 'paid' });
  assert.equal((await db.query('select stock from products where id=1')).rows[0].stock, 3);
});

test('migration preserves pre-existing legacy orders and original address', async () => {
  const legacy = new PGlite();
  try {
    await legacy.exec(fixture);
    await legacy.query('insert into orders(user_id,items,total,shipping_address,status) values($1,$2,100,$3,$4)', [userA, '[]', 'Legacy address', 'delivered']);
    await legacy.exec(fs.readFileSync(migrationPath, 'utf8'));
    const row = (await legacy.query('select shipping_address,status,recipient_name from orders')).rows[0];
    assert.deepEqual(row, { shipping_address: 'Legacy address', status: 'delivered', recipient_name: null });
  } finally { await legacy.close(); }
});
