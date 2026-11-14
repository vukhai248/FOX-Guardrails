'use client';

import React from 'react';
import Link from 'next/link';
import { useCart } from '@/store/useCart';
import { Trash2, ArrowRight, ShoppingBag, ChevronLeft } from 'lucide-react';

export default function CartPage() {
  const { items, updateQuantity, removeItem, clearCart, getTotalPrice, getTotalItems } = useCart();

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price);
  };

  if (items.length === 0) {
    return (
      <div className="container mx-auto px-4 py-20 text-center flex-1 flex flex-col items-center justify-center gap-6 transition-colors duration-200">
        <div className="p-5 rounded-full bg-card border border-border text-muted-foreground">
          <ShoppingBag className="w-12 h-12" />
        </div>
        <div className="space-y-2">
          <h1 className="text-xl font-bold text-foreground">Giỏ hàng của bạn đang trống</h1>
          <p className="text-muted-foreground text-sm max-w-sm">Hãy khám phá thêm các thiết bị công nghệ hấp dẫn và thêm vào giỏ hàng của bạn!</p>
        </div>
        <Link
          href="/products"
          className="flex items-center gap-2 px-6 py-3 font-semibold rounded-full bg-primary hover:opacity-90 text-primary-foreground shadow-lg shadow-primary/20 active:scale-95 transition-all text-sm cursor-pointer"
        >
          <span>Bắt đầu mua sắm</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 flex-1 space-y-8 transition-colors duration-200">
      {/* Tiêu đề & nút quay lại */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-border pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-foreground">Giỏ hàng của bạn</h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">Bạn đang có {getTotalItems()} sản phẩm trong giỏ hàng.</p>
        </div>
        <Link href="/products" className="inline-flex items-center gap-1.5 text-xs sm:text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ChevronLeft className="w-4 h-4" />
          <span>Tiếp tục mua sắm</span>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cột trái + giữa: Danh sách sản phẩm trong giỏ */}
        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-2xl border border-border overflow-hidden divide-y divide-border bg-card/10">
            {items.map((item) => (
              <div key={item.id} className="p-4 sm:p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                {/* Info & Ảnh */}
                <div className="flex gap-4 flex-1">
                  <div className="w-20 h-20 rounded-xl bg-background border border-border p-2 flex items-center justify-center flex-shrink-0">
                    <img src={item.image} alt={item.name} className="w-full h-full object-contain" />
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-bold text-primary tracking-wider">
                      {item.brand}
                    </span>
                    <h3 className="font-bold text-foreground text-sm sm:text-base line-clamp-1 hover:text-primary">
                      <Link href={`/products/${item.id}`}>{item.name}</Link>
                    </h3>
                    <p className="text-muted-foreground text-xs sm:text-sm">{formatPrice(item.price)}</p>
                  </div>
                </div>

                {/* Điều chỉnh số lượng & Xóa */}
                <div className="flex items-center justify-between sm:justify-end gap-6 w-full sm:w-auto border-t border-border sm:border-0 pt-4 sm:pt-0">
                  <div className="flex items-center border border-border rounded-xl overflow-hidden bg-background">
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      className="w-9 h-9 flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-all font-bold cursor-pointer"
                    >
                      -
                    </button>
                    <span className="w-10 text-center text-foreground text-sm font-bold">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="w-9 h-9 flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-all font-bold cursor-pointer"
                    >
                      +
                    </button>
                  </div>
                  <span className="font-bold text-foreground text-sm sm:text-base whitespace-nowrap min-w-[100px] text-right">
                    {formatPrice(item.price * item.quantity)}
                  </span>
                  <button
                    onClick={() => removeItem(item.id)}
                    className="p-2 text-muted-foreground hover:text-destructive transition-colors cursor-pointer"
                    title="Xóa khỏi giỏ"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Nút làm sạch giỏ hàng */}
          <div className="flex justify-end">
            <button
              onClick={clearCart}
              className="text-xs text-destructive hover:opacity-80 font-semibold border border-destructive/20 hover:border-destructive/40 bg-destructive/5 hover:bg-destructive/10 px-4 py-2 rounded-xl transition-all cursor-pointer"
            >
              Làm trống giỏ hàng
            </button>
          </div>
        </div>

        {/* Cột phải: Tổng kết đơn hàng */}
        <div>
          <div className="rounded-2xl border border-border bg-card/40 p-6 space-y-6">
            <h2 className="text-lg font-bold text-foreground border-b border-border pb-3">Tóm tắt đơn hàng</h2>
            
            <div className="space-y-3 text-xs sm:text-sm text-muted-foreground">
              <div className="flex justify-between">
                <span>Số lượng sản phẩm:</span>
                <span className="text-foreground font-semibold">{getTotalItems()}</span>
              </div>
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
              <span className="font-semibold text-foreground">Tổng cộng:</span>
              <span className="text-xl font-black text-primary">{formatPrice(getTotalPrice())}</span>
            </div>

            <Link
              href="/checkout"
              className="flex items-center justify-center gap-2 w-full h-12 rounded-xl bg-primary hover:opacity-90 text-primary-foreground font-bold hover:shadow-lg hover:shadow-primary/20 active:scale-95 transition-all text-sm cursor-pointer"
            >
              <span>Tiến hành thanh toán</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

