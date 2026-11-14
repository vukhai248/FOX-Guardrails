// Run against the frontend checkout after npm install:
// node docs/reports/checks/a1-chat-proxy.cjs <absolute-path-to-web_ui>
// Executes the actual Next route; only the upstream network is replaced.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const Module = require('node:module');
const { test } = require('node:test');

const webRoot = path.resolve(process.argv[2] || 'web_ui');
const frontendRequire = Module.createRequire(path.join(webRoot, 'package.json'));
const ts = frontendRequire('typescript');
const routePath = path.join(webRoot, 'src/app/api/chat/route.ts');
const compiled = ts.transpileModule(fs.readFileSync(routePath, 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
});
const routeModule = new Module(routePath);
routeModule.paths = Module._nodeModulePaths(path.dirname(routePath));
routeModule._compile(compiled.outputText, routePath);
const { POST } = routeModule.exports;

function setup(t, flag) {
  const originalFetch = global.fetch;
  const keys = ['NEXT_PUBLIC_ALLOW_MOCK_CHAT', 'NEXT_PUBLIC_RAG_SERVICE_URL'];
  const originalEnv = Object.fromEntries(keys.map(key => [key, process.env[key]]));
  if (flag === undefined) delete process.env.NEXT_PUBLIC_ALLOW_MOCK_CHAT;
  else process.env.NEXT_PUBLIC_ALLOW_MOCK_CHAT = flag;
  process.env.NEXT_PUBLIC_RAG_SERVICE_URL = 'http://127.0.0.1:59999/chat';
  t.after(() => {
    global.fetch = originalFetch;
    for (const [key, value] of Object.entries(originalEnv)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
  });
}

function request() {
  return new Request('http://localhost/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: 'tìm laptop',
      session_id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
      user_token: 'offline-test-token',
    }),
  });
}

for (const flag of [undefined, 'false', 'TRUE']) {
  test(`network failure returns 503 without fake answer; mock=${flag}`, async t => {
    setup(t, flag);
    global.fetch = async () => { throw new Error('offline backend'); };
    const response = await POST(request());
    const data = await response.json();
    assert.equal(response.status, 503);
    assert.equal(data.error.code, 'BACKEND_UNAVAILABLE');
    assert.equal(typeof data.error.message, 'string');
    assert.equal(data.reply, undefined);
  });
}

test('HTTP upstream failure returns 503 without fake answer', async t => {
  setup(t);
  global.fetch = async () => new Response('unavailable', { status: 500 });
  const response = await POST(request());
  const data = await response.json();
  assert.equal(response.status, 503);
  assert.equal(data.error.code, 'BACKEND_UNAVAILABLE');
  assert.equal(data.reply, undefined);
});

test('malformed backend response returns 503', async t => {
  setup(t);
  global.fetch = async () => new Response('not json', { status: 200 });
  const response = await POST(request());
  assert.equal(response.status, 503);
  assert.equal((await response.json()).error.code, 'BACKEND_UNAVAILABLE');
});

test('only explicit true enables mock fallback', async t => {
  setup(t, 'true');
  global.fetch = async () => { throw new Error('offline backend'); };
  const response = await POST(request());
  assert.equal(response.status, 200);
  assert.match((await response.json()).reply, /Mock Fallback/);
});

test('successful backend reply and session are forwarded unchanged', async t => {
  setup(t);
  let forwarded;
  global.fetch = async (url, options) => {
    forwarded = { url, ...options };
    return Response.json({ reply: 'real backend answer', session_id: 'returned-session', sources: [] });
  };
  const response = await POST(request());
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), {
    reply: 'real backend answer', session_id: 'returned-session', sources: [],
  });
  assert.equal(forwarded.headers.Authorization, 'Bearer offline-test-token');
  assert.deepEqual(JSON.parse(forwarded.body), {
    message: 'tìm laptop',
    session_id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
    user_token: 'offline-test-token',
  });
});
