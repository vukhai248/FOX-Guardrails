'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { CheckCircle2, ArrowRight, ShoppingBag, AlertCircle, Clock, MapPin, Phone, User, Package } from 'lucide-react';
import Link from 'next/link';

interface OrderItem {
  id?: number;
  product_id?: number;
  name: string;
  price: number;
  quantity: number;
  image?: string;
}

interface OrderDetail {
  order_id: string;
  status: string;
  payment_status: string;
  payment_method: string;
  total: number;
  items: OrderItem[];
  recipient_name: string;
  recipient_phone: string;
  address_line: string;
  ward: string;
  province: string;
  note?: string;
  created_at?: string;
}

function CheckoutSuccessContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const orderId = searchParams.get('order_id');
  const sessionId = searchParams.get('session_id');

  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    let pollCount = 0;
    const maxPolls = 5;
    let timer: NodeJS.Timeout;

    const fetchOrder = async () => {
      if (!orderId) {
        setIsLoading(false);
        setErrorMsg('Mã đơn hàng không hợp lệ hoặc không tìm thấy.');
        return;
      }

      try {
        const { data: { session } } = await supabase.auth.getSession();
        const token = session?.access_token;

        const res = await fetch(`/api/orders/${orderId}`, {
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
          }
        });

        if (!res.ok) {
          if (res.status === 404) {
            setErrorMsg('Không tìm thấy thông tin đơn hàng hoặc bạn không có quyền xem đơn hàng này.');
          } else {
            setErrorMsg('Lỗi khi tải thông tin đơn hàng từ máy chủ.');
          }
          setIsLoading(false);
          return;
        }

        const data: OrderDetail = await res.json();
        setOrder(data);

        // Nếu là Stripe và payment_status chưa cập nhật thành paid, poll lại sau 3s (tối đa 5 lần)
        if (data.payment_method === 'stripe' && data.payment_status !== 'paid' && pollCount < maxPolls) {
          pollCount++;
          timer = setTimeout(fetchOrder, 3000);
        } else {
          setIsLoading(false);
        }
      } catch (err: any) {
        console.error('Lỗi lấy chi tiết đơn hàng:', err);
        setErrorMsg('Không thể kết nối tới máy chủ để lấy thông tin đơn hàng.');
        setIsLoading(false);
      }
    };

    fetchOrder();

    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [orderId]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price);
  };

  const getPaymentStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-success/10 text-success border border-success/20">Đã thanh toán</span>;
      case 'cod_pending':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-600 border border-amber-500/20">Thanh toán khi nhận hàng (COD)</span>;
      case 'failed':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-destructive/10 text-destructive border border-destructive/20">Thanh toán thất bại</span>;
      case 'refunded':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-muted text-muted-foreground border border-border">Đã hoàn tiền</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-muted text-muted-foreground border border-border">Đang chờ xử lý</span>;
    }
  };

  const getOrderStatusBadge = (status: string) => {
    switch (status) {
      case 'processing':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-500/10 text-blue-600 border border-blue-500/20">Đang chuẩn bị hàng</span>;
      case 'shipping':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-purple-500/10 text-purple-600 border border-purple-500/20">Đang giao hàng</span>;
      case 'delivered':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-success/10 text-success border border-success/20">Đã giao thành công</span>;
      case 'cancelled':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-destructive/10 text-destructive border border-destructive/20">Đã hủy</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-600 border border-amber-500/20">Tiếp nhận đơn hàng</span>;
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-20 flex flex-col items-center justify-center gap-4 text-center">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <h2 className="text-lg font-bold text-foreground">Đang xác thực thông tin đơn hàng...</h2>
        <p className="text-xs text-muted-foreground">Hệ thống đang đồng bộ dữ liệu giao dịch từ máy chủ.</p>
      </div>
    );
  }

  if (errorMsg || !order) {
    return (
      <div className="container mx-auto px-4 py-16 flex flex-col items-center justify-center gap-6 max-w-md text-center">
        <div className="p-4 rounded-full bg-destructive/10 text-destructive">
          <AlertCircle className="w-12 h-12" />
        </div>
        <div className="space-y-2">
          <h1 className="text-xl font-bold text-foreground">Thông báo đơn hàng</h1>
          <p className="text-sm text-muted-foreground">{errorMsg || 'Không tìm thấy dữ liệu đơn hàng.'}</p>
        </div>
        <div className="flex gap-4">
          <Link href="/products" className="px-5 py-2.5 rounded-xl bg-primary text-primary-foreground text-sm font-bold hover:opacity-90 transition-all">
            Xem sản phẩm
          </Link>
          <Link href="/account" className="px-5 py-2.5 rounded-xl border border-border text-foreground text-sm font-bold hover:bg-muted transition-all">
            Trang tài khoản
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12 flex-1 flex flex-col items-center justify-center gap-8 max-w-2xl">
      {/* Icon Thành Công */}
      <div className="p-4 rounded-full bg-success/10 text-success">
        <CheckCircle2 className="w-14 h-14" />
      </div>

      {/* Tiêu đề thông báo */}
      <div className="space-y-2 text-center">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-foreground">Đặt hàng thành công!</h1>
        <p className="text-sm text-muted-foreground">
          Cảm ơn bạn đã tin tưởng mua sắm tại cửa hàng. Đơn hàng của bạn đã được ghi nhận trên hệ thống.
        </p>
      </div>

      {/* Thẻ Chi Tiết Đơn Hàng */}
      <div className="w-full bg-card border border-border rounded-2xl p-6 sm:p-8 space-y-6 shadow-sm">
        {/* Header Đơn Hàng */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-6 border-b border-border gap-4">
          <div>
            <span className="text-xs text-muted-foreground">Mã đơn hàng:</span>
            <p className="font-mono font-bold text-base text-foreground break-all">{order.order_id}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {getOrderStatusBadge(order.status)}
            {getPaymentStatusBadge(order.payment_status)}
          </div>
        </div>

        {/* Thông Tin Người Nhận & Giao Hàng */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="space-y-1.5 p-3.5 rounded-xl bg-muted/40 border border-border/60">
            <div className="flex items-center gap-2 font-bold text-foreground">
              <User className="w-3.5 h-3.5 text-primary" />
              <span>Người nhận hàng:</span>
            </div>
            <p className="text-muted-foreground">{order.recipient_name}</p>
            <div className="flex items-center gap-1.5 text-muted-foreground pt-1">
              <Phone className="w-3 h-3 text-primary" />
              <span>{order.recipient_phone}</span>
            </div>
          </div>

          <div className="space-y-1.5 p-3.5 rounded-xl bg-muted/40 border border-border/60">
            <div className="flex items-center gap-2 font-bold text-foreground">
              <MapPin className="w-3.5 h-3.5 text-primary" />
              <span>Địa chỉ nhận hàng:</span>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              {order.address_line}, {order.ward}, {order.province}
            </p>
            {order.note && (
              <p className="text-[11px] text-primary/90 italic pt-1 border-t border-border/60">
                Ghi chú: {order.note}
              </p>
            )}
          </div>
        </div>

        {/* Danh Sách Sản Phẩm */}
        <div className="space-y-3 pt-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
            <Package className="w-4 h-4 text-primary" />
            <span>Sản phẩm trong đơn ({order.items.length})</span>
          </h3>
          <div className="divide-y divide-border/60 border border-border/60 rounded-xl overflow-hidden bg-background">
            {order.items.map((item, idx) => (
              <div key={idx} className="p-3 sm:p-4 flex items-center justify-between gap-4 text-xs">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  {item.image && (
                    <img src={item.image} alt={item.name} className="w-10 h-10 object-contain rounded-lg border border-border bg-card p-0.5 flex-shrink-0" />
                  )}
                  <div className="min-w-0">
                    <p className="font-bold text-foreground truncate">{item.name}</p>
                    <span className="text-[11px] text-muted-foreground">Số lượng: {item.quantity}</span>
                  </div>
                </div>
                <span className="font-bold text-foreground whitespace-nowrap">{formatPrice(item.price * item.quantity)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Tổng Tiền */}
        <div className="flex justify-between items-center pt-4 border-t border-border">
          <span className="text-sm font-semibold text-muted-foreground">Tổng tiền thanh toán:</span>
          <span className="text-xl font-black text-primary">{formatPrice(order.total)}</span>
        </div>
      </div>

      {/* Các Nút Điều Hướng */}
      <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
        <Link
          href="/account"
          className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl border border-border bg-card hover:bg-muted text-foreground text-sm font-bold shadow-sm transition-all"
        >
          <span>Xem trong đơn hàng của tôi</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
        <Link
          href="/products"
          className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-primary hover:opacity-90 text-primary-foreground text-sm font-bold shadow-lg shadow-primary/20 transition-all"
        >
          <ShoppingBag className="w-4 h-4" />
          <span>Tiếp tục mua sắm</span>
        </Link>
      </div>
    </div>
  );
}

export default function CheckoutSuccessPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto px-4 py-20 flex flex-col items-center justify-center gap-4">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <span className="text-sm text-muted-foreground">Đang tải trang...</span>
      </div>
    }>
      <CheckoutSuccessContent />
    </Suspense>
  );
}
