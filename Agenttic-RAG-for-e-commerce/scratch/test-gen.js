// scratch/test-gen.js
// Script test generator sản phẩm điện tử để nạp 1200+ sản phẩm

const IMG = {
  iphone: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600',
  samsung_phone: 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600',
  xiaomi_phone: 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600',
  google_phone: 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600',
  other_phone: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600',
  macbook: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600',
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

function generateAllProducts() {
  const list = [];
  
  // 1. GENERATE PHONES (~200)
  const phoneBrands = [
    { brand: 'Apple', models: ['iPhone 15 Pro Max', 'iPhone 15 Pro', 'iPhone 15 Plus', 'iPhone 15', 'iPhone 14 Pro Max', 'iPhone 14 Pro', 'iPhone 13', 'iPhone 12', 'iPhone SE Gen 3'], img: IMG.iphone },
    { brand: 'Samsung', models: ['Galaxy S24 Ultra', 'Galaxy S24+', 'Galaxy S24', 'Galaxy Z Fold6', 'Galaxy Z Flip6', 'Galaxy S23 Ultra', 'Galaxy A55', 'Galaxy A35', 'Galaxy A15'], img: IMG.samsung_phone },
    { brand: 'Xiaomi', models: ['Xiaomi 14 Ultra', 'Xiaomi 14', 'Xiaomi 13T Pro', 'Redmi Note 13 Pro', 'Redmi Note 13', 'Poco X6 Pro'], img: IMG.xiaomi_phone },
    { brand: 'Google', models: ['Pixel 8 Pro', 'Pixel 8', 'Pixel 7a'], img: IMG.google_phone },
    { brand: 'Oppo', models: ['Find X7 Ultra', 'Reno11 Pro', 'A98'], img: IMG.other_phone },
    { brand: 'OnePlus', models: ['OnePlus 12', 'Nord CE 4'], img: IMG.other_phone },
    { brand: 'Vivo', models: ['X100 Pro', 'V30 Pro'], img: IMG.other_phone },
    { brand: 'Realme', models: ['GT 6', '12 Pro+', 'C65'], img: IMG.other_phone }
  ];
  
  const storages = ['128GB', '256GB', '512GB', '1TB'];
  const colors = ['Titan Tự Nhiên', 'Titan Đen', 'Titan Trắng', 'Xanh Đại Dương', 'Đen Huyền Bí', 'Trắng Ngọc Trai', 'Xám Tinh Tế', 'Hồng Pastel'];
  
  phoneBrands.forEach(b => {
    b.models.forEach(model => {
      storages.forEach(storage => {
        // Chỉ Apple/Samsung mới hay có bản 1TB
        if (storage === '1TB' && !['Apple', 'Samsung'].includes(b.brand)) return;
        
        // Random 2 màu cho mỗi cấu hình
        for (let k = 0; k < 2; k++) {
          const color = colors[Math.floor(Math.random() * colors.length)];
          const name = `${b.brand} ${model} ${storage} ${color}`;
          
          // Tính giá dựa trên model
          let basePrice = 12000000;
          if (model.includes('Ultra') || model.includes('Pro Max') || model.includes('Fold')) {
            basePrice = 28000000;
          } else if (model.includes('Pro') || model.includes('Flip')) {
            basePrice = 22000000;
          } else if (model.includes('Plus') || model.includes('+')) {
            basePrice = 18000000;
          } else if (model.includes('Note') || model.includes('Reno') || model.includes('A55') || model.includes('Nord')) {
            basePrice = 8000000;
          } else if (model.includes('A15') || model.includes('C65') || model.includes('13C')) {
            basePrice = 3500000;
          }
          
          // Thêm biến đổi theo dung lượng
          if (storage === '256GB') basePrice += 2000000;
          if (storage === '512GB') basePrice += 5000000;
          if (storage === '1TB') basePrice += 10000000;
          
          // Random chút giá lẻ
          basePrice += Math.floor(Math.random() * 9) * 100000;
          
          const discount = Math.random() > 0.3 ? Math.floor(5 + Math.random() * 20) : 0;
          const price = basePrice;
          const original_price = discount > 0 ? Math.round(price / (1 - discount/100) / 10000) * 10000 : price;
          
          list.push({
            category: 'phone',
            brand: b.brand,
            name,
            price,
            original_price,
            discount,
            stock: Math.floor(5 + Math.random() * 45),
            rating_avg: parseFloat((4.0 + Math.random() * 1.0).toFixed(1)),
            images: [b.img],
            description: `Điện thoại di động ${name} sở hữu thiết kế thời thượng, màn hình sắc nét và cấu hình mạnh mẽ đáp ứng mọi nhu cầu làm việc và giải trí đỉnh cao.`,
            specs: {
              chip: b.brand === 'Apple' ? 'Apple A-Series' : 'Snapdragon / Dimensity',
              ram: storage === '128GB' ? '8GB' : '12GB',
              storage,
              screen: 'Màn hình OLED sắc nét, 120Hz mượt mà',
              battery: '4500mAh - 5000mAh, sạc nhanh tiện lợi',
              os: b.brand === 'Apple' ? 'iOS' : 'Android'
            }
          });
        }
      });
    });
  });

  // 2. GENERATE LAPTOPS (~200)
  const laptopBrands = [
    { brand: 'Apple', models: ['MacBook Air M3 13"', 'MacBook Air M3 15"', 'MacBook Pro M3 14"', 'MacBook Pro M3 16"'], img: IMG.macbook },
    { brand: 'Dell', models: ['XPS 13 9320', 'XPS 15 9530', 'Inspiron 15', 'Latitude 5440'], img: IMG.dell_laptop },
    { brand: 'Asus', models: ['ROG Zephyrus G14', 'ROG Strix G16', 'ZenBook 14 OLED', 'VivoBook 15'], img: IMG.asus_laptop },
    { brand: 'Lenovo', models: ['ThinkPad X1 Carbon', 'ThinkPad T14', 'IdeaPad Slim 5', 'Legion 5 Pro'], img: IMG.lenovo_laptop },
    { brand: 'HP', models: ['Spectre x360', 'Envy 16', 'Pavilion 15', 'Victus 16'], img: IMG.hp_laptop },
    { brand: 'MSI', models: ['Titan GT77', 'Katana 15', 'Modern 14'], img: IMG.other_laptop },
    { brand: 'Razer', models: ['Blade 14', 'Blade 16'], img: IMG.other_laptop },
    { brand: 'LG', models: ['Gram 14', 'Gram 17'], img: IMG.other_laptop }
  ];

  const rams = ['8GB', '16GB', '32GB'];
  const ssds = ['256GB', '512GB', '1TB'];

  laptopBrands.forEach(b => {
    b.models.forEach(model => {
      rams.forEach(ram => {
        ssds.forEach(ssd => {
          // MacBook Pro thường ko có bản 8GB/256GB, Razer ko có bản 8GB
          if (ram === '8GB' && (model.includes('Pro') || b.brand === 'Razer' || model.includes('Titan'))) return;

          const name = `${b.brand} ${model} (${ram} RAM, ${ssd} SSD)`;
          
          let basePrice = 18000000;
          if (model.includes('Titan') || model.includes('Blade') || model.includes('Pro 16')) {
            basePrice = 55000000;
          } else if (model.includes('XPS') || model.includes('Spectre') || model.includes('Carbon') || model.includes('Gram')) {
            basePrice = 35000000;
          } else if (model.includes('ZenBook') || model.includes('ROG') || model.includes('Legion') || model.includes('Pro 14')) {
            basePrice = 28000000;
          } else if (model.includes('Inspiron') || model.includes('Pavilion') || model.includes('Victus') || model.includes('Katana')) {
            basePrice = 17000000;
          } else if (model.includes('Slim') || model.includes('Modern') || model.includes('Modern')) {
            basePrice = 12000000;
          }

          if (ram === '16GB') basePrice += 2500000;
          if (ram === '32GB') basePrice += 6000000;
          if (ssd === '512GB') basePrice += 150000;
          if (ssd === '1TB') basePrice += 4000000;

          basePrice += Math.floor(Math.random() * 9) * 100000;

          const discount = Math.random() > 0.4 ? Math.floor(5 + Math.random() * 15) : 0;
          const price = basePrice;
          const original_price = discount > 0 ? Math.round(price / (1 - discount/100) / 10000) * 10000 : price;

          list.push({
            category: 'laptop',
            brand: b.brand,
            name,
            price,
            original_price,
            discount,
            stock: Math.floor(3 + Math.random() * 20),
            rating_avg: parseFloat((4.2 + Math.random() * 0.8).toFixed(1)),
            images: [b.img],
            description: `Máy tính xách tay ${name} mang đến hiệu năng xử lý công việc và đồ họa mạnh mẽ trong thiết kế sang trọng bền bỉ.`,
            specs: {
              cpu: b.brand === 'Apple' ? 'Apple M3 Series' : 'Intel Core i7 / AMD Ryzen 7',
              ram,
              storage: ssd,
              screen: model.includes('OLED') || model.includes('XPS') ? 'Màn hình OLED sắc nét' : 'Màn hình IPS chuẩn màu',
              gpu: model.includes('ROG') || model.includes('Legion') || model.includes('Blade') ? 'NVIDIA GeForce RTX' : 'Intel Iris Xe / AMD Radeon',
              weight: model.includes('Gram') || model.includes('Air') ? 'Dưới 1.3kg siêu nhẹ' : '1.5kg - 2.3kg'
            }
          });
        });
      });
    });
  });

  // 3. GENERATE TV (~200)
  const tvBrands = [
    { brand: 'Samsung', models: ['Neo QLED 8K', 'Neo QLED 4K', 'QLED 4K', 'Crystal UHD', 'The Frame', 'UHD 4K Slim'], img: IMG.tv_samsung },
    { brand: 'LG', models: ['OLED evo C4', 'OLED G4 Gallery', 'QNED 4K', 'NanoCell 4K', 'UHD 4K Smart', 'UHD 4K ThinQ'], img: IMG.tv_lg },
    { brand: 'Sony', models: ['Bravia XR QD-OLED', 'Bravia Mini LED', 'Bravia LED 4K', 'Bravia X85L'], img: IMG.tv_sony },
    { brand: 'Xiaomi', models: ['TV S Pro QLED', 'TV A2 4K', 'TV A Pro', 'TV Redmi X'], img: IMG.tv_other },
    { brand: 'TCL', models: ['QD-Mini LED C855', 'QLED C745', 'UHD P635', 'Google TV P745'], img: IMG.tv_other }
  ];

  const tvSizes = ['43 inch', '50 inch', '55 inch', '65 inch', '75 inch', '85 inch'];

  tvBrands.forEach(b => {
    b.models.forEach(model => {
      tvSizes.forEach(size => {
        const name = `${b.brand} ${model} ${size} Smart TV`;
        
        let basePrice = 7000000;
        if (model.includes('8K') || model.includes('G4 Gallery') || model.includes('QD-OLED')) {
          basePrice = 45000000;
        } else if (model.includes('Mini LED') || model.includes('OLED evo')) {
          basePrice = 28000000;
        } else if (model.includes('QLED') || model.includes('QNED') || model.includes('The Frame')) {
          basePrice = 16000000;
        } else if (model.includes('NanoCell') || model.includes('Crystal')) {
          basePrice = 11000000;
        }

        const sizeFactor = size === '43 inch' ? 1.0 : size === '50 inch' ? 1.2 : size === '55 inch' ? 1.4 : size === '65 inch' ? 2.0 : size === '75 inch' ? 3.0 : 4.5;
        basePrice = Math.round(basePrice * sizeFactor);
        basePrice += Math.floor(Math.random() * 9) * 100000;

        const discount = Math.random() > 0.3 ? Math.floor(8 + Math.random() * 20) : 0;
        const price = basePrice;
        const original_price = discount > 0 ? Math.round(price / (1 - discount/100) / 10000) * 10000 : price;

        list.push({
          category: 'tv',
          brand: b.brand,
          name,
          price,
          original_price,
          discount,
          stock: Math.floor(2 + Math.random() * 15),
          rating_avg: parseFloat((4.1 + Math.random() * 0.9).toFixed(1)),
          images: [b.img],
          description: `Smart Tivi ${name} mang đến trải nghiệm điện ảnh rực rỡ với âm thanh Dolby Atmos sống động ngay tại phòng khách nhà bạn.`,
          specs: {
            screen_size: size,
            resolution: model.includes('8K') ? '8K Ultra HD (7680x4320)' : '4K Ultra HD (3840x2160)',
            panel: model.includes('OLED') ? 'OLED / QD-OLED tự phát sáng' : model.includes('QLED') ? 'QLED Quantum Dot' : 'LED / Mini LED',
            refresh_rate: model.includes('OLED') || model.includes('Mini LED') ? '120Hz / 144Hz' : '60Hz',
            os: b.brand === 'Samsung' ? 'Tizen OS' : b.brand === 'LG' ? 'webOS' : 'Google TV (Android TV)'
          }
        });
      });
    });
  });

  // 4. GENERATE EARPHONES (~200)
  const earphoneBrands = [
    { brand: 'Apple', models: ['AirPods Pro Gen 2', 'AirPods Max', 'AirPods Gen 4 ANC', 'AirPods Gen 4'], img: IMG.airpods },
    { brand: 'Sony', models: ['WF-1000XM5 Earbuds', 'WH-1000XM5 Headphone', 'LinkBuds S', 'WH-CH720N'], img: IMG.sony_headphone },
    { brand: 'JBL', models: ['Tour Pro 3 TWS', 'Tune Beam 2', 'Live 670NC'], img: IMG.other_earphone },
    { brand: 'Bose', models: ['QuietComfort Ultra Earbuds', 'QuietComfort 45', 'SoundSport Free'], img: IMG.sony_headphone },
    { brand: 'Sennheiser', models: ['Momentum 4 Wireless', 'Momentum True Wireless 4'], img: IMG.sony_headphone },
    { brand: 'Marshall', models: ['Motif II ANC', 'Major IV Black', 'Minor IV'], img: IMG.other_earphone },
    { brand: 'Beats', models: ['Studio Pro Wireless', 'Beats Fit Pro', 'Studio Buds+'], img: IMG.sony_headphone },
    { brand: 'Anker', models: ['Soundcore Liberty 4 NC', 'Soundcore Space Q45'], img: IMG.other_earphone }
  ];

  const earphoneColors = ['Đen sang trọng', 'Trắng tinh khôi', 'Xám Titanium', 'Xanh Navy', 'Hồng nhạt', 'Vàng Sand', 'Xanh Rêu'];

  earphoneBrands.forEach(b => {
    b.models.forEach(model => {
      // Mỗi model sinh ra các phiên bản màu khác nhau
      earphoneColors.forEach(color => {
        const name = `${b.brand} ${model} (${color})`;
        
        let basePrice = 1500000;
        if (model.includes('Max') || model.includes('Momentum 4') || model.includes('Studio Pro')) {
          basePrice = 8000000;
        } else if (model.includes('1000XM5') || model.includes('Ultra Earbuds') || model.includes('QC')) {
          basePrice = 5800000;
        } else if (model.includes('Pro Gen 2') || model.includes('Tour Pro') || model.includes('Motif')) {
          basePrice = 450000;
        } else if (model.includes('Gen 4') || model.includes('LinkBuds') || model.includes('Major')) {
          basePrice = 3000000;
        }

        basePrice += Math.floor(Math.random() * 5) * 100000;

        const discount = Math.random() > 0.4 ? Math.floor(5 + Math.random() * 25) : 0;
        const price = basePrice;
        const original_price = discount > 0 ? Math.round(price / (1 - discount/100) / 10000) * 10000 : price;

        list.push({
          category: 'earphone',
          brand: b.brand,
          name,
          price,
          original_price,
          discount,
          stock: Math.floor(10 + Math.random() * 50),
          rating_avg: parseFloat((4.3 + Math.random() * 0.7).toFixed(1)),
          images: [b.img],
          description: `Tai nghe ${name} sở hữu chất âm trung thực, âm bass mạnh mẽ và công nghệ chống ồn chủ động ANC hiện đại.`,
          specs: {
            connection: 'Bluetooth 5.3 kết nối ổn định',
            anc: model.includes('ANC') || model.includes('Pro') || model.includes('Ultra') || model.includes('1000X') ? 'Có chống ồn chủ động ANC' : 'Không có ANC',
            battery_life: model.includes('Headphone') || model.includes('Major') || model.includes('Momentum 4') ? 'Lên đến 30 - 60 giờ' : '5 - 8 giờ (kèm kén sạc 30 giờ)',
            waterproof: 'IPX4 kháng nước nhẹ'
          }
        });
      });
    });
  });

  // 5. GENERATE SMARTWATCH (~150)
  const watchBrands = [
    { brand: 'Apple', models: ['Watch Ultra 2 Titanium 49mm', 'Watch Series 9 GPS 45mm', 'Watch Series 9 41mm', 'Watch SE Gen 2 44mm'], img: IMG.apple_watch },
    { brand: 'Samsung', models: ['Galaxy Watch Ultra LTE 47mm', 'Galaxy Watch7 LTE 44mm', 'Galaxy Watch6 Classic 47mm'], img: IMG.samsung_watch },
    { brand: 'Garmin', models: ['Fenix 7X Pro Solar', 'Forerunner 965 Music', 'Venu 3S Ivory', 'Instinct 2X Solar'], img: IMG.garmin_watch },
    { brand: 'Huawei', models: ['Watch GT 4 46mm', 'Watch GT 4 41mm'], img: IMG.other_watch },
    { brand: 'Xiaomi', models: ['Watch S3 Black', 'Redmi Watch 4'], img: IMG.other_watch },
    { brand: 'Amazfit', models: ['Balance Sunset', 'GTS 4 Autumn'], img: IMG.other_watch }
  ];

  const watchStraps = ['Dây Cao Su Thể Thao', 'Dây Da Bò Cao Cấp', 'Dây Vải Dệt Trail Loop', 'Dây Kim Loại Thép Không Gỉ', 'Dây Silicone Mềm', 'Dây Vải Alpine Loop', 'Dây Da Hybrid'];

  watchBrands.forEach(b => {
    b.models.forEach(model => {
      // Mỗi model sinh 7 loại dây đeo khác nhau
      watchStraps.forEach(strap => {
        const name = `${b.brand} ${model} (${strap})`;
        
        let basePrice = 3000000;
        if (model.includes('Ultra') || model.includes('Fenix')) {
          basePrice = 18000000;
        } else if (model.includes('965') || model.includes('Series 9')) {
          basePrice = 10000000;
        } else if (model.includes('Watch7') || model.includes('Classic') || model.includes('Venu')) {
          basePrice = 7500000;
        } else if (model.includes('GT 4') || model.includes('SE') || model.includes('Instinct')) {
          basePrice = 4500000;
        }

        if (strap.includes('Da') || strap.includes('Thép')) basePrice += 1000000;
        basePrice += Math.floor(Math.random() * 5) * 100000;

        const discount = Math.random() > 0.4 ? Math.floor(5 + Math.random() * 20) : 0;
        const price = basePrice;
        const original_price = discount > 0 ? Math.round(price / (1 - discount/100) / 10000) * 10000 : price;

        list.push({
          category: 'smartwatch',
          brand: b.brand,
          name,
          price,
          original_price,
          discount,
          stock: Math.floor(5 + Math.random() * 30),
          rating_avg: parseFloat((4.1 + Math.random() * 0.9).toFixed(1)),
          images: [b.img],
          description: `Đồng hồ thông minh ${name} giúp bạn theo dõi sức khỏe, nhịp tim, giấc ngủ và định vị GPS chính xác trên mọi cung đường tập luyện.`,
          specs: {
            display: 'Màn hình AMOLED sắc nét Always-on',
            battery: model.includes('Solar') || model.includes('GT 4') ? 'Lên đến 14 - 30 ngày' : '1.5 - 3 ngày tiện lợi',
            waterproof: model.includes('Ultra') || model.includes('Fenix') ? '10ATM (Chống nước 100m)' : '5ATM (Chống nước 50m)',
            strap_material: strap,
            sensors: 'Đo nhịp tim, SpO2, ECG điện tâm đồ, theo dõi giấc ngủ'
          }
        });
      });
    });
  });

  // 6. GENERATE ACCESSORY (~250)
  const accBrands = [
    { brand: 'Anker', models: ['Prime GaN 100W Charger', '737 GaN 120W Charger', 'Nano 30W USB-C', 'Power Bank 10000mAh 30W', 'Power Bank 20000mAh 65W'], img: IMG.anker_accessory },
    { brand: 'Logitech', models: ['MX Master 3S Mouse', 'MX Keys S Keyboard', 'MX Anywhere 3S Mouse', 'G Pro X Superlight 2 Mouse', 'StreamCam Full HD', 'MX Brio 4K Webcam'], img: IMG.logitech_accessory },
    { brand: 'Apple', models: ['MagSafe Charger 1m', '20W USB-C Power Adapter', 'Pencil Pro Stylus'], img: IMG.other_accessory },
    { brand: 'Spigen', models: ['Tough Armor Phone Case', 'Ultra Hybrid Clear Case', 'GLAS.tR EZ Fit Screen Protector'], img: IMG.other_accessory },
    { brand: 'Ugreen', models: ['240W Nylon USB-C to USB-C Cable', '100W USB-C Hub 7-in-1', 'Laptop Stand Aluminum'], img: IMG.other_accessory },
    { brand: 'Baseus', models: ['Monitor Light Bar i-wok', 'Baseus Power Bank 30W'], img: IMG.other_accessory }
  ];

  accBrands.forEach(b => {
    b.models.forEach(model => {
      // Mỗi mẫu sinh ra 12 sản phẩm với màu sắc, bao bì hoặc tùy chọn chiều dài cáp khác nhau
      for (let k = 1; k <= 12; k++) {
        const optionLabel = k % 2 === 0 ? 'Màu Đen' : 'Màu Trắng/Xám';
        const name = `${b.brand} ${model} (${optionLabel} - Pack ${k})`;
        
        let basePrice = 300000;
        if (model.includes('Brio 4K') || model.includes('Pencil Pro') || model.includes('MX Keys') || model.includes('Superlight 2') || model.includes('MX Master 3S')) {
          basePrice = 2500000;
        } else if (model.includes('StreamCam') || model.includes('Power Bank 20000mAh') || model.includes('GaN 100W')) {
          basePrice = 1300000;
        } else if (model.includes('MagSafe') || model.includes('Hub 7-in-1') || model.includes('Monitor Light')) {
          basePrice = 800000;
        } else if (model.includes('Tough Armor') || model.includes('EZ Fit') || model.includes('Laptop Stand')) {
          basePrice = 450000;
        }

        basePrice += Math.floor(Math.random() * 3) * 50000;

        const discount = Math.random() > 0.4 ? Math.floor(5 + Math.random() * 30) : 0;
        const price = basePrice;
        const original_price = discount > 0 ? Math.round(price / (1 - discount/100) / 10000) * 10000 : price;

        list.push({
          category: 'accessory',
          brand: b.brand,
          name,
          price,
          original_price,
          discount,
          stock: Math.floor(20 + Math.random() * 80),
          rating_avg: parseFloat((4.2 + Math.random() * 0.8).toFixed(1)),
          images: [b.img],
          description: `Phụ kiện công nghệ cao cấp ${name} mang đến sự tiện nghi, độ bền bỉ cao và tương thích tối đa với các thiết bị thông minh của bạn.`,
          specs: {
            type: model.includes('Charger') || model.includes('Adapter') ? 'Bộ sạc nhanh công suất lớn' : model.includes('Mouse') || model.includes('Keyboard') ? 'Thiết bị ngoại vi cao cấp' : 'Phụ kiện bảo vệ & kết nối',
            brand_owner: b.brand,
            compatibility: 'Hỗ trợ đa nền tảng tốt',
            box_contents: 'Thân sản phẩm, Sách hướng dẫn sử dụng, Thẻ bảo hành chính hãng'
          }
        });
      }
    });
  });

  return list;
}

// Chạy test thử số lượng
const result = generateAllProducts();
console.log('Tổng sản phẩm sinh ra:', result.length);
const countMap = {};
result.forEach(p => {
  countMap[p.category] = (countMap[p.category] || 0) + 1;
});
console.log('Phân bổ danh mục:', countMap);
