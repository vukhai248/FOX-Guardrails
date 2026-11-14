const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://riycenndsrlpivzbcnmf.supabase.co';
const supabaseAnonKey = 'sb_publishable_q8xBVai0boAaz12XbWBGXw_3KarELDC';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function check() {
  try {
    console.log('🔄 Đang kết nối Supabase...');
    
    // Lấy tất cả products
    const { data: products, error: prodErr } = await supabase.from('products').select('id, name, category');
    if (prodErr) throw prodErr;
    console.log(`✅ Đã tải ${products.length} sản phẩm từ database.`);

    // Lấy các đơn hàng
    const { data: orders, error: ordErr } = await supabase.from('orders').select('id, status, items, total');
    if (ordErr) throw ordErr;
    
    console.log(`\n✅ Đã tải ${orders.length} đơn hàng từ database.`);
    const successfulOrders = orders.filter(o => o.status !== 'pending' && o.status !== 'cancelled');
    console.log(`📊 Số đơn hàng hợp lệ để tính doanh số: ${successfulOrders.length}`);

    successfulOrders.forEach((o, i) => {
      console.log(`\n📦 Đơn hàng thứ ${i+1} (ID: ${o.id}) | Trạng thái: ${o.status} | Tổng tiền: ${o.total}`);
      console.log('Các sản phẩm trong đơn hàng:');
      o.items?.forEach((item, idx) => {
        console.log(`  [${idx+1}] ID: ${item.id} | ProductID: ${item.product_id} | Name: "${item.name}" | Price: ${item.price} | Qty: ${item.quantity}`);
        
        // Thử tìm theo logic cũ và mới
        const matchedOld = products.find(p => p.name === item.name || p.id === item.product_id);
        const matchedNew = products.find(p => 
          p.id === item.id || 
          p.id === item.product_id || 
          item.name === p.name ||
          item.name.startsWith(p.name) ||
          item.name.includes(p.name)
        );
        
        console.log(`      -> Logic CŨ: ${matchedOld ? `Tìm thấy (Category: ${matchedOld.category})` : '❌ KHÔNG TÌM THẤY (rơi vào fallback accessory)'}`);
        console.log(`      -> Logic MỚI: ${matchedNew ? `Tìm thấy (Category: ${matchedNew.category})` : '❌ KHÔNG TÌM THẤY (rơi vào fallback accessory)'}`);
      });
    });

  } catch (err) {
    console.error('❌ Lỗi:', err);
  }
}

check();
