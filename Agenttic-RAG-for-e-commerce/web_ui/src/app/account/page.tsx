'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase, isSupabaseConfigured } from '@/lib/supabase';
import { ShoppingBag, User, LogOut, Clock, ShieldCheck, MapPin, Lock, Loader2, CheckCircle2, AlertCircle, Save, HelpCircle, LayoutDashboard, FileText, Edit3, X } from 'lucide-react';
import Link from 'next/link';

// Loại bỏ MOCK_ORDERS placeholder

type TabKey = 'orders' | 'profile' | 'password' | 'support';

export default function AccountPage() {
  const router = useRouter();

  const [user, setUser] = useState<any>(null);
  const [orders, setOrders] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabKey>('orders');

  // Form hồ sơ cá nhân
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [birthday, setBirthday] = useState('');
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileMsg, setProfileMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Form đổi mật khẩu
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordMsg, setPasswordMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Form gửi yêu cầu hỗ trợ (Khách hàng tạo)
  const [supportCategory, setSupportCategory] = useState('advisory');
  const [supportOrderId, setSupportOrderId] = useState('');
  const [supportNote, setSupportNote] = useState('');
  const [supportSaving, setSupportSaving] = useState(false);
  const [supportMsg, setSupportMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Sửa ghi chú đơn hàng pending
  const [editingOrderId, setEditingOrderId] = useState<string | null>(null);
  const [editingNoteText, setEditingNoteText] = useState<string>('');
  const [isSavingNote, setIsSavingNote] = useState<boolean>(false);
  const [orderNoteMsg, setOrderNoteMsg] = useState<{ orderId: string; type: 'success' | 'error'; text: string } | null>(null);

  const handleStartEditNote = (order: any) => {
    setEditingOrderId(order.id);
    setEditingNoteText(order.note || '');
    setOrderNoteMsg(null);
  };

  const handleCancelEditNote = () => {
    setEditingOrderId(null);
    setEditingNoteText('');
    setOrderNoteMsg(null);
  };

  const handleSaveOrderNote = async (orderId: string) => {
    if (editingNoteText.length > 500) {
      setOrderNoteMsg({ orderId, type: 'error', text: 'Ghi chú không được vượt quá 500 ký tự.' });
      return;
    }
    setIsSavingNote(true);
    setOrderNoteMsg(null);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token || '';

      const res = await fetch(`/api/orders/${orderId}/note`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ note: editingNoteText.trim() }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        if (res.status === 409 || data?.error?.code === 'NOT_EDITABLE') {
          throw new Error(data?.error?.message || 'Không thể sửa ghi chú vì đơn hàng không còn ở trạng thái chờ duyệt (pending).');
        }
        throw new Error(data?.error?.message || `Lỗi ${res.status}: Không thể cập nhật ghi chú.`);
      }

      setOrders((prev) =>
        prev.map((o) =>
          o.id === orderId
            ? { ...o, note: data?.note !== undefined ? data.note : editingNoteText.trim() }
            : o
        )
      );
      setOrderNoteMsg({ orderId, type: 'success', text: 'Cập nhật ghi chú giao hàng thành công!' });
      setEditingOrderId(null);
    } catch (err: any) {
      setOrderNoteMsg({ orderId, type: 'error', text: err.message || 'Lỗi khi lưu ghi chú.' });
    } finally {
      setIsSavingNote(false);
    }
  };

  const handleSendSupportTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!supportNote.trim()) {
      setSupportMsg({ type: 'error', text: 'Vui lòng nhập chi tiết nội dung yêu cầu hỗ trợ!' });
      return;
    }
    setSupportSaving(true);
    setSupportMsg(null);
    try {
      const { error } = await supabase.from('support_tickets').insert({
        customer_id: user.id,
        order_id: supportOrderId ? supportOrderId : null,
        category: supportCategory,
        risk_level: 'low',
        created_by: 'customer',
        status: 'open',
        note: supportNote.trim(),
      });
      if (error) throw error;
      setSupportMsg({ type: 'success', text: 'Gửi yêu cầu hỗ trợ thành công! Nhân viên sẽ phản hồi bạn sớm nhất.' });
      setSupportNote('');
      setSupportOrderId('');
    } catch (err: any) {
      console.error('Lỗi gửi support ticket:', err);
      setSupportMsg({ type: 'error', text: err.message || 'Lỗi hệ thống, không thể gửi yêu cầu hỗ trợ.' });
    } finally {
      setSupportSaving(false);
    }
  };

  const hydrateUser = (u: any) => {
    setUser(u);
    setFullName(u.user_metadata?.full_name || '');
    setPhone(u.user_metadata?.phone || '');
    setAddress(u.user_metadata?.address || '');
    setBirthday(u.user_metadata?.birthday || '');
  };

  useEffect(() => {
    const fetchUserDataAndOrders = async () => {
      setIsLoading(true);
      if (!isSupabaseConfigured) {
        console.error('Cấu hình Supabase (URL / ANON KEY) bị thiếu trong file .env.local!');
        setIsLoading(false);
        router.push('/auth/login');
        return;
      }
      try {
        const { data: { session } } = await supabase.auth.getSession();

        if (session?.user) {
          hydrateUser(session.user);

          const { data: orderData, error } = await supabase
            .from('orders')
            .select('*')
            .eq('user_id', session.user.id)
            .order('created_at', { ascending: false });

          if (error) throw error;

          setOrders(orderData || []);
        } else {
          const isMockLogged = localStorage.getItem('mock_user_logged');
          if (isMockLogged === 'true') {
            const mockUser = {
              id: 'mock_user_id_123456789',
              email: 'guest.developer@gmail.com',
              user_metadata: { full_name: 'Developer Guest', phone: '0900000000', address: '' },
            };
            hydrateUser(mockUser);

            // Kiểm tra mock_orders trong localStorage trước, nếu không có thì query Supabase
            const storedMockOrders = localStorage.getItem('mock_orders');
            if (storedMockOrders) {
              try {
                setOrders(JSON.parse(storedMockOrders));
              } catch {
                setOrders([]);
              }
            } else {
              const { data: orderData } = await supabase
                .from('orders')
                .select('*')
                .eq('user_id', mockUser.id)
                .order('created_at', { ascending: false });
              setOrders(orderData || []);
            }
          } else {
            router.push('/auth/login');
          }
        }
      } catch (err) {
        console.warn('Lỗi kết nối hoặc tải đơn hàng:', err);
        setOrders([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserDataAndOrders();
  }, [router]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    localStorage.removeItem('mock_user_logged');
    router.push('/');
    router.refresh();
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileMsg(null);
    setProfileSaving(true);
    try {
      const { error } = await supabase.auth.updateUser({
        data: { full_name: fullName, phone, address, birthday },
      });
      if (error) throw error;
      setUser((prev: any) => ({
        ...prev,
        user_metadata: { ...prev?.user_metadata, full_name: fullName, phone, address, birthday },
      }));
      setProfileMsg({ type: 'success', text: 'Cập nhật thông tin cá nhân thành công!' });
    } catch (err: any) {
      // Chế độ mock offline: cập nhật ngay trên giao diện
      setUser((prev: any) => ({
        ...prev,
        user_metadata: { ...prev?.user_metadata, full_name: fullName, phone, address, birthday },
      }));
      setProfileMsg({ type: 'success', text: 'Đã lưu thông tin (chế độ offline/mock).' });
    } finally {
      setProfileSaving(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordMsg(null);
    if (newPassword.length < 6) {
      setPasswordMsg({ type: 'error', text: 'Mật khẩu mới phải có ít nhất 6 ký tự.' });
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordMsg({ type: 'error', text: 'Mật khẩu nhập lại không khớp.' });
      return;
    }
    setPasswordSaving(true);
    try {
      const { error } = await supabase.auth.updateUser({ password: newPassword });
      if (error) throw error;
      setPasswordMsg({ type: 'success', text: 'Đổi mật khẩu thành công!' });
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setPasswordMsg({ type: 'error', text: err.message || 'Không thể đổi mật khẩu. Vui lòng thử lại.' });
    } finally {
      setPasswordSaving(false);
    }
  };

  const formatPrice = (price: number) =>
    new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', {
      year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit',
    });
  };

  const getStatusBadge = (status: string) => {
    const map: Record<string, { cls: string; label: string }> = {
      pending: { cls: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20', label: 'Chờ xử lý' },
      processing: { cls: 'bg-primary/10 text-primary border-primary/20', label: 'Đã thanh toán' },
      shipping: { cls: 'bg-primary/10 text-primary border-primary/20', label: 'Đang giao hàng' },
      delivered: { cls: 'bg-success/10 text-success border-success/20', label: 'Đã giao hàng' },
      cancelled: { cls: 'bg-destructive/10 text-destructive border-destructive/20', label: 'Đã hủy đơn' },
    };
    const s = map[status] || { cls: 'bg-muted text-muted-foreground border-border', label: 'Không xác định' };
    return <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${s.cls}`}>{s.label}</span>;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-16 flex items-center justify-center flex-1">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-muted-foreground">Đang tải thông tin tài khoản...</span>
        </div>
      </div>
    );
  }

  if (!user) return null;

  const tabs: { key: TabKey; label: string }[] = [
    { key: 'orders', label: `Đơn hàng của tôi (${orders.length})` },
    { key: 'profile', label: 'Thông tin cá nhân' },
    { key: 'password', label: 'Đổi mật khẩu' },
    { key: 'support', label: 'Gửi yêu cầu hỗ trợ' },
  ];

  return (
    <div className="container mx-auto px-4 py-8 flex flex-col md:flex-row gap-8 flex-1 transition-colors duration-200">
      {/* 1. SIDEBAR DỌC BÊN TRÁI */}
      <aside className="w-full md:w-64 flex-shrink-0 flex flex-col gap-6">
        {/* Info card */}
        <div className="rounded-2xl border border-border bg-card/45 p-5 flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center font-bold text-primary-foreground text-lg shadow-md shadow-primary/20 uppercase flex-shrink-0">
            {user.email?.substring(0, 2)}
          </div>
          <div className="overflow-hidden">
            <h2 className="text-sm font-extrabold text-foreground truncate">
              {user.user_metadata?.full_name || user.email?.split('@')[0]}
            </h2>
            <span className="text-[10px] text-muted-foreground block truncate">{user.email}</span>
          </div>
        </div>

        {/* Navigation menu */}
        <nav className="rounded-2xl border border-border bg-card/35 p-3 flex flex-row md:flex-col gap-1 overflow-x-auto no-scrollbar md:overflow-visible">
          {tabs.map((tab) => {
            const Icon = tab.key === 'orders' ? ShoppingBag 
                         : tab.key === 'profile' ? User 
                         : tab.key === 'password' ? Lock 
                         : HelpCircle;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer flex-1 md:flex-initial ${
                  activeTab === tab.key
                    ? 'bg-primary text-primary-foreground shadow-md shadow-primary/15'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Logout & Home links (Desktop only) */}
        <div className="hidden md:flex flex-col gap-3 px-3">
          {/* Chỉ hiển thị link Admin nếu có quyền */}
          {user && (user.user_metadata?.role === 'admin' || user.user_metadata?.role === 'staff') && (
            <Link
              href="/admin"
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-xs font-bold text-primary border border-primary/20 hover:border-primary/45 bg-primary/5 hover:bg-primary/10 rounded-xl transition-all cursor-pointer"
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Vào Trang Quản Trị</span>
            </Link>
          )}

          <Link
            href="/policy/warranty"
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-xs font-bold text-foreground border border-border hover:bg-muted/50 rounded-xl transition-all cursor-pointer shadow-sm"
          >
            <ShieldCheck className="w-4 h-4 text-primary" />
            <span>Chính sách bảo hành</span>
          </Link>

          <Link
            href="/policy/terms"
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-xs font-bold text-foreground border border-border hover:bg-muted/50 rounded-xl transition-all cursor-pointer shadow-sm"
          >
            <HelpCircle className="w-4 h-4 text-primary" />
            <span>Điều khoản sử dụng</span>
          </Link>

          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-xs font-bold text-destructive border border-destructive/20 hover:border-destructive/40 bg-destructive/5 hover:bg-destructive/10 rounded-xl transition-all cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            <span>Đăng xuất tài khoản</span>
          </button>
          <div className="text-center">
            <Link href="/" className="text-xs text-primary hover:underline font-semibold">
              ← Quay lại mua sắm
            </Link>
          </div>
        </div>
      </aside>

      {/* 2. NỘI DUNG HIỂN THỊ BÊN PHẢI */}
      <main className="flex-1 space-y-6 overflow-hidden">
        {/* Tiêu đề Panel hiện tại */}
        <div className="border-b border-border pb-4 hidden md:block">
          <h1 className="text-sm font-extrabold text-foreground uppercase tracking-wider">
            {activeTab === 'orders' ? 'Lịch sử đơn hàng' 
             : activeTab === 'profile' ? 'Thông tin cá nhân' 
             : activeTab === 'password' ? 'Bảo mật tài khoản' 
             : 'Hỗ trợ kỹ thuật & dịch vụ'}
          </h1>
        </div>

      {/* TAB: ĐƠN HÀNG */}
      {activeTab === 'orders' && (
        <div className="space-y-6">
          {orders.length === 0 ? (
            <div className="text-center py-16 border border-dashed border-border rounded-2xl flex flex-col items-center gap-3">
              <ShoppingBag className="w-10 h-10 text-muted-foreground" />
              <p className="text-muted-foreground text-sm">Bạn chưa thực hiện đơn đặt hàng nào.</p>
              <Link href="/products" className="text-xs px-4 py-2 bg-primary hover:opacity-90 text-primary-foreground rounded-full font-bold">
                Mua sắm ngay
              </Link>
            </div>
          ) : (
            <div className="space-y-6">
              {orders.map((order) => (
                <div key={order.id} className="rounded-2xl border border-border bg-card/40 overflow-hidden divide-y divide-border">
                  <div className="p-4 sm:p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-muted/30">
                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-semibold text-muted-foreground">Mã đơn hàng:</span>
                        <span className="text-xs font-mono font-bold text-foreground bg-background px-2 py-0.5 rounded border border-border break-all">{order.id}</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Clock className="w-3.5 h-3.5 text-primary" />
                        <span>Đặt lúc: {formatDate(order.created_at)}</span>
                      </div>
                    </div>
                    <div>{getStatusBadge(order.status)}</div>
                  </div>

                  <div className="p-4 sm:p-5 space-y-4">
                    {order.items.map((item: any, idx: number) => (
                      <div key={idx} className="flex gap-4 text-xs sm:text-sm">
                        <div className="w-14 h-14 rounded-xl bg-background border border-border p-1 flex items-center justify-center flex-shrink-0">
                          <img src={item.image} alt={item.name} className="w-full h-full object-contain" />
                        </div>
                        <div className="flex-1 space-y-0.5">
                          <h4 className="font-bold text-foreground line-clamp-1">{item.name}</h4>
                          <div className="flex justify-between text-muted-foreground">
                            <span>Số lượng: {item.quantity}</span>
                            <span className="text-foreground font-semibold">{formatPrice(item.price)}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="p-4 sm:p-5 space-y-3 bg-muted/20 text-xs sm:text-sm">
                    <div className="flex items-start gap-2 text-muted-foreground">
                      <MapPin className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span><strong className="text-foreground">Địa chỉ nhận hàng:</strong> {order.shipping_address}</span>
                    </div>

                    {/* Ghi chú giao hàng & Sửa ghi chú khi đơn pending */}
                    <div className="rounded-xl border border-border/60 bg-card/60 p-3 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 font-semibold text-foreground text-xs">
                          <FileText className="w-3.5 h-3.5 text-primary" />
                          <span>Ghi chú giao hàng:</span>
                        </div>
                        {order.status === 'pending' && editingOrderId !== order.id && (
                          <button
                            type="button"
                            onClick={() => handleStartEditNote(order)}
                            className="inline-flex items-center gap-1 text-[11px] font-bold text-primary hover:underline cursor-pointer"
                          >
                            <Edit3 className="w-3 h-3" />
                            <span>Sửa ghi chú</span>
                          </button>
                        )}
                      </div>

                      {orderNoteMsg && orderNoteMsg.orderId === order.id && (
                        <div
                          className={`p-2 rounded-lg border text-xs flex items-center gap-2 ${
                            orderNoteMsg.type === 'success'
                              ? 'border-success/30 bg-success/10 text-success'
                              : 'border-destructive/30 bg-destructive/10 text-destructive'
                          }`}
                        >
                          {orderNoteMsg.type === 'success' ? (
                            <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
                          ) : (
                            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                          )}
                          <span>{orderNoteMsg.text}</span>
                        </div>
                      )}

                      {editingOrderId === order.id ? (
                        <div className="space-y-2 pt-1">
                          <textarea
                            rows={2}
                            maxLength={500}
                            value={editingNoteText}
                            onChange={(e) => setEditingNoteText(e.target.value)}
                            placeholder="Nhập ghi chú giao hàng mới (ví dụ: gọi trước khi giao, giao giờ hành chính...)..."
                            className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground text-xs focus:outline-none focus:border-primary transition-colors resize-y"
                          />
                          <div className="flex justify-between items-center text-[10px] text-muted-foreground">
                            <span>{editingNoteText.length}/500 ký tự</span>
                            <div className="flex items-center gap-2">
                              <button
                                type="button"
                                onClick={handleCancelEditNote}
                                disabled={isSavingNote}
                                className="px-2.5 py-1 rounded-lg border border-border hover:bg-muted text-muted-foreground text-xs font-semibold cursor-pointer disabled:opacity-50"
                              >
                                Hủy
                              </button>
                              <button
                                type="button"
                                onClick={() => handleSaveOrderNote(order.id)}
                                disabled={isSavingNote}
                                className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-primary text-primary-foreground text-xs font-bold hover:opacity-90 cursor-pointer disabled:opacity-50"
                              >
                                {isSavingNote ? (
                                  <>
                                    <Loader2 className="w-3 h-3 animate-spin" />
                                    <span>Đang lưu...</span>
                                  </>
                                ) : (
                                  <>
                                    <Save className="w-3 h-3" />
                                    <span>Lưu</span>
                                  </>
                                )}
                              </button>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <p className="text-xs text-muted-foreground italic">
                          {order.note ? `"${order.note}"` : '(Không có ghi chú giao hàng)'}
                        </p>
                      )}
                    </div>

                    <div className="border-t border-border pt-3 flex justify-between items-center text-sm">
                      <span className="font-semibold text-muted-foreground">Tổng thanh toán:</span>
                      <span className="text-base font-black text-primary">{formatPrice(order.total)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB: HỒ SƠ CÁ NHÂN (SỬA ĐƯỢC) */}
      {activeTab === 'profile' && (
        <form onSubmit={handleSaveProfile} className="max-w-xl rounded-2xl border border-border bg-card/40 p-6 space-y-6">
          <h2 className="text-lg font-bold text-foreground flex items-center gap-2 border-b border-border pb-3">
            <User className="w-5 h-5 text-primary" />
            <span>Chỉnh sửa thông tin cá nhân</span>
          </h2>

          {profileMsg && (
            <div className={`p-3.5 rounded-xl border text-xs flex items-center gap-2.5 ${
              profileMsg.type === 'success'
                ? 'border-success/20 bg-success/5 text-success'
                : 'border-destructive/20 bg-destructive/5 text-destructive'
            }`}>
              {profileMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 flex-shrink-0" />}
              <span>{profileMsg.text}</span>
            </div>
          )}

          <div className="space-y-4 text-sm">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Địa chỉ Email (không thể thay đổi)</label>
              <input
                type="email"
                disabled
                value={user.email || ''}
                className="w-full h-11 px-4 rounded-xl border border-border bg-muted text-muted-foreground text-sm cursor-not-allowed"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Họ và tên</label>
              <input
                type="text"
                placeholder="Nguyễn Văn A"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full h-11 px-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary transition-colors"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Số điện thoại</label>
              <input
                type="tel"
                placeholder="09xxxxxxxx"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full h-11 px-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary transition-colors"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Ngày sinh</label>
              <input
                type="date"
                value={birthday}
                onChange={(e) => setBirthday(e.target.value)}
                className="w-full h-11 px-4 rounded-xl border border-border bg-background text-foreground text-sm focus:outline-none focus:border-primary transition-colors cursor-pointer"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Địa chỉ mặc định</label>
              <textarea
                rows={3}
                placeholder="Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành phố..."
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full p-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary resize-none transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={profileSaving}
            className="flex items-center justify-center gap-2 h-11 px-6 rounded-xl bg-primary hover:opacity-90 disabled:opacity-50 text-primary-foreground text-sm font-bold shadow-md shadow-primary/15 active:scale-[0.98] transition-all cursor-pointer"
          >
            {profileSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            <span>Lưu thay đổi</span>
          </button>
        </form>
      )}

      {/* TAB: ĐỔI MẬT KHẨU */}
      {activeTab === 'password' && (
        <form onSubmit={handleChangePassword} className="max-w-xl rounded-2xl border border-border bg-card/40 p-6 space-y-6">
          <h2 className="text-lg font-bold text-foreground flex items-center gap-2 border-b border-border pb-3">
            <Lock className="w-5 h-5 text-primary" />
            <span>Đổi mật khẩu</span>
          </h2>

          {passwordMsg && (
            <div className={`p-3.5 rounded-xl border text-xs flex items-center gap-2.5 ${
              passwordMsg.type === 'success'
                ? 'border-success/20 bg-success/5 text-success'
                : 'border-destructive/20 bg-destructive/5 text-destructive'
            }`}>
              {passwordMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 flex-shrink-0" />}
              <span>{passwordMsg.text}</span>
            </div>
          )}

          <div className="space-y-4 text-sm">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Mật khẩu mới</label>
              <input
                type="password"
                placeholder="Tối thiểu 6 ký tự"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full h-11 px-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary transition-colors"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Xác nhận mật khẩu mới</label>
              <input
                type="password"
                placeholder="Nhập lại mật khẩu mới"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full h-11 px-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={passwordSaving}
            className="flex items-center justify-center gap-2 h-11 px-6 rounded-xl bg-primary hover:opacity-90 disabled:opacity-50 text-primary-foreground text-sm font-bold shadow-md shadow-primary/15 active:scale-[0.98] transition-all cursor-pointer"
          >
            {passwordSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
            <span>Cập nhật mật khẩu</span>
          </button>
        </form>
      )}

      {/* TAB: GỬI YÊU CẦU HỖ TRỢ */}
      {activeTab === 'support' && (
        <form onSubmit={handleSendSupportTicket} className="max-w-xl rounded-2xl border border-border bg-card/40 p-6 space-y-6">
          <h2 className="text-lg font-bold text-foreground flex items-center gap-2 border-b border-border pb-3">
            <HelpCircle className="w-5 h-5 text-primary" />
            <span>Gửi yêu cầu hỗ trợ trực tiếp</span>
          </h2>

          {supportMsg && (
            <div className={`p-3.5 rounded-xl border text-xs flex items-center gap-2.5 ${
              supportMsg.type === 'success'
                ? 'border-success/20 bg-success/5 text-success'
                : 'border-destructive/20 bg-destructive/5 text-destructive'
            }`}>
              {supportMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 flex-shrink-0" />}
              <span>{supportMsg.text}</span>
            </div>
          )}

          <div className="space-y-4 text-sm">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Danh mục hỗ trợ</label>
              <select
                value={supportCategory}
                onChange={(e) => setSupportCategory(e.target.value)}
                className="w-full h-11 px-4 rounded-xl border border-border bg-background text-foreground text-sm focus:outline-none focus:border-primary cursor-pointer transition-colors"
              >
                <option value="advisory">Tư vấn mua hàng / Thông số kỹ thuật</option>
                <option value="negotiation">Đàm phán giá / Khuyến mãi</option>
                <option value="technical">Hỗ trợ kỹ thuật sản phẩm</option>
                <option value="other">Ý kiến khác / Góp ý</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Đơn hàng liên quan (Không bắt buộc)</label>
              <select
                value={supportOrderId}
                onChange={(e) => setSupportOrderId(e.target.value)}
                className="w-full h-11 px-4 rounded-xl border border-border bg-background text-foreground text-sm focus:outline-none focus:border-primary cursor-pointer transition-colors"
              >
                <option value="">-- Không liên quan đến đơn hàng nào --</option>
                {orders.map((o) => (
                  <option key={o.id} value={o.id}>
                    Đơn hàng #{o.id.substring(0, 8)}... ({formatPrice(o.total)})
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Mô tả chi tiết sự cố / Yêu cầu</label>
              <textarea
                rows={4}
                placeholder="Vui lòng mô tả chi tiết vấn đề bạn đang gặp phải hoặc thông tin cần tư vấn để chúng tôi hỗ trợ nhanh nhất..."
                value={supportNote}
                onChange={(e) => setSupportNote(e.target.value)}
                className="w-full p-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary resize-none transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={supportSaving}
            className="flex items-center justify-center gap-2 h-11 px-6 rounded-xl bg-primary hover:opacity-90 disabled:opacity-50 text-primary-foreground text-sm font-bold shadow-md shadow-primary/15 active:scale-[0.98] transition-all cursor-pointer"
          >
            {supportSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <HelpCircle className="w-4 h-4" />}
            <span>Gửi yêu cầu</span>
          </button>
        </form>
      )}
      </main>
    </div>
  );
}
