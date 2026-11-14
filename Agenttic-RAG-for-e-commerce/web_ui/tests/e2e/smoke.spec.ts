import { test, expect } from '@playwright/test';
import * as path from 'path';

test.describe('E2E Smoke Test Suite', () => {
  test('1. Trang chủ tải thành công và hiển thị các khối nội dung', async ({ page }) => {
    await page.goto('/');

    // Đợi trang tải xong và kiểm tra tiêu đề trang
    await expect(page).toHaveTitle(/.*(4Customer|Cửa hàng|Công nghệ).*/i);

    // Chụp ảnh màn hình trang chủ phục vụ kiểm tra CUA / trực quan
    await page.screenshot({
      path: path.join(__dirname, 'screenshots', 'homepage.png'),
      fullPage: false,
    });
  });

  test('2. Chat widget mở được và hiển thị giao diện trò chuyện', async ({ page }) => {
    await page.goto('/');

    // Tìm nút mở Chat Widget nổi ở góc phải dưới
    const chatButton = page.locator('button[title="Trò chuyện với trợ lý AI"]');
    await expect(chatButton).toBeVisible();

    // Nhấp mở chat widget
    await chatButton.click();

    // Kiểm tra cửa sổ chat mở ra (có tiêu đề 'Trực tuyến tư vấn')
    const chatHeader = page.locator('text=Trực tuyến tư vấn');
    await expect(chatHeader).toBeVisible();

    // Chụp ảnh màn hình chat widget đã mở
    await page.screenshot({
      path: path.join(__dirname, 'screenshots', 'chat_opened.png'),
      fullPage: false,
    });
  });

  test('3. Backend FastAPI RAG Service hoạt động và kết nối đủ DB/Chroma', async ({ request }) => {
    const response = await request.get('http://127.0.0.1:8080/health');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.supabase_connected).toBe(true);
    expect(data.chroma_connected).toBe(true);
    expect(data.chroma_products_count).toBeGreaterThan(0);
  });
});
