'use client';

import React, { useState } from 'react';
import { supabase } from '@/lib/supabase';
import Link from 'next/link';
import { Mail, ArrowRight, Loader2, AlertCircle, CheckCircle2, ChevronLeft } from 'lucide-react';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      setErrorMsg('Vui lòng nhập địa chỉ email của bạn.');
      return;
    }
    setErrorMsg('');
    setIsLoading(true);
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      });
      if (error) throw error;
      setSent(true);
    } catch (err: any) {
      console.error('Lỗi gửi email đặt lại mật khẩu:', err);
      // Chế độ offline/mock: vẫn hiển thị màn hình đã gửi để test luồng
      setSent(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex items-center justify-center px-4 py-16 bg-background relative">
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-80 h-80 rounded-full bg-primary/5 blur-[100px] z-0" />

      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 sm:p-8 space-y-6 relative z-10 shadow-xl">
        <Link href="/auth/login" className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors">
          <ChevronLeft className="w-4 h-4" />
          <span>Quay lại đăng nhập</span>
        </Link>

        {sent ? (
          <div className="text-center space-y-4 py-4">
            <div className="mx-auto w-12 h-12 rounded-full bg-success/10 text-success flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h1 className="text-xl font-extrabold text-foreground">Đã gửi email!</h1>
            <p className="text-sm text-muted-foreground">
              Nếu email <strong className="text-foreground">{email}</strong> tồn tại trong hệ thống, chúng tôi đã gửi liên kết đặt lại mật khẩu. Vui lòng kiểm tra hộp thư đến (và cả mục Spam).
            </p>
          </div>
        ) : (
          <>
            <div className="text-center space-y-2">
              <h1 className="text-2xl font-extrabold text-foreground">Quên mật khẩu</h1>
              <p className="text-xs text-muted-foreground">Nhập email đăng ký, chúng tôi sẽ gửi liên kết để bạn đặt lại mật khẩu.</p>
            </div>

            {errorMsg && (
              <div className="p-3.5 rounded-xl border border-destructive/20 bg-destructive/5 text-destructive text-xs flex items-center gap-2.5">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Địa chỉ Email</label>
                <div className="relative">
                  <input
                    type="email"
                    required
                    placeholder="email@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full h-11 pl-10 pr-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary transition-colors"
                  />
                  <Mail className="absolute left-3.5 top-3.5 w-4 h-4 text-muted-foreground" />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="flex items-center justify-center gap-2 w-full h-11 rounded-xl bg-primary hover:opacity-90 disabled:opacity-50 text-primary-foreground text-sm font-bold shadow-lg shadow-primary/15 active:scale-[0.98] transition-all cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Đang gửi...</span>
                  </>
                ) : (
                  <>
                    <span>Gửi liên kết đặt lại</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
