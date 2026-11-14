'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { Loader2, AlertCircle } from 'lucide-react';
import Link from 'next/link';

export default function AuthCallbackPage() {
  const router = useRouter();
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    // Supabase JS client tự động phát hiện phiên đăng nhập trong URL (detectSessionInUrl).
    // Ta chỉ cần chờ session sẵn sàng rồi điều hướng về trang tài khoản.
    let cancelled = false;

    const finalizeLogin = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        if (error) throw error;

        if (session?.user) {
          router.replace('/account');
          return;
        }

        // Nếu chưa có session ngay, lắng nghe sự kiện đăng nhập trả về từ OAuth
        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, s) => {
          if (s?.user && !cancelled) {
            router.replace('/account');
          }
        });

        // Sau 5 giây vẫn không có session -> coi như thất bại
        setTimeout(() => {
          if (!cancelled) {
            supabase.auth.getSession().then(({ data }) => {
              if (!data.session) {
                setErrorMsg('Không thể hoàn tất đăng nhập. Vui lòng thử lại.');
              }
            });
          }
        }, 5000);

        return () => subscription.unsubscribe();
      } catch (err: any) {
        if (!cancelled) setErrorMsg(err.message || 'Đã xảy ra lỗi khi xử lý đăng nhập.');
      }
    };

    finalizeLogin();
    return () => {
      cancelled = true;
    };
  }, [router]);

  return (
    <div className="flex-1 flex items-center justify-center px-4 py-16 bg-background">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 text-center space-y-4 shadow-xl">
        {errorMsg ? (
          <>
            <div className="mx-auto w-12 h-12 rounded-full bg-destructive/10 text-destructive flex items-center justify-center">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h1 className="text-lg font-bold text-foreground">Đăng nhập thất bại</h1>
            <p className="text-sm text-muted-foreground">{errorMsg}</p>
            <Link href="/auth/login" className="inline-block px-5 py-2.5 rounded-xl bg-primary hover:opacity-90 text-primary-foreground text-sm font-bold transition-all">
              Quay lại đăng nhập
            </Link>
          </>
        ) : (
          <>
            <Loader2 className="w-10 h-10 text-primary animate-spin mx-auto" />
            <h1 className="text-lg font-bold text-foreground">Đang hoàn tất đăng nhập...</h1>
            <p className="text-sm text-muted-foreground">Vui lòng chờ trong giây lát, chúng tôi đang xác thực tài khoản của bạn.</p>
          </>
        )}
      </div>
    </div>
  );
}
