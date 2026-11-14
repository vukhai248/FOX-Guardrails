-- A2: review before applying to Supabase. Never run database/setup.sql.
-- Existing orders are retained; structured address fields stay nullable for legacy rows.
BEGIN;

ALTER TABLE public.orders
  ADD COLUMN IF NOT EXISTS payment_method text NOT NULL DEFAULT 'cod',
  ADD COLUMN IF NOT EXISTS payment_status text NOT NULL DEFAULT 'unpaid',
  ADD COLUMN IF NOT EXISTS stripe_session_id text,
  ADD COLUMN IF NOT EXISTS paid_at timestamptz,
  ADD COLUMN IF NOT EXISTS recipient_name text,
  ADD COLUMN IF NOT EXISTS recipient_phone text,
  ADD COLUMN IF NOT EXISTS address_line text,
  ADD COLUMN IF NOT EXISTS ward text,
  ADD COLUMN IF NOT EXISTS province text,
  ADD COLUMN IF NOT EXISTS note text NOT NULL DEFAULT '',
  ADD COLUMN IF NOT EXISTS stock_decremented_at timestamptz;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid = 'public.orders'::regclass AND conname = 'orders_payment_method_check') THEN
    ALTER TABLE public.orders ADD CONSTRAINT orders_payment_method_check CHECK (payment_method IN ('stripe','cod'));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid = 'public.orders'::regclass AND conname = 'orders_payment_status_check') THEN
    ALTER TABLE public.orders ADD CONSTRAINT orders_payment_status_check CHECK (payment_status IN ('unpaid','paid','cod_pending','refunded','failed'));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid = 'public.orders'::regclass AND conname = 'orders_note_length_check') THEN
    ALTER TABLE public.orders ADD CONSTRAINT orders_note_length_check CHECK (char_length(note) <= 500);
  END IF;
END $$;
CREATE UNIQUE INDEX IF NOT EXISTS orders_stripe_session_id_unique ON public.orders(stripe_session_id);

-- Client INSERT-own previously allowed forging items/total/payment state without the API.
-- Owner SELECT/RLS remains; writes now go through authenticated server routes.
REVOKE INSERT, UPDATE, DELETE ON public.orders FROM anon, authenticated;

CREATE OR REPLACE FUNCTION public.decrement_stock_for_order(p_order_id uuid)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE
  v_order public.orders%ROWTYPE;
  v_item record;
  v_stock integer;
BEGIN
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'NOT_FOUND'; END IF;
  IF v_order.stock_decremented_at IS NOT NULL THEN RETURN; END IF;
  IF (v_order.payment_method = 'stripe' AND v_order.payment_status <> 'paid')
    OR (v_order.payment_method = 'cod' AND v_order.payment_status <> 'cod_pending') THEN
    RAISE EXCEPTION 'NOT_PAID';
  END IF;
  -- Every transaction locks product rows in the same order.
  FOR v_item IN
    SELECT product_id, sum(quantity)::integer AS quantity
    FROM jsonb_to_recordset(v_order.items) AS x(product_id integer, quantity integer)
    GROUP BY product_id ORDER BY product_id
  LOOP
    IF v_item.quantity IS NULL OR v_item.quantity <= 0 THEN RAISE EXCEPTION 'INVALID_FIELD'; END IF;
    SELECT stock INTO v_stock FROM public.products WHERE id = v_item.product_id FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'INVALID_PRODUCT'; END IF;
    IF v_stock < v_item.quantity THEN RAISE EXCEPTION 'OUT_OF_STOCK'; END IF;
    UPDATE public.products SET stock = stock - v_item.quantity WHERE id = v_item.product_id;
  END LOOP;
  UPDATE public.orders SET stock_decremented_at = now() WHERE id = p_order_id;
END $$;

CREATE OR REPLACE FUNCTION public.create_shop_order(
  p_user_id uuid, p_items jsonb, p_payment_method text,
  p_recipient_name text, p_recipient_phone text, p_address_line text,
  p_ward text, p_province text, p_note text DEFAULT ''
) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE
  v_item record;
  v_product public.products%ROWTYPE;
  v_items jsonb := '[]'::jsonb;
  v_total numeric := 0;
  v_order public.orders%ROWTYPE;
BEGIN
  IF p_user_id IS NULL OR p_payment_method IS NULL OR p_payment_method NOT IN ('stripe','cod') THEN RAISE EXCEPTION 'INVALID_FIELD'; END IF;
  IF p_items IS NULL OR jsonb_typeof(p_items) <> 'array' THEN RAISE EXCEPTION 'INVALID_FIELD'; END IF;
  IF jsonb_array_length(p_items) = 0 THEN RAISE EXCEPTION 'EMPTY_CART'; END IF;
  IF jsonb_array_length(p_items) > 100 THEN RAISE EXCEPTION 'INVALID_FIELD'; END IF;
  IF coalesce(char_length(btrim(p_recipient_name)),0) NOT BETWEEN 1 AND 200
    OR coalesce(char_length(btrim(p_recipient_phone)),0) NOT BETWEEN 1 AND 30
    OR coalesce(char_length(btrim(p_address_line)),0) NOT BETWEEN 1 AND 500
    OR coalesce(char_length(btrim(p_ward)),0) NOT BETWEEN 1 AND 200
    OR coalesce(char_length(btrim(p_province)),0) NOT BETWEEN 1 AND 200
    OR char_length(coalesce(p_note,'')) > 500 THEN RAISE EXCEPTION 'INVALID_FIELD'; END IF;
  IF EXISTS (
    SELECT 1 FROM jsonb_to_recordset(p_items) AS x(product_id integer, quantity integer)
    WHERE product_id IS NULL OR product_id <= 0 OR quantity IS NULL OR quantity <= 0 OR quantity > 10000
  ) THEN RAISE EXCEPTION 'INVALID_FIELD'; END IF;

  FOR v_item IN
    SELECT product_id, sum(quantity)::integer AS quantity
    FROM jsonb_to_recordset(p_items) AS x(product_id integer, quantity integer)
    GROUP BY product_id ORDER BY product_id
  LOOP
    IF v_item.quantity > 10000 THEN RAISE EXCEPTION 'INVALID_FIELD'; END IF;
    SELECT * INTO v_product FROM public.products WHERE id = v_item.product_id FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'INVALID_PRODUCT'; END IF;
    IF v_product.stock < v_item.quantity THEN RAISE EXCEPTION 'OUT_OF_STOCK'; END IF;
    IF v_product.final_price < 0 OR v_product.final_price::text IN ('NaN','Infinity','-Infinity') THEN RAISE EXCEPTION 'INVALID_PRODUCT'; END IF;
    v_total := v_total + round(v_product.final_price) * v_item.quantity;
    v_items := v_items || jsonb_build_array(jsonb_build_object(
      'product_id', v_product.id, 'name', v_product.name,
      'price', round(v_product.final_price), 'quantity', v_item.quantity, 'image', v_product.thumbnail
    ));
  END LOOP;
  IF v_total > 9999999999 THEN RAISE EXCEPTION 'INVALID_FIELD'; END IF;

  INSERT INTO public.orders(user_id, items, total, shipping_address, payment_method, payment_status,
    recipient_name, recipient_phone, address_line, ward, province, note)
  VALUES (p_user_id, v_items, v_total, concat_ws(', ', btrim(p_address_line), btrim(p_ward), btrim(p_province)),
    p_payment_method, CASE WHEN p_payment_method = 'cod' THEN 'cod_pending' ELSE 'unpaid' END,
    btrim(p_recipient_name), btrim(p_recipient_phone), btrim(p_address_line), btrim(p_ward), btrim(p_province), coalesce(p_note,''))
  RETURNING * INTO v_order;
  IF p_payment_method = 'cod' THEN
    PERFORM public.decrement_stock_for_order(v_order.id);
    SELECT * INTO v_order FROM public.orders WHERE id = v_order.id;
  END IF;
  RETURN to_jsonb(v_order);
END $$;

CREATE OR REPLACE FUNCTION public.attach_stripe_session(p_order_id uuid, p_session_id text)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE v_order public.orders%ROWTYPE;
BEGIN
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'NOT_FOUND'; END IF;
  IF p_session_id IS NULL OR left(p_session_id,8) <> 'cs_test_' OR v_order.payment_method <> 'stripe'
    OR (v_order.stripe_session_id IS NOT NULL AND v_order.stripe_session_id <> p_session_id) THEN
    RAISE EXCEPTION 'PAYMENT_MISMATCH';
  END IF;
  IF v_order.stripe_session_id = p_session_id THEN RETURN; END IF;
  IF v_order.status <> 'pending' OR v_order.payment_status <> 'unpaid' THEN RAISE EXCEPTION 'NOT_EDITABLE'; END IF;
  UPDATE public.orders SET stripe_session_id = p_session_id WHERE id = p_order_id;
END $$;

CREATE OR REPLACE FUNCTION public.finalize_stripe_order(
  p_order_id uuid, p_session_id text, p_amount_total bigint, p_currency text
) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE v_order public.orders%ROWTYPE;
BEGIN
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'NOT_FOUND'; END IF;
  IF v_order.payment_method <> 'stripe' OR p_session_id IS NULL OR left(p_session_id,8) <> 'cs_test_'
    OR (v_order.stripe_session_id IS NOT NULL AND v_order.stripe_session_id <> p_session_id)
    OR p_currency IS DISTINCT FROM 'vnd' OR p_amount_total IS DISTINCT FROM v_order.total THEN
    RAISE EXCEPTION 'PAYMENT_MISMATCH';
  END IF;
  IF v_order.payment_status = 'paid' THEN RETURN to_jsonb(v_order); END IF;
  IF v_order.payment_status <> 'unpaid' OR v_order.status <> 'pending' THEN RAISE EXCEPTION 'NOT_EDITABLE'; END IF;
  UPDATE public.orders SET stripe_session_id = p_session_id, payment_status = 'paid', paid_at = now(), status = 'processing'
    WHERE id = p_order_id;
  PERFORM public.decrement_stock_for_order(p_order_id);
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id;
  RETURN to_jsonb(v_order);
END $$;

CREATE OR REPLACE FUNCTION public.fail_stripe_order(p_order_id uuid)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
  UPDATE public.orders SET status = 'cancelled', payment_status = 'failed'
  WHERE id = p_order_id AND payment_method = 'stripe' AND payment_status = 'unpaid'
    AND stripe_session_id IS NULL AND status = 'pending';
END $$;

REVOKE ALL ON FUNCTION public.decrement_stock_for_order(uuid) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.create_shop_order(uuid,jsonb,text,text,text,text,text,text,text) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.attach_stripe_session(uuid,text) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.finalize_stripe_order(uuid,text,bigint,text) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.fail_stripe_order(uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.decrement_stock_for_order(uuid) TO service_role;
GRANT EXECUTE ON FUNCTION public.create_shop_order(uuid,jsonb,text,text,text,text,text,text,text) TO service_role;
GRANT EXECUTE ON FUNCTION public.attach_stripe_session(uuid,text) TO service_role;
GRANT EXECUTE ON FUNCTION public.finalize_stripe_order(uuid,text,bigint,text) TO service_role;
GRANT EXECUTE ON FUNCTION public.fail_stripe_order(uuid) TO service_role;
COMMIT;
