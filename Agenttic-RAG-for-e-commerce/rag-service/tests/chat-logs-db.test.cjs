// Minimal local PostgreSQL fixture; never execute database/setup.sql.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { PGlite } = require(process.env.PGLITE_MODULE_PATH || '@electric-sql/pglite');
const migrationPath = path.resolve(__dirname, '../../database/migrations/2026-11_chat_logs_guard.sql');

test('chat log migration preserves rows, defaults decision arrays and enforces server-only access', async () => {
  const db = new PGlite();
  try {
    await db.exec(`
      CREATE ROLE anon;
      CREATE ROLE authenticated;
      CREATE ROLE service_role BYPASSRLS;
      GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
      CREATE TABLE public.chat_logs (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(), session_id varchar(100) NOT NULL,
        user_id uuid, role varchar(20) NOT NULL CHECK(role IN ('user','agent','tool','system')),
        message text NOT NULL, tool_used varchar(100),
        risk_level varchar(20) CHECK(risk_level IN ('low','medium','high')),
        created_at timestamptz NOT NULL DEFAULT now()
      );
      GRANT ALL ON public.chat_logs TO anon, authenticated, service_role;
      INSERT INTO public.chat_logs(session_id,role,message) VALUES('legacy','user','keep this row');
    `);
    const migration = fs.readFileSync(migrationPath, 'utf8');
    await db.exec(migration);
    await db.exec(migration);
    assert.deepEqual((await db.query('SELECT message,guard_decision_ids FROM public.chat_logs')).rows,
      [{ message: 'keep this row', guard_decision_ids: [] }]);
    for (const role of ['anon', 'authenticated']) {
      await db.exec(`SET ROLE ${role}`);
      await assert.rejects(db.query('SELECT * FROM public.chat_logs'), /permission denied/);
      await assert.rejects(db.query("INSERT INTO public.chat_logs(session_id,role,message) VALUES('spoof','user','fake')"), /permission denied/);
      await db.exec('RESET ROLE');
    }
    await db.exec('SET ROLE service_role');
    await db.query(`INSERT INTO public.chat_logs(session_id,role,message,risk_level,guard_decision_ids)
      VALUES('s1','user','<PHONE>','low',ARRAY['input-1']),('s1','agent','<PHONE>','medium',ARRAY['output-1'])`);
    assert.equal((await db.query("SELECT count(*)::int as n FROM public.chat_logs WHERE session_id='s1'")).rows[0].n, 2);
    await assert.rejects(db.query("INSERT INTO public.chat_logs(session_id,role,message,guard_decision_ids) VALUES('s1','user','bad',NULL)"), /null value/);
    await assert.rejects(db.query("INSERT INTO public.chat_logs(session_id,role,message) VALUES('s1','assistant','bad role')"), /check constraint/);
    await db.exec('RESET ROLE');
  } finally {
    await db.close();
  }
});
