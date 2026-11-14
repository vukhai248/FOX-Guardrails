// scratch/clear_db.js
// Script Node.js xóa sạch toàn bộ sản phẩm trong bảng products của Supabase

const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

// 1. Đọc file .env.local để lấy thông số kết nối Supabase
const envPath = path.join(__dirname, '..', '.env.local');
let supabaseUrl = '';
let supabaseServiceKey = '';

try {
  const envContent = fs.readFileSync(envPath, 'utf8');
  const lines = envContent.split('\n');
  for (let line of lines) {
    line = line.trim();
    if (line.startsWith('NEXT_PUBLIC_SUPABASE_URL=')) {
      supabaseUrl = line.split('=')[1].trim();
    }
    if (line.startsWith('SUPABASE_SERVICE_ROLE_KEY=')) {
      supabaseServiceKey = line.split('=')[1].trim();
    }
  }
} catch (e) {
  console.error('Không thể đọc file .env.local:', e.message);
  process.exit(1);
}

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Thiếu cấu hình Supabase URL hoặc Service Role Key trong .env.local!');
  process.exit(1);
}

console.log('Đang kết nối tới Supabase:', supabaseUrl);
const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function clearDatabase() {
  console.log('Bắt đầu xóa sạch toàn bộ sản phẩm trong bảng products...');
  
  // Thực hiện xóa tất cả sản phẩm
  const { data, error } = await supabase
    .from('products')
    .delete()
    .gte('price', 0); // Xóa tất cả các bản ghi có giá trị lớn hơn hoặc bằng 0 (tức là toàn bộ sản phẩm)

  if (error) {
    console.error('Lỗi khi xóa sản phẩm trong Database:', error.message);
    process.exit(1);
  }
  
  console.log('===> THÀNH CÔNG: Đã xóa sạch toàn bộ sản phẩm trong Database của bạn!');
}

clearDatabase();
