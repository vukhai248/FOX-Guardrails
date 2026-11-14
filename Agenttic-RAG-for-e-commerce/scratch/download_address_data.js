const fs = require('fs');
const path = require('path');

const URL = 'https://provinces.open-api.vn/api/?depth=3';
const OUTPUT_DIR = path.join(__dirname, '..', 'public', 'data');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'vietnam-addresses.json');

console.log('⏳ Đang tải dữ liệu địa chính Việt Nam (Mới nhất 2025/2026) từ Open API...');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function download() {
  try {
    const response = await fetch(URL, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const rawProvinces = await response.json();
    console.log('✅ Tải dữ liệu thô thành công. Đang tối ưu hóa dung lượng...');

    // Tối ưu hóa: chỉ giữ lại các trường name cần thiết
    const optimized = rawProvinces.map(p => ({
      name: p.name,
      districts: (p.districts || []).map(d => ({
        name: d.name,
        wards: (d.wards || []).map(w => w.name)
      }))
    }));

    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(optimized, null, 2), 'utf8');
    
    const stats = fs.statSync(OUTPUT_FILE);
    const fileSizeInBytes = stats.size;
    const fileSizeInKilobytes = (fileSizeInBytes / 1024).toFixed(0);

    console.log(`🎉 HOÀN THÀNH! Đã lưu file địa chính tối ưu hóa.`);
    console.log(`📍 Đường dẫn: ${OUTPUT_FILE}`);
    console.log(`📦 Dung lượng file: ${fileSizeInKilobytes} KB`);
    console.log(`📊 Thống kê: Loaded ${optimized.length} tỉnh/thành phố.`);
  } catch (err) {
    console.error('❌ Lỗi tải hoặc xử lý dữ liệu:', err.message);
  }
}

download();
