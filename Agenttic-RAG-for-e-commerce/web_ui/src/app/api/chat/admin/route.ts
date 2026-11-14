import { NextResponse } from 'next/server';
import { requireRole } from '@/lib/server/auth';

export async function POST(request: Request) {
  // 1. Kiểm tra xác thực và phân quyền: chỉ admin và staff
  const auth = await requireRole(request, ['admin', 'staff']);
  if (auth.errorResponse) {
    return auth.errorResponse;
  }

  // 2. Khi cờ mock tắt (mặc định), trả về 503 ADMIN_ASSISTANT_UNAVAILABLE
  const allowMockAdmin = process.env.NEXT_PUBLIC_ALLOW_MOCK_ADMIN === 'true';
  if (!allowMockAdmin) {
    return NextResponse.json(
      {
        error: {
          code: 'ADMIN_ASSISTANT_UNAVAILABLE',
          message: 'Trợ lý admin chưa được kết nối.',
        },
      },
      { status: 503 }
    );
  }

  try {
    const body = await request.json();
    const { message, session_id } = body;

    if (!message) {
      return NextResponse.json(
        { error: 'Tin nhắn không được để trống' },
        { status: 400 }
      );
    }

    const msgLower = message.toLowerCase();
    let reply = '';
    let tool_used = '';
    let sources: string[] = [];

    // Giả lập logic định tuyến tool của Trợ lý AI Admin (RAG nội bộ)
    if (msgLower.includes('doanh thu') || msgLower.includes('thống kê') || msgLower.includes('doanh số')) {
      tool_used = 'admin_analytics_tool';
      reply = `Báo cáo doanh số và thống kê hệ thống (dữ liệu cập nhật real-time):
- **Doanh thu thực tế (đã thu tiền)**: Đang được tính từ các đơn hàng có trạng thái không phải *Chờ xử lý* (Pending) hoặc *Đã hủy* (Cancelled).
- **Tỷ lệ hoàn thành đơn hàng**: 100% đối với các đơn đã duyệt và hoàn tất.
- **Tồn kho cảnh báo**: Đang có 0 sản phẩm dưới ngưỡng an toàn (<= 5 chiếc).

Bạn có thể cấu hình thêm các chỉ số phân tích sâu hơn trong phần RAG service Python sau này.`;
      sources = ['supabase_orders_aggregation'];
    } 
    else if (msgLower.includes('chính sách') || msgLower.includes('hoàn tiền') || msgLower.includes('bảo hành')) {
      tool_used = 'policy_rag_tool';
      reply = `Tổng hợp quy định nội bộ phục vụ tư vấn viên (Admin Assistant Mode):
1. **Chính sách hoàn tiền (Đổi trả 1 đổi 1)**: Hỗ trợ đổi mới trong 30 ngày (laptop/điện thoại) hoặc 15 ngày (phụ kiện). Hoàn tiền chuyển khoản mất 3-5 ngày làm việc.
2. **Quy trình xử lý hoàn tiền của Staff**:
   - Bước 1: Tiếp nhận và tạo ticket trạng thái *open*.
   - Bước 2: Kiểm tra thiết bị ngoại quan, tem niêm phong.
   - Bước 3: Nhân viên kỹ thuật duyệt lỗi sản xuất $\rightarrow$ Chuyển trạng thái sang *resolved* và yêu cầu kế toán hoàn tiền.

*Lưu ý*: Đối với các ticket có mức độ rủi ro cao (khách hàng khiếu nại quá 3 lần, đe dọa...), bắt buộc phải bàn giao cho Quản lý (Manager) xử lý.`;
      sources = ['internal_refund_sop.md'];
    }
    else {
      reply = `Xin chào Admin! Tôi là Trợ lý AI Nội bộ (Admin Assistant) hỗ trợ quản trị hệ thống. 
Hiện tại tôi được tách riêng để bạn có thể tích hợp API RAG Service của Python phục vụ quản trị và xử lý nghiệp vụ nội bộ sau này.

Tôi có thể giả lập hỗ trợ bạn các nội dung:
1. 📊 **Tra cứu thống kê doanh thu / đơn hàng** (Ví dụ: "thống kê doanh thu hôm nay").
2. 📖 **Tra cứu quy trình xử lý nội bộ / SOP** (Ví dụ: "chính sách hoàn tiền").
3. 🛠️ **Soạn nháp nội dung trả lời ticket hỗ trợ**.

Admin cần tôi hỗ trợ thông tin gì?`;
    }

    return NextResponse.json({
      reply,
      tool_used,
      sources,
      session_id: session_id || 'mock-admin-session-id',
    });
  } catch (error) {
    console.error('Lỗi API Admin Chat:', error);
    return NextResponse.json(
      { error: 'Lỗi máy chủ nội bộ' },
      { status: 500 }
    );
  }
}
