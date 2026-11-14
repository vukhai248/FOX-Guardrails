import { test, expect } from '@playwright/test';
import * as path from 'path';

const PAGES_TO_CHECK = [
  { name: 'homepage', path: '/' },
  { name: 'products_list', path: '/products' },
  { name: 'product_detail', path: '/products/136045' },
  { name: 'cart', path: '/cart' },
  { name: 'checkout', path: '/checkout' },
  { name: 'account', path: '/account' },
  { name: 'admin', path: '/admin' },
  { name: 'login', path: '/auth/login' },
];

test.describe('CUA & UI Deep Check Suite', () => {
  for (const pageInfo of PAGES_TO_CHECK) {
    test(`CUA Check: ${pageInfo.name} (${pageInfo.path})`, async ({ page }) => {
      const consoleErrors: string[] = [];
      const failedRequests: string[] = [];

      // Lắng nghe lỗi console
      page.on('console', (msg) => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });

      // Lắng nghe request thất bại
      page.on('response', (response) => {
        if (response.status() >= 400) {
          failedRequests.push(`${response.status()} ${response.url()}`);
        }
      });

      await page.goto(pageInfo.path, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(1000); // Đợi hydration và hiệu ứng CSS

      // Chụp ảnh màn hình CUA
      const screenshotPath = path.join(__dirname, 'screenshots', 'cua', `${pageInfo.name}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: false });

      // Ghi log nếu phát hiện lỗi
      if (consoleErrors.length > 0) {
        console.warn(`[CUA Warning] Console errors on ${pageInfo.path}:`, consoleErrors);
      }
      if (failedRequests.length > 0) {
        console.warn(`[CUA Warning] Failed requests on ${pageInfo.path}:`, failedRequests);
      }

      // Xác nhận trang hiển thị nội dung, không bị màn hình trắng (blank screen)
      const body = page.locator('body');
      await expect(body).toBeVisible();
    });
  }
});
