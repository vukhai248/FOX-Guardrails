-- Migration 0 (chạy TRƯỚC 5 migration Phần A). Chỉ cộng thêm: tạo 3 bảng mà code đang dùng
-- nhưng Supabase thật chưa có (chat_logs, user_roles, support_tickets). Không DROP gì.
-- Schema lấy từ database/setup.sql:73,87,109; quyền chặt hơn setup.sql (xem chú thích từng bảng).
BEGIN;

-- user_roles: nguồn quyền admin/staff duy nhất (web_ui/src/lib/server/auth.ts). Chỉ server đọc/ghi.
CREATE TABLE IF NOT EXISTS public.user_roles (
  user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  role text NOT NULL CHECK (role IN ('admin', 'staff', 'customer')),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc'::text, now())
);
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.user_roles FROM PUBLIC, anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.user_roles TO service_role;

-- chat_logs: rag-service ghi, admin đọc, đều bằng service_role. Migration chat_logs_guard thêm cột guard.
CREATE TABLE IF NOT EXISTS public.chat_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id varchar(100) NOT NULL,
  user_id uuid,
  role varchar(20) NOT NULL CHECK (role IN ('user', 'agent', 'tool', 'system')),
  message text NOT NULL,
  tool_used varchar(100),
  risk_level varchar(20) CHECK (risk_level IN ('low', 'medium', 'high')),
  created_at timestamptz NOT NULL DEFAULT timezone('utc'::text, now())
);
ALTER TABLE public.chat_logs ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.chat_logs FROM PUBLIC, anon, authenticated;
GRANT SELECT, INSERT ON TABLE public.chat_logs TO service_role;

-- support_tickets: khách tạo ticket từ trang tài khoản/chat-widget, bot tạo qua JWT của khách
-- (rag-service/src/d_tools/support_ticket.py), admin cập nhật bằng service_role.
CREATE TABLE IF NOT EXISTS public.support_tickets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id uuid NOT NULL,
  order_id uuid REFERENCES public.orders(id) ON DELETE SET NULL,
  category varchar(50) NOT NULL CHECK (category IN ('advisory', 'negotiation', 'technical', 'attack_flagged', 'other')),
  risk_level varchar(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
  created_by varchar(20) NOT NULL CHECK (created_by IN ('agent', 'staff', 'customer')),
  status varchar(50) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved')),
  assigned_staff_id uuid,
  note text,
  created_at timestamptz NOT NULL DEFAULT timezone('utc'::text, now())
);
CREATE INDEX IF NOT EXISTS support_tickets_customer_created_idx
  ON public.support_tickets (customer_id, created_at DESC);
ALTER TABLE public.support_tickets ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.support_tickets FROM PUBLIC, anon, authenticated;
GRANT SELECT ON TABLE public.support_tickets TO authenticated;
-- Khách chỉ được ghi đúng các cột client đang gửi; sau khi tạo chỉ được sửa note (luồng chat 2 chiều).
-- Khác setup.sql: setup.sql cho khách sửa mọi cột (tự đổi status, risk_level, assigned_staff_id).
GRANT INSERT (customer_id, order_id, category, risk_level, created_by, status, note)
  ON TABLE public.support_tickets TO authenticated;
GRANT UPDATE (note) ON TABLE public.support_tickets TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.support_tickets TO service_role;

DROP POLICY IF EXISTS tickets_select_own ON public.support_tickets;
CREATE POLICY tickets_select_own ON public.support_tickets
  FOR SELECT TO authenticated USING (auth.uid() = customer_id);

DROP POLICY IF EXISTS tickets_insert_own ON public.support_tickets;
-- Ticket mới luôn mở, rủi ro thấp, do khách hoặc bot (dưới JWT khách) tạo, và chỉ gắn được đơn của chính khách.
CREATE POLICY tickets_insert_own ON public.support_tickets
  FOR INSERT TO authenticated WITH CHECK (
    auth.uid() = customer_id
    AND created_by IN ('customer', 'agent')
    AND status = 'open'
    AND risk_level = 'low'
    AND assigned_staff_id IS NULL
    AND (order_id IS NULL OR EXISTS (
      SELECT 1 FROM public.orders o WHERE o.id = order_id AND o.user_id = auth.uid()))
  );

DROP POLICY IF EXISTS tickets_update_own ON public.support_tickets;
CREATE POLICY tickets_update_own ON public.support_tickets
  FOR UPDATE TO authenticated USING (auth.uid() = customer_id) WITH CHECK (auth.uid() = customer_id);

NOTIFY pgrst, 'reload schema';
COMMIT;
