-- Integration completion for A3: authenticated, purchased-product reviews.
-- Owner reviews/applies; never run database/setup.sql.
BEGIN;
REVOKE INSERT, UPDATE, DELETE ON public.reviews FROM anon, authenticated;

CREATE OR REPLACE FUNCTION public.create_product_review(p_user_id uuid, p_product_id integer, p_rating integer, p_comment text)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE v_id uuid;
BEGIN
  IF p_user_id IS NULL OR p_product_id IS NULL OR p_product_id<1 OR p_rating IS NULL
    OR p_rating NOT BETWEEN 1 AND 5 OR p_comment IS NULL OR char_length(p_comment)>1000 THEN
    RAISE EXCEPTION 'INVALID_FIELD';
  END IF;
  IF NOT EXISTS(SELECT 1 FROM public.products WHERE id=p_product_id) THEN
    RAISE EXCEPTION 'INVALID_PRODUCT';
  END IF;
  -- Accepted COD or paid purchase qualifies; unpaid Stripe/cancelled carts do not.
  IF NOT EXISTS(SELECT 1 FROM public.orders o WHERE o.user_id=p_user_id AND o.status<>'cancelled'
    AND o.payment_status IN ('paid','cod_pending')
    AND o.items @> jsonb_build_array(jsonb_build_object('product_id',p_product_id))) THEN
    RAISE EXCEPTION 'NOT_PURCHASED';
  END IF;
  INSERT INTO public.reviews(user_id,product_id,rating,comment) VALUES(p_user_id,p_product_id,p_rating,p_comment)
    RETURNING id INTO v_id;
  RETURN jsonb_build_object('review_id',v_id);
END $$;
REVOKE ALL ON FUNCTION public.create_product_review(uuid,integer,integer,text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.create_product_review(uuid,integer,integer,text) TO service_role;
COMMIT;
