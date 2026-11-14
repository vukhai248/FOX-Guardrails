const {test,before,after,beforeEach}=require('node:test');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const {PGlite}=require(process.env.PGLITE_MODULE_PATH||'@electric-sql/pglite');
const {fixture,args,rpc}=require('./payment-fixture.cjs');
let db;const newMigration=path.resolve(__dirname,'../../../../../database/migrations/2026-11_expired_checkout.sql');
before(async()=>{db=new PGlite();await db.exec(fixture);
  await db.exec(fs.readFileSync(path.resolve(__dirname,'../../../../../database/migrations/2026-11_payment_and_address.sql'),'utf8'));
  await db.exec(fs.readFileSync(newMigration,'utf8'));});
after(async()=>{if(db)await db.close();});
beforeEach(async()=>{await db.exec("TRUNCATE public.orders,public.products;INSERT INTO public.products(id,name,final_price,stock)VALUES(1,'Phone',12500,5)");});
test('expiry is idempotent for its unpaid bound session without affecting inventory',async()=>{
  const order=await rpc(db,'create_shop_order',args('stripe'));
  await rpc(db,'attach_stripe_session',{p_order_id:order.id,p_session_id:'cs_test_expired'});
  for(let i=0;i<2;i++)await rpc(db,'fail_stripe_order',{p_order_id:order.id,p_session_id:'cs_test_expired'});
  const row=(await db.query('SELECT status,payment_status,stripe_session_id FROM orders WHERE id=$1',[order.id])).rows[0];
  assert.deepEqual(row,{status:'cancelled',payment_status:'failed',stripe_session_id:'cs_test_expired'});
  assert.equal((await db.query('SELECT stock FROM products')).rows[0].stock,5);
});
test('expiry cannot change paid orders, COD, or an order bound to another session',async()=>{
  const paid=await rpc(db,'create_shop_order',args('stripe'));
  await rpc(db,'finalize_stripe_order',{p_order_id:paid.id,p_session_id:'cs_test_paid',p_amount_total:25000,p_currency:'vnd'});
  const before=(await db.query('SELECT * FROM orders WHERE id=$1',[paid.id])).rows;
  await rpc(db,'fail_stripe_order',{p_order_id:paid.id,p_session_id:'cs_test_paid'});
  assert.deepEqual((await db.query('SELECT * FROM orders WHERE id=$1',[paid.id])).rows,before);
  const other=await rpc(db,'create_shop_order',args('stripe'));
  await rpc(db,'attach_stripe_session',{p_order_id:other.id,p_session_id:'cs_test_new'});
  await rpc(db,'fail_stripe_order',{p_order_id:other.id,p_session_id:'cs_test_old'});
  assert.equal((await db.query('SELECT payment_status FROM orders WHERE id=$1',[other.id])).rows[0].payment_status,'unpaid');
  const cod=await rpc(db,'create_shop_order',args('cod',[{product_id:1,quantity:1}]));
  await rpc(db,'fail_stripe_order',{p_order_id:cod.id,p_session_id:'cs_test_expired'});
  assert.equal((await db.query('SELECT payment_status FROM orders WHERE id=$1',[cod.id])).rows[0].payment_status,'cod_pending');
});
test('expiry handles an unbound session; overload keeps old cleanup and service-only permissions',async()=>{
  const order=await rpc(db,'create_shop_order',args('stripe'));
  await rpc(db,'fail_stripe_order',{p_order_id:order.id,p_session_id:'cs_test_unbound'});
  assert.equal((await db.query('SELECT payment_status FROM orders WHERE id=$1',[order.id])).rows[0].payment_status,'failed');
  const cleanup=await rpc(db,'create_shop_order',args('stripe'));
  await rpc(db,'fail_stripe_order',{p_order_id:cleanup.id});
  assert.equal((await db.query('SELECT payment_status FROM orders WHERE id=$1',[cleanup.id])).rows[0].payment_status,'failed');
  await db.exec(fs.readFileSync(newMigration,'utf8'));
  for(const role of ['anon','authenticated']){await db.exec(`SET ROLE ${role}`);
    await assert.rejects(rpc(db,'fail_stripe_order',{p_order_id:order.id,p_session_id:'cs_test_unbound'}),/permission denied/);
    await db.exec('RESET ROLE');}
  await db.exec('SET ROLE service_role');await rpc(db,'fail_stripe_order',{p_order_id:order.id,p_session_id:'cs_test_unbound'});await db.exec('RESET ROLE');
});

test('deleted product after payment is acknowledged as permanent with only order ID/code logged',async t=>{
  const {loader}=require('./load-ts.cjs');
  const {createOrderHandlers}=loader()(path.resolve(__dirname,'../order-handlers.ts'));
  const order=await rpc(db,'create_shop_order',args('stripe'));
  await db.query('DELETE FROM products WHERE id=1');
  const logged=[];t.mock.method(console,'error',(...values)=>logged.push(values));
  const handlers=createOrderHandlers({rpc:(name,params)=>rpc(db,name,params),verifyEvent:()=>({
    type:'checkout.session.completed',livemode:false,data:{object:{id:'cs_test_deleted',livemode:false,mode:'payment',
      payment_status:'paid',metadata:{order_id:order.id},amount_total:25000,currency:'vnd'}}})});
  const response=await handlers.webhook(new Request('http://localhost/api/stripe/webhook',{method:'POST',headers:{'stripe-signature':'offline'},body:'{}'}));
  assert.equal(response.status,200);assert.deepEqual(await response.json(),{received:true});
  assert.deepEqual(logged,[[{order_id:order.id,code:'INVALID_PRODUCT'}]]);
  assert.equal((await db.query('SELECT payment_status FROM orders WHERE id=$1',[order.id])).rows[0].payment_status,'unpaid');
});
