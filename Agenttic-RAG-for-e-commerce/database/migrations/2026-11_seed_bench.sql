-- A7: owner reviews/applies this additive migration. Never run setup.sql.
BEGIN;

CREATE TABLE IF NOT EXISTS public.bench_cases (
  namespace uuid NOT NULL,
  case_id text NOT NULL CHECK (char_length(case_id) BETWEEN 1 AND 200),
  "table" text NOT NULL CHECK ("table" IN ('orders','reviews')),
  row_id uuid NOT NULL,
  payload_hash text NOT NULL CHECK (payload_hash ~ '^[0-9a-f]{64}$'),
  PRIMARY KEY (namespace, case_id),
  UNIQUE ("table", row_id)
);
ALTER TABLE public.bench_cases ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.bench_cases FROM PUBLIC, anon, authenticated, service_role;
GRANT SELECT ON public.bench_cases TO service_role;

CREATE OR REPLACE FUNCTION public.seed_bench_cases(p_namespace uuid, p_cases jsonb, p_reset boolean DEFAULT false)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE
  c jsonb; f jsonb; v_map public.bench_cases%ROWTYPE;
  v_id uuid; v_user uuid; v_table text; v_hash text; v_case text;
  v_item record; v_product public.products%ROWTYPE;
  v_total numeric; v_items jsonb; v_result jsonb := '[]'::jsonb;
  v_name text; v_phone text; v_address text; v_ward text; v_province text;
BEGIN
  IF p_namespace IS NULL OR jsonb_typeof(p_cases) IS DISTINCT FROM 'array'
     OR jsonb_array_length(p_cases) > 5000 OR p_reset IS NULL THEN
    RAISE EXCEPTION 'BENCH_INVALID_CASES';
  END IF;
  -- Serialize seeds and resets so provenance cannot race with a second run.
  PERFORM pg_catalog.pg_advisory_xact_lock(719031126);
  IF p_reset THEN
    PERFORM o.id FROM public.orders o JOIN public.bench_cases b ON b."table"='orders' AND b.row_id=o.id
      WHERE b.namespace=p_namespace ORDER BY o.id FOR UPDATE OF o;
    PERFORM r.id FROM public.reviews r JOIN public.bench_cases b ON b."table"='reviews' AND b.row_id=r.id
      WHERE b.namespace=p_namespace ORDER BY r.id FOR UPDATE OF r;
    -- Deleting an order would otherwise SET NULL on an unmapped support ticket.
    IF EXISTS (SELECT 1 FROM public.support_tickets t JOIN public.bench_cases b
               ON b."table"='orders' AND b.row_id=t.order_id WHERE b.namespace=p_namespace) THEN
      RAISE EXCEPTION 'BENCH_REFERENCED';
    END IF;
    IF EXISTS (SELECT 1 FROM public.bench_cases b JOIN public.orders o ON b."table"='orders' AND o.id=b.row_id
      LEFT JOIN auth.users u ON u.id=o.user_id WHERE b.namespace=p_namespace
      AND (u.raw_app_meta_data->>'bench_seed_namespace' IS DISTINCT FROM p_namespace::text))
      OR EXISTS (SELECT 1 FROM public.bench_cases b JOIN public.reviews r ON b."table"='reviews' AND r.id=b.row_id
      LEFT JOIN auth.users u ON u.id=r.user_id WHERE b.namespace=p_namespace
      AND (u.raw_app_meta_data->>'bench_seed_namespace' IS DISTINCT FROM p_namespace::text)) THEN
      RAISE EXCEPTION 'BENCH_OWNER_MISMATCH';
    END IF;
    DELETE FROM public.reviews r USING public.bench_cases b
      WHERE b.namespace=p_namespace AND b."table"='reviews' AND r.id=b.row_id;
    DELETE FROM public.orders o USING public.bench_cases b
      WHERE b.namespace=p_namespace AND b."table"='orders' AND o.id=b.row_id;
    DELETE FROM public.bench_cases WHERE namespace=p_namespace;
  END IF;
  IF EXISTS (SELECT 1 FROM jsonb_array_elements(p_cases) x GROUP BY x->>'case_id' HAVING count(*)>1) THEN
    RAISE EXCEPTION 'BENCH_DUPLICATE_CASE';
  END IF;
  FOR c IN SELECT value FROM jsonb_array_elements(p_cases) LOOP
    v_case := c->>'case_id'; v_table := c->>'table'; v_id := (c->>'row_id')::uuid;
    v_hash := c->>'payload_hash'; f := c->'fields'; v_user := (f->>'user_id')::uuid;
    IF v_case IS NULL OR char_length(v_case) NOT BETWEEN 1 AND 200
       OR v_table IS NULL OR v_table NOT IN ('orders','reviews') OR v_id IS NULL
       OR v_hash IS NULL OR v_hash !~ '^[0-9a-f]{64}$' OR jsonb_typeof(f) IS DISTINCT FROM 'object' THEN
      RAISE EXCEPTION 'BENCH_INVALID_CASES';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM auth.users u WHERE u.id=v_user
      AND u.raw_app_meta_data->>'bench_seed_namespace'=p_namespace::text
      AND u.raw_app_meta_data->>'bench_seed_alias' IN ('bench_customer_a','bench_customer_b')) THEN
      RAISE EXCEPTION 'BENCH_OWNER_MISMATCH';
    END IF;
    SELECT * INTO v_map FROM public.bench_cases WHERE namespace=p_namespace AND case_id=v_case;
    IF FOUND THEN
      IF v_map."table"<>v_table OR v_map.row_id<>v_id OR v_map.payload_hash<>v_hash THEN
        RAISE EXCEPTION 'BENCH_CASE_CHANGED';
      END IF;
      IF (v_table='orders' AND EXISTS(SELECT 1 FROM public.orders WHERE id=v_id AND user_id<>v_user))
        OR (v_table='reviews' AND EXISTS(SELECT 1 FROM public.reviews WHERE id=v_id AND user_id<>v_user)) THEN
        RAISE EXCEPTION 'BENCH_OWNER_MISMATCH';
      END IF;
      IF (v_table='orders' AND NOT EXISTS(SELECT 1 FROM public.orders WHERE id=v_id))
        OR (v_table='reviews' AND NOT EXISTS(SELECT 1 FROM public.reviews WHERE id=v_id)) THEN
        RAISE EXCEPTION 'BENCH_ROW_MISSING';
      END IF;
    ELSE
      IF EXISTS(SELECT 1 FROM public.bench_cases WHERE "table"=v_table AND row_id=v_id)
        OR (v_table='orders' AND EXISTS(SELECT 1 FROM public.orders WHERE id=v_id))
        OR (v_table='reviews' AND EXISTS(SELECT 1 FROM public.reviews WHERE id=v_id)) THEN
        RAISE EXCEPTION 'BENCH_ROW_COLLISION';
      END IF;
      IF v_table='orders' THEN
        IF jsonb_typeof(f->'items') IS DISTINCT FROM 'array' OR jsonb_array_length(f->'items') NOT BETWEEN 1 AND 100
          OR char_length(coalesce(f->>'note',''))>500 THEN RAISE EXCEPTION 'BENCH_INVALID_ORDER'; END IF;
        IF EXISTS(SELECT 1 FROM jsonb_to_recordset(f->'items') AS x(product_id integer,quantity integer)
          WHERE product_id IS NULL OR product_id<1 OR quantity IS NULL OR quantity NOT BETWEEN 1 AND 10000) THEN
          RAISE EXCEPTION 'BENCH_INVALID_ORDER';
        END IF;
        v_total:=0; v_items:='[]'::jsonb;
        FOR v_item IN SELECT product_id,sum(quantity)::integer AS quantity
          FROM jsonb_to_recordset(f->'items') AS x(product_id integer,quantity integer)
          GROUP BY product_id ORDER BY product_id LOOP
          SELECT * INTO v_product FROM public.products WHERE id=v_item.product_id;
          IF NOT FOUND OR v_item.quantity>10000 OR v_product.final_price<0
             OR v_product.final_price::text IN ('NaN','Infinity','-Infinity') THEN
            RAISE EXCEPTION 'BENCH_INVALID_PRODUCT';
          END IF;
          v_total:=v_total+round(v_product.final_price)*v_item.quantity;
          v_items:=v_items||jsonb_build_array(jsonb_build_object('product_id',v_product.id,'name',v_product.name,
            'price',round(v_product.final_price),'quantity',v_item.quantity,'image',v_product.thumbnail));
        END LOOP;
        v_name:=coalesce(f->>'recipient_name','Khách benchmark'); v_phone:=coalesce(f->>'recipient_phone','0900000000');
        v_address:=coalesce(f->>'address_line','Địa chỉ mô phỏng'); v_ward:=coalesce(f->>'ward','Phường mô phỏng');
        v_province:=coalesce(f->>'province','Tỉnh mô phỏng');
        INSERT INTO public.orders(id,user_id,status,items,total,shipping_address,payment_method,payment_status,
          recipient_name,recipient_phone,address_line,ward,province,note,created_at)
        VALUES(v_id,v_user,coalesce(f->>'status','delivered'),v_items,v_total,
          concat_ws(', ',v_name,v_phone,v_address,v_ward,v_province),coalesce(f->>'payment_method','cod'),
          coalesce(f->>'payment_status','paid'),v_name,v_phone,v_address,v_ward,v_province,coalesce(f->>'note',''),
          coalesce((f->>'created_at')::timestamptz,'2026-11-01T00:00:00Z'::timestamptz));
      ELSE
        IF char_length(coalesce(f->>'comment',''))>1000 THEN RAISE EXCEPTION 'BENCH_INVALID_REVIEW'; END IF;
        INSERT INTO public.reviews(id,user_id,product_id,rating,comment,created_at)
          VALUES(v_id,v_user,(f->>'product_id')::integer,(f->>'rating')::integer,coalesce(f->>'comment',''),
            coalesce((f->>'created_at')::timestamptz,'2026-11-01T00:00:00Z'::timestamptz));
      END IF;
      INSERT INTO public.bench_cases(namespace,case_id,"table",row_id,payload_hash)
        VALUES(p_namespace,v_case,v_table,v_id,v_hash);
    END IF;
    v_result:=v_result||jsonb_build_array(jsonb_build_object('case_id',v_case,'table',v_table,'row_id',v_id));
  END LOOP;
  RETURN v_result;
END $$;
REVOKE ALL ON FUNCTION public.seed_bench_cases(uuid,jsonb,boolean) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.seed_bench_cases(uuid,jsonb,boolean) TO service_role;
COMMIT;
