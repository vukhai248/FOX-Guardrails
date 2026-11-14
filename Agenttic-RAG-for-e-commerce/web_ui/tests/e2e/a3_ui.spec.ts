import { test, expect } from '@playwright/test';

test.describe('Gói A3-UI: Customer Data Surface & Order Workflow', () => {

  test('A3.1: Form Checkout tách trường, gọi POST /api/orders và redirect checkout-success không lộ PII', async ({ page }) => {
    // 1. Chuẩn bị giỏ hàng với 1 sản phẩm vào đúng key của Zustand useCart & thông tin địa chỉ tách trường đã lưu
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('e-commerce-cart-storage', JSON.stringify({
        state: {
          items: [
            {
              id: '1',
              name: 'iPhone 15 Pro Max 256GB',
              price: 29990000,
              quantity: 1,
              image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300',
              category: 'Điện thoại',
              brand: 'Apple'
            }
          ]
        },
        version: 0
      }));
      localStorage.setItem('mock_user_logged', 'true');
      localStorage.setItem('saved_full_name', 'Nguyễn Văn Test');
      localStorage.setItem('saved_phone', '0987654321');
      localStorage.setItem('saved_province', 'Thành phố Hà Nội');
      localStorage.setItem('saved_district', 'Quận Ba Đình');
      localStorage.setItem('saved_ward', 'Phường Phúc Xá');
      localStorage.setItem('saved_detail_address', 'Số 123 Phố Đội Cấn');
    });

    // 2. Mock API POST /api/orders theo Hợp đồng API §3
    let orderRequestBody: Record<string, unknown> | null = null;
    await page.route('**/api/orders', async (route) => {
      if (route.request().method() === 'POST') {
        orderRequestBody = JSON.parse(route.request().postData() || '{}');
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            order_id: 'ord-test-uuid-a3-001',
            status: 'pending',
            payment_status: 'cod_pending',
            total: 29990000
          })
        });
      } else {
        await route.continue();
      }
    });

    // 3. Mock API GET /api/orders/ord-test-uuid-a3-001
    await page.route('**/api/orders/ord-test-uuid-a3-001', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          order_id: 'ord-test-uuid-a3-001',
          status: 'pending',
          payment_status: 'cod_pending',
          payment_method: 'cod',
          total: 29990000,
          recipient_name: 'Nguyễn Văn Test',
          recipient_phone: '0987654321',
          address_line: 'Số 123 Phố Đội Cấn, Quận Ba Đình',
          ward: 'Phường Phúc Xá',
          province: 'Thành phố Hà Nội',
          note: 'Giao giờ hành chính, gọi trước 15 phút',
          created_at: new Date().toISOString(),
          items: [
            {
              id: 1,
              name: 'iPhone 15 Pro Max 256GB',
              price: 29990000,
              quantity: 1,
              image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300'
            }
          ]
        })
      });
    });

    // 4. Điều hướng vào trang /checkout
    await page.goto('/checkout');
    await expect(page.locator('h1')).toContainText('Thanh toán đơn hàng', { timeout: 10000 });

    // Khắc phục F6 (Root Cause của hiện tượng flake test A3.1):
    // Trang /checkout nạp file địa chính bất đồng bộ `/data/vietnam-addresses.json` rồi mới phục hồi
    // Tỉnh/Quận/Phường từ localStorage vào state. Khi 6 workers chạy song song tải CPU cao, nếu click submit
    // trước khi fetch giải quyết xong, validation form chặn lại và không kích hoạt POST /api/orders.
    // Chờ 3 dropdown hiển thị đầy đủ tên địa chính trước khi tiếp tục:
    await expect(page.locator('button:has-text("Thành phố Hà Nội")')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('button:has-text("Quận Ba Đình")')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('button:has-text("Phường Phúc Xá")')).toBeVisible({ timeout: 10000 });

    // 5. Điền thêm ghi chú giao hàng (≤ 500 ký tự)
    const noteInput = page.locator('input[placeholder*="Ví dụ: Giao hàng giờ hành chính"]');
    await noteInput.fill('Giao giờ hành chính, gọi trước 15 phút');

    // 6. Chọn phương thức COD
    await page.locator('text=Thu tiền khi nhận hàng (COD)').click();

    // 7. Bấm đặt hàng
    await page.locator('button:has-text("Xác nhận đặt hàng")').click();

    // 8. Chờ chuyển hướng tới /checkout-success
    // Khắc phục F6 (flake test do cold compilation): Khi chạy cả bộ test ngay sau `npm run build`,
    // Next.js Turbopack dev server phải biên dịch on-demand route `/checkout-success` lần đầu tiên,
    // trong khi nhiều workers chạy song song gây nghẽn CPU. Tăng timeout lên 15000ms để đảm bảo ổn định.
    await page.waitForURL('**/checkout-success?order_id=ord-test-uuid-a3-001*', { timeout: 15000 });

    // 9. Xác minh URL KHÔNG chứa PII (không chứa SĐT, tên, địa chỉ)
    const currentUrl = page.url();
    expect(currentUrl).not.toContain('0987654321');
    expect(currentUrl).not.toContain('Nguy%E1%BB%85n');
    expect(currentUrl).not.toContain('Landmark');
    expect(currentUrl).toContain('order_id=ord-test-uuid-a3-001');

    // 10. Xác minh nội dung trang checkout-success hiển thị đúng dữ liệu từ GET /api/orders/{id}
    await expect(page.locator('text=ord-test-uuid-a3-001')).toBeVisible();
    await expect(page.locator('text=Nguyễn Văn Test')).toBeVisible();
    await expect(page.locator('text=0987654321')).toBeVisible();
    await expect(page.locator('text=Giao giờ hành chính, gọi trước 15 phút')).toBeVisible();

    // 11. Xác minh payload đã gửi lên POST /api/orders đúng cấu trúc hợp đồng API §3
    expect(orderRequestBody).not.toBeNull();
    expect(orderRequestBody!.recipient_name).toBe('Nguyễn Văn Test');
    expect(orderRequestBody!.recipient_phone).toBe('0987654321');
    expect(orderRequestBody!.province).toBe('Thành phố Hà Nội');
    expect(orderRequestBody!.ward).toBe('Phường Phúc Xá');
    expect(orderRequestBody!.note).toBe('Giao giờ hành chính, gọi trước 15 phút');
    expect(orderRequestBody!.payment_method).toBe('cod');

    // Chụp ảnh màn hình CUA nghiệm thu
    await page.screenshot({ path: 'tests/e2e/screenshots/a3/checkout_success_cod.png', fullPage: true });
  });

  test('A3.2: Form Review sản phẩm - Xử lý 403 NOT_PURCHASED và thành công 201', async ({ page }) => {
    // 1. Mock REST Supabase cho products/1 và reviews
    await page.route('**/rest/v1/products*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          name: 'iPhone 15 Pro Max 256GB',
          price: 29990000,
          stock: 15,
          category: 'Điện thoại',
          brand: 'Apple',
          images: ['https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600'],
          specs: {
            cpu: 'Apple A17 Pro',
            ram: '8GB',
            storage: '256GB'
          }
        })
      });
    });

    await page.route('**/rest/v1/reviews*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 101,
            product_id: 1,
            user_name: 'Trần Bình',
            rating: 5,
            comment: 'Máy đẹp, chụp ảnh siêu nét!',
            created_at: '2026-11-01'
          }
        ])
      });
    });

    // 2. Giả lập đã đăng nhập
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('mock_user_logged', 'true');
    });

    // 3. Điều hướng vào trang chi tiết sản phẩm 1
    await page.goto('/products/1');
    await expect(page.locator('text=Đánh giá từ khách hàng')).toBeVisible({ timeout: 10000 });

    // 4. Điền nhận xét có ký tự đặc biệt / emoji / zero-width
    const testComment = 'Sản phẩm chất lượng tuyệt vời! Đóng gói cẩn thận 🚀 \u200B\u200C Test Unicode Tags & Emoji.';
    const commentBox = page.locator('#review-comment');
    await commentBox.fill(testComment);

    // 5. Click chọn 4 sao
    await page.locator('button[aria-label="4 sao"]').click();

    // 6. Giả lập trường hợp CHƯA MUA: POST /api/reviews trả về 403 NOT_PURCHASED
    let reviewPayload: Record<string, unknown> | null = null;
    await page.route('**/api/reviews', async (route) => {
      reviewPayload = JSON.parse(route.request().postData() || '{}');
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({
          error: {
            code: 'NOT_PURCHASED',
            message: 'Chỉ khách hàng đã mua sản phẩm này mới có thể gửi đánh giá.'
          }
        })
      });
    });

    await page.locator('button:has-text("Gửi đánh giá")').click();

    // Xác minh cảnh báo 403 xuất hiện rõ ràng trên giao diện
    await expect(page.locator('text=Chỉ khách hàng đã mua sản phẩm này mới có thể gửi đánh giá.')).toBeVisible();
    await page.screenshot({ path: 'tests/e2e/screenshots/a3/review_not_purchased_403.png' });

    // 7. Giả lập trường hợp ĐÃ MUA: POST /api/reviews trả về 201
    await page.route('**/api/reviews', async (route) => {
      reviewPayload = JSON.parse(route.request().postData() || '{}');
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          review_id: 8888,
          message: 'Đánh giá thành công'
        })
      });
    });

    await page.locator('button:has-text("Gửi đánh giá")').click();

    // Xác minh thông báo thành công và review mới xuất hiện trên UI
    await expect(page.locator('text=Đánh giá của bạn đã được ghi nhận thành công!')).toBeVisible();
    await expect(page.locator(`text=${testComment}`)).toBeVisible();

    // Xác minh payload đúng hợp đồng API §3
    expect(reviewPayload).not.toBeNull();
    expect(reviewPayload!.product_id).toBe(1);
    expect(reviewPayload!.rating).toBe(4);
    expect(reviewPayload!.comment).toBe(testComment);

    await page.screenshot({ path: 'tests/e2e/screenshots/a3/review_success_201.png' });
  });

  test('A3.3: Trang /account - Sửa ghi chú đơn hàng pending gọi PATCH /api/orders/{id}/note', async ({ page }) => {
    // 1. Thiết lập trạng thái mock user và mock_orders đã đăng nhập
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('mock_user_logged', 'true');
      localStorage.setItem('mock_orders', JSON.stringify([
        {
          id: 'ord-pending-test-01',
          status: 'pending',
          payment_status: 'cod_pending',
          total: 15500000,
          shipping_address: '123 Đường Số 1, Quận 1, TP. Hồ Chí Minh',
          note: 'Ghi chú ban đầu: Giao buổi sáng',
          created_at: new Date().toISOString(),
          items: [
            {
              id: 10,
              name: 'Laptop ASUS Zenbook 14 OLED',
              price: 15500000,
              quantity: 1,
              image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=300'
            }
          ]
        },
        {
          id: 'ord-delivered-test-02',
          status: 'delivered',
          payment_status: 'paid',
          total: 2500000,
          shipping_address: '456 Lê Lợi, Quận 1, TP. Hồ Chí Minh',
          note: 'Đơn này đã giao thành công',
          created_at: new Date().toISOString(),
          items: [
            {
              id: 11,
              name: 'Tai nghe Sony WH-1000XM5',
              price: 2500000,
              quantity: 1,
              image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300'
            }
          ]
        }
      ]));
    });

    await page.goto('/account');
    await expect(page.locator('text=Lịch sử đơn hàng')).toBeVisible({ timeout: 10000 });

    // 2. Xác minh nút "Sửa ghi chú" CHỈ xuất hiện đúng 1 lần (ở đơn pending, không có ở đơn delivered)
    const editBtn = page.locator('button:has-text("Sửa ghi chú")');
    await expect(editBtn).toHaveCount(1);
    await expect(editBtn).toBeVisible();

    // 3. Click nút "Sửa ghi chú"
    await editBtn.click();

    const noteTextarea = page.locator('textarea[placeholder*="Nhập ghi chú giao hàng mới"]');
    await expect(noteTextarea).toBeVisible();

    // 4. Thử trường hợp thành công (PATCH 200)
    let patchPayload: Record<string, unknown> | null = null;
    await page.route('**/api/orders/ord-pending-test-01/note', async (route) => {
      patchPayload = JSON.parse(route.request().postData() || '{}');
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          order_id: 'ord-pending-test-01',
          note: 'Ghi chú mới: Gọi trước 30 phút, để tại quầy lễ tân 🏢'
        })
      });
    });

    await noteTextarea.fill('Ghi chú mới: Gọi trước 30 phút, để tại quầy lễ tân 🏢');
    await page.locator('button:has-text("Lưu")').click();

    // Xác minh thông báo cập nhật thành công và ghi chú mới xuất hiện
    await expect(page.locator('text=Cập nhật ghi chú giao hàng thành công!')).toBeVisible();
    await expect(page.locator('text=Ghi chú mới: Gọi trước 30 phút, để tại quầy lễ tân 🏢')).toBeVisible();
    expect(patchPayload!.note).toBe('Ghi chú mới: Gọi trước 30 phút, để tại quầy lễ tân 🏢');

    await page.screenshot({ path: 'tests/e2e/screenshots/a3/account_edit_note_success.png' });

    // 5. Thử trường hợp lỗi 409 NOT_EDITABLE khi đơn không còn pending
    await editBtn.click();
    await page.route('**/api/orders/ord-pending-test-01/note', async (route) => {
      await route.fulfill({
        status: 409,
        contentType: 'application/json',
        body: JSON.stringify({
          error: {
            code: 'NOT_EDITABLE',
            message: 'Không thể sửa ghi chú vì đơn hàng không còn ở trạng thái chờ duyệt (pending).'
          }
        })
      });
    });

    await page.locator('button:has-text("Lưu")').click();
    await expect(page.locator('text=Không thể sửa ghi chú vì đơn hàng không còn ở trạng thái chờ duyệt (pending).')).toBeVisible();

    await page.screenshot({ path: 'tests/e2e/screenshots/a3/account_edit_note_409.png' });
  });

});
