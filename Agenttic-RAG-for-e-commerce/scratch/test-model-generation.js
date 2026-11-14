// scratch/test-model-generation.js
// Thử nghiệm thuật toán sinh 1000+ model sản phẩm e-commerce độc nhất
// Tích hợp gộp các Edition (Chính hãng, Nhập khẩu, Likenew 99%, Cũ 95%, Trôi bảo hành) làm mảng JSON editions

const EDITIONS_TEMPLATE = [
  { name: 'Chính hãng (VN/A)', condition: 'Mới 100%', priceFactor: 1.0 },
  { name: 'Nhập khẩu', condition: 'Mới 100% (Nhập khẩu)', priceFactor: 0.95 },
  { name: 'Cũ 99% (Likenew)', condition: 'Đã qua sử dụng (Đẹp 99%)', priceFactor: 0.85 },
  { name: 'Cũ 95%', condition: 'Đã qua sử dụng (Xước nhẹ 95%)', priceFactor: 0.75 },
  { name: 'Trôi bảo hành', condition: 'Mới trôi bảo hành', priceFactor: 0.9 }
];

const PHONE_COLORS = ['Titan Tự Nhiên', 'Titan Đen', 'Titan Trắng', 'Xanh Dương', 'Đen Huyền Bí', 'Trắng Ngọc Trai', 'Xám Tinh Tế', 'Hồng cánh sen'];
const LAPTOP_COLORS = ['Xám Không Gian (Space Gray)', 'Bạc Ánh Kim (Silver)', 'Vàng Đồng (Starlight)', 'Đen Nhám (Matte Black)'];
const WATCH_STRAPS = ['Dây Cao Su Thể Thao', 'Dây Da Bò Cao Cấp', 'Dây Vải Dệt Trail Loop', 'Dây Kim Loại Thép Không Gỉ', 'Dây Silicone Mềm'];

// Ánh xạ ảnh cụ thể cho từng dòng máy để không bị placeholder
function getProductImage(category, brand, family, modelName) {
  const normName = modelName.toLowerCase();
  
  if (category === 'phone') {
    if (brand === 'Apple') {
      if (normName.includes('15')) return 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600';
      if (normName.includes('14')) return 'https://images.unsplash.com/photo-1678685888221-cda773a3dcdb?w=600';
      if (normName.includes('13')) return 'https://images.unsplash.com/photo-1632661676897-6df02930415a?w=600';
      if (normName.includes('12')) return 'https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600';
      if (normName.includes('11')) return 'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=600';
      return 'https://images.unsplash.com/photo-1565538810844-1e119d81a202?w=600'; // iPhone SE/X/XS
    }
    if (brand === 'Samsung') {
      if (normName.includes('ultra')) return 'https://images.unsplash.com/photo-1610945415295-d9b21034d1ac?w=600';
      if (normName.includes('s24') || normName.includes('s23')) return 'https://images.unsplash.com/photo-1678911820864-b2c75188e605?w=600';
      return 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600';
    }
    if (brand === 'Xiaomi') return 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600';
    if (brand === 'Google') return 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600';
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
    return 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600';
  }
  
  if (category === 'tv') {
    if (brand === 'Samsung') return 'https://images.unsplash.com/photo-1593784991095-a205069470b6?w=600';
    if (brand === 'LG') return 'https://images.unsplash.com/photo-1558888401-3cc1de77652d?w=600';
    return 'https://images.unsplash.com/photo-1593359677879-a4bb92f4e10a?w=600';
  }
  
  if (category === 'earphone') {
    if (brand === 'Apple') {
      if (normName.includes('max')) return 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600';
      return 'https://images.unsplash.com/photo-1588449668338-d134ae7f3639?w=600';
    }
    if (normName.includes('wh-1000')) return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600';
    return 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600';
  }
  
  if (category === 'smartwatch') {
    if (brand === 'Apple') return 'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600';
    if (brand === 'Samsung') return 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600';
    return 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=600';
  }
  
  // accessory
  if (brand === 'Logitech') return 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600';
  return 'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600';
}

function generateModelList() {
  const list = [];

  // 1. GENERATE PHONES (~300+ models)
  // Apple: các đời iPhone X, XR, XS, 11, 12, 13, 14, 15, 16 qua các hậu tố
  const applePhoneFamilies = [
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
    { name: 'iPhone SE Gen 2', price: 5200000 }
  ];
  const applePhoneSuffixes = ['Pro Max', 'Pro', 'Plus', 'thường', 'mini'];

  applePhoneFamilies.forEach(fam => {
    applePhoneSuffixes.forEach(suf => {
      // Loại bỏ các sự kết hợp không hợp lệ ngoài thực tế
      if (fam.name.includes('SE') && suf !== 'thường') return;
      if (fam.name.includes('XS') && ['mini', 'Plus', 'thường'].includes(suf)) return;
      if (fam.name.includes('XR') && suf !== 'thường') return;
      if (fam.name.includes('X') && fam.name === 'iPhone X' && suf !== 'thường') return;
      if (['iPhone 11', 'iPhone XS', 'iPhone XR', 'iPhone X'].includes(fam.name) && suf === 'Plus') return;
      if (['iPhone 14', 'iPhone 15', 'iPhone 16'].includes(fam.name) && suf === 'mini') return;
      if (['iPhone 11', 'iPhone 12', 'iPhone 13'].includes(fam.name) && suf === 'Plus') return;

      const modelName = suf === 'thường' ? fam.name : `${fam.name} ${suf}`;
      const name = `Apple ${modelName}`;

      let startPrice = fam.price;
      if (suf === 'Pro Max') startPrice += 9000000;
      else if (suf === 'Pro') startPrice += 6000000;
      else if (suf === 'Plus') startPrice += 3000000;
      else if (suf === 'mini') startPrice -= 2000000;

      const colors = PHONE_COLORS.slice(0, 3 + Math.floor(Math.random() * 4));
      const img = getProductImage('phone', 'Apple', fam.name, modelName);

      // Tạo các Edition và trong mỗi Edition chứa các variants giá khác nhau
      const editions = EDITIONS_TEMPLATE.map(ed => {
        const edPrice = Math.round(startPrice * ed.priceFactor);
        const variants = ['128GB', '256GB', '512GB', '1TB'].map((storage, idx) => {
          if (storage === '1TB' && !['Pro', 'Pro Max'].includes(suf)) return null;
          if (['iPhone X', 'iPhone XR', 'iPhone XS'].includes(fam.name) && storage === '1TB') return null;
          
          return {
            label: storage,
            price: Math.round((edPrice + idx * 2500000 * ed.priceFactor) / 10000) * 10000
          };
        }).filter(Boolean);

        return {
          name: ed.name,
          condition: ed.condition,
          variants
        };
      });

      // Lấy giá đại diện từ Edition chính hãng cấu hình thấp nhất
      const reprPrice = editions[0].variants[0].price;
      const discount = Math.random() > 0.4 ? Math.floor(5 + Math.random() * 15) : 0;
      const original_price = discount > 0 ? Math.round(reprPrice / (1 - discount/100) / 10000) * 10000 : reprPrice;

      list.push({
        category: 'phone',
        brand: 'Apple',
        name,
        price: reprPrice,
        original_price,
        discount,
        stock: Math.floor(10 + Math.random() * 90),
        rating_avg: parseFloat((4.0 + Math.random() * 1.0).toFixed(1)),
        images: [img],
        description: `Điện thoại di động thông minh ${name} thiết kế tinh xảo, cấu hình cực mạnh mẽ, camera chụp ảnh đỉnh cao và pin dung lượng lớn.`,
        specs: {
          chip: 'Apple A-Series Bionic / Pro',
          screen: 'Super Retina XDR OLED 120Hz mượt mà',
          color_options: colors,
          color_images: colors.map(() => img),
          editions
        }
      });
    });
  });

  // Samsung: các dòng S, Note, A qua các năm và chip
  const samsungPhoneFamilies = [
    { name: 'Galaxy S24', price: 18000000 },
    { name: 'Galaxy S23', price: 15000000 },
    { name: 'Galaxy S22', price: 12000000 },
    { name: 'Galaxy S21', price: 9500000 },
    { name: 'Galaxy S20', price: 7500000 },
    { name: 'Galaxy Note 20', price: 8500000 },
    { name: 'Galaxy Note 10', price: 6200000 },
    { name: 'Galaxy A55', price: 8500000 },
    { name: 'Galaxy A35', price: 6500000 },
    { name: 'Galaxy A15', price: 3800000 }
  ];
  const samsungPhoneSuffixes = ['Ultra', 'Plus', 'thường', 'FE'];

  samsungPhoneFamilies.forEach(fam => {
    samsungPhoneSuffixes.forEach(suf => {
      if (fam.name.includes('A') && suf !== 'thường') return;
      if (fam.name.includes('Note') && suf === 'FE') return;
      if (fam.name.includes('Note 10') && suf === 'Plus' && suf === 'FE') return; // Note 10 chỉ có thường/Plus
      if (fam.name.includes('Note 20') && suf === 'Plus') return; // Note 20 chỉ có thường/Ultra
      if (fam.name.includes('Note') && suf === 'Plus') return;

      const modelName = suf === 'thường' ? fam.name : `${fam.name} ${suf}`;
      const name = `Samsung ${modelName}`;

      let startPrice = fam.price;
      if (suf === 'Ultra') startPrice += 8000000;
      else if (suf === 'Plus') startPrice += 3000000;
      else if (suf === 'FE') startPrice -= 2000000;

      const colors = PHONE_COLORS.slice(0, 3 + Math.floor(Math.random() * 4));
      const img = getProductImage('phone', 'Samsung', fam.name, modelName);

      const editions = EDITIONS_TEMPLATE.map(ed => {
        const edPrice = Math.round(startPrice * ed.priceFactor);
        const variants = ['128GB', '256GB', '512GB', '1TB'].map((storage, idx) => {
          if (storage === '1TB' && suf !== 'Ultra') return null;
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
        brand: 'Samsung',
        name,
        price: reprPrice,
        original_price,
        discount,
        stock: Math.floor(10 + Math.random() * 90),
        rating_avg: parseFloat((4.0 + Math.random() * 1.0).toFixed(1)),
        images: [img],
        description: `Điện thoại di động Samsung ${name} thiết kế hiện đại, cấu hình mạnh mẽ đáp ứng mọi nhu cầu hàng ngày.`,
        specs: {
          chip: 'Snapdragon / Exynos thế hệ mới',
          screen: 'Dynamic AMOLED 2X 120Hz',
          color_options: colors,
          color_images: colors.map(() => img),
          editions
        }
      });
    });
  });

  // Tương tự, ta sinh thêm Xiaomi (~80), Google Pixel (~40)
  
  return list;
}

const list = generateModelList();
console.log('Tổng sản phẩm sinh thử:', list.length);
console.log('Ví dụ sản phẩm 1:', JSON.stringify(list[0], null, 2));
