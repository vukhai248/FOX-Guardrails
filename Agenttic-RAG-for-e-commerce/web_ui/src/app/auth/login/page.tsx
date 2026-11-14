'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import Link from 'next/link';
import { Mail, Lock, ArrowRight, Loader2, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    // Nếu user đã đăng nhập sẵn, chuyển hướng trực tiếp về trang cá nhân
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        router.push('/account');
      }
    };
    checkSession();
  }, [router]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMsg('Vui lòng nhập đầy đủ Email và Mật khẩu!');
      return;
    }

    setErrorMsg('');
    setIsLoading(true);

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        throw new Error(error.message);
      }

      if (data.user) {
        router.push('/account');
        router.refresh();
      }
    } catch (err: any) {
      console.error('Lỗi đăng nhập:', err);
      setErrorMsg(err.message || 'Email hoặc Mật khẩu không chính xác. Vui lòng kiểm tra lại kết nối CSDL Supabase.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setErrorMsg('');
    setIsGoogleLoading(true);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      if (error) throw error;
    } catch (err: any) {
      console.error('Lỗi đăng nhập Google OAuth:', err);
      setErrorMsg(err.message || 'Không thể kết nối dịch vụ Google OAuth.');
      setIsGoogleLoading(false);
    }
  };

  return (
    <div className="flex-1 flex items-center justify-center px-4 py-16 bg-background relative">
      {/* Background blur accent */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-80 h-80 rounded-full bg-primary/5 blur-[100px] z-0" />

      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 sm:p-8 space-y-6 relative z-10 shadow-xl">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-extrabold text-foreground">Đăng nhập tài khoản</h1>
          <p className="text-xs text-muted-foreground">Khám phá các thiết bị công nghệ đỉnh cao và dịch vụ hỗ trợ AI</p>
        </div>

        {errorMsg && (
          <div className="p-3.5 rounded-xl border border-destructive/20 bg-destructive/5 text-destructive text-xs flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground">Địa chỉ Email</label>
            <div className="relative">
              <input
                type="email"
                required
                autoComplete="off"
                suppressHydrationWarning
                placeholder="email@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-11 pl-10 pr-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary transition-colors"
              />
              <Mail className="absolute left-3.5 top-3.5 w-4 h-4 text-muted-foreground" />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold text-muted-foreground">Mật khẩu</label>
              <Link href="/auth/forgot-password" className="text-[10px] text-primary hover:underline">
                Quên mật khẩu?
              </Link>
            </div>
            <div className="relative">
              <input
                type="password"
                required
                autoComplete="off"
                suppressHydrationWarning
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full h-11 pl-10 pr-4 rounded-xl border border-border bg-background text-foreground placeholder-muted-foreground/60 text-sm focus:outline-none focus:border-primary transition-colors"
              />
              <Lock className="absolute left-3.5 top-3.5 w-4 h-4 text-muted-foreground" />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="flex items-center justify-center gap-2 w-full h-11 rounded-xl bg-primary hover:opacity-90 disabled:bg-muted disabled:text-muted-foreground text-primary-foreground text-sm font-bold shadow-lg shadow-primary/15 hover:shadow-primary/30 active:scale-[0.98] disabled:scale-100 transition-all"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Đang xác thực...</span>
              </>
            ) : (
              <>
                <span>Đăng nhập</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Dấu phân cách */}
        <div className="relative flex items-center justify-center text-[10px] uppercase font-bold text-muted-foreground tracking-wider">
          <div className="border-t border-border flex-1"></div>
          <span className="px-3 bg-card relative z-10">Hoặc tiếp tục với</span>
          <div className="border-t border-border flex-1"></div>
        </div>

        {/* Đăng nhập OAuth Google */}
        <button
          type="button"
          onClick={handleGoogleLogin}
          disabled={isGoogleLoading}
          className="flex items-center justify-center gap-3 w-full h-11 rounded-xl border border-border bg-background hover:bg-muted text-foreground text-xs sm:text-sm font-semibold hover:border-muted-foreground/40 disabled:opacity-50 active:scale-[0.98] transition-all cursor-pointer"
        >
          {isGoogleLoading ? (
            <Loader2 className="w-4 h-4 animate-spin text-primary" />
          ) : (
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#EA4335" d="M12 5.04c1.9 0 3.51.65 4.58 1.68l3.43-3.43C17.93 1.34 15.19.5 12 .5 7.42.5 3.54 3.12 1.62 6.94l3.96 3.07C6.51 7.23 9.01 5.04 12 5.04z" />
              <path fill="#4285F4" d="M23.49 12.27c0-.82-.07-1.6-.21-2.27H12v4.51h6.44c-.28 1.48-1.12 2.73-2.38 3.58l3.96 3.07c2.32-2.14 3.47-5.3 3.47-8.89z" />
              <path fill="#FBBC05" d="M5.58 14.81c-.24-.72-.38-1.49-.38-2.31s.14-1.59.38-2.31L1.62 7.12C.59 9.17 0 11.51 0 14s.59 4.83 1.62 6.88l3.96-3.07z" />
              <path fill="#34A853" d="M12 23.5c3.24 0 5.97-1.07 7.96-2.92l-3.96-3.07c-1.1.74-2.51 1.18-4 1.18-2.99 0-5.49-2.19-6.42-4.97L1.62 16.8c1.92 3.82 5.8 6.7 10.38 6.7z" />
            </svg>
          )}
          <span>Đăng nhập Google</span>
        </button>

        {/* Đăng ký */}
        <p className="text-center text-xs text-muted-foreground">
          Chưa có tài khoản?{' '}
          <Link href="/auth/register" className="text-primary hover:underline font-semibold">
            Đăng ký miễn phí
          </Link>
        </p>
      </div>
    </div>
  );
}
