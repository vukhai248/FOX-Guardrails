import { createClient } from '@supabase/supabase-js';

// Giá trị placeholder hợp lệ để createClient không ném lỗi khi chưa cấu hình env.
// Ở chế độ này, mọi truy vấn Supabase sẽ thất bại và các trang tự động dùng dữ liệu fallback tĩnh.
const PLACEHOLDER_URL = 'https://placeholder.supabase.co';
const PLACEHOLDER_ANON_KEY = 'public-anon-placeholder-key';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || PLACEHOLDER_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || PLACEHOLDER_ANON_KEY;

export const isSupabaseConfigured =
  !!process.env.NEXT_PUBLIC_SUPABASE_URL && !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!isSupabaseConfigured && typeof window !== 'undefined') {
  console.warn(
    'Cảnh báo: Chưa cấu hình NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY. Đang chạy ở chế độ dữ liệu tĩnh (fallback).'
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
