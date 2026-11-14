const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { PGlite } = require(process.env.PGLITE_MODULE_PATH || '@electric-sql/pglite');
const { fixture, userA, userB } = require('../../web_ui/src/lib/server/__tests__/payment-fixture.cjs');
const ns = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const orderId = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
const reviewId = 'cccccccc-cccc-4ccc-8ccc-cccccccccccc';
const hash = 'a'.repeat(64);
const cases = () => [
  { case_id: 'order-a', table: 'orders', row_id: orderId, payload_hash: hash, fields: {
    user_id: userA, items: [{ product_id: 1, quantity: 2 }], note: 'Giao\u200b 🦊\u{E0001}' } },
  { case_id: 'review-a', table: 'reviews', row_id: reviewId, payload_hash: hash, fields: {
    user_id: userA, product_id: 1, rating: 5, comment: 'Tốt\u200b👍' } },
];

async function setup() {
  const db = new PGlite();
  await db.exec(fixture);
  await db.exec(`
    CREATE TABLE auth.users(id uuid PRIMARY KEY, raw_app_meta_data jsonb NOT NULL DEFAULT '{}');
    CREATE TABLE public.reviews(id uuid PRIMARY KEY, user_id uuid NOT NULL, product_id int REFERENCES public.products(id),
      rating int CHECK(rating BETWEEN 1 AND 5), comment text, created_at timestamptz DEFAULT now());
    CREATE TABLE public.support_tickets(id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      order_id uuid REFERENCES public.orders(id) ON DELETE SET NULL);
    INSERT INTO public.products(id,name,final_price,stock) VALUES(1,'Synthetic phone',12500,20);
    INSERT INTO auth.users VALUES('${userA}','{"bench_seed_namespace":"${ns}","bench_seed_alias":"bench_customer_a"}'),
      ('${userB}','{}');
  `);
  await db.exec(fs.readFileSync(path.resolve(__dirname, '../../database/migrations/2026-11_payment_and_address.sql'), 'utf8'));
  await db.exec(fs.readFileSync(path.resolve(__dirname, '../../database/migrations/2026-11_seed_bench.sql'), 'utf8'));
  return db;
}
async function seed(db, rows, reset = false) {
  return (await db.query('SELECT public.seed_bench_cases($1::uuid,$2::jsonb,$3::boolean) as result', [ns, JSON.stringify(rows), reset])).rows[0].result;
}

test('seed twice is identical; reset affects mapped rows only and never stock or legacy data', async () => {
  const db = await setup();
  try {
    await db.exec(`INSERT INTO public.orders(user_id,items,total,shipping_address) VALUES('${userB}','[]',1,'real legacy address')`);
    const first = await seed(db, cases());
    const snapshot = (await db.query('SELECT * FROM public.orders ORDER BY id')).rows;
    assert.deepEqual(await seed(db, cases()), first);
    assert.deepEqual((await db.query('SELECT * FROM public.orders ORDER BY id')).rows, snapshot);
    assert.equal((await db.query('SELECT stock FROM public.products')).rows[0].stock, 20);
    const order = (await db.query('SELECT * FROM public.orders WHERE id=$1', [orderId])).rows[0];
    assert.equal(Number(order.total), 25000);
    assert.equal(order.note, 'Giao\u200b 🦊\u{E0001}');
    await seed(db, [], true);
    assert.equal((await db.query('SELECT count(*)::int as n FROM public.bench_cases')).rows[0].n, 0);
    assert.deepEqual((await db.query('SELECT shipping_address FROM public.orders')).rows, [{ shipping_address: 'real legacy address' }]);
    assert.equal((await db.query('SELECT count(*)::int as n FROM public.reviews')).rows[0].n, 0);
    await db.exec(fs.readFileSync(path.resolve(__dirname, '../../database/migrations/2026-11_seed_bench.sql'), 'utf8'));
  } finally { await db.close(); }
});

test('invalid whole batch rolls back rows and mappings; changed case needs explicit reset', async () => {
  const db = await setup();
  try {
    const invalid = cases(); invalid[1].fields.product_id = 999;
    await assert.rejects(seed(db, invalid));
    assert.equal((await db.query('SELECT count(*)::int as n FROM public.orders')).rows[0].n, 0);
    assert.equal((await db.query('SELECT count(*)::int as n FROM public.bench_cases')).rows[0].n, 0);
    await seed(db, cases());
    const changed = cases(); changed[0].payload_hash = 'b'.repeat(64);
    await assert.rejects(seed(db, changed), /BENCH_CASE_CHANGED/);
    await assert.rejects(seed(db, invalid, true));
    assert.equal((await db.query('SELECT count(*)::int as n FROM public.bench_cases')).rows[0].n, 2);
    await seed(db, changed, true);
  } finally { await db.close(); }
});

test('cannot seed real users, overwrite unmapped IDs, or reset externally referenced orders', async () => {
  const db = await setup();
  try {
    const foreign = cases(); foreign[0].fields.user_id = userB;
    await assert.rejects(seed(db, foreign), /BENCH_OWNER_MISMATCH/);
    await db.query(`INSERT INTO public.orders(id,user_id,items,total,shipping_address) VALUES($1,$2,'[]',1,'untouched')`, [orderId, userB]);
    await assert.rejects(seed(db, cases()), /BENCH_ROW_COLLISION/);
    assert.equal((await db.query('SELECT shipping_address FROM public.orders WHERE id=$1', [orderId])).rows[0].shipping_address, 'untouched');
    await db.query('DELETE FROM public.orders WHERE id=$1', [orderId]);
    await seed(db, cases());
    await db.query('INSERT INTO public.support_tickets(order_id) VALUES($1)', [orderId]);
    await assert.rejects(seed(db, [], true), /BENCH_REFERENCED/);
    assert.equal((await db.query('SELECT order_id FROM public.support_tickets')).rows[0].order_id, orderId);
  } finally { await db.close(); }
});

test('mappings and seed RPC are inaccessible to clients; service role can only use controlled writes', async () => {
  const db = await setup();
  try {
    for (const role of ['anon', 'authenticated']) {
      await db.exec(`SET ROLE ${role}`);
      await assert.rejects(db.query('SELECT * FROM public.bench_cases'), /permission denied/);
      await assert.rejects(seed(db, []), /permission denied/);
      await db.exec('RESET ROLE');
    }
    await db.exec('SET ROLE service_role');
    assert.equal((await seed(db, cases())).length, 2);
    await assert.rejects(db.query('DELETE FROM public.bench_cases'), /permission denied/);
    await seed(db, [], true);
  } finally { await db.close(); }
});

test('reset refuses transferred ownership and preserves another namespace', async () => {
  const db = await setup();
  try {
    await seed(db, cases());
    await db.query('UPDATE public.orders SET user_id=$1 WHERE id=$2', [userB, orderId]);
    await assert.rejects(seed(db, [], true), /BENCH_OWNER_MISMATCH/);
    assert.equal((await db.query('SELECT user_id FROM public.orders WHERE id=$1', [orderId])).rows[0].user_id, userB);
    await db.query('UPDATE public.orders SET user_id=$1 WHERE id=$2', [userA, orderId]);
    const other = 'dddddddd-dddd-4ddd-8ddd-dddddddddddd';
    await db.query('UPDATE auth.users SET raw_app_meta_data=$1 WHERE id=$2', [JSON.stringify({bench_seed_namespace:other,bench_seed_alias:'bench_customer_b'}),userB]);
    const rows = cases().slice(1); rows[0].fields.user_id=userB; rows[0].row_id='eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee';
    await db.query('SELECT public.seed_bench_cases($1,$2::jsonb,false)', [other,JSON.stringify(rows)]);
    await seed(db, [], true);
    assert.equal((await db.query('SELECT count(*)::int as n FROM public.bench_cases WHERE namespace=$1', [other])).rows[0].n, 1);
    assert.equal((await db.query('SELECT user_id FROM public.reviews')).rows[0].user_id, userB);
  } finally { await db.close(); }
});

test('recreated Auth account cannot silently reuse mappings owned by the old UUID',async()=>{
  const db=await setup();
  try{
    await seed(db,cases());
    await db.query('UPDATE auth.users SET raw_app_meta_data=$1 WHERE id=$2',[
      JSON.stringify({bench_seed_namespace:ns,bench_seed_alias:'bench_customer_a'}),userB]);
    const recreated=cases();for(const row of recreated)row.fields.user_id=userB;
    await assert.rejects(seed(db,recreated),/BENCH_OWNER_MISMATCH/);
    assert.equal((await db.query('SELECT user_id FROM public.orders WHERE id=$1',[orderId])).rows[0].user_id,userA);
  }finally{await db.close();}
});
