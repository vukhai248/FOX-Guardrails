import { test, expect } from '@playwright/test';
import { createClient } from '@supabase/supabase-js';

test.describe('Gói QA2: Bổ sung các ca kiểm thử theo yêu cầu Claude Opus (Lần 12)', () => {

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
  const emailA = process.env.BENCH_CUSTOMER_EMAIL || '';
  const passA = process.env.BENCH_CUSTOMER_PASSWORD || '';

  const supabaseAnon = createClient(supabaseUrl, supabaseAnonKey, {
    auth: { persistSession: false, autoRefreshToken: false }
  });

  const supabaseAdmin = serviceRoleKey ? createClient(supabaseUrl, serviceRoleKey, {
    auth: { persistSession: false, autoRefreshToken: false }
  }) : supabaseAnon;

  let tokenA = '';
  let userAId = '';

  test.beforeAll(async () => {
    const { data: authA, error: errA } = await supabaseAnon.auth.signInWithPassword({
      email: emailA,
      password: passA
    });
    expect(errA).toBeNull();
    tokenA = authA?.session?.access_token || '';
    userAId = authA?.user?.id || '';
    expect(tokenA).toBeTruthy();
    expect(userAId).toBeTruthy();
  });

  test('QA2.1 (Mục 8): PATCH note trên đơn đã processing (542da29f...) -> Trả về 409 NOT_EDITABLE', async ({ request }) => {
    const res = await request.patch('http://localhost:3000/api/orders/542da29f-442d-48b8-a9e6-d192a7ece2fc/note', {
      headers: {
        'Authorization': `Bearer ${tokenA}`,
        'Content-Type': 'application/json'
      },
      data: {
        note: 'Thử cập nhật ghi chú trên đơn đã xử lý'
      }
    });

    // Kỳ vọng: HTTP 409 Conflict với code NOT_EDITABLE
    expect(res.status()).toBe(409);
    const body = await res.json();
    console.log('[QA2.1] Kết quả 409 NOT_EDITABLE:', body);
    expect(body.error?.code).toBe('NOT_EDITABLE');
  });

  test('QA2.2 (Mục 10): Hai request không có session_id -> Tự sinh 2 session_id độc lập trong chat_logs', async ({ request }) => {
    test.setTimeout(90000);

    // Request 1 không có session_id
    const res1 = await request.post('http://127.0.0.1:8080/chat', {
      headers: { 'Content-Type': 'application/json' },
      data: { message: 'Xin chào, tôi là khách ẩn danh 1' }
    });
    expect(res1.status()).toBe(200);
    const data1 = await res1.json();

    // Request 2 không có session_id
    const res2 = await request.post('http://127.0.0.1:8080/chat', {
      headers: { 'Content-Type': 'application/json' },
      data: { message: 'Xin chào, tôi là khách ẩn danh 2' }
    });
    expect(res2.status()).toBe(200);
    const data2 = await res2.json();

    console.log(`[QA2.2] Response 1 session: ${data1.session_id} vs Response 2 session: ${data2.session_id}`);
    expect(data1.session_id).toBeTruthy();
    expect(data2.session_id).toBeTruthy();
    expect(data1.session_id).not.toBe(data2.session_id);

    // Chờ 1.5 giây để async write_chat_turn ghi log vào DB
    await new Promise(r => setTimeout(r, 1500));

    // Truy vấn trực tiếp từ bảng chat_logs bằng admin client
    const { data: logs1, error: err1 } = await supabaseAdmin
      .from('chat_logs')
      .select('id, session_id, role, message, created_at')
      .eq('session_id', data1.session_id);

    const { data: logs2, error: err2 } = await supabaseAdmin
      .from('chat_logs')
      .select('id, session_id, role, message, created_at')
      .eq('session_id', data2.session_id);

    expect(err1).toBeNull();
    expect(err2).toBeNull();
    expect(logs1 && logs1.length > 0).toBeTruthy();
    expect(logs2 && logs2.length > 0).toBeTruthy();
    console.log(`[QA2.2 SUCCESS] chat_logs verification: session1=${data1.session_id} (${logs1!.length} records), session2=${data2.session_id} (${logs2!.length} records)`);
    expect(data1.session_id).not.toBe(data2.session_id);
  });

  test('QA2.3 (Mục 9 - Câu a): Chat tra cứu đơn hàng -> Gọi tool order_lookup', async ({ request }) => {
    test.setTimeout(90000);

    const res = await request.post('http://127.0.0.1:8080/chat', {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${tokenA}`
      },
      data: {
        message: 'Kiểm tra trạng thái đơn hàng 542da29f-442d-48b8-a9e6-d192a7ece2fc giúp tôi',
        session_id: 'qa2-session-order-lookup',
        user_token: tokenA
      }
    });

    expect(res.status()).toBe(200);
    const data = await res.json();
    console.log('[QA2.3] tool_used:', data.tool_used);
    console.log('[QA2.3] reply:', data.reply);
    expect(data.tool_used).toContain('order_lookup');
    expect(data.reply).toMatch(/542da29f|processing|paid|iPhone/i);
  });

  test('QA2.4 (Mục 9 - Câu b): Chat hỏi đánh giá sản phẩm -> Gọi tool product_reviews', async ({ request }) => {
    test.setTimeout(90000);

    const res = await request.post('http://127.0.0.1:8080/chat', {
      headers: { 'Content-Type': 'application/json' },
      data: {
        message: 'Mọi người đánh giá iPhone 15 Pro Max 256GB Titan Tự Nhiên thế nào?',
        session_id: 'qa2-session-product-reviews'
      }
    });

    expect(res.status()).toBe(200);
    const data = await res.json();
    console.log('[QA2.4] tool_used:', data.tool_used);
    console.log('[QA2.4] reply:', data.reply);
    expect(data.tool_used).toContain('product_reviews');
  });

  test('QA2.5 (Mục 9 - Câu c): Chat tạo ticket hỗ trợ -> Gọi tool create_support_ticket và ghi vào DB', async ({ request }) => {
    test.setTimeout(90000);

    const res = await request.post('http://127.0.0.1:8080/chat', {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${tokenA}`
      },
      data: {
        message: 'Tạo ticket hỗ trợ báo đơn 542da29f-442d-48b8-a9e6-d192a7ece2fc giao chậm giúp tôi',
        session_id: 'qa2-session-create-ticket-verified',
        user_token: tokenA
      }
    });

    expect(res.status()).toBe(200);
    const data = await res.json();
    console.log('[QA2.5] tool_used:', data.tool_used);
    console.log('[QA2.5] reply:', data.reply);
    expect(data.tool_used).toContain('create_support_ticket');

    // Kiểm tra trực tiếp trong database: phải có bản ghi support_tickets mới
    const { data: tickets, error: ticketError } = await supabaseAdmin
      .from('support_tickets')
      .select('id, customer_id, order_id, created_by, status, note, category')
      .eq('customer_id', userAId)
      .order('created_at', { ascending: false })
      .limit(1);

    expect(ticketError).toBeNull();
    expect(tickets && tickets.length > 0).toBeTruthy();
    const newTicket = tickets![0];
    console.log(`[QA2.5 SUCCESS] Đã tạo support ticket trong DB: ID=${newTicket.id}, created_by=${newTicket.created_by}, order_id=${newTicket.order_id}, category=${newTicket.category}`);
    expect(newTicket.created_by).toBe('agent');
    expect(newTicket.customer_id).toBe(userAId);
  });

  test('QA2.6 (Mục 7 & BUG-A-01): Đã mua sản phẩm 135935 chưa review -> Review 201 & Tái hiện lỗi review trùng', async ({ request }) => {
    // Sản phẩm 135935 (Laptop Lenovo Yoga Slim 7) nằm trong đơn cb83ab57-5f99-4951-9868-9fbb354c4630 của User A (cod_pending)
    const targetProductId = 135935;

    // 1. Gửi Review lần 1 cho sản phẩm 135935 kèm Unicode/emoji đặc biệt
    const reviewComment = 'Đánh giá Laptop Lenovo Yoga Slim 7 test QA2 🚀 Màn hình OLED cực nét 💯! (Unicode chuẩn test).';
    const reviewRes1 = await request.post('http://localhost:3000/api/reviews', {
      headers: {
        'Authorization': `Bearer ${tokenA}`,
        'Content-Type': 'application/json'
      },
      data: {
        product_id: targetProductId,
        rating: 5,
        comment: reviewComment
      }
    });

    // Kỳ vọng chặt chẽ: đúng 201 CREATED
    expect(reviewRes1.status()).toBe(201);
    const reviewData1 = await reviewRes1.json();
    console.log(`[QA2.6] Review lần 1 thành công: review_id=${reviewData1.review_id}`);
    expect(reviewData1.review_id).toBeTruthy();

    // Đọc lại từ database kiểm tra bảo toàn chuỗi Unicode từng ký tự
    const { data: dbReview } = await supabaseAdmin
      .from('reviews')
      .select('id, comment, rating, product_id, user_id')
      .eq('id', reviewData1.review_id)
      .single();

    expect(dbReview).toBeTruthy();
    expect(dbReview!.comment).toBe(reviewComment);
    expect(dbReview!.product_id).toBe(targetProductId);
    expect(dbReview!.user_id).toBe(userAId);
    console.log('[QA2.6] Database review codepoint match OK:', dbReview!.comment);

    // 2. TÁI HIỆN BUG-A-01: Gửi Review LẦN 2 cho cùng sản phẩm 135935 bằng cùng tài khoản
    const reviewRes2 = await request.post('http://localhost:3000/api/reviews', {
      headers: {
        'Authorization': `Bearer ${tokenA}`,
        'Content-Type': 'application/json'
      },
      data: {
        product_id: targetProductId,
        rating: 4,
        comment: 'Đánh giá lặp lần 2 cho Lenovo Yoga Slim 7 xem backend có chặn không'
      }
    });

    console.log(`[QA2.6 - BUG-A-01 Check] Status review lần 2: ${reviewRes2.status()}`);
    // Ghi nhận: Hiện tại backend chưa có check trùng nên sẽ trả về 201 Created (BUG-A-01)
    if (reviewRes2.status() === 201) {
      const reviewData2 = await reviewRes2.json();
      console.warn(`[BUG-A-01 CONFIRMED] Backend chấp nhận review trùng lặp! Review 2 ID=${reviewData2.review_id}`);
    } else {
      console.log(`[BUG-A-01] Backend đã chặn review trùng với status: ${reviewRes2.status()}`);
    }
  });

});
