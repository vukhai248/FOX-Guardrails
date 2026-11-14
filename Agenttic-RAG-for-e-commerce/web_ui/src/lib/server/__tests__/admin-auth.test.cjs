const {test}=require('node:test');const assert=require('node:assert/strict');const path=require('node:path');
const {loader}=require('./load-ts.cjs');
const authPath=path.resolve(__dirname,'../auth.ts');
const envKeys=['NEXT_PUBLIC_SUPABASE_URL','NEXT_PUBLIC_SUPABASE_ANON_KEY','SUPABASE_SERVICE_ROLE_KEY'];
function clearEnv(t){const saved=Object.fromEntries(envKeys.map(k=>[k,process.env[k]]));for(const k of envKeys)delete process.env[k];
  t.after(()=>{for(const k of envKeys){if(saved[k]===undefined)delete process.env[k];else process.env[k]=saved[k];}});}
test('admin module and routes import without creating any client; missing config returns safe 500',async t=>{
  clearEnv(t);let creates=0;
  const load=loader({'@supabase/supabase-js':{createClient:()=>{creates++;throw Error('must not construct');}}});
  const auth=load(authPath);assert.equal(creates,0);
  assert.equal((await auth.requireRole(new Request('http://localhost'))).errorResponse.status,401);
  for(const name of ['orders','tickets','users','chat-logs']){
    const route=load(path.resolve(__dirname,`../../../app/api/admin/${name}/route.ts`));
    assert.equal(creates,0);
    const response=await route.GET(new Request('http://localhost',{headers:{Authorization:'Bearer token'}}));
    assert.equal(response.status,500);const body=await response.json();assert.equal(body.error.code,'INTERNAL_ERROR');
    assert.doesNotMatch(JSON.stringify(body),/SUPABASE|must not construct|token/);
  }
  assert.equal(creates,0);
});
test('lazy admin proxy binds methods, reuses client and role comes from DB not user metadata',async t=>{
  clearEnv(t);process.env.NEXT_PUBLIC_SUPABASE_URL='https://offline.supabase.invalid';
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY='anon';process.env.SUPABASE_SERVICE_ROLE_KEY='service';
  const keys=[];const admin={from(name){assert.equal(this,admin);assert.equal(name,'user_roles');return {select:()=>({eq:()=>({maybeSingle:async()=>({data:{role:'customer'},error:null})})})};}};
  const auth=loader({'@supabase/supabase-js':{createClient:(url,key)=>{keys.push(key);return key==='service'?admin:{auth:{getUser:async()=>({data:{user:{id:'u1',user_metadata:{role:'admin'}}},error:null})}};}}})(authPath);
  assert.deepEqual(keys,[]);auth.supabaseAdmin.from('user_roles');auth.supabaseAdmin.from('user_roles');assert.deepEqual(keys,['service']);
  const result=await auth.requireRole(new Request('http://localhost',{headers:{Authorization:'Bearer token'}}),['admin']);
  assert.equal(result.errorResponse.status,403);assert.deepEqual(keys,['service','anon']);
});
