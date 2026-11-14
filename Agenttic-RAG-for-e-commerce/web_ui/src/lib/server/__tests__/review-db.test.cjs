const { test }=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const {PGlite}=require(process.env.PGLITE_MODULE_PATH||'@electric-sql/pglite');
const {fixture,userA,userB,args,rpc}=require('./payment-fixture.cjs');
test('review SQL enforces owner purchase and Unicode length with client writes disabled',async()=>{
  const db=new PGlite();
  try{
    await db.exec(fixture);
    await db.exec(`CREATE TABLE public.reviews(id uuid PRIMARY KEY DEFAULT gen_random_uuid(),product_id int NOT NULL REFERENCES public.products(id),
      user_id uuid NOT NULL,rating int NOT NULL CHECK(rating BETWEEN 1 AND 5),comment text,created_at timestamptz NOT NULL DEFAULT now());
      ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;
      CREATE POLICY read_reviews ON public.reviews FOR SELECT USING(true);
      GRANT ALL ON public.reviews TO anon,authenticated,service_role;
      INSERT INTO public.products(id,name,final_price,stock)VALUES(1,'Phone',12500,20);`);
    await db.exec(fs.readFileSync(path.resolve(__dirname,'../../../../../database/migrations/2026-11_payment_and_address.sql'),'utf8'));
    const sql=fs.readFileSync(path.resolve(__dirname,'../../../../../database/migrations/2026-11_product_reviews.sql'),'utf8');
    await db.exec(sql);await db.exec(sql);
    const review=(user=userA,comment='Tốt\u200b👍\u{E0001}')=>rpc(db,'create_product_review',{p_user_id:user,p_product_id:1,p_rating:5,p_comment:comment});
    await assert.rejects(review(),/NOT_PURCHASED/);
    const order=await rpc(db,'create_shop_order',args());
    const result=await review();assert.ok(result.review_id);
    assert.equal((await db.query('SELECT comment FROM public.reviews')).rows[0].comment,'Tốt\u200b👍\u{E0001}');
    await assert.rejects(review(userB),/NOT_PURCHASED/);
    await assert.rejects(review(userA,'👍'.repeat(1001)),/INVALID_FIELD/);
    await db.query("UPDATE public.orders SET status='cancelled' WHERE id=$1",[order.id]);
    await assert.rejects(review(),/NOT_PURCHASED/);
    for(const role of ['anon','authenticated']){
      await db.exec(`SET ROLE ${role}`);
      assert.equal((await db.query('SELECT count(*)::int as n FROM public.reviews')).rows[0].n,1);
      await assert.rejects(review(),/permission denied/);
      await assert.rejects(db.query("INSERT INTO public.reviews(product_id,user_id,rating)VALUES(1,$1,5)",[userA]),/permission denied/);
      await db.exec('RESET ROLE');
    }
  }finally{await db.close();}
});
