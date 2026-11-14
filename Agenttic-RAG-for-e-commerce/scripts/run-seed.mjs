// scripts/run-seed.mjs
// Script chạy seed thông minh: tự phát hiện schema và điều chỉnh
// Chạy: node scripts/run-seed.mjs

import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';

function loadEnv() {
  const envPath = path.resolve(process.cwd(), '.env.local');
  if (!fs.existsSync(envPath)) {
    console.error('❌ Không tìm thấy file .env.local ở thư mục gốc');
    process.exit(1);
  }
  const content = fs.readFileSync(envPath, 'utf8');
  const env = {};
  content.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) return;
    const idx = trimmed.indexOf('=');
    if (idx === -1) return;
    const key = trimmed.substring(0, idx).trim();
    const val = trimmed.substring(idx + 1).trim().replace(/^['"]|['"]$/g, '');
    env[key] = val;
  });
  return env;
}

const env = loadEnv();
const SUPABASE_URL = env.NEXT_PUBLIC_SUPABASE_URL;
const SERVICE_ROLE_KEY = env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
  console.error('❌ Thiếu NEXT_PUBLIC_SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong .env.local');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false }
});

async function detectSchema() {
  const { error } = await supabase.from('products').select('discount').limit(1);
  return !error;
}

async function detectTvConstraint() {
  const { error } = await supabase.from('products').insert({
    category: 'tv', brand: 'Test', name: 'Test TV', price: 1000, stock: 1,
    description: 'Test', specs: {}, images: ['https://test.com']
  }).select('id');
  
  if (error && error.message.includes('check')) {
    return false;
  }
  if (!error) {
    await supabase.from('products').delete().eq('name', 'Test TV').eq('brand', 'Test');
  }
  return true;
}

async function clearProducts() {
  console.log('🗑️ Xóa toàn bộ sản phẩm cũ...');
  const { error } = await supabase.from('products').delete().not('id', 'is', null);
  if (error) throw new Error('Lỗi xóa: ' + error.message);
  console.log('✅ Xóa sản phẩm cũ thành công');
}

// ============================================================
// HÀM ÁNH XẠ ẢNH SẢN PHẨM CHUẨN XÁC TỪ UNSPLASH
// Tránh placeholder chung chung, phù hợp chi tiết cho từng mẫu mã
// ============================================================
function getProductImage(category, brand, family, modelName) {
  const normName = modelName.toLowerCase();
  
  if (category === 'phone') {
    if (brand === 'Apple') {
      if (normName.includes('16')) return 'https://images.unsplash.com/photo-1727375052926-d9487c6f0ca9?w=600';
      if (normName.includes('15')) return 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600';
      if (normName.includes('14')) return 'https://images.unsplash.com/photo-1678685888221-cda773a3dcdb?w=600';
      if (normName.includes('13')) return 'https://images.unsplash.com/photo-1632661676897-6df02930415a?w=600';
      if (normName.includes('12')) return 'https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600';
      if (normName.includes('11')) return 'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=600';
      return 'https://images.unsplash.com/photo-1565538810844-1e119d81a202?w=600'; // SE, X, XS, XR
    }
    if (brand === 'Samsung') {
      if (normName.includes('ultra')) return 'https://images.unsplash.com/photo-1610945415295-d9b21034d1ac?w=600';
      if (normName.includes('s24') || normName.includes('s23')) return 'https://images.unsplash.com/photo-1678911820864-b2c75188e605?w=600';
      return 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600';
    }
    if (brand === 'Xiaomi') return 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600';
    if (brand === 'Google') return 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600';
    if (brand === 'Oppo') return 'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600';
    if (brand === 'Huawei') return 'https://images.unsplash.com/photo-1565849906662-757077f5c9ef?w=600';
    return 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600';
  }
  
  if (category === 'laptop') {
    if (brand === 'Apple') {
      if (normName.includes('pro')) return 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=600';
      return 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600'; // Air
    }
    if (brand === 'Dell') {
      if (normName.includes('xps')) return 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600';
      return 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600';
    }
    if (brand === 'Asus') return 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600';
    if (brand === 'Lenovo') return 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600';
    if (brand === 'HP') return 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=600';
    if (brand === 'Microsoft') return 'https://images.unsplash.com/photo-1585776245991-cf89dd7fc73a?w=600';
    return 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600';
  }
  
  if (category === 'tv') {
    if (brand === 'Samsung') return 'https://images.unsplash.com/photo-1593784991095-a205069470b6?w=600';
    if (brand === 'LG') return 'https://images.unsplash.com/photo-1558888401-3cc1de77652d?w=600';
    if (brand === 'Sony') return 'https://images.unsplash.com/photo-1567690187548-f07b1d7bf5a9?w=600';
    return 'https://images.unsplash.com/photo-1593359677879-a4bb92f4e10a?w=600';
  }
  
  if (category === 'earphone') {
    if (brand === 'Apple') {
      if (normName.includes('max')) return 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600';
      return 'https://images.unsplash.com/photo-1588449668338-d134ae7f3639?w=600';
    }
    if (normName.includes('wh-1000')) return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600';
    if (brand === 'Sony') return 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600';
    if (brand === 'Marshall') return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600';
    return 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600';
  }
  
  if (category === 'smartwatch') {
    if (brand === 'Apple') return 'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600';
    if (brand === 'Samsung') return 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600';
    return 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=600';
  }
  
  // accessory
  if (brand === 'Logitech') return 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600';
  if (brand === 'Anker') return 'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600';
  return 'https://images.unsplash.com/photo-1585776245991-cf89dd7fc73a?w=600';
}

const PHONE_COLORS = ['Titan Tự Nhiên', 'Titan Đen', 'Titan Trắng', 'Xanh Dương', 'Đen Huyền Bí', 'Trắng Ngọc Trai', 'Xám Tinh Tế', 'Hồng cánh sen'];
const LAPTOP_COLORS = ['Xám Không Gian (Space Gray)', 'Bạc Ánh Kim (Silver)', 'Vàng Đồng (Starlight)', 'Đen Nhám (Matte Black)'];
const TV_COLORS = ['Đen Huyền Bí'];
const WATCH_STRAPS = ['Dây Cao Su Thể Thao', 'Dây Da Bò Cao Cấp', 'Dây Vải Dệt Trail Loop', 'Dây Kim Loại Thép Không Gỉ', 'Dây Silicone Mềm'];

// Khuôn mẫu Edition gộp chọn
const EDITIONS_TEMPLATE = [
  { name: 'Chính hãng (VN/A)', condition: 'Mới 100%', priceFactor: 1.0 },
  { name: 'Nhập khẩu (Mã LL/A, ZP/A...)', condition: 'Mới 100% (Nhập khẩu)', priceFactor: 0.95 },
  { name: 'Cũ 99% (Likenew)', condition: 'Đã qua sử dụng (Đẹp 99%)', priceFactor: 0.85 },
  { name: 'Cũ 95%', condition: 'Đã qua sử dụng (Xước nhẹ 95%)', priceFactor: 0.75 },
  { name: 'Trôi bảo hành', condition: 'Mới trôi bảo hành', priceFactor: 0.9 }
];

// ============================================================
// HÌNH THÀNH MÔ HÌNH 1000+ SẢN PHẨM KHÔNG TRÙNG HIỂN THỊ VỚI EDITIONS
// ============================================================
function generateAllProducts() {
  const list = [];

  // Các phiên bản khu vực phân phối điện thoại để đa dạng hóa model RAG
  const REGION_VERSIONS = [
    { suffix: 'Mã VN/A (Việt Nam)', factor: 1.0 },
    { suffix: 'Mã LL/A (Bản Mỹ)', factor: 0.96 },
    { suffix: 'Mã ZP/A (Singapore)', factor: 0.98 },
    { suffix: 'Mã KH/A (Bản Hàn)', factor: 0.95 }
  ];

  // 1. GENERATE PHONES (~450 models độc nhất)
  const phoneBrands = [
    {
      brand: 'Apple',
      families: [
        { name: 'iPhone 16', price: 22000000 },
        { name: 'iPhone 15', price: 19000000 },
        { name: 'iPhone 14', price: 16500000 },
        { name: 'iPhone 13', price: 13500000 },
        { name: 'iPhone 12', price: 11000000 },
        { name: 'iPhone 11', price: 8500000 },
        { name: 'iPhone XS Max', price: 7500000 },
        { name: 'iPhone XS', price: 6500000 },
        { name: 'iPhone XR', price: 5500000 },
        { name: 'iPhone X', price: 4800000 },
        { name: 'iPhone SE Gen 3', price: 7900000 },
        { name: 'iPhone SE Gen 2', price: 5200000 },
        { name: 'iPhone 8 Plus', price: 4000000 },
        { name: 'iPhone 8', price: 3200000 },
        { name: 'iPhone 7 Plus', price: 3000000 },
        { name: 'iPhone 7', price: 2200000 },
        { name: 'iPhone 6s Plus', price: 2000000 },
        { name: 'iPhone 6s', price: 1500000 }
      ],
      suffixes: ['Pro Max', 'Pro', 'Plus', 'thường', 'mini']
    },
    {
      brand: 'Samsung',
      families: [
        { name: 'Galaxy S24', price: 18000000 },
        { name: 'Galaxy S23', price: 15000000 },
        { name: 'Galaxy S22', price: 12000000 },
        { name: 'Galaxy S21', price: 9500000 },
        { name: 'Galaxy S20', price: 7500000 },
        { name: 'Galaxy Note 20', price: 8500000 },
        { name: 'Galaxy Note 10', price: 6200000 },
        { name: 'Galaxy A55', price: 8500000 },
        { name: 'Galaxy A35', price: 6500000 },
        { name: 'Galaxy A15', price: 3800000 },
        { name: 'Galaxy M54', price: 7900000 },
        { name: 'Galaxy M34', price: 5200000 },
        { name: 'Galaxy A25', price: 5500000 },
        { name: 'Galaxy A05s', price: 2900000 },
        { name: 'Galaxy Note 9', price: 4500000 },
        { name: 'Galaxy S10', price: 4200000 }
      ],
      suffixes: ['Ultra', 'Plus', 'thường', 'FE']
    },
    {
      brand: 'Xiaomi',
      families: [
        { name: 'Xiaomi 14', price: 17000000 },
        { name: 'Xiaomi 13', price: 14000000 },
        { name: 'Xiaomi 12', price: 11000000 },
        { name: 'Redmi Note 13', price: 5500000 },
        { name: 'Redmi Note 12', price: 4200000 },
        { name: 'Poco F6', price: 9500000 },
        { name: 'Poco X6', price: 7000000 },
        { name: 'Redmi 13C', price: 2900000 },
        { name: 'Redmi A3', price: 1900000 },
        { name: 'Redmi Note 11', price: 3200000 },
        { name: 'Poco F5', price: 7200000 }
      ],
      suffixes: ['Ultra', 'Pro', 'thường', 'Lite']
    },
    {
      brand: 'Google',
      families: [
        { name: 'Pixel 9', price: 21000000 },
        { name: 'Pixel 8', price: 16000000 },
        { name: 'Pixel 7', price: 12000000 },
        { name: 'Pixel 6', price: 8500000 },
        { name: 'Pixel 5', price: 5200000 },
        { name: 'Pixel 4a', price: 3500000 },
        { name: 'Pixel 4 XL', price: 3800000 }
      ],
      suffixes: ['Pro', 'thường', 'a']
    },
    {
      brand: 'Oppo',
      families: [
        { name: 'Oppo Find X7', price: 19000000 },
        { name: 'Oppo Find X6', price: 15500000 },
        { name: 'Oppo Reno11', price: 9500000 },
        { name: 'Oppo Reno10', price: 7800000 },
        { name: 'Oppo A98', price: 6200000 },
        { name: 'Oppo A78', price: 4500000 },
        { name: 'Oppo Reno9', price: 5800000 }
      ],
      suffixes: ['Ultra', 'Pro', 'thường']
    },
    {
      brand: 'Vivo',
      families: [
        { name: 'Vivo X100', price: 18000000 },
        { name: 'Vivo X90', price: 14500000 },
        { name: 'Vivo V30', price: 9200000 },
        { name: 'Vivo V29', price: 7500000 },
        { name: 'Vivo Y36', price: 4800000 },
        { name: 'Vivo Y17s', price: 3000000 },
        { name: 'Vivo V27', price: 5900000 }
      ],
      suffixes: ['Pro', 'thường']
    },
    {
      brand: 'Realme',
      families: [
        { name: 'Realme GT5', price: 11000000 },
        { name: 'Realme 12 Pro', price: 8200000 },
        { name: 'Realme 11 Pro', price: 6800000 },
        { name: 'Realme C67', price: 4200000 },
        { name: 'Realme C55', price: 3200000 }
      ],
      suffixes: ['Pro', 'thường']
    },
    {
      brand: 'OnePlus',
      families: [
        { name: 'OnePlus 12', price: 16500000 },
        { name: 'OnePlus 11', price: 13500000 },
        { name: 'OnePlus 10 Pro', price: 9800000 },
        { name: 'OnePlus Nord 3', price: 7500000 },
        { name: 'OnePlus Nord CE 3', price: 5200000 }
      ],
      suffixes: ['Pro', 'thường']
    }
  ];

  phoneBrands.forEach(b => {
    b.families.forEach(fam => {
      b.suffixes.forEach(suf => {
        // Lọc các đời máy không hợp lệ thực tế
        if (b.brand === 'Apple') {
          if (fam.name.includes('SE') && suf !== 'thường') return;
          if (fam.name.includes('XS') && ['mini', 'Plus', 'thường'].includes(suf)) return;
          if (fam.name.includes('XR') && suf !== 'thường') return;
          if (fam.name.includes('X') && fam.name === 'iPhone X' && suf !== 'thường') return;
          if (['iPhone 11', 'iPhone XS', 'iPhone XR', 'iPhone X', 'iPhone 8', 'iPhone 7', 'iPhone 6s'].includes(fam.name) && suf === 'Plus' && fam.name !== 'iPhone 8 Plus' && fam.name !== 'iPhone 7 Plus' && fam.name !== 'iPhone 6s Plus') return;
          if (fam.name.includes('Plus') && suf !== 'thường') return;
          if (['iPhone 14', 'iPhone 15', 'iPhone 16'].includes(fam.name) && suf === 'mini') return;
          if (['iPhone 11', 'iPhone 12', 'iPhone 13'].includes(fam.name) && suf === 'Plus') return;
        }
        if (b.brand === 'Samsung') {
          if (fam.name.includes('A') && suf !== 'thường') return;
          if (fam.name.includes('M') && suf !== 'thường') return;
          if (fam.name.includes('Note') && suf === 'FE') return;
          if (fam.name.includes('Note 10') && suf === 'Ultra') return; 
          if (fam.name.includes('Note 20') && suf === 'Plus') return; 
          if (fam.name.includes('Note 9') && suf !== 'thường') return;
          if (fam.name.includes('S10') && suf === 'FE') return;
        }
        if (b.brand === 'Xiaomi') {
          if (fam.name.includes('Redmi') && suf !== 'thường') return;
          if (fam.name.includes('Poco') && (suf === 'Ultra' || suf === 'Lite')) return;
        }
        if (b.brand === 'Google') {
          if (fam.name.includes('5') && suf !== 'thường') return;
          if (fam.name.includes('4') && suf !== 'thường') return;
        }
        if (b.brand === 'Oppo' || b.brand === 'Vivo' || b.brand === 'Realme' || b.brand === 'OnePlus') {
          if (fam.name.includes('A') && suf !== 'thường') return;
          if (fam.name.includes('Y') && suf !== 'thường') return;
          if (fam.name.includes('C') && suf !== 'thường') return;
          if (fam.name.includes('Nord') && suf === 'Pro') return;
        }

        const baseModelName = suf === 'thường' ? fam.name : `${fam.name} ${suf}`;
        
        // Nhân bản theo Region để RAG phong phú, không trùng tên sản phẩm trên web
        const regionsToUse = b.brand === 'Apple' ? REGION_VERSIONS : REGION_VERSIONS.slice(0, 2);
        
        regionsToUse.forEach(reg => {
          const name = b.brand === 'Apple' 
            ? `${baseModelName} (${reg.suffix})` 
            : `${b.brand} ${baseModelName} (${reg.suffix})`;

          let startPrice = fam.price;
          if (suf === 'Pro Max' || suf === 'Ultra') startPrice += 9000000;
          else if (suf === 'Pro') startPrice += 6000000;
          else if (suf === 'Plus') startPrice += 3000000;
          else if (suf === 'mini' || suf === 'Lite' || suf === 'a') startPrice -= 2000000;

          // Nhân với hệ số mã vùng & đảm bảo không âm
          startPrice = Math.max(1500000, Math.round(startPrice * reg.factor));

          const colors = PHONE_COLORS.slice(0, 3 + Math.floor(Math.random() * 4));
          const img = getProductImage('phone', b.brand, fam.name, baseModelName);

          // Tạo Editions gộp chọn
          const editions = EDITIONS_TEMPLATE.map(ed => {
            const edPrice = Math.max(1200000, Math.round(startPrice * ed.priceFactor));
            const variants = ['128GB', '256GB', '512GB', '1TB'].map((storage, idx) => {
              if (storage === '1TB' && !['Pro', 'Pro Max', 'Ultra'].includes(suf)) return null;
              if (['iPhone X', 'iPhone XR', 'iPhone XS', 'iPhone 11', 'Galaxy S20', 'Pixel 6'].includes(fam.name) && storage === '1TB') return null;
              if (fam.name.includes('A15') && (storage === '512GB' || storage === '1TB')) return null;
              
              return {
                label: storage,
                price: Math.round((edPrice + idx * 2000000 * ed.priceFactor) / 10000) * 10000
              };
            }).filter(Boolean);

            return {
              name: ed.name,
              condition: ed.condition,
              variants
            };
          });

          const reprPrice = editions[0].variants[0].price;
          const discount = Math.random() > 0.4 ? Math.floor(5 + Math.random() * 15) : 0;
          const original_price = discount > 0 ? Math.round(reprPrice / (1 - discount/100) / 10000) * 10000 : reprPrice;

          list.push({
            category: 'phone',
            brand: b.brand,
            name,
            price: reprPrice,
            original_price,
            discount,
            stock: Math.floor(10 + Math.random() * 90),
            rating_avg: parseFloat((4.0 + Math.random() * 1.0).toFixed(1)),
            images: [img],
            description: `Điện thoại di động thông minh ${name} chất lượng cao, thiết kế sang trọng lịch lãm và cấu hình cực khủng hoạt động mượt mà.`,
            specs: {
              chip: b.brand === 'Apple' ? 'Apple A-Series Bionic / Pro' : 'Snapdragon / Dimensity',
              screen: 'Super AMOLED / LTPO OLED 120Hz mượt mà',
              color_options: colors,
              color_images: colors.map(() => img),
              editions
            }
          });
        });
      });
    });
  });

  // 2. GENERATE LAPTOPS (~300+ models độc nhất)
  const laptopBrands = [
    {
      brand: 'Apple',
      families: ['MacBook Air M3', 'MacBook Air M2', 'MacBook Air M1', 'MacBook Pro M3 Pro', 'MacBook Pro M3 Max', 'MacBook Pro M2', 'MacBook Pro M1 Pro'],
      sizes: ['13 inch', '14 inch', '15 inch', '16 inch']
    },
    {
      brand: 'Dell',
      families: ['Dell XPS 13', 'Dell XPS 15', 'Dell Inspiron 15 (Gen 13)', 'Dell Inspiron 14 (Gen 12)', 'Dell Latitude 14', 'Dell Vostro 15', 'Dell Precision 15'],
      sizes: ['13.3"', '14"', '15.6"', '16"']
    },
    {
      brand: 'Asus',
      families: ['Asus ROG Zephyrus G14', 'Asus ROG Strix G16', 'Asus ZenBook 14 OLED', 'Asus VivoBook 15', 'Asus TUF Gaming A15', 'Asus ExpertBook B9'],
      sizes: ['14"', '15.6"', '16"']
    },
    {
      brand: 'Lenovo',
      families: ['ThinkPad X1 Carbon Gen 11', 'ThinkPad T14 Gen 4', 'IdeaPad Slim 5', 'Legion 5 Pro', 'Yoga Book 9i Dual Screen'],
      sizes: ['13.3"', '14"', '15.6"', '16"']
    },
    {
      brand: 'HP',
      families: ['HP Spectre x360 14', 'HP Envy 16', 'HP Pavilion 15', 'HP Victus 16', 'HP ProBook 440 G10', 'HP EliteBook 840 G10'],
      sizes: ['13.5"', '14"', '15.6"', '16"']
    },
    {
      brand: 'Acer',
      families: ['Acer Swift Go 14', 'Acer Aspire 5', 'Acer Nitro V 15', 'Acer Predator Helios 16', 'Acer Spin 5'],
      sizes: ['14"', '15.6"', '16"']
    },
    {
      brand: 'MSI',
      families: ['MSI Modern 14', 'MSI Prestige 16', 'MSI Katana 15', 'MSI Cyborg 15', 'MSI Stealth 16'],
      sizes: ['14"', '15.6"', '16"']
    }
  ];

  // Các phiên bản CPU để phân mảnh laptop
  const CPU_VERSIONS = [
    { suffix: 'Intel Core i5', factor: 1.0 },
    { suffix: 'Intel Core i7', factor: 1.2 },
    { suffix: 'AMD Ryzen 7', factor: 1.05 }
  ];

  laptopBrands.forEach(b => {
    b.families.forEach(fam => {
      b.sizes.forEach(size => {
        if (b.brand === 'Apple') {
          if (fam.includes('Air') && ['14 inch', '16 inch'].includes(size)) return;
          if (fam.includes('Pro') && ['13 inch', '15 inch'].includes(size) && !fam.includes('M2')) return;
        }

        // Với Apple ta giữ nguyên, các brand khác ta nhân bản qua CPU_VERSIONS
        const versionsToUse = b.brand === 'Apple' ? [{ suffix: 'Chip Apple Silicon', factor: 1.0 }] : CPU_VERSIONS;

        versionsToUse.forEach(cpu => {
          const name = `${b.brand} ${fam} ${size} (${cpu.suffix})`;
          const colors = LAPTOP_COLORS.slice(0, 2 + Math.floor(Math.random() * 3));
          const img = getProductImage('laptop', b.brand, fam, name);

          let basePrice = 14000000;
          if (fam.includes('Spectre') || fam.includes('Carbon') || fam.includes('XPS') || fam.includes('Max') || fam.includes('Blade') || fam.includes('Studio')) {
            basePrice = 38000000;
          } else if (fam.includes('ZenBook') || fam.includes('Pro') || fam.includes('Zephyrus') || fam.includes('Legion') || fam.includes('Predator') || fam.includes('EliteBook')) {
            basePrice = 27000000;
          } else if (fam.includes('Inspiron') || fam.includes('Pavilion') || fam.includes('Victus') || fam.includes('TUF') || fam.includes('Nitro') || fam.includes('Modern')) {
            basePrice = 17000000;
          }

          // Nhân hệ số CPU
          basePrice = Math.round(basePrice * cpu.factor);

          const editions = EDITIONS_TEMPLATE.slice(0, 3).map(ed => {
            const edPrice = Math.round(basePrice * ed.priceFactor);
            const configOpts = [
              { ram: '8GB', ssd: '256GB', priceOffset: 0 },
              { ram: '16GB', ssd: '512GB', priceOffset: 3500000 },
              { ram: '16GB', ssd: '1TB', priceOffset: 6500000 }
            ];

            const finalConfigs = (fam.includes('Max') || fam.includes('Carbon') || fam.includes('XPS') || fam.includes('Predator')) 
              ? configOpts.filter(c => c.ram !== '8GB')
              : configOpts;

            const variants = finalConfigs.map(c => ({
              label: `${c.ram} RAM / ${c.ssd} SSD`,
              price: Math.round((edPrice + c.priceOffset * ed.priceFactor) / 10000) * 10000
            }));

            return {
              name: ed.name,
              condition: ed.condition,
              variants
            };
          });

          const reprPrice = editions[0].variants[0].price;
          const discount = Math.random() > 0.4 ? Math.floor(5 + Math.random() * 12) : 0;
          const original_price = discount > 0 ? Math.round(reprPrice / (1 - discount/100) / 10000) * 10000 : reprPrice;

          list.push({
            category: 'laptop',
            brand: b.brand,
            name,
            price: reprPrice,
            original_price,
            discount,
            stock: Math.floor(5 + Math.random() * 25),
            rating_avg: parseFloat((4.3 + Math.random() * 0.7).toFixed(1)),
            images: [img],
            description: `Máy tính xách tay cao cấp ${name} sở hữu hiệu năng mạnh mẽ, bàn phím gõ êm ái và màn hình hiển thị sắc nét đỉnh cao.`,
            specs: {
              screen: `${size} hiển thị sắc nét chuẩn màu sắc`,
              color_options: colors,
              color_images: colors.map(() => img),
              editions
            }
          });
        });
      });
    });
  });

  // 3. GENERATE TV (~150 models độc nhất)
  const tvBrands = [
    { brand: 'Samsung', families: ['Neo QLED 8K QN900C', 'Neo QLED 4K QN90C', 'QLED 4K Q70C', 'Crystal UHD CU8000', 'The Frame LS03C'] },
    { brand: 'LG', families: ['OLED evo G3 Gallery', 'OLED C3 Series', 'QNED 4K QNED80', 'NanoCell NANO75', 'UHD Smart TV UR7800'] },
    { brand: 'Sony', families: ['Bravia XR A95L QD-OLED', 'Bravia XR X90L LED', 'Bravia X80L Google TV', 'Bravia X75K 4K'] },
    { brand: 'Xiaomi', families: ['TV S Pro 65/75 Mini LED', 'TV A Pro Bezelless HDR', 'TV EA Pro Metal Frame'] },
    { brand: 'TCL', families: ['QD-Mini LED C845', 'QLED C745 Gaming', 'UHD Google TV P745'] }
  ];

  const tvSizes = ['43 inch', '50 inch', '55 inch', '65 inch', '75 inch', '85 inch'];

  tvBrands.forEach(b => {
    b.families.forEach(fam => {
      // Nhân bản qua 3 đời Model Year để tăng lượng TV benchmark
      ['2024', '2023', '2022'].forEach(year => {
        const name = `${b.brand} ${fam} (${year})`;
        const img = getProductImage('tv', b.brand, fam, name);

        let basePrice = 6000000;
        if (fam.includes('8K') || fam.includes('Gallery') || fam.includes('QD-OLED')) basePrice = 42000000;
        else if (fam.includes('Mini LED') || fam.includes('OLED') || fam.includes('QN90')) basePrice = 25000000;
        else if (fam.includes('QLED') || fam.includes('QNED') || fam.includes('The Frame')) basePrice = 14500000;

        // Trượt giá theo năm sản xuất
        if (year === '2023') basePrice = Math.round(basePrice * 0.88);
        if (year === '2022') basePrice = Math.round(basePrice * 0.78);

        const editions = EDITIONS_TEMPLATE.slice(0, 2).map(ed => {
          const edPrice = Math.round(basePrice * ed.priceFactor);
          const variants = tvSizes.map(size => {
            const sizeFactor = size === '43 inch' ? 1.0 : size === '50 inch' ? 1.25 : size === '55 inch' ? 1.5 : size === '65 inch' ? 2.1 : size === '75 inch' ? 3.2 : 4.8;
            return {
              label: size,
              price: Math.round(edPrice * sizeFactor / 100000) * 100000
            };
          });

          return {
            name: ed.name,
            condition: ed.condition,
            variants
          };
        });

        const reprPrice = editions[0].variants[0].price;
        const discount = Math.random() > 0.3 ? Math.floor(5 + Math.random() * 20) : 0;
        const original_price = discount > 0 ? Math.round(reprPrice / (1 - discount/100) / 10000) * 10000 : reprPrice;

        list.push({
          category: 'tv',
          brand: b.brand,
          name,
          price: reprPrice,
          original_price,
          discount,
          stock: Math.floor(3 + Math.random() * 15),
          rating_avg: parseFloat((4.1 + Math.random() * 0.9).toFixed(1)),
          images: [img],
          description: `Smart Tivi ${name} mang đến trải nghiệm nghe nhìn đỉnh cao chuẩn rạp phim tại gia với hình ảnh siêu sắc nét và âm thanh vòm sống động.`,
          specs: {
            resolution: fam.includes('8K') ? '8K Ultra HD (7680x4320)' : '4K Ultra HD (3840x2160)',
            color_options: TV_COLORS,
            color_images: [img],
            editions
          }
        });
      });
    });
  });

  // 4. GENERATE EARPHONES (~150+ models độc nhất)
  const earphoneBrands = [
    { brand: 'Apple', families: ['AirPods Pro Gen 2 USB-C', 'AirPods Max', 'AirPods Gen 4 ANC', 'AirPods Gen 3 Lightning'] },
    { brand: 'Sony', families: ['WF-1000XM5 ANC', 'WH-1000XM5 Over-Ear', 'LinkBuds S Ultra Light', 'WH-CH720N Wireless', 'WH-CH520 Extra Bass'] },
    { brand: 'JBL', families: ['Tour Pro 3 Smart Case', 'Tune Beam 2 Waterproof', 'Live 670NC Noise Cancelling', 'Wave Beam Signature Sound'] },
    { brand: 'Bose', families: ['QuietComfort Ultra ANC', 'QuietComfort 45 Classic', 'QuietComfort Earbuds II'] },
    { brand: 'Sennheiser', families: ['Momentum 4 Wireless', 'Momentum True Wireless 4', 'Accentum Wireless ANC'] },
    { brand: 'Marshall', families: ['Motif II ANC', 'Minor III Earbuds', 'Major IV Bluetooth', 'Monitor II ANC'] },
    { brand: 'Beats', families: ['Beats Fit Pro ANC', 'Beats Studio Buds +', 'Beats Studio Pro Over-Ear'] },
    { brand: 'Jabra', families: ['Jabra Elite 10 ANC', 'Jabra Elite 8 Active', 'Jabra Elite 4 Active'] }
  ];

  const earColors = ['Đen Huyền Bí', 'Trắng Ngọc Trai', 'Xanh Navy', 'Bạc Sang Trọng', 'Hồng Nhẹ Nhàng'];

  earphoneBrands.forEach(b => {
    b.families.forEach(fam => {
      // Mỗi tai nghe sinh ra 2 thế hệ sản phẩm (đời mới/đời cũ)
      ['Mới 100%', 'Refurbished (Tân trang)'].forEach(status => {
        const isRefurb = status.includes('Refurbished');
        const name = `${b.brand} ${fam}${isRefurb ? ' - Refurbished' : ''}`;
        const img = getProductImage('earphone', b.brand, fam, name);
        
        let basePrice = 1200000;
        if (fam.includes('Max') || fam.includes('Momentum 4') || fam.includes('Ultra') || fam.includes('Monitor II')) basePrice = 7500000;
        else if (fam.includes('1000XM5') || fam.includes('QC 45')) basePrice = 5500000;
        else if (fam.includes('Pro') || fam.includes('Tour') || fam.includes('Motif')) basePrice = 4000000;

        if (isRefurb) basePrice = Math.round(basePrice * 0.75);

        const editions = EDITIONS_TEMPLATE.slice(0, 3).map(ed => {
          const edPrice = Math.round(basePrice * ed.priceFactor);
          const variants = [
            { label: 'Bản Tiêu Chuẩn', price: edPrice },
            { label: 'Bản Có Hộp Sạc Không Dây MagSafe', price: Math.round((edPrice + 800000 * ed.priceFactor) / 10000) * 10000 }
          ];

          return {
            name: ed.name,
            condition: ed.condition,
            variants
          };
        });

        const reprPrice = editions[0].variants[0].price;
        const discount = Math.random() > 0.4 ? Math.floor(5 + Math.random() * 20) : 0;
        const original_price = discount > 0 ? Math.round(reprPrice / (1 - discount/100) / 10000) * 10000 : reprPrice;

        list.push({
          category: 'earphone',
          brand: b.brand,
          name,
          price: reprPrice,
          original_price,
          discount,
          stock: Math.floor(10 + Math.random() * 70),
          rating_avg: parseFloat((4.2 + Math.random() * 0.8).toFixed(1)),
          images: [img],
          description: `Tai nghe cao cấp ${name} mang đến chất âm đỉnh cao, công nghệ chống ồn chủ động ANC tiên tiến và thời lượng pin sử dụng bền bỉ cả ngày dài.`,
          specs: {
            anc: 'Chống ồn chủ động ANC thông minh thích ứng',
            color_options: earColors.slice(0, 2 + Math.floor(Math.random() * 3)),
            color_images: earColors.map(() => img),
            editions
          }
        });
      });
    });
  });

  // 5. GENERATE SMARTWATCH (~120+ models độc nhất)
  const watchBrands = [
    { brand: 'Apple', families: ['Watch Ultra 2 LTE', 'Watch Series 9 GPS', 'Watch Series 8 Aluminum', 'Watch SE Gen 2', 'Watch Series 7 Steel'] },
    { brand: 'Samsung', families: ['Watch Ultra Titan', 'Watch7 LTE Steel', 'Watch6 Classic Bluetooth', 'Watch6 Active LTE', 'Watch5 Pro GPS'] },
    { brand: 'Garmin', families: ['Fenix 7X Pro Solar Solar', 'Forerunner 965 AMOLED', 'Venu 3S Health Tracker', 'Instinct 2X Solar Rugged', 'Forerunner 265 Music'] },
    { brand: 'Huawei', families: ['Watch GT 4 Pro Steel', 'Watch GT 3 Pro Ceramic', 'Watch Fit 3 Active', 'Watch Ultimate Titan'] },
    { brand: 'Xiaomi', families: ['Watch S3 Steel', 'Watch 2 Pro AMOLED', 'Redmi Watch 4 Active', 'Smart Band 8 Pro'] }
  ];

  watchBrands.forEach(b => {
    b.families.forEach(fam => {
      // Sinh 2 Edition size mặt khác nhau của smartwatch
      const name = `${b.brand} ${fam}`;
      const img = getProductImage('smartwatch', b.brand, fam, name);

      let basePrice = 3500000;
      if (fam.includes('Ultra') || fam.includes('Fenix')) basePrice = 18000000;
      else if (fam.includes('965') || fam.includes('Series 9') || fam.includes('Ultimate')) basePrice = 11000000;
      else if (fam.includes('Watch7') || fam.includes('Classic') || fam.includes('Venu') || fam.includes('Watch 2') || fam.includes('Watch5')) basePrice = 7000000;

      const editions = EDITIONS_TEMPLATE.slice(0, 3).map(ed => {
        const edPrice = Math.round(basePrice * ed.priceFactor);
        const finalVariants = [
          { label: 'Mặt Nhỏ (41mm / 42mm)', price: edPrice },
          { label: 'Mặt Lớn (45mm / 47mm)', price: Math.round((edPrice + 1200000 * ed.priceFactor) / 10000) * 10000 }
        ];
        if (fam.includes('Ultra') || fam.includes('Fenix') || fam.includes('Ultimate')) {
          finalVariants.length = 0;
          finalVariants.push({ label: 'Mặt Titan Siêu Bền (49mm / 51mm)', price: edPrice });
        }

        return {
          name: ed.name,
          condition: ed.condition,
          variants: finalVariants
        };
      });

      const reprPrice = editions[0].variants[0].price;
      const discount = Math.random() > 0.4 ? Math.floor(5 + Math.random() * 15) : 0;
      const original_price = discount > 0 ? Math.round(reprPrice / (1 - discount/100) / 10000) * 10000 : reprPrice;

      list.push({
        category: 'smartwatch',
        brand: b.brand,
        name,
        price: reprPrice,
        original_price,
        discount,
        stock: Math.floor(5 + Math.random() * 40),
        rating_avg: parseFloat((4.2 + Math.random() * 0.8).toFixed(1)),
        images: [img],
        description: `Đồng hồ thông minh cao cấp ${name} hỗ trợ đắc lực quản lý công việc và theo dõi các chỉ số sức khỏe, rèn luyện thể thao chuyên nghiệp hàng ngày.`,
        specs: {
          waterproof: 'IP68 / 5ATM chống nước tốt bơi lội thoải mái',
          color_options: WATCH_STRAPS.slice(0, 3 + Math.floor(Math.random() * 3)),
          color_images: WATCH_STRAPS.map(() => img),
          editions
        }
      });
    });
  });

  // 6. GENERATE ACCESSORY (~200+ models độc nhất)
  const accBrands = [
    { brand: 'Anker', families: ['Cáp Sạc Prime GaN 100W Fast Charge', 'Củ Sạc 737 GaN 120W 3-Ports', 'Sạc Nhanh Nano 30W Cute Design', 'Sạc Dự Phòng PowerCore 10000mAh', 'Sạc Dự Phòng PowerBank 20000mAh 65W', 'Cáp PowerLine+ USB-C to Lightning', 'Đế Sạc Không Dây Anker 3-in-1'] },
    { brand: 'Logitech', families: ['Chuột MX Master 3S Silent Mouse', 'Bàn Phím MX Keys S Backlit Keyboard', 'Chuột Không Dây MX Anywhere 3S Compact', 'Chuột Gaming G Pro X Superlight 2', 'StreamCam Full HD Auto-Focus', 'Webcam MX Brio Ultra HD 4K', 'Chuột Công Thái Học Lift Ergonomic'] },
    { brand: 'Apple', families: ['Sạc Không Dây MagSafe Charger 15W', 'Củ Sạc Nhanh 20W USB-C Adapter', 'Bút Cảm Ứng Pencil Pro Bluetooth', 'Bàn Phím Magic Keyboard iPad Air', 'Ví Da MagSafe iPhone FineWoven'] },
    { brand: 'Ugreen', families: ['Cáp Sạc Nhanh 240W Nylon Braided', 'Bộ Chuyển Đổi Hub 7-in-1 Type-C', 'Giá Đỡ Laptop Nhôm Ergonomic Stand', 'Bộ Phụ Kiện Sạc GaN Nexode 65W', 'Đế Tản Nhiệt Laptop Ugreen Dual Fan'] },
    { brand: 'Baseus', families: ['Đèn Treo Màn Hình ScreenBar Eye-Care', 'Sạc Dự Phòng Bipow 30W 20000mAh', 'Củ Sạc GaN5 Pro 65W 3-Ports', 'Tẩu Sạc Ô Tô Baseus 160W Super Charge'] }
  ];

  accBrands.forEach(b => {
    b.families.forEach(fam => {
      // Mỗi phụ kiện sinh ra bản thường và bản màu sắc đặc biệt
      ['Bản Màu Cơ Bản', 'Bản Màu Sắc Đặc Biệt'].forEach(type => {
        const name = `${b.brand} ${fam} - ${type}`;
        const img = getProductImage('accessory', b.brand, fam, name);
        const colors = ['Màu Đen Nhám', 'Màu Trắng Sữa', 'Màu Xám Không Gian', 'Màu Xanh Mint'];

        let basePrice = 250000;
        if (fam.includes('Brio') || fam.includes('MX Keys') || fam.includes('Superlight') || fam.includes('MX Master') || fam.includes('Magic Keyboard')) basePrice = 2300000;
        else if (fam.includes('StreamCam') || fam.includes('GaN 100W') || fam.includes('20000mAh') || fam.includes('Pencil')) basePrice = 1200000;
        else if (fam.includes('MagSafe') || fam.includes('Hub 7-in-1')) basePrice = 650000;

        if (type.includes('Đặc Biệt')) basePrice += 150000;

        const editions = EDITIONS_TEMPLATE.slice(0, 2).map(ed => {
          const edPrice = Math.round(basePrice * ed.priceFactor);
          const variants = [
            { label: 'Bản Tiêu Chuẩn', price: edPrice },
            { label: 'Bản Fullbox Kèm Đồ Chơi', price: Math.round((edPrice + 250000 * ed.priceFactor) / 10000) * 10000 }
          ];

          return {
            name: ed.name,
            condition: ed.condition,
            variants
          };
        });

        const reprPrice = editions[0].variants[0].price;
        const discount = Math.random() > 0.4 ? Math.floor(5 + Math.random() * 30) : 0;
        const original_price = discount > 0 ? Math.round(reprPrice / (1 - discount/100) / 10000) * 10000 : reprPrice;

        list.push({
          category: 'accessory',
          brand: b.brand,
          name,
          price: reprPrice,
          original_price,
          discount,
          stock: Math.floor(20 + Math.random() * 80),
          rating_avg: parseFloat((4.2 + Math.random() * 0.8).toFixed(1)),
          images: [img],
          description: `Phụ kiện cao cấp ${name} mang lại sự tiện ích vượt trội, nâng tầm hiệu suất làm việc và giải trí cùng thiết bị của bạn.`,
          specs: {
            color_options: colors.slice(0, 2 + Math.floor(Math.random() * 2)),
            color_images: colors.map(() => img),
            editions
          }
        });
      });
    });
  });

  return list;
}

async function seed(productsToSeed, hasDiscount) {
  const BATCH_SIZE = 50;
  let total = 0;
  
  for (let i = 0; i < productsToSeed.length; i += BATCH_SIZE) {
    const batch = productsToSeed.slice(i, i + BATCH_SIZE).map(prod => {
      if (!hasDiscount) {
        const { discount, original_price, ...rest } = prod;
        return rest;
      }
      return prod;
    });
    
    const { data, error } = await supabase.from('products').insert(batch).select('id');
    
    if (error) {
      console.error(`❌ Lỗi batch ${Math.floor(i/BATCH_SIZE)+1}:`, error.message);
      for (const prod of batch) {
        const insertData = hasDiscount ? prod : (() => { const { discount, original_price, ...r } = prod; return r; })();
        const { error: e2 } = await supabase.from('products').insert(insertData);
        if (e2) {
          console.error(`  ❌ "${prod.name}": ${e2.message}`);
        } else {
          total++;
        }
      }
    } else {
      total += data.length;
      const batchNum = Math.floor(i/BATCH_SIZE)+1;
      const cat = [...new Set(batch.map(p => p.category))].join('/');
      console.log(`✅ Batch ${batchNum}: ${data.length} SP [${cat}] (tổng: ${total}/${productsToSeed.length})`);
    }
  }
  return total;
}

async function main() {
  console.log('🚀 BẮT ĐẦU SEED DATABASE VỚI EDITIONS GOM NHÓM (1000+)\n');
  
  console.log('🔍 Kiểm tra schema database...');
  const hasDiscount = await detectSchema();
  const hasTv = await detectTvConstraint();
  console.log(`  - Cột discount/original_price: ${hasDiscount ? '✅ Có' : '❌ Chưa có'}`);
  console.log(`  - Hỗ trợ category TV: ${hasTv ? '✅ Có' : '❌ Chưa có'}\n`);
  
  if (!hasDiscount) {
    console.log('⚠️ CẢNH BÁO: Cột discount/original_price chưa tồn tại!');
    console.log('   Sẽ seed KHÔNG bao gồm discount/original_price.');
    console.log('   👉 Hãy chạy alter_v2.sql trong Supabase SQL Editor trước, rồi chạy lại script này.\n');
  }
  
  if (!hasTv) {
    console.log('⚠️ CẢNH BÁO: Constraint products_category_check chưa cho phép category "tv"!');
    console.log('   Sẽ BỎ QUA tất cả sản phẩm TV.');
    console.log('   👉 Hãy chạy alter_v2.sql trong Supabase SQL Editor trước, rồi chạy lại script này.\n');
  }
  
  const allProducts = generateAllProducts();
  const productsToSeed = hasTv 
    ? allProducts 
    : allProducts.filter(p => p.category !== 'tv');
  
  const categoryCounts = productsToSeed.reduce((acc, p) => {
    acc[p.category] = (acc[p.category] || 0) + 1; return acc;
  }, {});
  console.log(`📊 Phân bổ: ${JSON.stringify(categoryCounts)}`);
  console.log(`📦 Tổng sản phẩm sẽ seed: ${productsToSeed.length}\n`);
  
  await clearProducts();
  
  const inserted = await seed(productsToSeed, hasDiscount);
  
  const { count } = await supabase.from('products').select('*', { count: 'exact', head: true });
  
  console.log('\n🎉 SEED HOÀN TẤT!');
  console.log(`✅ Đã insert: ${inserted} sản phẩm`);
  console.log(`📊 Số lượng trong DB: ${count} sản phẩm`);
  
  if (!hasDiscount) {
    console.log('\n📋 BƯỚC TIẾP THEO:');
    console.log('1. Mở Supabase Dashboard → SQL Editor');
    console.log('2. Chạy file alter_v2.sql');
    console.log('3. Chạy lại: node scripts/run-seed.mjs');
    console.log('4. Lần này sẽ có đầy đủ discount, original_price và category TV!');
  }
}

main().catch(console.error);
