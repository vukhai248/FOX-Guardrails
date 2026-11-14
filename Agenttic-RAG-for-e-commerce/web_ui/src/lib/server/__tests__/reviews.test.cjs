const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { loader } = require('./load-ts.cjs');
const load = loader();
const { createReviewHandler } = load(path.resolve(__dirname,'../review-handlers.ts'));
function request(body, token='token-a') {
  return new Request('http://localhost/api/reviews', {method:'POST',headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{})},body:JSON.stringify(body)});
}
function context(extra={}) {
  const calls=[];
  const deps={authenticate:async token=>token==='token-a'?'verified-user':null,
    rpc:async(name,args)=>{calls.push({name,args});return {review_id:'review-1'};},...extra};
  return {calls,deps,handler:createReviewHandler(deps)};
}
test('review route authenticates, injects verified owner and preserves Unicode exactly',async()=>{
  const ctx=context(); const comment='Tốt\u200b👍\u{E0001}';
  const response=await ctx.handler(request({product_id:1,rating:5,comment,user_id:'victim'}));
  assert.equal(response.status,201); assert.deepEqual(await response.json(),{review_id:'review-1'});
  assert.deepEqual(ctx.calls,[{name:'create_product_review',args:{p_user_id:'verified-user',p_product_id:1,p_rating:5,p_comment:comment}}]);
});
test('review requires authentication and actual purchase server-side',async()=>{
  for(const token of [null,'bad']) {
    const ctx=context();assert.equal((await ctx.handler(request({product_id:1,rating:5,comment:''},token))).status,401);
    assert.equal(ctx.calls.length,0);
  }
  const ctx=context({rpc:async()=>{throw Error('NOT_PURCHASED');}});
  const response=await ctx.handler(request({product_id:1,rating:5,comment:''}));
  assert.equal(response.status,403); assert.equal((await response.json()).error.code,'NOT_PURCHASED');
});
test('review bounds are codepoint-based and invalid inputs never reach DB',async()=>{
  for(const body of [null,{}, {product_id:0,rating:5,comment:''},{product_id:2147483648,rating:5,comment:''},{product_id:1,rating:6,comment:''},
    {product_id:1,rating:1.5,comment:''},{product_id:1,rating:5,comment:'👍'.repeat(1001)}]){
    const ctx=context();assert.equal((await ctx.handler(request(body))).status,400);assert.equal(ctx.calls.length,0);
  }
  const ctx=context();assert.equal((await ctx.handler(request({product_id:1,rating:5,comment:'👍'.repeat(1000)}))).status,201);
});
test('review route registration exists and internal errors do not leak',async()=>{
  const ctx=context();
  const route=loader({'@/lib/server/payment-runtime':{paymentDependencies:ctx.deps}})(path.resolve(__dirname,'../../../app/api/reviews/route.ts'));
  assert.equal((await route.POST(request({product_id:1,rating:4,comment:'good'}))).status,201);
  const bad=context({rpc:async()=>{throw Error('private DB address 0912345678');}});
  const response=await bad.handler(request({product_id:1,rating:4,comment:'good'}));
  assert.equal(response.status,500);assert.doesNotMatch(JSON.stringify(await response.json()),/private|0912345678/);
});
