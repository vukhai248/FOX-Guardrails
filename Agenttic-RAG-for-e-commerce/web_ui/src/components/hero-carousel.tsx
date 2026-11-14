'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react';

interface Slide {
  badge: string;
  title: string;
  highlight: string;
  desc: string;
  ctaLabel: string;
  ctaHref: string;
  image: string;
}

const SLIDES: Slide[] = [
  {
    badge: 'Công Nghệ Đột Phá - Trải Nghiệm Premium',
    title: 'Khởi nguồn của',
    highlight: 'Kỷ Nguyên Công Nghệ',
    desc: 'Laptop cấu hình khủng, điện thoại flagship đỉnh cao, đồng hồ thông minh dã ngoại và tai nghe chống ồn tốt nhất hiện nay.',
    ctaLabel: 'Mua sắm ngay',
    ctaHref: '/products',
    image: 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=600',
  },
  {
    badge: 'Ưu Đãi Laptop - Giảm Đến 15%',
    title: 'MacBook & Laptop Gaming',
    highlight: 'Hiệu Năng Vượt Trội',
    desc: 'Bộ sưu tập laptop mới nhất từ Apple, Dell, Asus ROG và Lenovo ThinkPad. Trả góp 0% và bảo hành chính hãng toàn quốc.',
    ctaLabel: 'Khám phá Laptop',
    ctaHref: '/products?category=laptop',
    image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600',
  },
  {
    badge: 'Flagship Mới - Đặt Trước Hôm Nay',
    title: 'Điện Thoại Cao Cấp',
    highlight: 'Camera Đỉnh Cao',
    desc: 'iPhone 15 Pro Max, Galaxy S24 Ultra và Xiaomi 14 Ultra chính hãng. Quà tặng hấp dẫn khi đặt trước sớm.',
    ctaLabel: 'Xem điện thoại',
    ctaHref: '/products?category=phone',
    image: 'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=600',
  },
];

export default function HeroCarousel() {
  const [current, setCurrent] = useState(0);

  const next = useCallback(() => setCurrent((c) => (c + 1) % SLIDES.length), []);
  const prev = () => setCurrent((c) => (c - 1 + SLIDES.length) % SLIDES.length);

  useEffect(() => {
    const timer = setInterval(next, 6000);
    return () => clearInterval(timer);
  }, [next]);

  return (
    <section className="relative w-full h-[450px] md:h-[550px] overflow-hidden bg-gradient-to-tr from-card via-background to-primary/5 border-b border-border">
      <div className="absolute top-20 left-10 w-72 h-72 rounded-full bg-primary/5 blur-[100px]" />
      <div className="absolute bottom-10 right-20 w-80 h-80 rounded-full bg-primary/10 blur-[120px]" />

      {SLIDES.map((slide, index) => (
        <div
          key={index}
          className={`absolute inset-0 transition-opacity duration-700 ease-in-out ${
            index === current ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'
          }`}
          aria-hidden={index !== current}
        >
          <div className="container mx-auto h-full px-4 grid grid-cols-1 md:grid-cols-2 items-center gap-8 relative">
            <div className="space-y-6">
              <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/20">
                {slide.badge}
              </span>
              <h1 className="text-4xl md:text-6xl font-extrabold text-foreground leading-tight text-balance">
                {slide.title} <br />
                <span className="bg-gradient-to-r from-foreground to-primary bg-clip-text text-transparent">
                  {slide.highlight}
                </span>
              </h1>
              <p className="text-muted-foreground text-sm md:text-base max-w-md leading-relaxed text-pretty">
                {slide.desc}
              </p>
              <div className="flex gap-4">
                <Link
                  href={slide.ctaHref}
                  className="flex items-center gap-2 px-6 py-3 font-semibold rounded-full bg-primary hover:opacity-90 text-primary-foreground shadow-lg shadow-primary/15 active:scale-95 transition-all text-sm cursor-pointer"
                >
                  <span>{slide.ctaLabel}</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  href="/policy/warranty"
                  className="flex items-center gap-2 px-6 py-3 font-semibold rounded-full border border-border hover:border-muted-foreground/35 bg-card text-muted-foreground hover:text-foreground transition-all text-sm"
                >
                  Chính sách bảo hành
                </Link>
              </div>
            </div>

            <div className="hidden md:flex justify-center relative">
              <div className="w-[380px] h-[380px] rounded-3xl bg-card border border-border flex items-center justify-center p-8 relative overflow-hidden shadow-2xl group hover:border-primary/30 transition-all duration-500">
                <div className="absolute -top-10 -right-10 w-44 h-44 rounded-full bg-primary/5 blur-3xl" />
                <img
                  src={slide.image}
                  alt={slide.highlight}
                  className="w-full h-auto object-contain rounded-xl shadow-lg"
                />
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Nút điều hướng */}
      <button
        onClick={prev}
        aria-label="Slide trước"
        className="absolute left-4 top-1/2 -translate-y-1/2 z-20 p-2.5 rounded-full bg-card/80 border border-border text-muted-foreground hover:text-foreground hover:bg-card backdrop-blur-sm transition-all cursor-pointer"
      >
        <ChevronLeft className="w-5 h-5" />
      </button>
      <button
        onClick={next}
        aria-label="Slide tiếp theo"
        className="absolute right-4 top-1/2 -translate-y-1/2 z-20 p-2.5 rounded-full bg-card/80 border border-border text-muted-foreground hover:text-foreground hover:bg-card backdrop-blur-sm transition-all cursor-pointer"
      >
        <ChevronRight className="w-5 h-5" />
      </button>

      {/* Chấm chỉ báo slide */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 flex gap-2">
        {SLIDES.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrent(index)}
            aria-label={`Chuyển tới slide ${index + 1}`}
            className={`h-2 rounded-full transition-all cursor-pointer ${
              index === current ? 'w-6 bg-primary' : 'w-2 bg-muted-foreground/40 hover:bg-muted-foreground/70'
            }`}
          />
        ))}
      </div>
    </section>
  );
}
