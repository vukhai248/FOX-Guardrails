import { NextResponse } from 'next/server';
import { requireRole, supabaseAdmin } from '@/lib/server/auth';

// 1. GET API: Lấy danh sách toàn bộ support tickets
export async function GET(request: Request) {
  try {
    const authResult = await requireRole(request, ['admin', 'staff']);
    if (authResult.errorResponse) {
      return authResult.errorResponse;
    }

    const { data: tickets, error } = await supabaseAdmin
      .from('support_tickets')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      throw error;
    }

    return NextResponse.json({ tickets: tickets || [] });
  } catch (error: unknown) {
    const errMessage = error instanceof Error ? error.message : 'Lỗi hệ thống khi tải danh sách ticket';
    console.error('Lỗi khi tải danh sách support tickets:', error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: errMessage } },
      { status: 500 }
    );
  }
}

// 2. PUT API: Cập nhật thông tin / trạng thái / phản hồi của ticket
export async function PUT(request: Request) {
  try {
    const authResult = await requireRole(request, ['admin', 'staff']);
    if (authResult.errorResponse) {
      return authResult.errorResponse;
    }

    const body = await request.json();
    const { ticketId, status, note, assigned_staff_id } = body;

    if (!ticketId) {
      return NextResponse.json(
        { error: { code: 'BAD_REQUEST', message: 'Thiếu ticketId cần cập nhật' } },
        { status: 400 }
      );
    }

    const updatePayload: Record<string, unknown> = {};
    if (status !== undefined) updatePayload.status = status;
    if (note !== undefined) updatePayload.note = note;
    if (assigned_staff_id !== undefined) updatePayload.assigned_staff_id = assigned_staff_id;

    const { data, error } = await supabaseAdmin
      .from('support_tickets')
      .update(updatePayload)
      .eq('id', ticketId)
      .select()
      .single();

    if (error) {
      throw error;
    }

    return NextResponse.json({ success: true, ticket: data });
  } catch (error: unknown) {
    const errMessage = error instanceof Error ? error.message : 'Lỗi hệ thống khi cập nhật ticket';
    console.error('Lỗi khi cập nhật ticket:', error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: errMessage } },
      { status: 500 }
    );
  }
}
