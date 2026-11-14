// Deliberately minimal fixture. Never execute database/setup.sql, even in tests.
const fixture = `
CREATE ROLE anon;
CREATE ROLE authenticated;
CREATE ROLE service_role BYPASSRLS;
CREATE SCHEMA auth;
CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql AS
  $$ SELECT nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
GRANT USAGE ON SCHEMA public, auth TO anon, authenticated, service_role;
CREATE TABLE public.products (
  id int PRIMARY KEY, name text NOT NULL, final_price numeric NOT NULL,
  stock integer NOT NULL, thumbnail text
);
CREATE TABLE public.orders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL,
  status varchar(50) NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','processing','shipping','delivered','cancelled')),
  items jsonb NOT NULL, total numeric(12,2) NOT NULL CHECK(total >= 0),
  shipping_address text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY orders_select_own ON public.orders FOR SELECT TO authenticated USING(auth.uid() = user_id);
CREATE POLICY orders_insert_own ON public.orders FOR INSERT TO authenticated WITH CHECK(auth.uid() = user_id);
GRANT ALL ON public.products, public.orders TO anon, authenticated, service_role;
`;

const userA = '11111111-1111-4111-8111-111111111111';
const userB = '22222222-2222-4222-8222-222222222222';
const args = (method = 'cod', items = [{ product_id: 1, quantity: 2 }]) => ({
  p_user_id: userA, p_items: items, p_payment_method: method,
  p_recipient_name: 'Test Recipient', p_recipient_phone: '0900000000',
  p_address_line: 'Test address', p_ward: 'Test ward', p_province: 'Test province', p_note: '',
});
async function rpc(db, name, params) {
  if (!/^[a-z_]+$/.test(name) || Object.keys(params).some(key => !/^p_[a-z_]+$/.test(key))) throw Error('invalid test RPC');
  const keys = Object.keys(params);
  const values = Object.values(params).map(value => typeof value === 'object' && value !== null ? JSON.stringify(value) : value);
  const sql = `select public.${name}(${keys.map((key, i) => `${key} => $${i + 1}`).join(',')}) as result`;
  return (await db.query(sql, values)).rows[0].result;
}
module.exports = { fixture, userA, userB, args, rpc };
