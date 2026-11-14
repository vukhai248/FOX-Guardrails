// scratch/test-gen-variants.js
// Thử nghiệm Generator sản phẩm e-commerce gom nhóm Variants (1000+ sản phẩm độc nhất)

const IMG = {
  iphone: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600',
  samsung_phone: 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600',
  xiaomi_phone: 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600',
  google_phone: 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600',
  other_phone: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600',
  macbook: 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=600',
  dell_laptop: 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600',
  asus_laptop: 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600',
  lenovo_laptop: 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600',
  hp_laptop: 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=600',
  other_laptop: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600',
  tv_samsung: 'https://images.unsplash.com/photo-1601944179066-29786cb9d32a?w=600',
  tv_lg: 'https://images.unsplash.com/photo-1558888401-3cc1de77652d?w=600',
  tv_sony: 'https://images.unsplash.com/photo-1567690187548-f07b1d7bf5a9?w=600',
  tv_other: 'https://images.unsplash.com/photo-1593359677879-a4bb92f4e10a?w=600',
  airpods: 'https://images.unsplash.com/photo-1588449668338-d134ae7f3639?w=600',
  sony_headphone: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600',
  other_earphone: 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600',
  apple_watch: 'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600',
  samsung_watch: 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600',
  garmin_watch: 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=600',
  other_watch: 'https://images.unsplash.com/photo-1517502884422-41eaead166d4?w=600',
  anker_accessory: 'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600',
  logitech_accessory: 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600',
  other_accessory: 'https://images.unsplash.com/photo-1585776245991-cf89dd7fc73a?w=600'
};

const PHONE_COLORS = ['Titan Tự Nhiên', 'Titan Đen', 'Titan Trắng', 'Xanh Dương', 'Đen Huyền Bí', 'Trắng Ngọc Trai', 'Xám Tinh Tế', 'Hồng cánh sen'];
const LAPTOP_COLORS = ['Xám Không Gian (Space Gray)', 'Bạc Ánh Kim (Silver)', 'Vàng Đồng (Starlight)', 'Đen Nhám (Matte Black)'];
const TV_COLORS = ['Đen Huyền Bí'];
const WATCH_STRAPS = ['Dây Cao Su Thể Thao', 'Dây Da Bò Cao Cấp', 'Dây Vải Dệt Trail Loop', 'Dây Kim Loại Thép Không Gỉ', 'Dây Silicone Mềm'];

const EDITIONS = [
  { suffix: 'Chính hãng', priceFactor: 1.0, condition: 'Mới 100%' },
  { suffix: 'Nhập khẩu', priceFactor: 0.95, condition: 'Mới 100% (Nhập khẩu)' },
  { suffix: 'Likenew 99%', priceFactor: 0.85, condition: 'Đã qua sử dụng (Đẹp 99%)' },
  { suffix: 'Cũ đẹp 95%', priceFactor: 0.75, condition: 'Đã qua sử dụng (Xước nhẹ 95%)' },
  { suffix: 'Trôi bảo hành', priceFactor: 0.9, condition: 'Mới trôi bảo hành' }
];

function generateAllProducts() {
  const list = [];

  // 1. GENERATE PHONES (~200+ models)
  const phoneBrands = [
    { brand: 'Apple', families: ['iPhone 15', 'iPhone 14', 'iPhone 13', 'iPhone 12', 'iPhone SE'], suffixes: ['Pro Max', 'Pro', 'Plus', 'thường'], img: IMG.iphone },
    { brand: 'Samsung', families: ['Galaxy S24', 'Galaxy S23', 'Galaxy S22', 'Galaxy A55', 'Galaxy A35', 'Galaxy A15'], suffixes: ['Ultra', 'Plus', 'thường', 'FE'], img: IMG.samsung_phone },
    { brand: 'Xiaomi', families: ['Xiaomi 14', 'Xiaomi 13', 'Redmi Note 13', 'Redmi Note 12', 'Poco X6'], suffixes: ['Ultra', 'Pro', 'thường'], img: IMG.xiaomi_phone },
    { brand: 'Google', families: ['Pixel 8', 'Pixel 7'], suffixes: ['Pro', 'thường'], img: IMG.google_phone }
  ];

  phoneBrands.forEach(b => {
    b.families.forEach(fam => {
      let validSuffixes = b.suffixes;
      if (fam.includes('SE') || fam.includes('A') || fam.includes('M')) validSuffixes = ['thường'];
      
      validSuffixes.forEach(suf => {
        const modelName = suf === 'thường' ? fam : `${fam} ${suf}`;
        
        // Nhân bản theo các loại Edition khác nhau
        EDITIONS.forEach(ed => {
          const edSuffix = (b.brand === 'Apple' && ed.suffix === 'Chính hãng') ? 'Chính hãng (VN/A)' : ed.suffix;
          const name = `${b.brand} ${modelName} (${edSuffix})`;
          
          const colors = PHONE_COLORS.slice(0, 3 + Math.floor(Math.random() * 4));
          const variants = [];
          const baseStorageOpts = ['128GB', '256GB', '512GB', '1TB'];
          
          let startPrice = 8000000;
          if (modelName.includes('Ultra') || modelName.includes('Pro Max')) startPrice = 26000000;
          else if (modelName.includes('Pro')) startPrice = 20000000;
          else if (modelName.includes('Plus')) startPrice = 16000000;
          else if (fam.includes('A5') || fam.includes('Reno')) startPrice = 9000000;

          startPrice = Math.round(startPrice * ed.priceFactor);

          baseStorageOpts.forEach((storage, idx) => {
            if (storage === '1TB' && !['Apple', 'Samsung'].includes(b.brand)) return;
            if (storage === '1TB' && !modelName.includes('Pro') && !modelName.includes('Ultra')) return;
            
            const price = Math.round((startPrice + idx * 2000000 * ed.priceFactor) / 10000) * 10000;
            variants.push({
              label: storage,
              price
            });
          });

          const reprPrice = variants[0].price;
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
            images: [b.img],
            description: `Điện thoại di động thông minh ${name} tình trạng ${ed.condition}. Thiết kế tinh xảo, cấu hình cực mạnh mẽ, camera chụp ảnh đỉnh cao và pin dung lượng lớn.`,
            specs: {
              condition: ed.condition,
              chip: b.brand === 'Apple' ? 'Apple A-Series Bionic / Pro' : 'Snapdragon / Dimensity',
              screen: 'Super AMOLED / LTPO OLED 120Hz mượt mà',
              color_options: colors,
              color_images: colors.map(() => b.img),
              variants: variants
            }
          });
        });
      });
    });
  });

  // 2. GENERATE LAPTOPS (~300+ models)
  const laptopBrands = [
    { brand: 'Apple', families: ['MacBook Air M3', 'MacBook Pro M3 Pro', 'MacBook Pro M3 Max'], sizes: ['13 inch', '14 inch', '15 inch', '16 inch'], img: IMG.macbook },
    { brand: 'Dell', families: ['Dell XPS 13', 'Dell XPS 15', 'Dell Inspiron 15'], sizes: ['13.4"', '15.6"'], img: IMG.dell_laptop },
    { brand: 'Asus', families: ['Asus ROG Zephyrus', 'Asus ZenBook 14', 'Asus VivoBook 15'], sizes: ['14"', '15.6"'], img: IMG.asus_laptop },
    { brand: 'Lenovo', families: ['ThinkPad X1 Carbon', 'IdeaPad Slim 5', 'Legion 5 Pro'], sizes: ['14"', '16"'], img: IMG.lenovo_laptop },
    { brand: 'HP', families: ['HP Spectre x360', 'HP Pavilion 15', 'HP Victus 16'], sizes: ['14"', '15.6"'], img: IMG.hp_laptop }
  ];

  laptopBrands.forEach(b => {
    b.families.forEach(fam => {
      b.sizes.forEach(size => {
        if (b.brand === 'Apple') {
          if (fam.includes('Air') && ['14 inch', '16 inch'].includes(size)) return;
          if (fam.includes('Pro') && ['13 inch', '15 inch'].includes(size)) return;
        }

        const laptopEditions = EDITIONS.slice(0, 3);
        
        laptopEditions.forEach(ed => {
          const edSuffix = (b.brand === 'Apple' && ed.suffix === 'Chính hãng') ? 'Chính hãng (VN/A)' : ed.suffix;
          const name = `${fam} ${size} (${edSuffix})`;
          
          const colors = LAPTOP_COLORS.slice(0, 2 + Math.floor(Math.random() * 3));
          const variants = [];
          const configOpts = [
            { ram: '8GB', ssd: '256GB', priceOffset: 0 },
            { ram: '16GB', ssd: '512GB', priceOffset: 3500000 },
            { ram: '16GB', ssd: '1TB', priceOffset: 6500000 }
          ];

          let basePrice = 14000000;
          if (fam.includes('Spectre') || fam.includes('Carbon') || fam.includes('XPS') || fam.includes('Max')) {
            basePrice = 38000000;
          } else if (fam.includes('ZenBook') || fam.includes('Pro') || fam.includes('Zephyrus') || fam.includes('Legion')) {
            basePrice = 27000000;
          } else if (fam.includes('Inspiron') || fam.includes('Pavilion') || fam.includes('Victus')) {
            basePrice = 17000000;
          }

          basePrice = Math.round(basePrice * ed.priceFactor);

          const finalConfigs = (fam.includes('Max') || fam.includes('Carbon') || fam.includes('XPS')) 
            ? configOpts.filter(c => c.ram !== '8GB')
            : configOpts;

          finalConfigs.forEach(c => {
            variants.push({
              label: `${c.ram} RAM / ${c.ssd} SSD`,
              price: Math.round((basePrice + c.priceOffset * ed.priceFactor) / 10000) * 10000
            });
          });

          const reprPrice = variants[0].price;
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
            images: [b.img],
            description: `Máy tính xách tay cao cấp ${name} tình trạng ${ed.condition}. Kết hợp hoàn hảo giữa thiết kế mỏng nhẹ tinh xảo và hiệu năng hoạt động vượt trội.`,
            specs: {
              condition: ed.condition,
              screen: `${size} hiển thị sắc nét chuẩn màu sắc`,
              color_options: colors,
              color_images: colors.map(() => b.img),
              variants: variants
            }
          });
        });
      });
    });
  });

  // 3. GENERATE TV (~200+ models)
  const tvBrands = [
    { brand: 'Samsung', families: ['Samsung Neo QLED 8K', 'Samsung Neo QLED 4K', 'Samsung QLED 4K', 'Samsung Crystal UHD', 'Samsung The Frame'], img: IMG.tv_samsung },
    { brand: 'LG', families: ['LG OLED evo C4', 'LG OLED Gallery G4', 'LG QNED 4K', 'LG NanoCell 4K', 'LG UHD Smart TV'], img: IMG.tv_lg },
    { brand: 'Sony', families: ['Sony Bravia XR QD-OLED', 'Sony Bravia Mini LED X95L', 'Sony Bravia LED X80L', 'Sony Bravia Google TV'], img: IMG.tv_sony },
    { brand: 'Xiaomi', families: ['Xiaomi TV S Pro QLED', 'Xiaomi TV A2 HDR', 'Xiaomi TV A Pro Bezelless'], img: IMG.tv_other },
    { brand: 'TCL', families: ['TCL QD-Mini LED C855', 'TCL QLED C745', 'TCL UHD Google TV P635'], img: IMG.tv_other }
  ];

  const sizes = ['43 inch', '50 inch', '55 inch', '65 inch', '75 inch', '85 inch'];

  tvBrands.forEach(b => {
    b.families.forEach(fam => {
      const tvEditions = [EDITIONS[0], EDITIONS[1]];
      
      tvEditions.forEach(ed => {
        const name = `${fam} (${ed.suffix})`;
        const variants = [];

        let basePrice = 6000000;
        if (fam.includes('8K') || fam.includes('Gallery') || fam.includes('QD-OLED')) basePrice = 40000000;
        else if (fam.includes('Mini LED') || fam.includes('OLED evo')) basePrice = 24000000;
        else if (fam.includes('QLED') || fam.includes('QNED') || fam.includes('The Frame')) basePrice = 14000000;

        basePrice = Math.round(basePrice * ed.priceFactor);

        sizes.forEach(size => {
          const sizeFactor = size === '43 inch' ? 1.0 : size === '50 inch' ? 1.25 : size === '55 inch' ? 1.5 : size === '65 inch' ? 2.1 : size === '75 inch' ? 3.2 : 4.8;
          variants.push({
            label: size,
            price: Math.round(basePrice * sizeFactor / 100000) * 100000
          });
        });

        const reprPrice = variants[0].price;
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
          images: [b.img],
          description: `Smart Tivi ${name} phân phối ${ed.suffix} chính thức. Mang đến độ tương phản hoàn hảo và màu sắc sống động chân thực cho trải nghiệm giải trí đỉnh cao.`,
          specs: {
            condition: ed.condition,
            resolution: fam.includes('8K') ? '8K Ultra HD (7680x4320)' : '4K Ultra HD (3840x2160)',
            color_options: TV_COLORS,
            color_images: [b.img],
            variants: variants
          }
        });
      });
    });
  });

  // 4. GENERATE EARPHONES (~150+ models)
  const earphoneBrands = [
    { brand: 'Apple', families: ['AirPods Pro', 'AirPods Max', 'AirPods Gen 4', 'AirPods Gen 3'], img: IMG.airpods },
    { brand: 'Sony', families: ['Sony WF-1000XM5', 'Sony WH-1000XM5', 'Sony LinkBuds S', 'Sony WH-CH720N', 'Sony WH-CH520'], img: IMG.sony_headphone },
    { brand: 'JBL', families: ['JBL Tour Pro 3', 'JBL Tune Beam 2', 'JBL Live 670NC', 'JBL Wave Beam'], img: IMG.other_earphone },
    { brand: 'Bose', families: ['Bose QuietComfort Ultra', 'Bose QuietComfort 45', 'Bose QuietComfort Earbuds'], img: IMG.sony_headphone },
    { brand: 'Sennheiser', families: ['Sennheiser Momentum 4', 'Sennheiser Momentum TW 4', 'Sennheiser Accentum'], img: IMG.sony_headphone }
  ];

  const colors = ['Đen Huyền Bí', 'Trắng Ngọc Trai', 'Xanh Navy', 'Bạc Sang Trọng', 'Hồng Nhẹ Nhàng'];

  earphoneBrands.forEach(b => {
    b.families.forEach(fam => {
      const earEditions = [EDITIONS[0], EDITIONS[2]];
      
      earEditions.forEach(ed => {
        const name = `${fam} (${ed.suffix})`;
        
        let basePrice = 1200000;
        if (fam.includes('Max') || fam.includes('Momentum 4') || fam.includes('Ultra')) basePrice = 7500000;
        else if (fam.includes('1000XM5') || fam.includes('QC 45')) basePrice = 5500000;
        else if (fam.includes('Pro') || fam.includes('Tour')) basePrice = 4000000;

        basePrice = Math.round(basePrice * ed.priceFactor);

        const variants = [
          { label: 'Bản Tiêu Chuẩn', price: basePrice },
          { label: 'Bản Có Hộp Sạc Không Dây', price: Math.round((basePrice + 800000 * ed.priceFactor) / 10000) * 10000 }
        ];

        const reprPrice = variants[0].price;
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
          images: [b.img],
          description: `Tai nghe cao cấp ${name} chất âm đẳng cấp, tình trạng ${ed.condition}. Tích hợp công nghệ ANC chống ồn chủ động đỉnh cao và đàm thoại cực rõ nét.`,
          specs: {
            condition: ed.condition,
            anc: 'Chống ồn chủ động ANC thông minh thích ứng',
            color_options: colors.slice(0, 2 + Math.floor(Math.random() * 3)),
            color_images: colors.map(() => b.img),
            variants: variants
          }
        });
      });
    });
  });

  // 5. GENERATE SMARTWATCH (~150+ models)
  const watchBrands = [
    { brand: 'Apple', families: ['Apple Watch Ultra 2', 'Apple Watch Series 9 GPS', 'Apple Watch Series 8', 'Apple Watch SE Gen 2'], img: IMG.apple_watch },
    { brand: 'Samsung', families: ['Galaxy Watch Ultra LTE', 'Galaxy Watch7 LTE', 'Galaxy Watch6 Classic', 'Galaxy Watch6 LTE'], img: IMG.samsung_watch },
    { brand: 'Garmin', families: ['Garmin Fenix 7X Pro Solar', 'Garmin Forerunner 965', 'Garmin Venu 3S', 'Garmin Instinct 2X'], img: IMG.garmin_watch },
    { brand: 'Huawei', families: ['Huawei Watch GT 4', 'Huawei Watch GT 3 Pro', 'Huawei Watch Fit 3'], img: IMG.other_watch }
  ];

  watchBrands.forEach(b => {
    b.families.forEach(fam => {
      const watchEditions = [EDITIONS[0], EDITIONS[2]];
      
      watchEditions.forEach(ed => {
        const name = `${fam} (${ed.suffix})`;

        let basePrice = 3500000;
        if (fam.includes('Ultra') || fam.includes('Fenix')) basePrice = 18000000;
        else if (fam.includes('965') || fam.includes('Series 9')) basePrice = 11000000;
        else if (fam.includes('Watch7') || fam.includes('Classic') || fam.includes('Venu')) basePrice = 7000000;

        basePrice = Math.round(basePrice * ed.priceFactor);

        const finalVariants = [
          { label: 'Mặt 41mm / 42mm', price: basePrice },
          { label: 'Mặt 45mm / 47mm', price: Math.round((basePrice + 1200000 * ed.priceFactor) / 10000) * 10000 }
        ];
        if (fam.includes('Ultra') || fam.includes('Fenix')) {
          finalVariants.length = 0;
          finalVariants.push({ label: 'Mặt Titan 49mm / 51mm', price: basePrice });
        }

        const reprPrice = finalVariants[0].price;
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
          images: [b.img],
          description: `Đồng hồ thông minh ${name} giúp bạn rèn luyện thể thao chuyên nghiệp và quản lý cuộc sống thông minh hằng ngày. Tình trạng ${ed.condition}.`,
          specs: {
            condition: ed.condition,
            waterproof: 'IP68 / 5ATM chống nước bơi lội an toàn',
            color_options: WATCH_STRAPS.slice(0, 3 + Math.floor(Math.random() * 3)),
            color_images: WATCH_STRAPS.map(() => b.img),
            variants: finalVariants
          }
        });
      });
    });
  });

  // 6. GENERATE ACCESSORY (~250+ models)
  const accBrands = [
    { brand: 'Anker', families: ['Cáp Sạc Anker Prime GaN 100W', 'Củ Sạc Anker 737 GaN 120W', 'Sạc Nhanh Anker Nano 30W', 'Sạc Dự Phòng Anker 10000mAh', 'Sạc Dự Phòng Anker 20000mAh 65W', 'Cáp Anker PowerLine USB-C'], img: IMG.anker_accessory },
    { brand: 'Logitech', families: ['Chuột Logitech MX Master 3S', 'Bàn Phím Logitech MX Keys S', 'Chuột Không Dây MX Anywhere 3S', 'Chuột Gaming G Pro X Superlight 2', 'Logitech StreamCam Full HD', 'Webcam Logitech MX Brio 4K'], img: IMG.logitech_accessory },
    { brand: 'Apple', families: ['Sạc Apple MagSafe 15W', 'Củ Sạc Apple 20W USB-C', 'Bút Cảm Ứng Apple Pencil Pro'], img: IMG.other_accessory },
    { brand: 'Spigen', families: ['Ốp Lưng Spigen Tough Armor', 'Ốp Lưng Spigen Ultra Hybrid Clear', 'Kính Cường Lực Spigen GLAS.tR'], img: IMG.other_accessory },
    { brand: 'Ugreen', families: ['Cáp Ugreen 240W Nylon', 'Bộ Chuyển Đổi Ugreen Hub 7-in-1', 'Giá Đỡ Laptop Ugreen Nhôm'], img: IMG.other_accessory },
    { brand: 'Baseus', families: ['Đèn Treo Màn Hình Baseus', 'Sạc Dự Phòng Baseus 30W'], img: IMG.other_accessory }
  ];

  accBrands.forEach(b => {
    b.families.forEach(fam => {
      const accEditions = [EDITIONS[0], EDITIONS[1]];
      
      accEditions.forEach(ed => {
        const colors = ['Màu Đen Nhám', 'Màu Trắng Sữa', 'Màu Xám Không Gian', 'Màu Xanh Mint'];
        const name = `${fam} (${ed.suffix})`;

        let basePrice = 250000;
        if (fam.includes('Brio') || fam.includes('MX Keys') || fam.includes('Superlight') || fam.includes('MX Master')) basePrice = 2300000;
        else if (fam.includes('StreamCam') || fam.includes('GaN 100W') || fam.includes('20000mAh') || fam.includes('Pencil')) basePrice = 1200000;
        else if (fam.includes('MagSafe') || fam.includes('Hub 7-in-1')) basePrice = 650000;

        basePrice = Math.round(basePrice * ed.priceFactor);

        const variants = [
          { label: 'Bản Tiêu Chuẩn', price: basePrice },
          { label: 'Bản Premium Pack', price: Math.round((basePrice + 350000 * ed.priceFactor) / 10000) * 10000 }
        ];

        const reprPrice = variants[0].price;
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
          images: [b.img],
          description: `Phụ kiện ${name} tình trạng ${ed.condition}. Mang đến sự tiện dụng tối đa và độ bền bỉ cao cho quá trình sử dụng thiết bị hằng ngày của bạn.`,
          specs: {
            condition: ed.condition,
            color_options: colors.slice(0, 2 + Math.floor(Math.random() * 2)),
            color_images: colors.map(() => b.img),
            variants: variants
          }
        });
      });
    });
  });

  return list;
}

const result = generateAllProducts();
console.log('Tổng sản phẩm mô hình (variants đã gom):', result.length);
const countMap = {};
result.forEach(p => {
  countMap[p.category] = (countMap[p.category] || 0) + 1;
});
console.log('Phân bổ danh mục:', countMap);
