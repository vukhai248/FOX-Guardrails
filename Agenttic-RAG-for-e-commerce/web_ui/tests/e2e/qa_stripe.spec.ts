import { test, expect } from '@playwright/test';
import { createClient } from '@supabase/supabase-js';

test.describe('Checklist Mục 3: Thanh toán Stripe Test Mode (Thẻ 4242...) & Webhook Cập nhật Tồn kho', () => {

  test('E2E Stripe Live Test: Tạo đơn -> Thanh toán thẻ 4242 -> Webhook delivered -> Đơn chuyển paid & Giảm tồn kho đúng 1 lần', async ({ page, request }) => {
    test.setTimeout(120000); // 2 phút cho toàn bộ luồng Stripe Checkout & Webhook

    // 1. Kiểm tra cấu hình môi trường
    const email = process.env.BENCH_CUSTOMER_EMAIL;
    const password = process.env.BENCH_CUSTOMER_PASSWORD;
    expect(email, 'Thiếu BENCH_CUSTOMER_EMAIL trong .env.bench').toBeTruthy();
    expect(password, 'Thiếu BENCH_CUSTOMER_PASSWORD trong .env.bench').toBeTruthy();

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
    expect(supabaseUrl, 'Thiếu NEXT_PUBLIC_SUPABASE_URL').toBeTruthy();
    expect(supabaseAnonKey, 'Thiếu NEXT_PUBLIC_SUPABASE_ANON_KEY').toBeTruthy();

    const supabase = createClient(supabaseUrl, supabaseAnonKey, {
      auth: { persistSession: false, autoRefreshToken: false }
    });

    // 2. Đăng nhập tài khoản bench_customer_a
    const { data: authData, error: loginError } = await supabase.auth.signInWithPassword({
      email: email!,
      password: password!,
    });
    expect(loginError, `Đăng nhập bench_customer thất bại: ${loginError?.message}`).toBeNull();
    const accessToken = authData!.session!.access_token;
    const userId = authData!.user!.id;
    console.log(`[QA Stripe] Đăng nhập thành công với user: ${userId}`);

    // 3. Lấy 1 sản phẩm có tồn kho > 0 từ database
    const { data: products, error: productError } = await supabase
      .from('products')
      .select('id, name, price, stock')
      .gt('stock', 0)
      .order('id')
      .limit(1);

    expect(productError, `Lỗi đọc sản phẩm: ${productError?.message}`).toBeNull();
    expect(products && products.length > 0, 'Không tìm thấy sản phẩm có tồn kho > 0').toBeTruthy();
    const product = products![0];
    const initialStock = product.stock;
    console.log(`[QA Stripe] Sản phẩm test: ID=${product.id}, Tên="${product.name}", Giá=${product.price}, Tồn kho ban đầu=${initialStock}`);

    // 4. Gọi POST /api/orders tạo đơn hàng Stripe
    const createOrderRes = await request.post('http://localhost:3000/api/orders', {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      data: {
        items: [{ product_id: product.id, quantity: 1 }],
        payment_method: 'stripe',
        recipient_name: 'Bench Customer A',
        recipient_phone: '0987654321',
        address_line: '123 Đường Test',
        ward: 'Phường Phúc Xá',
        province: 'Thành phố Hà Nội',
        note: 'Đơn QA tự động thanh toán thẻ Stripe test 4242'
      }
    });

    expect(createOrderRes.status(), `Tạo đơn Stripe thất bại: ${await createOrderRes.text()}`).toBe(201);
    const orderData = await createOrderRes.json();
    const orderId = orderData.order_id;
    const checkoutUrl = orderData.checkout_url;
    console.log(`[QA Stripe] Đơn hàng đã tạo: order_id=${orderId}, checkout_url=${checkoutUrl}`);
    expect(orderId).toBeTruthy();
    expect(checkoutUrl).toBeTruthy();
    expect(orderData.status).toBe('pending');
    expect(orderData.payment_status).toBe('unpaid');

    // 5. Mở trang Stripe Checkout bằng Playwright Page
    console.log(`[QA Stripe] Điều hướng tới trang Stripe Checkout...`);
    await page.goto(checkoutUrl, { waitUntil: 'domcontentloaded' });

    // Đợi form thanh toán của Stripe tải xong
    await page.waitForTimeout(2000);

    // Kiểm tra và điền email nếu trường email hiển thị và trống
    const emailInput = page.locator('input#email, input[name="email"]');
    if (await emailInput.isVisible({ timeout: 3000 }).catch(() => false)) {
      const currentEmail = await emailInput.inputValue();
      if (!currentEmail) {
        await emailInput.fill(email!);
      }
    }

    // Điền số thẻ test Stripe 4242...
    const cardInput = page.locator('input#cardNumber, input[name="cardNumber"]');
    await cardInput.waitFor({ state: 'visible', timeout: 15000 });
    // Nhập chậm để tránh Stripe mask bị mất số
    await cardInput.pressSequentially('4242424242424242', { delay: 50 });

    // Điền ngày hết hạn trong tương lai
    const expiryInput = page.locator('input#cardExpiry, input[name="cardExpiry"]');
    await expiryInput.waitFor({ state: 'visible', timeout: 5000 });
    await expiryInput.pressSequentially('1234', { delay: 50 });

    // Điền CVC
    const cvcInput = page.locator('input#cardCvc, input[name="cardCvc"]');
    await cvcInput.waitFor({ state: 'visible', timeout: 5000 });
    await cvcInput.pressSequentially('123', { delay: 50 });

    // Điền Tên chủ thẻ (nếu có trường billingName)
    const nameInput = page.locator('input#billingName, input[name="billingName"]');
    if (await nameInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      await nameInput.fill('Bench Customer A');
    }

    console.log(`[QA Stripe] Đã điền xong thông tin thẻ test 4242... Bấm nút thanh toán...`);

    // Bấm nút Pay / Thanh toán
    const submitBtn = page.locator('button[type="submit"], button[data-testid="hosted-payment-submit-button"]');
    await submitBtn.waitFor({ state: 'visible', timeout: 5000 });
    await submitBtn.click();

    // 6. Chờ Stripe xử lý và chuyển hướng về /checkout-success
    console.log(`[QA Stripe] Đang chờ chuyển hướng về /checkout-success...`);
    await page.waitForURL((url) => url.pathname.includes('/checkout-success'), { timeout: 30000 });
    console.log(`[QA Stripe] Đã chuyển hướng thành công tới: ${page.url()}`);
    expect(page.url()).toContain(`order_id=${orderId}`);

    // 7. Polling kiểm tra trạng thái đơn hàng qua API GET /api/orders/{id}
    console.log(`[QA Stripe] Đang chờ Webhook Stripe CLI cập nhật trạng thái đơn sang 'paid'...`);
    let isPaid = false;
    let attempts = 0;
    while (!isPaid && attempts < 15) {
      await page.waitForTimeout(2000);
      attempts++;
      const detailRes = await request.get(`http://localhost:3000/api/orders/${orderId}`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
      if (detailRes.status() === 200) {
        const detail = await detailRes.json();
        console.log(`[QA Stripe] Lần kiểm tra ${attempts}: payment_status=${detail.payment_status}, status=${detail.status}`);
        if (detail.payment_status === 'paid') {
          isPaid = true;
          break;
        }
      }
    }

    expect(isPaid, 'Đơn hàng chưa chuyển sang trạng thái paid sau 30 giây chờ webhook').toBeTruthy();

    // 8. Xác minh cơ sở dữ liệu Supabase: Tồn kho của sản phẩm phải GIẢM ĐÚNG 1 ĐƠN VỊ
    const { data: updatedProducts, error: checkError } = await supabase
      .from('products')
      .select('stock')
      .eq('id', product.id);

    expect(checkError).toBeNull();
    const finalStock = updatedProducts![0].stock;
    console.log(`[QA Stripe] Tồn kho ban đầu: ${initialStock} -> Tồn kho sau khi thanh toán: ${finalStock}`);
    expect(finalStock).toBe(initialStock - 1);

    // 9. Xác minh đơn hàng trong database Supabase
    // Kiểm tra đơn hàng thuộc bench_customer_a
    const { data: dbOrders, error: orderCheckError } = await supabase
      .from('orders')
      .select('id, payment_status, status, total')
      .eq('id', orderId);

    expect(orderCheckError).toBeNull();
    expect(dbOrders && dbOrders.length === 1).toBeTruthy();
    expect(dbOrders![0].payment_status).toBe('paid');

    console.log(`[QA Stripe SUCCESS] HOÀN TẤT THÀNH CÔNG KIỂM THỬ MỤC 3! Order ID=${orderId}`);
  });
});
