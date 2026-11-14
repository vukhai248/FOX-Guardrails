import { NextResponse } from 'next/server';
import { requireRole, supabaseAdmin } from '@/lib/server/auth';

// 1. GET API: Lấy danh sách toàn bộ đơn hàng (hoặc lọc theo userId)
export async function GET(request: Request) {
  try {
    const authResult = await requireRole(request, ['admin', 'staff']);
    if (authResult.errorResponse) {
      return authResult.errorResponse;
    }

    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');

    let query = supabaseAdmin
      .from('orders')
      .select('*')
      .order('created_at', { ascending: false });

    if (userId) {
      query = query.eq('user_id', userId);
    }

    const { data: orders, error } = await query;

    if (error) {
      throw error;
    }

    return NextResponse.json({ orders: orders || [] });
  } catch (error: unknown) {
    const errMessage = error instanceof Error ? error.message : 'Lỗi hệ thống khi tải danh sách đơn hàng';
    console.error('Lỗi khi tải danh sách đơn hàng:', error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: errMessage } },
      { status: 500 }
    );
  }
}

// 2. PUT API: Cập nhật trạng thái đơn hàng
export async function PUT(request: Request) {
  try {
    const authResult = await requireRole(request, ['admin', 'staff']);
    if (authResult.errorResponse) {
      return authResult.errorResponse;
    }

    const body = await request.json();
    const { orderId, status } = body;

    if (!orderId || !status) {
      return NextResponse.json(
        { error: { code: 'BAD_REQUEST', message: 'Thiếu orderId hoặc status cần cập nhật' } },
        { status: 400 }
      );
    }

    const validStatuses = ['pending', 'processing', 'shipping', 'delivered', 'cancelled'];
    if (!validStatuses.includes(status)) {
      return NextResponse.json(
        { error: { code: 'BAD_REQUEST', message: 'Trạng thái đơn hàng không hợp lệ' } },
        { status: 400 }
      );
    }

    const { data, error } = await supabaseAdmin
      .from('orders')
      .update({ status })
      .eq('id', orderId)
      .select()
      .single();

    if (error) {
      throw error;
    }

    return NextResponse.json({ success: true, order: data });
  } catch (error: unknown) {
    const errMessage = error instanceof Error ? error.message : 'Lỗi hệ thống khi cập nhật đơn hàng';
    console.error('Lỗi khi cập nhật trạng thái đơn hàng:', error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: errMessage } },
      { status: 500 }
    );
  }
}
