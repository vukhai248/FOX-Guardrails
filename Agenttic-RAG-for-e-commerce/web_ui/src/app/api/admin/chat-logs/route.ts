import { NextResponse } from 'next/server';
import { requireRole, supabaseAdmin } from '@/lib/server/auth';

// GET API: Lấy danh sách nhật ký hội thoại (chat_logs)
export async function GET(request: Request) {
  try {
    const authResult = await requireRole(request, ['admin', 'staff']);
    if (authResult.errorResponse) {
      return authResult.errorResponse;
    }

    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('session_id') || searchParams.get('sessionId');
    const riskLevel = searchParams.get('riskLevel') || searchParams.get('risk_level');
    const role = searchParams.get('role');
    const limit = Math.min(Math.max(parseInt(searchParams.get('limit') || '100', 10), 1), 500);
    const offset = Math.max(parseInt(searchParams.get('offset') || '0', 10), 0);

    let query = supabaseAdmin
      .from('chat_logs')
      .select('*', { count: 'exact' })
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1);

    if (sessionId) {
      query = query.eq('session_id', sessionId);
    }
    if (riskLevel) {
      query = query.eq('risk_level', riskLevel);
    }
    if (role) {
      query = query.eq('role', role);
    }

    const { data: logs, count, error } = await query;

    if (error) {
      console.error('Lỗi khi truy vấn chat_logs từ DB:', error);
      throw error;
    }

    return NextResponse.json({
      chat_logs: logs || [],
      total: count || (logs ? logs.length : 0),
      limit,
      offset,
    });
  } catch (error: unknown) {
    const errMessage = error instanceof Error ? error.message : 'Lỗi hệ thống khi tải nhật ký hội thoại';
    console.error('Lỗi API GET /api/admin/chat-logs:', error);
    return NextResponse.json(
      {
        error: {
          code: 'INTERNAL_ERROR',
          message: errMessage,
        },
      },
      { status: 500 }
    );
  }
}
