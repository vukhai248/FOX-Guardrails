-- setup.sql
-- Script khởi tạo cơ sở dữ liệu mới hoàn toàn cho dự án Web TMĐT Điện tử & Agentic RAG

-- Xóa bảng cũ nếu tồn tại để tránh xung đột
DROP TABLE IF EXISTS public.chat_logs CASCADE;
DROP TABLE IF EXISTS public.support_tickets CASCADE;
DROP TABLE IF EXISTS public.reviews CASCADE;
DROP TABLE IF EXISTS public.orders CASCADE;
DROP TABLE IF EXISTS public.products CASCADE;
DROP TABLE IF EXISTS public.policies CASCADE;
DROP TABLE IF EXISTS public.user_roles CASCADE;

-- 1. Bảng products (Có specs kiểu JSONB để hỗ trợ thông số kỹ thuật động cực kỳ linh hoạt)
CREATE TABLE public.products (
    id INT PRIMARY KEY,                                 -- Nhận trực tiếp product_id dạng số nguyên
    name VARCHAR(255) NOT NULL,                         -- Tên sản phẩm
    brand TEXT,                                         -- Thương hiệu
    sku TEXT,                                           -- Mã SKU định danh sản phẩm
    url TEXT,                                           -- Đường dẫn chi tiết sản phẩm
    category TEXT NOT NULL,                             -- Danh mục sản phẩm
    price NUMERIC NOT NULL,                             -- Giá gốc chưa giảm
    special_price NUMERIC,                              -- Giá khuyến mại đặc biệt (nếu có)
    final_price NUMERIC NOT NULL,                       -- Giá thực tế bán
    discount NUMERIC DEFAULT 0.0,                       -- Phần trăm giảm giá (ví dụ: 6.32%)
    stock INTEGER NOT NULL DEFAULT 0,                   -- Số lượng tồn kho
    thumbnail TEXT,                                     -- URL ảnh nhỏ
    image_url TEXT,                                     -- URL ảnh lớn đại diện
    
    -- Các trường thông số kỹ thuật phẳng dự phòng
    cpu TEXT,
    ram TEXT,
    storage TEXT,
    display_size TEXT,
    display_resolution TEXT,
    battery TEXT,
    os TEXT,
    gpu TEXT,
    weight TEXT,
    dimensions TEXT,
    included_accessories TEXT,
    camera_primary TEXT,
    camera_secondary TEXT,
    camera_video TEXT,
    
    description TEXT NOT NULL,                          -- Mô tả thô (chứa chuỗi thông số gộp)
    key_selling_points TEXT,                            -- Đặc điểm nổi bật của sản phẩm (HTML từ attributes_json)
    specs JSONB,                                        -- TOÀN BỘ thông số kỹ thuật chi tiết của Cellphones (dạng Key-Value động)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Bảng orders
CREATE TABLE public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- Liên kết với auth.users của Supabase Auth
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'shipping', 'delivered', 'cancelled')),
    items JSONB NOT NULL, -- Chứa mảng [{product_id, name, price, quantity, image}]
    total NUMERIC(12, 2) NOT NULL CHECK (total >= 0),
    shipping_address TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Bảng reviews (Liên kết khóa ngoại kiểu INT)
CREATE TABLE public.reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id INT NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Bảng support_tickets
CREATE TABLE public.support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    order_id UUID REFERENCES public.orders(id) ON DELETE SET NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('advisory', 'negotiation', 'technical', 'attack_flagged', 'other')),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    created_by VARCHAR(20) NOT NULL CHECK (created_by IN ('agent', 'staff', 'customer')),
    status VARCHAR(50) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved')),
    assigned_staff_id UUID,
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Bảng chat_logs
CREATE TABLE public.chat_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) NOT NULL,
    user_id UUID,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'agent', 'tool', 'system')),
    message TEXT NOT NULL,
    tool_used VARCHAR(100),
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Bảng policies (Chính sách)
CREATE TABLE public.policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,                      -- Phân loại: 'return_refund', 'warranty', 'shipping', 'faq'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 7. Bảng user_roles (Nguồn quyền server-side DUY NHẤT cho Admin/Staff)
CREATE TABLE public.user_roles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('admin', 'staff', 'customer')),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Bật RLS
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

-- Cho phép đọc công khai (Read-only public access)
CREATE POLICY "Cho phép đọc công khai sản phẩm" ON public.products FOR SELECT USING (true);
CREATE POLICY "Cho phép đọc công khai đánh giá" ON public.reviews FOR SELECT USING (true);
CREATE POLICY "Cho phép đọc công khai chính sách" ON public.policies FOR SELECT USING (true);

-- user_roles: RLS deny-all với client - chỉ service_role phía server thao tác
-- (không tạo bất kỳ policy nào cho bảng này)

-- Luồng khách hàng dưới RLS (thao tác quản trị đi qua API server dùng service_role nên không cần policy)
CREATE POLICY "orders_select_own" ON public.orders FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "orders_insert_own" ON public.orders FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "tickets_select_own" ON public.support_tickets FOR SELECT TO authenticated USING (auth.uid() = customer_id);
CREATE POLICY "tickets_insert_own" ON public.support_tickets FOR INSERT TO authenticated WITH CHECK (auth.uid() = customer_id);
CREATE POLICY "tickets_update_own" ON public.support_tickets FOR UPDATE TO authenticated USING (auth.uid() = customer_id) WITH CHECK (auth.uid() = customer_id);

-- Quản trị viên và nhân viên thao tác qua Next.js Server API Routes với SERVICE_ROLE_KEY
-- đảm bảo an toàn tuyệt đối, phân quyền role động dựa trên user_metadata/user_roles.

