import 'server-only';
import { NextResponse } from 'next/server';
import { createClient, type SupabaseClient, type User } from '@supabase/supabase-js';

const INTERNAL_MESSAGE = 'Không thể xác thực quyền hạn lúc này.';
let adminClient: SupabaseClient | undefined;
let authClient: SupabaseClient | undefined;

function configuredClient(admin: boolean): SupabaseClient {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env[admin ? 'SUPABASE_SERVICE_ROLE_KEY' : 'NEXT_PUBLIC_SUPABASE_ANON_KEY'];
  if (!url || !key) throw new Error(INTERNAL_MESSAGE);
  try {
    return createClient(url, key, { auth: { autoRefreshToken: false, persistSession: false } });
  } catch {
    throw new Error(INTERNAL_MESSAGE);
  }
}

export function getSupabaseAdmin(): SupabaseClient {
  adminClient ??= configuredClient(true);
  return adminClient;
}

// Preserve Anti's existing imports while deferring construction until property access.
export const supabaseAdmin = new Proxy({} as SupabaseClient, {
  get(_target, property) {
    const client = getSupabaseAdmin();
    const value = Reflect.get(client, property, client);
    return typeof value === 'function' ? value.bind(client) : value;
  },
});

export type AllowedRole = 'admin' | 'staff' | 'customer';
export interface AuthSuccess { user: User; role: AllowedRole; errorResponse?: null; }
export interface AuthFailure { user?: null; role?: null; errorResponse: NextResponse; }
export type AuthResult = AuthSuccess | AuthFailure;

function failure(code: string, status: number, message: string): AuthFailure {
  return { errorResponse: NextResponse.json({ error: { code, message } }, { status }) };
}

export async function requireRole(request: Request, allowedRoles: AllowedRole[] = ['admin', 'staff']): Promise<AuthResult> {
  const token = request.headers.get('authorization')?.match(/^Bearer\s+(\S+)$/i)?.[1];
  if (!token) return failure('UNAUTHENTICATED', 401, 'Vui lòng đăng nhập để tiếp tục.');
  try {
    authClient ??= configuredClient(false);
    const { data: { user }, error } = await authClient.auth.getUser(token);
    if (error || !user) return failure('UNAUTHENTICATED', 401, 'Phiên đăng nhập không hợp lệ.');
    const { data: roleRow, error: roleError } = await getSupabaseAdmin()
      .from('user_roles').select('role').eq('user_id', user.id).maybeSingle();
    if (roleError) return failure('INTERNAL_ERROR', 500, INTERNAL_MESSAGE);
    const role = (roleRow?.role || 'customer') as AllowedRole;
    if (!allowedRoles.includes(role)) return failure('FORBIDDEN', 403, 'Bạn không có quyền thực hiện thao tác này.');
    return { user, role };
  } catch {
    return failure('INTERNAL_ERROR', 500, INTERNAL_MESSAGE);
  }
}
