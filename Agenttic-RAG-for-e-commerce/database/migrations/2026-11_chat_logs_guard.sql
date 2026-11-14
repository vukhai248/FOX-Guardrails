-- A5: additive migration. Owner applies after review; never run setup.sql.
BEGIN;

ALTER TABLE public.chat_logs
  ADD COLUMN IF NOT EXISTS guard_decision_ids text[] NOT NULL DEFAULT '{}'::text[];

ALTER TABLE public.chat_logs ENABLE ROW LEVEL SECURITY;
-- Admin reads and rag-service writes use server credentials, never a browser JWT.
REVOKE ALL ON TABLE public.chat_logs FROM anon, authenticated;
GRANT SELECT, INSERT ON TABLE public.chat_logs TO service_role;

CREATE INDEX IF NOT EXISTS chat_logs_session_created_idx
  ON public.chat_logs (session_id, created_at);

COMMIT;
