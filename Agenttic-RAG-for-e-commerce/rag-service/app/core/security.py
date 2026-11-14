from typing import Optional
from supabase import create_client, Client, ClientOptions
from configs.setting import settings

# 1. Client tĩnh cho verify token (dùng ANON KEY - quyền hạn thấp, bảo mật hơn)
# Fallback sang service role key nếu anon_key chưa được khai báo
anon_key = settings.SUPABASE_ANON_KEY or settings.SUPABASE_SERVICE_ROLE_KEY
if not settings.SUPABASE_ANON_KEY:
    print("WARNING: SUPABASE_ANON_KEY is empty. Verification is falling back to Service Role Key.")

supabase_anon_client: Client = create_client(settings.SUPABASE_URL, anon_key)

# 2. Client tĩnh cho admin/backend operations (dùng SERVICE ROLE KEY - quyền admin tối cao)
supabase_admin_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

# 3. Client động đại diện cho từng người dùng cụ thể (áp dụng RLS)
def get_user_supabase_client(user_token: str) -> Client:
    """
    Create a dynamic Supabase Client scoped to the user's JWT token (low privilege).
    This enforces Row-Level Security (RLS) policies at the database level.
    
    Args:
        user_token (str): The JWT access token of the authenticated user.
        
    Returns:
        Client: A Supabase Client instance authorized as the user.
    """
    # Remove "Bearer " prefix if present
    if user_token.startswith("Bearer "):
        user_token = user_token[7:]
        
    # Fallback to Service Role Key only if Anon Key is missing
    active_key = settings.SUPABASE_ANON_KEY or settings.SUPABASE_SERVICE_ROLE_KEY
    
    # Inject the user's JWT token into the Authorization Header
    options = ClientOptions(
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    return create_client(settings.SUPABASE_URL, active_key, options=options)


def verify_supabase_jwt(token: str) -> Optional[str]:
    """
    Verify Supabase JWT token online using the Supabase Anon client (low privilege).
    This avoids using the admin Service Role Key to inspect client tokens.
    
    Args:
        token (str): The JWT access token received from frontend Next.js (Supabase session).
        
    Returns:
        Optional[str]: The user's UUID if the token is valid, otherwise None.
    """
    if not token:
        return None
        
    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
        
    try:
        # Gọi trực tiếp API xác thực của Supabase để kiểm tra token bằng Client quyền thấp
        response = supabase_anon_client.auth.get_user(token)
        if response and response.user:
            return response.user.id
        return None
    except Exception as e:
        print(f"Supabase online token verification failed: {str(e)}")
        return None
