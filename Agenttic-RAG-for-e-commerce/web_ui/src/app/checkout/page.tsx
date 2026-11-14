'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useCart } from '@/store/useCart';
import { supabase } from '@/lib/supabase';
import { CreditCard, Truck, ChevronLeft, Loader2, AlertCircle, ChevronDown, Check } from 'lucide-react';
import Link from 'next/link';

interface CustomSelectProps {
  label: string;
  placeholder: string;
  value: string;
  options: string[];
  onChange: (val: string) => void;
  disabled?: boolean;
}

function CustomSelect({ label, placeholder, value, options, onChange, disabled }: CustomSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="space-y-1.5 flex-1 relative select-none" ref={dropdownRef}>
      <label className="text-xs font-semibold text-muted-foreground">{label}</label>
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full h-11 px-4 rounded-xl border text-sm flex items-center justify-between cursor-pointer transition-all ${
          isOpen
            ? 'border-primary bg-background text-foreground'
            : 'border-border bg-background text-foreground hover:border-muted-foreground/35'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
      >
        <span className={value ? 'text-foreground' : 'text-muted-foreground/60'}>
          {value || placeholder}
        </span>
        <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && !disabled && (
        <div className="absolute top-[calc(100%+4px)] left-0 w-full bg-card border border-border rounded-xl shadow-2xl p-1.5 z-50 animate-in fade-in slide-in-from-top-1 duration-150">
          <div className="max-h-44 overflow-y-auto pr-1 custom-scroll space-y-0.5">
            <div
              onClick={() => {
                onChange('');
                setIsOpen(false);
              }}
              className={`px-3 py-2 rounded-lg text-xs cursor-pointer transition-colors ${
                !value ? 'bg-primary/10 text-primary font-bold' : 'hover:bg-muted/60 text-muted-foreground hover:text-foreground'
              }`}
            >
              {placeholder}
            </div>
            {options.map((opt) => (
              <div
                key={opt}
                onClick={() => {
                  onChange(opt);
                  setIsOpen(false);
                }}
                className={`px-3 py-2 rounded-lg text-xs cursor-pointer transition-colors ${
                  value === opt ? 'bg-primary/10 text-primary font-bold' : 'hover:bg-muted/60 text-muted-foreground hover:text-foreground'
                }`}
              >
                {opt}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function CheckoutPage() {
  const router = useRouter();
  const { items, getTotalPrice, clearCart } = useCart();

  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [province, setProvince] = useState('');
  const [district, setDistrict] = useState('');
  const [ward, setWard] = useState('');
  const [detailAddress, setDetailAddress] = useState('');
  const [note, setNote] = useState('');
  const [saveAddress, setSaveAddress] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<'stripe' | 'cod'>('stripe');
  
  const [availableDistricts, setAvailableDistricts] = useState<string[]>([]);
  const [availableWards, setAvailableWards] = useState<string[]>([]);
  const [addressData, setAddressData] = useState<any[]>([]);
  
  const [user, setUser] = useState<any>(null);
  const [isLoadingUser, setIsLoadingUser] = useState(true);
  const [isCartHydrated, setIsCartHydrated] = useState(false);
  const [isOrderSubmitted, setIsOrderSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Tải dữ liệu địa chính từ file JSON tĩnh và phục hồi thông tin đã lưu
  useEffect(() => {
    const loadAddressData = async () => {
      try {
        const res = await fetch('/data/vietnam-addresses.json');
        if (!res.ok) throw new Error('Không thể tải file JSON địa chính');
        const data = await res.json();
        setAddressData(data);

        // Phục hồi địa chỉ đã lưu sau khi dữ liệu địa chính đã sẵn sàng
        const savedFullName = localStorage.getItem('saved_full_name');
        const savedPhone = localStorage.getItem('saved_phone');
        const savedProvince = localStorage.getItem('saved_province');
        const savedDistrict = localStorage.getItem('saved_district');
        const savedWard = localStorage.getItem('saved_ward');
        const savedDetail = localStorage.getItem('saved_detail_address');
        const savedSave = localStorage.getItem('saved_address_checkbox') === 'true';

        if (savedFullName) setFullName(savedFullName);
        if (savedPhone) setPhone(savedPhone);
        if (savedSave) setSaveAddress(savedSave);

        if (savedProvince) {
          setProvince(savedProvince);
          const foundProvince = data.find((p: any) => p.name === savedProvince);
          if (foundProvince) {
            setAvailableDistricts(foundProvince.districts.map((d: any) => d.name));
            if (savedDistrict) {
              setDistrict(savedDistrict);
              const foundDistrict = foundProvince.districts.find((d: any) => d.name === savedDistrict);
              if (foundDistrict) {
                setAvailableWards(foundDistrict.wards);
                if (savedWard) setWard(savedWard);
              }
            }
          }
        }
        if (savedDetail) setDetailAddress(savedDetail);
      } catch (err) {
        console.error('Lỗi khi tải dữ liệu địa chính Việt Nam:', err);
      }
    };

    loadAddressData();
  }, []);

  // Cập nhật khi chọn Tỉnh/Thành
  const handleProvinceChange = (val: string) => {
    setProvince(val);
    setDistrict('');
    setWard('');
    setAvailableWards([]);
    if (val) {
      const foundProvince = addressData.find(p => p.name === val);
      setAvailableDistricts(foundProvince ? foundProvince.districts.map((d: any) => d.name) : []);
    } else {
      setAvailableDistricts([]);
    }
  };

  // Cập nhật khi chọn Quận/Huyện
  const handleDistrictChange = (val: string) => {
    setDistrict(val);
    setWard('');
    if (province && val) {
      const foundProvince = addressData.find(p => p.name === province);
      const foundDistrict = foundProvince?.districts.find((d: any) => d.name === val);
      setAvailableWards(foundDistrict ? foundDistrict.wards : []);
    } else {
      setAvailableWards([]);
    }
  };

  useEffect(() => {
    const checkUser = async () => {
      setIsLoadingUser(true);
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.user) {
          setUser(session.user);
          setFullName(session.user.user_metadata?.full_name || '');
          setPhone(session.user.user_metadata?.phone || '');
        }
      } catch (err) {
        console.error('Lỗi kiểm tra auth:', err);
      } finally {
        setIsLoadingUser(false);
      }
    };

    checkUser();
  }, []);

  useEffect(() => {
    setIsCartHydrated(true);
  }, []);

  // Nếu giỏ hàng đã hydrate xong mà vẫn trống (và không phải đang đặt hàng) thì mới quay lại trang giỏ
  useEffect(() => {
    if (isCartHydrated && !isOrderSubmitted && items.length === 0) {
      router.push('/cart');
    }
  }, [isCartHydrated, isOrderSubmitted, items.length, router]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price);
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !phone.trim() || !province || !district || !ward || !detailAddress.trim()) {
      setErrorMsg('Vui lòng chọn đầy đủ Tỉnh/Quận/Phường và điền Số nhà, tên đường!');
      return;
    }

    // Kiểm tra định dạng số điện thoại Việt Nam cơ bản
    const phoneRegex = /^(0|84)[3|5|7|8|9][0-9]{8}$/;
    if (!phoneRegex.test(phone.trim())) {
      setErrorMsg('Số điện thoại không hợp lệ! Vui lòng nhập số điện thoại Việt Nam (ví dụ: 0987654321).');
      return;
    }

    // Chống spam địa chỉ quá ngắn
    if (detailAddress.trim().length < 3) {
      setErrorMsg('Số nhà, tên đường quá ngắn! Vui lòng nhập thông tin chi tiết để giao nhận chính xác.');
      return;
    }

    setErrorMsg('');
    setIsSubmitting(true);

    try {
      const addressLine = district ? `${detailAddress.trim()}, ${district}` : detailAddress.trim();
      const payload = {
        items: items.map((item) => ({
          product_id: Number(item.id),
          quantity: item.quantity,
        })),
        payment_method: paymentMethod, // 'stripe' | 'cod'
        recipient_name: fullName.trim(),
        recipient_phone: phone.trim(),
        address_line: addressLine,
        ward: ward.trim(),
        province: province.trim(),
        note: note.trim() || undefined,
      };

      // Xử lý lưu địa chỉ nếu check lưu
      if (saveAddress) {
        localStorage.setItem('saved_full_name', fullName.trim());
        localStorage.setItem('saved_phone', phone.trim());
        localStorage.setItem('saved_province', province);
        localStorage.setItem('saved_district', district);
        localStorage.setItem('saved_ward', ward);
        localStorage.setItem('saved_detail_address', detailAddress.trim());
        localStorage.setItem('saved_address_checkbox', 'true');
      } else {
        localStorage.removeItem('saved_full_name');
        localStorage.removeItem('saved_phone');
        localStorage.removeItem('saved_province');
        localStorage.removeItem('saved_district');
        localStorage.removeItem('saved_ward');
        localStorage.removeItem('saved_detail_address');
        localStorage.setItem('saved_address_checkbox', 'false');
      }

      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;

      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error?.message || data.message || 'Lỗi khi tạo đơn hàng');
      }

      // Đánh dấu đã submit đơn thành công để tránh effect redirect về /cart khi giỏ trống
      setIsOrderSubmitted(true);
      clearCart();

      if (paymentMethod === 'stripe' && data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        // Chuyển hướng an toàn, URL tuyệt đối không chứa PII (tên, SĐT, địa chỉ)
        router.push(`/checkout-success?order_id=${data.order_id}`);
      }
    } catch (err: any) {
      console.error('Lỗi thanh toán:', err);
      setErrorMsg(err.message || 'Có lỗi xảy ra trong quá trình xử lý thanh toán.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isCartHydrated) {
    return (
      <div className="container mx-auto px-4 py-16 flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
          <span className="text-sm text-muted-foreground">Đang tải thông tin thanh toán...</span>
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-8 flex-1 space-y-8 transition-colors duration-200">
      {/* Quay lại */}
      <div>
        <Link href="/cart" className="inline-flex items-center gap-1.5 text-xs sm:text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ChevronLeft className="w-4 h-4" />
          <span>Quay lại giỏ hàng</span>
        </Link>
      </div>

      <h1 className="text-2xl sm:text-3xl font-extrabold text-foreground border-b border-border pb-6">Thanh toán đơn hàng</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cột trái + giữa: Form nhập thông tin */}
        <form onSubmit={handleCheckout} className="lg:col-span-2 space-y-6">
          {errorMsg && (
            <div className="p-4 rounded-xl border border-destructive/20 bg-destructive/5 text-destructive text-xs sm:text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {isLoadingUser ? (
            <div className="h-10 w-full animate-pulse bg-card rounded-xl" />
          ) : !user ? (
            <div className="p-4 rounded-xl border border-primary/20 bg-primary/5 text-primary text-xs sm:text-sm flex items-center justify-between gap-4">
              <span>Đăng nhập giúp lưu đơn hàng vào tài khoản của bạn để tra cứu sau này.</span>
              <Link href="/auth/login" className="px-4 py-1.5 bg-primary hover:opacity-90 text-primary-foreground text-xs font-bold rounded-lg whitespace-nowrap transition-all">
                Đăng nhập ngay
              </Link>
            </div>
          ) : null}

          {/* Form Thông tin */}
          <div className="rounded-2xl border border-border bg-card/10 p-6 space-y-4">
            <h2 className="text-lg font-bold text-foreground mb-2">1. Thông tin giao nhận hàng</h2>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Họ và tên người nhận</label>
                <input
                  type="text"
                  required
                  placeholder="Nguyễn Văn A"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full h-11 px-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Số điện thoại liên hệ</label>
                <input
                  type="tel"
                  required
                  placeholder="09xxxxxxxx"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full h-11 px-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <CustomSelect
                label="Tỉnh / Thành phố"
                placeholder="Chọn tỉnh/thành phố"
                value={province}
                options={addressData.map((p) => p.name)}
                onChange={handleProvinceChange}
              />
              
              <CustomSelect
                label="Quận / Huyện"
                placeholder="Chọn quận/huyện"
                value={district}
                options={availableDistricts}
                onChange={handleDistrictChange}
                disabled={!province}
              />
              
              <CustomSelect
                label="Phường / Xã"
                placeholder="Chọn phường/xã"
                value={ward}
                options={availableWards}
                onChange={(val) => setWard(val)}
                disabled={!district}
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">
                Số nhà, tên đường (Vui lòng chọn quận/huyện và phường/xã trước) <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                required
                disabled={!ward}
                placeholder="Ví dụ: Số 123, ngõ 45, phố Trần Thái Tông"
                value={detailAddress}
                onChange={(e) => setDetailAddress(e.target.value)}
                className="w-full h-11 px-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>

            {/* Checkbox lưu địa chỉ */}
            <div className="flex items-center gap-2.5 pt-1.5 select-none">
              <button
                type="button"
                id="saveAddress"
                onClick={() => setSaveAddress(!saveAddress)}
                className="flex items-center justify-center cursor-pointer"
              >
                <div className={`w-4.5 h-4.5 rounded-md border flex items-center justify-center transition-all ${
                  saveAddress
                    ? 'bg-primary border-primary text-white shadow-sm shadow-primary/20 scale-105'
                    : 'border-border bg-background hover:border-muted-foreground/50'
                }`}>
                  {saveAddress && (
                    <Check className="w-3 h-3 stroke-[3.5]" />
                  )}
                </div>
              </button>
              <label 
                htmlFor="saveAddress" 
                onClick={() => setSaveAddress(!saveAddress)} 
                className="text-xs text-muted-foreground cursor-pointer select-none"
              >
                Lưu địa chỉ cho lần mua kế tiếp
              </label>
            </div>

            {/* Ghi chú khác nếu có */}
            <div className="space-y-1.5 pt-2 border-t border-border/40">
              <label className="text-xs font-semibold text-muted-foreground">Ghi chú khác (nếu có)</label>
              <input
                type="text"
                placeholder="Ví dụ: Giao hàng giờ hành chính, gọi điện trước khi giao..."
                value={note}
                onChange={(e) => setNote(e.target.value)}
                className="w-full h-11 px-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          {/* Phương thức thanh toán */}
          <div className="rounded-2xl border border-border bg-card/10 p-6 space-y-4">
            <h2 className="text-lg font-bold text-foreground mb-2">2. Phương thức thanh toán</h2>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setPaymentMethod('stripe')}
                className={`p-4 rounded-xl border flex items-center justify-between text-left transition-all ${
                  paymentMethod === 'stripe'
                    ? 'border-primary bg-primary/5 text-foreground'
                    : 'border-border bg-background/40 text-muted-foreground hover:border-muted-foreground/40'
                }`}
              >
                <div className="flex items-center gap-3">
                  <CreditCard className="w-5 h-5 text-primary" />
                  <div>
                    <span className="font-bold text-sm block">Thẻ tín dụng / Stripe</span>
                    <span className="text-[10px] text-muted-foreground">Chấp nhận Visa, Master, JCB (Test)</span>
                  </div>
                </div>
                <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${paymentMethod === 'stripe' ? 'border-primary' : 'border-border'}`}>
                  {paymentMethod === 'stripe' && <div className="w-2 h-2 rounded-full bg-primary" />}
                </div>
              </button>

              <button
                type="button"
                onClick={() => setPaymentMethod('cod')}
                className={`p-4 rounded-xl border flex items-center justify-between text-left transition-all ${
                  paymentMethod === 'cod'
                    ? 'border-primary bg-primary/5 text-foreground'
                    : 'border-border bg-background/40 text-muted-foreground hover:border-muted-foreground/40'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Truck className="w-5 h-5 text-success" />
                  <div>
                    <span className="font-bold text-sm block">Thu tiền khi nhận hàng (COD)</span>
                    <span className="text-[10px] text-muted-foreground">Kiểm tra đồng kiểm và thanh toán mặt</span>
                  </div>
                </div>
                <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${paymentMethod === 'cod' ? 'border-primary' : 'border-border'}`}>
                  {paymentMethod === 'cod' && <div className="w-2 h-2 rounded-full bg-primary" />}
                </div>
              </button>
            </div>
          </div>
        </form>

        {/* Cột phải: Xem lại giỏ hàng */}
        <div>
          <div className="rounded-2xl border border-border bg-card/45 p-6 space-y-4 sticky top-24">
            <h2 className="text-lg font-bold text-foreground border-b border-border pb-3">Giỏ hàng của bạn</h2>
            
            {/* Danh sách items tóm tắt */}
            <div className="max-h-56 overflow-y-auto space-y-3 pr-2 scrollbar-thin">
              {items.map((item) => (
                <div key={item.id} className="flex gap-3 text-xs sm:text-sm">
                  <div className="w-12 h-12 rounded-lg bg-background border border-border p-1 flex items-center justify-center flex-shrink-0">
                    <img src={item.image} alt={item.name} className="w-full h-full object-contain" />
                  </div>
                  <div className="flex-1 space-y-0.5">
                    <h4 className="font-semibold text-foreground line-clamp-1">{item.name}</h4>
                    <div className="flex justify-between text-muted-foreground text-xs">
                      <span>SL: {item.quantity}</span>
                      <span className="text-primary font-bold">{formatPrice(item.price * item.quantity)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="border-t border-border pt-4 space-y-2 text-xs sm:text-sm text-muted-foreground">
              <div className="flex justify-between">
                <span>Tạm tính:</span>
                <span className="text-foreground font-semibold">{formatPrice(getTotalPrice())}</span>
              </div>
              <div className="flex justify-between">
                <span>Vận chuyển:</span>
                <span className="text-success font-semibold">Miễn phí giao hàng</span>
              </div>
            </div>

            <div className="border-t border-border pt-4 flex justify-between items-center">
              <span className="font-semibold text-foreground text-sm">Tổng thanh toán:</span>
              <span className="text-xl font-black text-primary">{formatPrice(getTotalPrice())}</span>
            </div>

            <button
              onClick={handleCheckout}
              disabled={isSubmitting}
              className="flex items-center justify-center gap-2 w-full h-12 rounded-xl bg-primary hover:opacity-90 disabled:bg-muted disabled:text-muted-foreground text-primary-foreground font-bold hover:shadow-lg hover:shadow-primary/20 active:scale-95 disabled:scale-100 disabled:opacity-50 transition-all text-sm mt-4 cursor-pointer"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Đang xử lý đơn hàng...</span>
                </>
              ) : (
                <>
                  <span>Xác nhận đặt hàng</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
