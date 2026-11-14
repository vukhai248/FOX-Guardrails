'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { supabase, isSupabaseConfigured } from '@/lib/supabase';
import { 
  Laptop, Smartphone, Watch, Headphones, Layers, ArrowRight, Star, ShoppingCart, 
  Sparkles, Tablet, Cpu, Tv, RefreshCw, BadgeAlert, Award, ChevronRight, CheckCircle2 
} from 'lucide-react';
import { useCart } from '@/store/useCart';
import HeroCarousel from '@/components/hero-carousel';

// Dữ liệu fallback tĩnh giống hệt seed data trong setup.sql để website hoạt động khi chưa có DB
const FALLBACK_PRODUCTS = [
  {
    id: 'prod-air-m3',
    category: 'laptop',
    brand: 'Apple',
    name: 'MacBook Air M3 13 inch',
    price: 27990000,
    stock: 15,
    description: 'MacBook Air M3 phiên bản 2024 siêu mỏng nhẹ, hiệu năng cực đỉnh nhờ chip Apple M3 thế hệ mới.',
    images: ['https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600'],
    rating_avg: 4.8
  },
  {
    id: 'prod-iphone15-pm',
    category: 'phone',
    brand: 'Apple',
    name: 'iPhone 15 Pro Max 256GB',
    price: 29990000,
    stock: 25,
    description: 'Siêu phẩm iPhone 15 Pro Max với khung viền Titanium siêu nhẹ và bền bỉ. Camera zoom quang học 5x cực đại.',
    images: ['https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=600'],
    rating_avg: 4.8
  },
  {
    id: 'prod-s24-ultra',
    category: 'phone',
    brand: 'Samsung',
    name: 'Samsung Galaxy S24 Ultra 256GB',
    price: 26990000,
    stock: 20,
    description: 'Galaxy S24 Ultra tích hợp trí tuệ nhân tạo Galaxy AI vượt trội và bút S Pen đi kèm tiện dụng.',
    images: ['https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600'],
    rating_avg: 4.7
  },
  {
    id: 'prod-watch-ultra2',
    category: 'smartwatch',
    brand: 'Apple',
    name: 'Apple Watch Ultra 2 Titanium',
    price: 21490000,
    stock: 10,
    description: 'Đồng hồ thể thao chuyên nghiệp bền bỉ nhất của Apple với vỏ Titanium hàng không và mặt kính Sapphire.',
    images: ['https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600'],
    rating_avg: 4.8
  },
  {
    id: 'prod-airpods-pro2',
    category: 'earphone',
    brand: 'Apple',
    name: 'Apple AirPods Pro Gen 2 USB-C',
    price: 5690000,
    stock: 30,
    description: 'Tai nghe True Wireless tốt nhất dành cho người dùng hệ sinh thái Apple. Khả năng chống ồn chủ động ANC đỉnh cao.',
    images: ['https://images.unsplash.com/photo-1588449668338-d134ae7f3639?w=600'],
    rating_avg: 4.8
  },
  {
    id: 'prod-wf-1000xm5',
    category: 'earphone',
    brand: 'Sony',
    name: 'Sony WF-1000XM5',
    price: 5990000,
    stock: 15,
    description: 'Đỉnh cao chống ồn chủ động của thế giới tai nghe In-ear. Hỗ trợ giải mã âm thanh chất lượng cao Hi-Res Audio LDAC.',
    images: ['https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600'],
    rating_avg: 4.7
  },
  {
    id: 'prod-sarc-gan-67w',
    category: 'accessory',
    brand: 'Anker',
    name: 'Sạc Anker Prime GaN 67W 3 Cổng',
    price: 990000,
    stock: 50,
    description: 'Củ sạc siêu nhỏ gọn sử dụng vật liệu GaN thế hệ mới giúp tản nhiệt mát mẻ và tối ưu công suất.',
    images: ['https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600'],
    rating_avg: 4.7
  },
  {
    id: 'prod-chuot-mx3s',
    category: 'accessory',
    brand: 'Logitech',
    name: 'Chuột không dây Logitech MX Master 3S',
    price: 2490000,
    stock: 20,
    description: 'Chuột công thái học hàng đầu dành cho lập trình viên và dân văn phòng chuyên nghiệp. Cảm biến 8000 DPI siêu nhạy.',
    images: ['https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600'],
    rating_avg: 4.9
  }
];

interface MegaMenuColumn {
  title: string;
  items: { label: string; href: string; badge?: string }[];
}

interface MegaMenuData {
  [category: string]: {
    columns: MegaMenuColumn[];
  };
}

// Định nghĩa dữ liệu Mega Menu bay ngang cực kỳ phong phú và chi tiết cho từng loại thiết bị
const MEGA_MENU_DATA: MegaMenuData = {
  phone: {
    columns: [
      {
        title: 'Hãng điện thoại & Tablet',
        items: [
          { label: 'iPhone (Apple)', href: '/products?category=phone&brand=Apple' },
          { label: 'iPad (Máy tính bảng)', href: '/products?category=smartwatch&brand=Apple' },
          { label: 'Samsung Galaxy', href: '/products?category=phone&brand=Samsung' },
          { label: 'Xiaomi Redmi', href: '/products?category=phone&brand=Xiaomi' },
          { label: 'Google Pixel', href: '/products?category=phone&brand=Google' },
          { label: 'Oppo', href: '/products?category=phone' }
        ]
      },
      {
        title: 'Chọn theo mức giá',
        items: [
          { label: 'Dưới 5.000.000đ', href: '/products?category=phone&max=5000000' },
          { label: 'Từ 5.000.000đ - 10.000.000đ', href: '/products?category=phone&min=5000000&max=10000000' },
          { label: 'Từ 10.000.000đ - 20.000.000đ', href: '/products?category=phone&min=10000000&max=20000000' },
          { label: 'Trên 20.000.000đ', href: '/products?category=phone&min=20000000' }
        ]
      },
      {
        title: 'Điện thoại HOT 🔥',
        items: [
          { label: 'iPhone 15 Pro Max', href: '/products/prod-iphone15-pm', badge: 'Hot' },
          { label: 'Galaxy S24 Ultra', href: '/products/prod-s24-ultra', badge: 'Hot' },
          { label: 'Xiaomi 14 Ultra', href: '/products/prod-8', badge: 'New' },
          { label: 'Google Pixel 8 Pro', href: '/products/prod-9' }
        ]
      }
    ]
  },
  laptop: {
    columns: [
      {
        title: 'Hãng Laptop',
        items: [
          { label: 'MacBook (Apple)', href: '/products?category=laptop&brand=Apple' },
          { label: 'Dell XPS / Inspiron', href: '/products?category=laptop&brand=Dell' },
          { label: 'Asus ROG / Zenbook', href: '/products?category=laptop&brand=Asus' },
          { label: 'Lenovo ThinkPad', href: '/products?category=laptop&brand=Lenovo' }
        ]
      },
      {
        title: 'Chọn theo mức giá',
        items: [
          { label: 'Dưới 15 triệu', href: '/products?category=laptop&max=15000000' },
          { label: 'Từ 15 - 30 triệu', href: '/products?category=laptop&min=15000000&max=30000000' },
          { label: 'Trên 30 triệu', href: '/products?category=laptop&min=30000000' }
        ]
      },
      {
        title: 'Laptop HOT 🔥',
        items: [
          { label: 'MacBook Air M3 13"', href: '/products/prod-air-m3', badge: 'Bán chạy' },
          { label: 'MacBook Pro M3 Pro', href: '/products/prod-2', badge: 'Pro' },
          { label: 'Dell XPS 13 Plus', href: '/products/prod-3' },
          { label: 'Asus ROG Zephyrus G14', href: '/products/prod-4', badge: 'Gaming' }
        ]
      }
    ]
  },
  smartwatch: {
    columns: [
      {
        title: 'Thương hiệu đồng hồ',
        items: [
          { label: 'Apple Watch Series', href: '/products?category=smartwatch&brand=Apple' },
          { label: 'Garmin Outdoor GPS', href: '/products?category=smartwatch&brand=Garmin' },
          { label: 'Huawei Watch GT', href: '/products?category=smartwatch&brand=Huawei' }
        ]
      },
      {
        title: 'Chọn theo mức giá',
        items: [
          { label: 'Dưới 5 triệu', href: '/products?category=smartwatch&max=5000000' },
          { label: 'Từ 5 - 15 triệu', href: '/products?category=smartwatch&min=5000000&max=15000000' },
          { label: 'Trên 15 triệu', href: '/products?category=smartwatch&min=15000000' }
        ]
      },
      {
        title: 'Đồng hồ HOT 🔥',
        items: [
          { label: 'Apple Watch Ultra 2', href: '/products/prod-watch-ultra2', badge: 'VIP' },
          { label: 'Garmin Fenix 7 Pro', href: '/products/prod-11', badge: 'Solar' },
          { label: 'Huawei Watch GT 4', href: '/products/prod-12' }
        ]
      }
    ]
  },
  earphone: {
    columns: [
      {
        title: 'Thương hiệu tai nghe',
        items: [
          { label: 'AirPods (Apple)', href: '/products?category=earphone&brand=Apple' },
          { label: 'Sony Headphone', href: '/products?category=earphone&brand=Sony' },
          { label: 'Samsung Buds / JBL', href: '/products?category=earphone' }
        ]
      },
      {
        title: 'Chọn theo mức giá',
        items: [
          { label: 'Dưới 2 triệu', href: '/products?category=earphone&max=2000000' },
          { label: 'Từ 2 - 5 triệu', href: '/products?category=earphone&min=2000000&max=5000000' },
          { label: 'Trên 5 triệu', href: '/products?category=earphone&min=5000000' }
        ]
      },
      {
        title: 'Tai nghe HOT 🔥',
        items: [
          { label: 'AirPods Pro Gen 2', href: '/products/prod-airpods-pro2', badge: 'Hot' },
          { label: 'Sony WH-1000XM5 Over-ear', href: '/products/prod-15', badge: 'Best' },
          { label: 'Sony WF-1000XM5', href: '/products/prod-14' }
        ]
      }
    ]
  },
  accessory: {
    columns: [
      {
        title: 'Thương hiệu phụ kiện',
        items: [
          { label: 'Anker GaN Charger', href: '/products?category=accessory&brand=Anker' },
          { label: 'Logitech Mouse/Keyboard', href: '/products?category=accessory&brand=Logitech' },
          { label: 'Apple Accessory', href: '/products?category=accessory' }
        ]
      },
      {
        title: 'Chọn theo mức giá',
        items: [
          { label: 'Dưới 500k', href: '/products?category=accessory&max=500000' },
          { label: 'Từ 500k - 1.5 triệu', href: '/products?category=accessory&min=500000&max=1500000' },
          { label: 'Trên 1.5 triệu', href: '/products?category=accessory&min=1500000' }
        ]
      },
      {
        title: 'Phụ kiện HOT 🔥',
        items: [
          { label: 'Chuột MX Master 3S', href: '/products/prod-chuot-mx3s', badge: 'Hot' },
          { label: 'Sạc Anker Prime 67W', href: '/products/prod-sarc-gan-67w', badge: 'GaN' }
        ]
      }
    ]
  },
  tv: {
    columns: [
      {
        title: 'Thương hiệu Tivi',
        items: [
          { label: 'Samsung Smart TV', href: '/products?category=tv&brand=Samsung' },
          { label: 'Sony Bravia 4K', href: '/products?category=tv&brand=Sony' },
          { label: 'LG OLED Smart TV', href: '/products?category=tv&brand=LG' },
          { label: 'Xiaomi TV', href: '/products?category=tv&brand=Xiaomi' },
          { label: 'TCL Smart TV', href: '/products?category=tv&brand=TCL' }
        ]
      },
      {
        title: 'Chọn theo mức giá',
        items: [
          { label: 'Dưới 15 triệu', href: '/products?category=tv&max=15000000' },
          { label: 'Từ 15 triệu - 40 triệu', href: '/products?category=tv&min=15000000&max=40000000' },
          { label: 'Trên 40 triệu', href: '/products?category=tv&min=40000000' }
        ]
      },
      {
        title: 'Tivi HOT 🔥',
        items: [
          { label: 'LG OLED evo C4 65"', href: '/products', badge: 'OLED' },
          { label: 'Samsung Neo QLED 8K', href: '/products', badge: 'Cao cấp' },
          { label: 'Sony Bravia XR OLED', href: '/products', badge: 'Best' }
        ]
      }
    ]
  }
};

export default function HomePage() {
  const [products, setProducts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hoveredCategory, setHoveredCategory] = useState<string | null>(null);
  const addItem = useCart((state) => state.addItem);

  useEffect(() => {
    const fetchFeaturedProducts = async () => {
      setIsLoading(true);
      if (!isSupabaseConfigured) {
        setProducts(FALLBACK_PRODUCTS);
        setIsLoading(false);
        return;
      }
      try {
        const { data, error } = await supabase
          .from('products')
          .select('*')
          .limit(8);

        if (error) throw error;
        
        const mappedData = (data || []).map((p: any) => {
          const images = p.images && p.images.length > 0 ? p.images : [];
          if (images.length === 0) {
            if (p.image_url) images.push(p.image_url);
            else if (p.thumbnail) images.push(p.thumbnail);
            else images.push('https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600');
          }
          return {
            ...p,
            images,
            rating_avg: p.rating_avg !== undefined ? p.rating_avg : 4.7
          };
        });

        setProducts(mappedData);
      } catch (err) {
        console.warn('Lỗi kết nối CSDL:', err);
        setProducts([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFeaturedProducts();
  }, []);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price);
  };

  const handleAddToCart = (e: React.MouseEvent, prod: any) => {
    e.preventDefault();
    e.stopPropagation();
    addItem({
      id: prod.id,
      name: prod.name,
      price: prod.price,
      image: prod.images[0],
      category: prod.category,
      brand: prod.brand,
    });
    alert(`Đã thêm "${prod.name}" vào giỏ hàng!`);
  };

  const renderProductCard = (prod: any) => (
    <Link
      key={prod.id}
      href={`/products/${prod.id}`}
      className="group rounded-2xl border border-border bg-card/30 hover:bg-card/70 hover:border-primary/45 p-4 flex flex-col justify-between transition-all duration-300 relative overflow-hidden"
    >
      <div className="space-y-4">
        <div className="w-full aspect-square rounded-xl bg-card p-4 flex items-center justify-center overflow-hidden relative border border-border/40">
          <img
            src={prod.images[0]}
            alt={prod.name}
            className="max-h-full max-w-full object-contain transform group-hover:scale-105 transition-transform duration-300"
          />
          {prod.rating_avg && (
            <span className="absolute top-2 right-2 flex items-center gap-1 px-2 py-0.5 rounded-full bg-black/60 backdrop-blur-sm border border-white/10 text-[10px] text-yellow-500 font-bold">
              <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
              <span>{prod.rating_avg}</span>
            </span>
          )}
        </div>
        <div>
          <span className="text-[10px] uppercase font-bold text-primary tracking-wider">{prod.brand}</span>
          <h3 className="font-bold text-foreground text-sm line-clamp-1 group-hover:text-primary transition-colors mt-0.5">
            {prod.name}
          </h3>
          <p className="text-muted-foreground text-xs line-clamp-2 mt-1.5 leading-relaxed">{prod.description}</p>
        </div>
      </div>

      <div className="flex items-center justify-between gap-2 mt-4 border-t border-border/50 pt-3">
        <span className="font-extrabold text-foreground text-sm md:text-base whitespace-nowrap">{formatPrice(prod.price)}</span>
        <button
          onClick={(e) => handleAddToCart(e, prod)}
          className="p-2 rounded-xl bg-primary hover:bg-primary/95 text-primary-foreground shadow-md shadow-primary/10 active:scale-95 transition-all cursor-pointer"
          title="Thêm vào giỏ"
        >
          <ShoppingCart className="w-4 h-4" />
        </button>
      </div>
    </Link>
  );

  // Danh mục menu dọc của trang chủ
  const sidebarItems = [
    { name: 'Điện thoại, Tablet', slug: 'phone', icon: Smartphone },
    { name: 'Laptop cao cấp', slug: 'laptop', icon: Laptop },
    { name: 'Đồng hồ thông minh', slug: 'smartwatch', icon: Watch },
    { name: 'Âm thanh, Tai nghe', slug: 'earphone', icon: Headphones },
    { name: 'Phụ kiện công nghệ', slug: 'accessory', icon: Layers },
    // Các danh mục bổ sung cho phong phú
    { name: 'PC, Màn hình, Máy in', slug: 'pc', icon: Cpu },
    { name: 'Tivi, Điện máy', slug: 'tv', icon: Tv },
    { name: 'Thu cũ đổi mới', slug: 'trade-in', icon: RefreshCw },
    { name: 'Hàng cũ giá rẻ', slug: 'used-items', icon: BadgeAlert },
    { name: 'Khuyến mãi đặc quyền', slug: 'promo', icon: Sparkles }
  ];

  return (
    <div className="flex flex-col gap-16 pb-16 transition-colors duration-200">
      
      {/* 1. HERO AREA: SIDEBAR DANH MỤC DỌC & HERO CAROUSEL */}
      <section className="container mx-auto px-4 mt-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch relative">
          
          {/* MENU DANH MỤC DỌC (Chiếm 3 cột trên Desktop) */}
          <aside 
            onMouseLeave={() => setHoveredCategory(null)}
            className="lg:col-span-3 bg-card border border-border rounded-2xl p-3 flex flex-col justify-between relative z-30 shadow-sm hidden lg:flex"
          >
            <div className="space-y-0.5 relative">
              {sidebarItems.map((item) => {
                const Icon = item.icon;
                const isHovered = hoveredCategory === item.slug;
                
                const targetHref = ['pc', 'trade-in', 'used-items', 'promo'].includes(item.slug)
                  ? '/products'
                  : `/products?category=${item.slug}`;

                return (
                  <Link
                    key={item.slug}
                    href={targetHref}
                    onMouseEnter={() => {
                      if (MEGA_MENU_DATA[item.slug]) {
                        setHoveredCategory(item.slug);
                      } else {
                        setHoveredCategory(null);
                      }
                    }}
                    className={`flex items-center justify-between px-3.5 py-3 rounded-xl cursor-pointer transition-all border border-transparent ${
                      isHovered
                        ? 'bg-primary/10 border-primary/20 text-primary font-bold'
                        : 'text-muted-foreground hover:bg-muted/40 hover:text-foreground'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className={`w-4 h-4 flex-shrink-0 ${isHovered ? 'text-primary' : 'text-muted-foreground'}`} />
                      <span className="text-xs font-semibold">{item.name}</span>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/60" />
                  </Link>
                );
              })}

              {/* MEGA MENU BAY NGANG (Flyout Panel) */}
              {hoveredCategory && MEGA_MENU_DATA[hoveredCategory] && (
                <div 
                  className="absolute top-0 left-full ml-4 w-[760px] min-h-full bg-card/95 backdrop-blur-md border border-border rounded-2xl shadow-2xl p-6 z-40 flex gap-8 animate-in fade-in slide-in-from-left-3 duration-200"
                >
                  {MEGA_MENU_DATA[hoveredCategory].columns.map((col, idx) => (
                    <div key={idx} className="flex-1 flex flex-col gap-4">
                      <h4 className="text-xs font-black uppercase text-foreground tracking-wider pb-2 border-b border-border/80 select-none">
                        {col.title}
                      </h4>
                      <div className="flex flex-col gap-2">
                        {col.items.map((subItem, sIdx) => (
                          <Link
                            key={sIdx}
                            href={subItem.href}
                            onClick={() => setHoveredCategory(null)}
                            className="flex items-center justify-between text-xs font-semibold text-muted-foreground hover:text-primary hover:font-bold transition-all py-1.5 rounded-lg"
                          >
                            <span>{subItem.label}</span>
                            {subItem.badge && (
                              <span className={`text-[8px] font-black uppercase px-1.5 py-0.5 rounded-md ${
                                subItem.badge === 'Hot' || subItem.badge === 'Bán chạy'
                                  ? 'bg-red-500 text-white animate-pulse'
                                  : 'bg-primary text-primary-foreground'
                              }`}>
                                {subItem.badge}
                              </span>
                            )}
                          </Link>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </aside>

          {/* HERO CAROUSEL BANNER (Chiếm 9 cột trên Desktop) */}
          <div className="lg:col-span-9 w-full overflow-hidden rounded-2xl border border-border bg-card shadow-sm flex flex-col justify-center min-h-[350px]">
            <HeroCarousel />
          </div>

        </div>
      </section>

      {/* 2. SẢN PHẨM NỔI BẬT */}
      <section className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-8 border-b border-border/60 pb-3">
          <div>
            <h2 className="text-xl md:text-2xl font-black text-foreground uppercase tracking-wide">
              Sản phẩm bán chạy nhất
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5 font-medium">Các mặt hàng có lượt mua cao và đánh giá xuất sắc</p>
          </div>
          <Link href="/products" className="flex items-center gap-1.5 text-xs font-bold text-primary hover:underline transition-all">
            <span>Xem tất cả</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-80 rounded-2xl bg-card/60 animate-pulse border border-border" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {products.slice(0, 4).map((prod) => renderProductCard(prod))}
          </div>
        )}
      </section>

      {/* 3. SẢN PHẨM MỚI */}
      <section className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-8 border-b border-border/60 pb-3">
          <div>
            <h2 className="text-xl md:text-2xl font-black text-foreground uppercase tracking-wide">
              Thiết bị số mới về
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5 font-medium">Các sản phẩm công nghệ đời mới nhất thị trường</p>
          </div>
          <Link href="/products" className="flex items-center gap-1.5 text-xs font-bold text-primary hover:underline transition-all">
            <span>Xem tất cả</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-80 rounded-2xl bg-card/60 animate-pulse border border-border" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {products.slice(4, 8).map((prod) => renderProductCard(prod))}
          </div>
        )}
      </section>

    </div>
  );
}
