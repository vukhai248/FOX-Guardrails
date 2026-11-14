-- K2: additional overload for a signed checkout.session.expired event.
-- Owner reviews/applies after the existing migrations; never run setup.sql.
BEGIN;
CREATE OR REPLACE FUNCTION public.fail_stripe_order(p_order_id uuid, p_session_id text)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
  IF p_session_id IS NULL OR left(p_session_id,8)<>'cs_test_' OR char_length(p_session_id)<=8 THEN
    RAISE EXCEPTION 'PAYMENT_MISMATCH';
  END IF;
  -- Atomic predicate is rechecked after a competing payment transaction releases its row lock.
  UPDATE public.orders SET status='cancelled', payment_status='failed',
    stripe_session_id=coalesce(stripe_session_id,p_session_id)
  WHERE id=p_order_id AND payment_method='stripe' AND payment_status='unpaid' AND status='pending'
    AND (stripe_session_id IS NULL OR stripe_session_id=p_session_id);
END $$;
REVOKE ALL ON FUNCTION public.fail_stripe_order(uuid,text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.fail_stripe_order(uuid,text) TO service_role;
NOTIFY pgrst, 'reload schema';
COMMIT;
