import { test, expect } from '@playwright/test';

test.describe('Gói A6: Render an toàn trong Chat Widget (H11 - Allowlist, Homoglyph Punycode, Chặn Raw HTML, Guard Badge)', () => {

  test('A6.1: Render link nội bộ hợp lệ, chặn link ngoài không thuộc allowlist', async ({ page }) => {
    await page.goto('/');

    // 1. Mở Chat Widget
    const chatBtn = page.locator('button[title="Trò chuyện với trợ lý AI"]');
    await expect(chatBtn).toBeVisible({ timeout: 10000 });
    await chatBtn.click();

    // 2. Mock response chứa link nội bộ và link ngoài không an toàn
    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          reply: 'Xem [Chi tiết sản phẩm](/products/iphone-15) hoặc bấm vào [Trang ngoài lừa đảo](https://google.com/malicious).',
          guard: { action: 'allow' }
        })
      });
    });

    // 3. Gửi tin nhắn
    const inputField = page.locator('input[placeholder*="Hỏi về sản phẩm"]');
    await inputField.fill('Kiểm tra link');
    await inputField.press('Enter');

    // 4. Verify link nội bộ render thẻ a click được
    const internalLink = page.locator('a[href="/products/iphone-15"]');
    await expect(internalLink).toBeVisible({ timeout: 10000 });
    await expect(internalLink).toHaveText('Chi tiết sản phẩm');

    // 5. Verify link ngoài KHÔNG render thẻ a click được mà bị chuyển thành text gạch ngang kèm nhãn cảnh báo
    const externalLinkTag = page.locator('a[href="https://google.com/malicious"]');
    await expect(externalLinkTag).toHaveCount(0);

    const blockedLinkWarning = page.locator('text=(liên kết ngoài đã bị chặn)');
    await expect(blockedLinkWarning).toBeVisible();
    await expect(page.locator('text=Trang ngoài lừa đảo')).toBeVisible();

    // Chụp ảnh bằng chứng CUA
    await page.screenshot({ path: 'tests/e2e/screenshots/a6/a6_links_check.png' });
  });

  test('A6.2: Ẩn ảnh ngoài không thuộc allowlist, hiển thị ảnh trong allowlist', async ({ page }) => {
    await page.goto('/');

    const chatBtn = page.locator('button[title="Trò chuyện với trợ lý AI"]');
    await chatBtn.click();

    // Mock response chứa ảnh ngoài độc hại và ảnh Unsplash (trong allowlist)
    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          reply: 'Ảnh minh họa: ![Ảnh Unsplash hợp lệ](https://images.unsplash.com/photo-sample.jpg) và ![Pixel theo dõi](https://attacker-tracker.com/pixel.png)',
          guard: { action: 'allow' }
        })
      });
    });

    const inputField = page.locator('input[placeholder*="Hỏi về sản phẩm"]');
    await inputField.fill('Kiểm tra ảnh');
    await inputField.press('Enter');

    // 1. Verify ảnh ngoài không thuộc allowlist: KHÔNG render thẻ img tải về, chỉ hiển thị alt text
    const trackerImg = page.locator('img[src*="attacker-tracker.com"]');
    await expect(trackerImg).toHaveCount(0);

    const hiddenImgText = page.locator('text=[Ảnh ngoài đã bị ẩn: Pixel theo dõi]');
    await expect(hiddenImgText).toBeVisible({ timeout: 10000 });

    // 2. Verify ảnh trong allowlist (images.unsplash.com) render thẻ img trong hộp thoại chat
    const allowedImg = page.locator('img[alt="Ảnh Unsplash hợp lệ"]');
    await expect(allowedImg).toBeVisible({ timeout: 10000 });
    await expect(allowedImg).toHaveAttribute('src', 'https://images.unsplash.com/photo-sample.jpg');

    await page.screenshot({ path: 'tests/e2e/screenshots/a6/a6_images_check.png' });
  });

  test('A6.3: Phát hiện và chặn tấn công tên miền giả mạo Homoglyph (Punycode Attack)', async ({ page }) => {
    await page.goto('/');

    const chatBtn = page.locator('button[title="Trò chuyện với trợ lý AI"]');
    await chatBtn.click();

    // Chữ 'а' trong 'аmazon.com' là ký tự Cyrillic \u0430 (giả mạo chữ 'a' Latin)
    const cyrillicA = '\u0430';
    const homoglyphUrl = `https://${cyrillicA}mazon.com/deal`;

    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          reply: `Ưu đãi đặc biệt: [Amazon Khuyến Mãi](${homoglyphUrl}) truy cập ngay!`,
          guard: { action: 'allow' }
        })
      });
    });

    const inputField = page.locator('input[placeholder*="Hỏi về sản phẩm"]');
    await inputField.fill('Kiểm tra homoglyph');
    await inputField.press('Enter');

    // 1. Verify không có link nào được render
    const homoglyphLink = page.locator(`a[href*="mazon.com"]`);
    await expect(homoglyphLink).toHaveCount(0);

    // 2. Verify nhãn cảnh báo giả mạo tên miền xuất hiện
    const warningLabel = page.locator('text=(tên miền giả mạo đã bị chặn)');
    await expect(warningLabel).toBeVisible({ timeout: 10000 });

    await page.screenshot({ path: 'tests/e2e/screenshots/a6/a6_homoglyph_check.png' });
  });

  test('A6.4: Chặn parse HTML thô (Raw HTML Mitigation / XSS Prevention)', async ({ page }) => {
    await page.goto('/');

    const chatBtn = page.locator('button[title="Trò chuyện với trợ lý AI"]');
    await chatBtn.click();

    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          reply: 'Tin nhắn: <script id="xss-test">window.__xss_success = true;</script><div id="raw-html-tag">Thẻ HTML thô</div>',
          guard: { action: 'allow' }
        })
      });
    });

    const inputField = page.locator('input[placeholder*="Hỏi về sản phẩm"]');
    await inputField.fill('Kiểm tra raw html');
    await inputField.press('Enter');

    // Chờ tin nhắn bot hiển thị
    await page.waitForTimeout(1000);

    // 1. Script không được thực thi
    const isXssExecuted = await page.evaluate(() => (window as unknown as Record<string, boolean>).__xss_success);
    expect(isXssExecuted).toBeUndefined();

    // 2. Thẻ script không tồn tại dưới dạng DOM node
    const scriptElement = page.locator('#xss-test');
    await expect(scriptElement).toHaveCount(0);

    // 3. Thẻ div thô không được parse thành DOM node độc lập
    const divElement = page.locator('#raw-html-tag');
    await expect(divElement).toHaveCount(0);

    await page.screenshot({ path: 'tests/e2e/screenshots/a6/a6_raw_html_check.png' });
  });

  test('A6.5: Hiển thị nhãn Guard Action khi response có guard.action ≠ allow (H11)', async ({ page }) => {
    await page.goto('/');

    const chatBtn = page.locator('button[title="Trò chuyện với trợ lý AI"]');
    await chatBtn.click();

    // 1. Thử nghiệm guard.action = 'block'
    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          reply: 'Nội dung phản hồi này đã bị can thiệp và làm sạch bởi hệ thống bảo vệ FOX-Guardrails.',
          guard: {
            action: 'block',
            decision_id: 'dec_guard_98765',
            flags: ['PII_LEAK_PREVENTION', 'MALICIOUS_PROMPT']
          }
        })
      });
    });

    const inputField = page.locator('input[placeholder*="Hỏi về sản phẩm"]');
    await inputField.fill('Hỏi câu hỏi nhạy cảm');
    await inputField.press('Enter');

    // Verify badge block xuất hiện đúng định dạng và có decision_id
    const blockBadge = page.locator('[data-testid="guard-badge-block"]');
    await expect(blockBadge).toBeVisible({ timeout: 10000 });
    await expect(blockBadge).toContainText('🛡️ Đã can thiệp bảo vệ: Nội dung bị chặn (#dec_guard_98765)');

    // Chụp ảnh CUA chứng minh badge Guard Action
    await page.screenshot({ path: 'tests/e2e/screenshots/a6/a6_guard_badge_block.png' });

    // 2. Thử nghiệm guard.action = 'flag'
    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          reply: 'Phản hồi này được gắn cờ cảnh báo rủi ro.',
          guard: {
            action: 'flag',
            decision_id: 'dec_flag_12345'
          }
        })
      });
    });

    await inputField.fill('Hỏi câu hỏi cần cảnh báo');
    await inputField.press('Enter');

    const flagBadge = page.locator('[data-testid="guard-badge-flag"]');
    await expect(flagBadge).toBeVisible({ timeout: 10000 });
    await expect(flagBadge).toContainText('⚠️ Đang kiểm duyệt bảo vệ (#dec_flag_12345)');

    await page.screenshot({ path: 'tests/e2e/screenshots/a6/a6_guard_badge_flag.png' });
  });

  test('A6.6: Chặn triệt để các vector Bypass Allowlist (F1 - Protocol-relative, Backslash, Schemes nguy hiểm)', async ({ page }) => {
    await page.goto('/');

    const chatBtn = page.locator('button[title="Trò chuyện với trợ lý AI"]');
    await chatBtn.click();

    // Mock response chứa toàn bộ các vector tấn công bypass allowlist
    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          reply: [
            'Kiểm tra các vector bypass:',
            '1. [ProtoRelative](//evil-shop.example/a)',
            '2. [SlashBackslash](/\\evil-shop.example)',
            '3. [Backslash](\\evil-shop.example)',
            '4. [JsScheme](javascript:alert(1))',
            '5. [DataScheme](data:text/html,malicious)',
            '6. [UpperCaseHost](HTTPS://EVIL-SHOP.EXAMPLE)',
            'Ảnh bypass: ![Ảnh ProtocolRelative](//attacker-tracker.com/pixel.png)'
          ].join('\n\n'),
          guard: { action: 'allow' }
        })
      });
    });

    const inputField = page.locator('input[placeholder*="Hỏi về sản phẩm"]');
    await inputField.fill('Kiểm tra bypass vectors');
    await inputField.press('Enter');

    // Chờ tin nhắn hiển thị
    await page.waitForTimeout(1000);

    // 1. Xác minh không có thẻ <a> nào trỏ tới domain độc hại evil-shop.example (dùng cờ i để không phân biệt hoa thường, bắt cả HTTPS://EVIL-SHOP.EXAMPLE)
    const evilLinks = page.locator('a[href*="evil-shop.example" i]');
    await expect(evilLinks).toHaveCount(0);

    // 2. Không có thẻ <a> nào chứa javascript: hoặc data:
    const jsLinks = page.locator('a[href^="javascript:"], a[href^="data:"]');
    await expect(jsLinks).toHaveCount(0);

    // 3. Ảnh protocol-relative ngoài allowlist phải bị ẩn (không render thẻ <img>)
    const evilImg = page.locator('img[src*="attacker-tracker.com"]');
    await expect(evilImg).toHaveCount(0);

    // 4. Có text ẩn ảnh ngoài
    const hiddenImgText = page.locator('text=[Ảnh ngoài đã bị ẩn: Ảnh ProtocolRelative]');
    await expect(hiddenImgText).toBeVisible({ timeout: 10000 });

    // Chụp ảnh bằng chứng CUA kiểm tra bypass vectors
    await page.screenshot({ path: 'tests/e2e/screenshots/a6/a6_bypass_vectors_blocked.png' });
  });

});
