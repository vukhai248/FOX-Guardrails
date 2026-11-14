import { NextResponse } from 'next/server';
import { requireRole, supabaseAdmin, AllowedRole } from '@/lib/server/auth';

// 1. GET API: Lấy danh sách toàn bộ người dùng trong hệ thống
export async function GET(request: Request) {
  try {
    const authResult = await requireRole(request, ['admin', 'staff']);
    if (authResult.errorResponse) {
      return authResult.errorResponse;
    }

    // Lấy danh sách users từ Supabase Auth Admin API
    const { data: { users }, error } = await supabaseAdmin.auth.admin.listUsers();

    if (error) {
      throw error;
    }

    return NextResponse.json({ users });
  } catch (error: unknown) {
    const errMessage = error instanceof Error ? error.message : 'Lỗi hệ thống khi tải danh sách người dùng';
    console.error('Lỗi khi lấy danh sách users:', error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: errMessage } },
      { status: 500 }
    );
  }
}

// 2. PUT API: Cập nhật Role cho một người dùng (upsert vào bảng user_roles)
export async function PUT(request: Request) {
  try {
    const authResult = await requireRole(request, ['admin']);
    if (authResult.errorResponse) {
      return authResult.errorResponse;
    }

    const body = await request.json();
    const { userId, role } = body;

    if (!userId || !role) {
      return NextResponse.json(
        { error: { code: 'BAD_REQUEST', message: 'Thiếu userId hoặc role cần cập nhật' } },
        { status: 400 }
      );
    }

    const validRoles: AllowedRole[] = ['admin', 'staff', 'customer'];
    if (!validRoles.includes(role)) {
      return NextResponse.json(
        { error: { code: 'BAD_REQUEST', message: 'Vai trò người dùng không hợp lệ' } },
        { status: 400 }
      );
    }

    // 1. Upsert vào bảng public.user_roles (nguồn quyền server-side duy nhất)
    const { error: upsertError } = await supabaseAdmin
      .from('user_roles')
      .upsert({
        user_id: userId,
        role: role,
        updated_at: new Date().toISOString(),
      });

    if (upsertError) {
      console.error('Lỗi khi upsert vào bảng user_roles:', upsertError);
      throw upsertError;
    }

    // 2. Đồng bộ user_metadata trong Supabase Auth (để client UI đồng bộ thông tin hiển thị)
    const { data: { user }, error: getError } = await supabaseAdmin.auth.admin.getUserById(userId);
    let updatedUser = user;
    if (!getError && user) {
      const currentMetadata = user.user_metadata || {};
      const { data: resUpdated } = await supabaseAdmin.auth.admin.updateUserById(userId, {
        user_metadata: { ...currentMetadata, role },
      });
      if (resUpdated?.user) {
        updatedUser = resUpdated.user;
      }
    }

    return NextResponse.json({ success: true, user: updatedUser });
  } catch (error: unknown) {
    const errMessage = error instanceof Error ? error.message : 'Lỗi hệ thống khi cập nhật vai trò người dùng';
    console.error('Lỗi khi cập nhật role user:', error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: errMessage } },
      { status: 500 }
    );
  }
}
