// scratch/import_products.js
// Script import thông minh: gộp màu sắc + cấu hình (RAM/ROM), việt hóa, sửa ảnh brand
// Chạy: node scratch/import_products.js

const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

// ─────────────────────────────────────────────────────────────────────────────
// 1. KẾT NỐI SUPABASE
// ─────────────────────────────────────────────────────────────────────────────
const envPath = path.join(__dirname, '..', '.env.local');
let supabaseUrl = '', supabaseServiceKey = '';
try {
  const envContent = fs.readFileSync(envPath, 'utf8');
  for (let line of envContent.split('\n')) {
    line = line.trim();
    if (line.startsWith('NEXT_PUBLIC_SUPABASE_URL='))     supabaseUrl      = line.split('=').slice(1).join('=').trim();
    if (line.startsWith('SUPABASE_SERVICE_ROLE_KEY='))   supabaseServiceKey = line.split('=').slice(1).join('=').trim();
  }
} catch (e) { console.error('Không đọc được .env.local:', e.message); process.exit(1); }
if (!supabaseUrl || !supabaseServiceKey) { console.error('Thiếu Supabase config!'); process.exit(1); }
const supabase = createClient(supabaseUrl, supabaseServiceKey);

// ─────────────────────────────────────────────────────────────────────────────
// 2. BỘ DỊCH THUẬT QUY TẮC (Việt hóa)
// ─────────────────────────────────────────────────────────────────────────────
const COLOR_VI = {
  'black': 'Đen', 'midnight black': 'Đen Midnight', 'carbon black': 'Đen Carbon',
  'matte black': 'Đen Nhám', 'glossy black': 'Đen Bóng', 'onyx black': 'Đen Onyx',
  'bold black': 'Đen Đậm', 'classic black': 'Đen Classic', 'phantom black': 'Đen Phantom',
  'white': 'Trắng', 'pearl white': 'Trắng Ngọc', 'cream white': 'Trắng Kem',
  'silver': 'Bạc', 'stainless steel': 'Thép Không Gỉ',
  'red': 'Đỏ', 'raging red': 'Đỏ Cuồng Nhiệt', 'active red': 'Đỏ Active',
  'dark red': 'Đỏ Đậm', 'ruby red': 'Đỏ Ruby',
  'blue': 'Xanh Dương', 'active blue': 'Xanh Dương Active', 'royal blue': 'Xanh Hoàng Gia',
  'dark blue': 'Xanh Đậm', 'navy blue': 'Xanh Navy', 'cobalt blue': 'Xanh Cobalt',
  'steel blue': 'Xanh Thép', 'midnight blue': 'Xanh Midnight', 'teal': 'Xanh Mòng Két',
  'aqua': 'Xanh Nước', 'ice blue': 'Xanh Băng',
  'green': 'Xanh Lá', 'army green': 'Xanh Quân Đội', 'dark green': 'Xanh Lá Đậm',
  'olive green': 'Xanh Olive', 'forest green': 'Xanh Rừng', 'mint green': 'Xanh Bạc Hà',
  'sage green': 'Xanh Xô Thơm',
  'yellow': 'Vàng', 'gold': 'Vàng Gold', 'golden': 'Vàng Kim', 'lemon': 'Vàng Chanh',
  'orange': 'Cam', 'copper': 'Đồng',
  'purple': 'Tím', 'violet': 'Tím Violet', 'lavender': 'Tím Lavender',
  'pink': 'Hồng', 'rose': 'Hồng Đỏ', 'rose gold': 'Vàng Hồng',
  'grey': 'Xám', 'gray': 'Xám', 'titanium grey': 'Xám Titanium', 'space grey': 'Xám Vũ Trụ',
  'charcoal': 'Xám Than', 'graphite': 'Xám Graphite',
  'coral': 'San Hô', 'peach': 'Đào',
  'mint': 'Bạc Hà',
  'rainbow': 'Cầu Vồng', 'multicolor': 'Nhiều Màu',
  'transparent': 'Trong Suốt', 'clear': 'Trong Suốt',
  'brown': 'Nâu', 'tan': 'Nâu Nhạt',
  'cream': 'Kem', 'ivory': 'Ngà',
  'lime': 'Xanh Chanh',
  'cyan': 'Xanh Cyan',
  'sand': 'Vàng Cát', 'beige': 'Beige',
  'dark': 'Đậm', 'light': 'Nhạt',
};

const CATEGORY_MAP = {
  'laptop': 'laptop',
  'tablet': 'tablet',
  'mobile': 'phone',
  'smartphone': 'phone',
  'phone': 'phone',
  'earphone': 'earphone',
  'earphones': 'earphone',
  'headphone': 'earphone',
  'headphones': 'earphone',
  'smartwatch': 'smartwatch',
  'watch': 'smartwatch',
  'speaker': 'accessory',
  'charger': 'accessory',
  'cable': 'accessory',
  'camera': 'accessory',
};

function detectCategory(name, subCat) {
  const lower = (name + ' ' + subCat).toLowerCase();
  if (/\b(laptop|macbook|notebook|chromebook|vivobook|zenbook)\b/.test(lower)) return 'laptop';
  if (/\b(tablet|ipad)\b/.test(lower)) return 'accessory'; // tablet → accessory (không có category riêng)
  if (/\b(earphone|headphone|earbud|in.ear|tws|airpod|basshead|wired.*ear|wireless.*ear)\b/.test(lower)) return 'earphone';
  if (/\b(smartwatch|fitness.band|band\s*\d|galaxy.watch|apple.watch|mi.band|noise.*watch)\b/.test(lower)) return 'smartwatch';
  if (/\b(iphone|samsung.galaxy|redmi|poco|realme|vivo|oppo|oneplus|moto|nokia|pixel)\b/.test(lower)) return 'phone';
  if (/\b(speaker|bluetooth.speaker|soundbar)\b/.test(lower)) return 'accessory';
  if (/\b(charger|cable|hub|adapter|power.bank|tripod|stand|case|cover|screen.guard)\b/.test(lower)) return 'accessory';
  return 'accessory';
}

// ─────────────────────────────────────────────────────────────────────────────
// 3. HÀM NORMALIZE TÊN ĐỂ SO KHỚP (gộp sản phẩm cùng dòng)
// ─────────────────────────────────────────────────────────────────────────────
// Các màu sắc dạng regex để tách ra khỏi tên
const COLOR_PATTERN = [
  'midnight black','carbon black','matte black','glossy black','onyx black','bold black',
  'classic black','phantom black','raging red','active red','dark red','ruby red',
  'active blue','royal blue','dark blue','navy blue','cobalt blue','steel blue',
  'midnight blue','ice blue','army green','dark green','olive green','forest green',
  'mint green','sage green','titanium grey','space grey','titanium gray','space gray',
  'rose gold','lemon yellow','light blue','dark grey','pearl white','cream white',
  'black','white','red','blue','green','yellow','gold','silver','grey','gray',
  'pink','purple','violet','orange','coral','mint','teal','aqua','cyan','copper',
  'rose','charcoal','graphite','brown','cream','ivory','beige','sand','lime',
  'lavender','peach','rainbow','multicolor','transparent','clear','golden',
].sort((a, b) => b.length - a.length); // Dài trước để tránh partial match

const colorRegex = new RegExp(
  '\\b(' + COLOR_PATTERN.map(c => c.replace(/[-\s]+/g, '[\\s-]+')).join('|') + ')\\b',
  'gi'
);

// Các pattern RAM/ROM/Storage để tách
const RAM_ROM_PATTERN = /\b(\d+GB?\s*RAM[,\s]*\d+GB?\s*(Storage|ROM|Internal)?|\d+\s*GB\s*RAM|\d+\s*GB\s*(Storage|ROM)|(\d+\+\d+)\s*GB?)\b/gi;
const STORAGE_PATTERN = /\b((\d+)\s*(GB|TB)\s*(Storage|ROM|Internal|SSD|HDD)?)\b/gi;
const RAM_ONLY_PATTERN = /\b(\d+)\s*GB\s*RAM\b/gi;

function extractRAMStorage(text) {
  // Tìm pattern "XGB RAM, YGB Storage" hoặc "X+Y"
  const combinedMatch = text.match(/(\d+)\s*GB?\s*RAM[,\s]+(\d+)\s*GB?\s*(Storage|ROM|Internal)?/i);
  if (combinedMatch) {
    return { ram: combinedMatch[1] + 'GB', storage: combinedMatch[2] + 'GB' };
  }
  // Tìm pattern "(Color, XGB RAM, YGB Storage)"
  const parenMatch = text.match(/\(([^)]+)\)/);
  if (parenMatch) {
    const inner = parenMatch[1];
    const ramMatch = inner.match(/(\d+)\s*GB?\s*RAM/i);
    const storMatch = inner.match(/(\d+)\s*GB?\s*(Storage|ROM|Internal|bộ nhớ trong)/i);
    if (ramMatch || storMatch) {
      return {
        ram: ramMatch ? ramMatch[1] + 'GB' : null,
        storage: storMatch ? storMatch[1] + 'GB' : null
      };
    }
  }
  return { ram: null, storage: null };
}

function extractColors(text) {
  const found = [];
  const parenMatch = text.match(/\(([^)]+)\)/);
  const searchIn = parenMatch ? parenMatch[1] : text;
  
  const matches = searchIn.match(colorRegex);
  if (matches) {
    for (const m of matches) {
      const lower = m.toLowerCase().replace(/[-\s]+/g, ' ').trim();
      const vi = COLOR_VI[lower];
      if (vi && !found.includes(vi)) found.push(vi);
    }
  }
  return found;
}

function normalizeName(name) {
  let n = name.toLowerCase();
  // Xóa phần trong ngoặc đơn (chứa màu, RAM, cấu hình)
  n = n.replace(/\([^)]*\)/g, '');
  // Normalize dấu gạch ngang và khoảng cách
  n = n.replace(/[-_]/g, ' ');
  // Normalize các từ đồng nghĩa
  n = n.replace(/\bearphone[s]?\b/g, 'headphone');
  n = n.replace(/\bheadphone[s]?\b/g, 'headphone');
  n = n.replace(/\bwireles[s]?\b/g, 'wireless');
  n = n.replace(/\bbluetooth\b/g, 'bt');
  // Xóa màu sắc khỏi tên
  n = n.replace(colorRegex, '');
  // Xóa RAM/ROM pattern
  n = n.replace(/\d+\s*gb\s*(ram|rom|storage|ssd|internal|tb)?\b/gi, '');
  n = n.replace(/\d+\s*tb\b/gi, '');
  // Xóa storage size patterns
  n = n.replace(/\b(8|16|32|64|128|256|512|1024)\s*gb\b/gi, '');
  // Xóa "5g", "4g"
  n = n.replace(/\b[45]g\b/gi, '');
  // Xóa phiên bản phụ cuối như "gen 2", "v2"
  // n = n.replace(/\b(gen|version|v)\s*\d+\b/gi, '');
  // Xóa nhiều khoảng trắng thừa
  n = n.replace(/\s+/g, ' ').trim();
  return n;
}

// ─────────────────────────────────────────────────────────────────────────────
// 4. ĐỌC VÀ PARSE CSV
// ─────────────────────────────────────────────────────────────────────────────
function parseCSV(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  const headers = parseCSVLine(lines[0]);
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const values = parseCSVLine(line);
    if (values.length < headers.length - 1) continue;
    const row = {};
    headers.forEach((h, idx) => { row[h] = (values[idx] || '').trim(); });
    rows.push(row);
  }
  return rows;
}

function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') { current += '"'; i++; }
      else inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current);
  return result;
}

// ─────────────────────────────────────────────────────────────────────────────
// 5. PHÂN TÍCH GIÁ (rupee → VNĐ)
// ─────────────────────────────────────────────────────────────────────────────
const INR_TO_VND = 290; // 1 INR ≈ 290 VNĐ (tỷ giá tham khảo)

function parsePrice(priceStr) {
  if (!priceStr) return 0;
  // Xóa ký hiệu tiền tệ và dấu phẩy
  const cleaned = priceStr.replace(/[₹,\s$€£]/g, '').replace(/[^\d.]/g, '');
  const inr = parseFloat(cleaned) || 0;
  // Làm tròn đến 100 VNĐ
  const vnd = Math.round((inr * INR_TO_VND) / 100) * 100;
  return vnd;
}

// ─────────────────────────────────────────────────────────────────────────────
// 6. SỬA ẢNH BRAND (replace ảnh lỗi Amazon)
// ─────────────────────────────────────────────────────────────────────────────
// Ảnh Amazon thường dùng chung (sai brand) - các image ID bị lỗi phổ biến
const WRONG_IMAGE_IDS = [
  '81eM15lVcJL', // Ảnh iPhone vàng bị gán cho nhiều brand khác
  '71AvQd3VzqL', // Ảnh lỗi
  '61uWU0WDMCL', // Ảnh generic
];

const BRAND_FALLBACK_IMAGES = {
  'samsung': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&auto=format',
  'xiaomi': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format',
  'redmi': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format',
  'poco': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format',
  'google': 'https://images.unsplash.com/photo-1598520106830-8c45c2035460?w=600&auto=format',
  'pixel': 'https://images.unsplash.com/photo-1598520106830-8c45c2035460?w=600&auto=format',
  'oneplus': 'https://images.unsplash.com/photo-1567581935884-3349723552ca?w=600&auto=format',
  'oppo': 'https://images.unsplash.com/photo-1556656793-08538906a9f8?w=600&auto=format',
  'vivo': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format',
  'realme': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format',
  'motorola': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format',
  'nokia': 'https://images.unsplash.com/photo-1520923642038-b4259acecbd7?w=600&auto=format',
  'apple': 'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=600&auto=format',
  'iphone': 'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=600&auto=format',
  'macbook': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format',
  'boat': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format',
  'sony': 'https://images.unsplash.com/photo-1545127398-14699f92334b?w=600&auto=format',
  'jbl': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&auto=format',
  'anker': 'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600&auto=format',
  'logitech': 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format',
  'hp': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&auto=format',
  'dell': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format',
  'lenovo': 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=600&auto=format',
  'asus': 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=600&auto=format',
  'acer': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&auto=format',
  'mi': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format',
  'noise': 'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&auto=format',
  'fastrack': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format',
  'titan': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format',
  'casio': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format',
  'default': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=600&auto=format',
};

function isImageWrong(imageUrl, productName, brand) {
  if (!imageUrl) return true;
  // Kiểm tra các image ID lỗi nổi tiếng
  for (const wrongId of WRONG_IMAGE_IDS) {
    if (imageUrl.includes(wrongId)) return true;
  }
  // Kiểm tra ảnh iPhone (quả táo) nhưng sản phẩm không phải Apple
  const lowerBrand = (brand || '').toLowerCase();
  const lowerName = (productName || '').toLowerCase();
  if (imageUrl.includes('81eM15lVcJL') && lowerBrand !== 'apple' && !lowerName.includes('iphone')) {
    return true;
  }
  return false;
}

function getBrandFallbackImage(brand, name) {
  const lower = (brand + ' ' + name).toLowerCase();
  for (const [key, url] of Object.entries(BRAND_FALLBACK_IMAGES)) {
    if (lower.includes(key)) return url;
  }
  return BRAND_FALLBACK_IMAGES['default'];
}

// ─────────────────────────────────────────────────────────────────────────────
// 7. TẠO MÔ TẢ TIẾNG VIỆT
// ─────────────────────────────────────────────────────────────────────────────
function generateVietnameseDescription(name, brand, category, ram, storage, colors) {
  const catLabel = {
    phone: 'điện thoại', laptop: 'laptop', earphone: 'tai nghe',
    smartwatch: 'đồng hồ thông minh', accessory: 'phụ kiện', tablet: 'máy tính bảng',
  }[category] || 'thiết bị';

  let desc = `Sản phẩm ${name} thuộc dòng ${catLabel} cao cấp của thương hiệu ${brand}.`;

  if (ram && storage) {
    desc += ` Được trang bị ${ram} RAM và bộ nhớ trong ${storage}, đảm bảo hiệu năng mượt mà cho mọi tác vụ.`;
  } else if (ram) {
    desc += ` Trang bị ${ram} RAM cho hiệu năng đa nhiệm vượt trội.`;
  } else if (storage) {
    desc += ` Bộ nhớ trong ${storage} rộng rãi, thoải mái lưu trữ mọi dữ liệu.`;
  }

  if (colors && colors.length > 0) {
    desc += ` Có sẵn màu sắc: ${colors.join(', ')}.`;
  }

  const extras = {
    phone: 'Thiết kế hiện đại, màn hình sắc nét, pin bền bỉ cho cả ngày dài sử dụng.',
    laptop: 'Hiệu năng cao, mỏng nhẹ, phù hợp cho công việc và giải trí.',
    earphone: 'Âm thanh chất lượng cao, chống ồn hiệu quả, mang đến trải nghiệm nghe nhạc tuyệt vời.',
    smartwatch: 'Theo dõi sức khỏe toàn diện, thông báo thông minh, pin lâu dài.',
    accessory: 'Chất lượng cao cấp, tương thích rộng rãi với nhiều thiết bị.',
    tablet: 'Màn hình lớn sắc nét, hiệu năng mạnh mẽ cho học tập và giải trí.',
  };
  desc += ' ' + (extras[category] || '');

  return desc.trim();
}

// ─────────────────────────────────────────────────────────────────────────────
// 8. PHÁT HIỆN THƯƠNG HIỆU
// ─────────────────────────────────────────────────────────────────────────────
const KNOWN_BRANDS = [
  'Apple', 'Samsung', 'Xiaomi', 'Redmi', 'POCO', 'Realme', 'Vivo', 'OPPO',
  'OnePlus', 'Motorola', 'Nokia', 'Google', 'Pixel', 'Sony', 'boAt', 'JBL',
  'Anker', 'Logitech', 'HP', 'Dell', 'Lenovo', 'ASUS', 'Acer', 'MSI',
  'Noise', 'Fastrack', 'Titan', 'Casio', 'Fossil', 'boult', 'Zebronics',
  'Ambrane', 'PTron', 'Skullcandy', 'Marshall', 'Bose', 'Sennheiser',
  'Audio-Technica', 'Jabra', 'Plantronics', 'Razer', 'Corsair', 'HyperX',
  'Belkin', 'Ugreen', 'Baseus', 'Itel', 'Lava', 'Micromax', 'Infinix',
  'Tecno', 'Honor', 'Huawei',
];

function detectBrand(name) {
  for (const brand of KNOWN_BRANDS) {
    const regex = new RegExp('\\b' + brand.replace(/[-+]/g, '[-+]?') + '\\b', 'i');
    if (regex.test(name)) return brand;
  }
  // Nếu không tìm được, lấy từ đầu tiên
  const firstWord = name.split(/[\s(]/)[0].trim();
  return firstWord || 'Unknown';
}

// ─────────────────────────────────────────────────────────────────────────────
// 9. HÀM LẦY TÊN TIẾNG VIỆT (Việt hóa tên sản phẩm)
// ─────────────────────────────────────────────────────────────────────────────
function vietnamizeName(name) {
  // Lấy tên base sau khi đã xóa màu và cấu hình RAM/ROM
  let base = name;
  // Bỏ phần trong ngoặc đơn nếu chứa màu/cấu hình
  base = base.replace(/\([^)]*\)/g, '').trim();
  // Bỏ màu sắc ở đuôi tên (thường xuất hiện cuối tên, sau dấu phẩy)
  base = base.replace(/,?\s*(midnight black|carbon black|matte black|glossy black|bold black|phantom black|raging red|active red|active blue|royal blue|navy blue|cobalt blue|steel blue|midnight blue|rose gold|pearl white|cream white|space gr[ae]y|titanium gr[ae]y|army green|dark green|forest green|mint green|olive green|black|white|red|blue|green|yellow|gold|silver|gr[ae]y|pink|purple|violet|orange|coral|mint|teal|aqua|cyan|copper|rose|charcoal|graphite|brown|cream|ivory|beige|sand|lime|lavender|peach|rainbow|multicolor|transparent|clear|golden)\s*$/gi, '');
  return base.trim();
}

// ─────────────────────────────────────────────────────────────────────────────
// 10. MAIN: ĐỌC CSV, GỘP SẢN PHẨM, IMPORT VÀO SUPABASE
// ─────────────────────────────────────────────────────────────────────────────
async function main() {
  console.log('='.repeat(60));
  console.log('BẮT ĐẦU IMPORT DỮ LIỆU SẢN PHẨM THÔNG MINH');
  console.log('='.repeat(60));

  // Đọc file CSV
  const csvPath = path.join(__dirname, '..', 'data for system', 'electronics_product.csv');
  console.log('\n📂 Đọc file CSV:', csvPath);
  const rows = parseCSV(csvPath);
  console.log(`✅ Đọc thành công ${rows.length} dòng thô từ CSV`);

  // ─── BƯỚC 1: LỌC VÀ PARSE DỮ LIỆU THÔ ───
  console.log('\n🔧 Bước 1: Parse và lọc dữ liệu...');
  const validRows = [];
  for (const row of rows) {
    const name = (row['name'] || '').trim();
    if (!name || name.length < 3) continue;
    const price = parsePrice(row['discount_price'] || row['actual_price']);
    if (price < 10000) continue; // Lọc sản phẩm giá quá thấp (lỗi parse)
    if (price > 150000000) continue; // Lọc giá bất thường
    validRows.push({
      name,
      price,
      imageUrl: (row['image'] || '').trim(),
      link: (row['link'] || '').trim(),
      ratings: parseFloat(row['ratings'] || '0') || 0,
      no_of_ratings: parseInt((row['no_of_ratings'] || '0').replace(/[^0-9]/g, '')) || 0,
      mainCategory: (row['main_category'] || '').toLowerCase(),
      subCategory: (row['sub_category'] || '').toLowerCase(),
    });
  }
  console.log(`✅ Còn lại ${validRows.length} dòng hợp lệ sau khi lọc`);

  // Ưu tiên sản phẩm có nhiều đánh giá nhất
  validRows.sort((a, b) => b.no_of_ratings - a.no_of_ratings);

  // ─── BƯỚC 2: GỘP SẢN PHẨM THEO TÊN CHUẨN HÓA ───
  console.log('\n🔧 Bước 2: Gộp sản phẩm theo tên chuẩn hóa...');
  
  // Map: normalizedName -> group object
  const groups = new Map();
  
  for (const row of validRows) {
    const normalized = normalizeName(row.name);
    if (!normalized || normalized.length < 3) continue;
    
    const colors = extractColors(row.name);
    const { ram, storage } = extractRAMStorage(row.name);
    const brand = detectBrand(row.name);
    const category = detectCategory(row.name, row.subCategory);
    
    if (!groups.has(normalized)) {
      // Tạo nhóm mới
      groups.set(normalized, {
        baseName: vietnamizeName(row.name),
        brand,
        category,
        basePrice: row.price,
        minPrice: row.price,
        maxPrice: row.price,
        totalRatings: row.no_of_ratings,
        ratingSum: row.ratings * row.no_of_ratings,
        link: row.link,
        // Màu sắc và ảnh tương ứng
        colorMap: new Map(), // color -> imageUrl
        // Variants cấu hình
        variantMap: new Map(), // "XGB RAM/YGB" -> { price, ram, storage, imageUrl }
        // Ảnh chính
        mainImage: null,
        // Các dòng thô
        rawRows: [],
      });
    }
    
    const group = groups.get(normalized);
    group.rawRows.push(row);
    group.totalRatings += row.no_of_ratings;
    group.ratingSum += row.ratings * row.no_of_ratings;
    group.minPrice = Math.min(group.minPrice, row.price);
    group.maxPrice = Math.max(group.maxPrice, row.price);

    // Xử lý ảnh
    const imgUrl = isImageWrong(row.imageUrl, row.name, brand)
      ? getBrandFallbackImage(brand, row.name)
      : row.imageUrl;

    // Lưu ảnh chính (ảnh đầu tiên, có chất lượng tốt nhất)
    if (!group.mainImage) group.mainImage = imgUrl;

    // Thêm màu sắc
    if (colors.length > 0) {
      for (const color of colors) {
        if (!group.colorMap.has(color)) {
          group.colorMap.set(color, imgUrl);
        }
      }
    }

    // Thêm variant RAM/ROM
    if (ram || storage) {
      const variantKey = [ram, storage].filter(Boolean).join(' / ');
      if (!group.variantMap.has(variantKey)) {
        group.variantMap.set(variantKey, {
          label: variantKey,
          price: row.price,
          ram: ram || '',
          storage: storage || '',
        });
      }
    }
  }

  console.log(`✅ Gộp ${validRows.length} dòng thô thành ${groups.size} nhóm sản phẩm`);

  // ─── BƯỚC 3: CHỌN TOP N SẢN PHẨM ───
  const MAX_PRODUCTS = 1500;
  
  // Sắp xếp nhóm theo số lượng đánh giá (phổ biến nhất trước)
  const sortedGroups = [...groups.values()].sort((a, b) => b.totalRatings - a.totalRatings);
  const selectedGroups = sortedGroups.slice(0, MAX_PRODUCTS);
  console.log(`\n✅ Chọn top ${selectedGroups.length} sản phẩm phổ biến nhất`);

  // ─── BƯỚC 4: TẠO PAYLOAD CHO SUPABASE ───
  console.log('\n🔧 Bước 4: Tạo dữ liệu để import...');
  const products = [];

  for (const group of selectedGroups) {
    const colorOptions = [...group.colorMap.keys()];
    const colorImages = colorOptions.map(c => group.colorMap.get(c));
    const variants = [...group.variantMap.values()]
      .sort((a, b) => a.price - b.price); // Sắp xếp giá tăng dần

    // Tính rating trung bình
    const avgRating = group.totalRatings > 0
      ? Math.min(5, parseFloat((group.ratingSum / group.totalRatings).toFixed(1)))
      : 4.0;

    // Tên sản phẩm: lấy tên base đã được Việt hóa (bỏ màu và cấu hình)
    const productName = group.baseName;

    // Ảnh chính
    const mainImage = group.mainImage || getBrandFallbackImage(group.brand, productName);

    // Tạo ảnh array (ảnh chính + ảnh màu)
    const allImages = [mainImage];
    for (const img of colorImages) {
      if (img && img !== mainImage && !allImages.includes(img)) {
        allImages.push(img);
      }
    }

    // Lấy RAM và storage từ variant đầu tiên (nếu có)
    const firstVariant = variants.length > 0 ? variants[0] : null;

    // Mô tả tiếng Việt
    const description = generateVietnameseDescription(
      productName,
      group.brand,
      group.category,
      firstVariant?.ram || null,
      firstVariant?.storage || null,
      colorOptions
    );

    // Specs JSONB
    const specs = {
      original_link: group.link || '',
      ratings_count: String(group.totalRatings),
    };
    if (colorOptions.length > 0) {
      specs.color_options = colorOptions;
      specs.color_images = colorImages;
    }
    if (variants.length > 0) {
      specs.variants = variants;
    }
    if (firstVariant?.ram)     specs.ram     = firstVariant.ram;
    if (firstVariant?.storage) specs.storage = firstVariant.storage;

    products.push({
      category: group.category,
      brand: group.brand,
      name: productName,
      price: group.minPrice, // Giá thấp nhất (giá base)
      stock: 100,
      description,
      images: allImages,
      specs,
      rating_avg: avgRating,
    });
  }

  console.log(`✅ Chuẩn bị xong ${products.length} sản phẩm để import`);

  // ─── BƯỚC 5: XÓA DỮ LIỆU CŨ VÀ IMPORT MỚI ───
  console.log('\n🗑️  Bước 5: Xóa toàn bộ sản phẩm cũ...');
  const { error: deleteError } = await supabase.from('products').delete().gte('price', 0);
  if (deleteError) { console.error('Lỗi xóa:', deleteError.message); process.exit(1); }
  console.log('✅ Đã xóa sạch bảng products');

  // Import theo batch 50
  console.log(`\n📤 Bước 6: Import ${products.length} sản phẩm vào Supabase (batch 50)...`);
  const BATCH_SIZE = 50;
  let successCount = 0;
  let errorCount = 0;

  for (let i = 0; i < products.length; i += BATCH_SIZE) {
    const batch = products.slice(i, i + BATCH_SIZE);
    const { error } = await supabase.from('products').insert(batch);
    if (error) {
      console.error(`  ❌ Lỗi batch ${i}-${i + BATCH_SIZE}:`, error.message);
      errorCount += batch.length;
    } else {
      successCount += batch.length;
      process.stdout.write(`\r  ✅ Đã import ${successCount}/${products.length} sản phẩm...`);
    }
  }

  console.log(`\n\n${'='.repeat(60)}`);
  console.log(`🎉 HOÀN THÀNH!`);
  console.log(`   ✅ Thành công: ${successCount} sản phẩm`);
  if (errorCount > 0) console.log(`   ❌ Lỗi: ${errorCount} sản phẩm`);
  console.log(`   📦 Tổng: ${products.length} nhóm sản phẩm (gộp từ ${validRows.length} dòng CSV)`);
  console.log(`${'='.repeat(60)}`);

  // Thống kê nhanh
  const withColors = products.filter(p => p.specs.color_options?.length > 0).length;
  const withVariants = products.filter(p => p.specs.variants?.length > 1).length;
  const byCategory = {};
  for (const p of products) { byCategory[p.category] = (byCategory[p.category] || 0) + 1; }
  
  console.log('\n📊 Thống kê:');
  console.log(`   🎨 Sản phẩm có lựa chọn màu sắc: ${withColors}`);
  console.log(`   ⚙️  Sản phẩm có nhiều cấu hình:   ${withVariants}`);
  console.log(`   📂 Theo danh mục:`);
  for (const [cat, count] of Object.entries(byCategory)) {
    console.log(`      - ${cat}: ${count}`);
  }
}

main().catch(err => { console.error('Lỗi không xác định:', err); process.exit(1); });
