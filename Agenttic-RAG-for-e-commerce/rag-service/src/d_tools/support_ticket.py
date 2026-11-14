from uuid import UUID

from app.core.security import get_user_supabase_client
from src.d_tools.tool_result import ToolResult


def create_support_ticket(category, note, order_id=None, current_user_id=None, user_token=None) -> ToolResult:
    def result(text):
        return ToolResult("create_support_ticket", text)

    if not current_user_id or not user_token:
        return result("Vui lòng đăng nhập để tạo ticket hỗ trợ.")
    if (not isinstance(category, str) or category not in {"advisory", "negotiation", "technical", "attack_flagged", "other"}
            or not isinstance(note, str) or not note.strip() or len(note) > 2000):
        return result("Thông tin ticket không hợp lệ (ghi chú từ 1 đến 2000 ký tự).")
    if order_id is not None and order_id != "":
        try:
            order_id = str(UUID(order_id))
        except (ValueError, TypeError, AttributeError):
            return result("Mã đơn hàng không hợp lệ.")
    try:
        # No service-role fallback for writes. The caller must supply verified auth.
        client = get_user_supabase_client(user_token)
        if order_id:
            orders = (client.table("orders").select("id").eq("id", order_id)
                      .eq("user_id", current_user_id).limit(1).execute()).data
            if not orders:
                return result("Không tìm thấy đơn hàng thuộc tài khoản của bạn.")
        response = client.table("support_tickets").insert({
            "customer_id": current_user_id, "order_id": order_id or None, "category": category,
            "note": note, "risk_level": "low", "created_by": "agent", "status": "open",
        }).execute()
        if not response.data:
            return result("Không thể xác nhận ticket đã tạo. Vui lòng kiểm tra với nhân viên hỗ trợ.")
        return result(f"Ticket đã được tạo. ticket_id: {response.data[0]['id']}")
    except Exception:
        return result("Không thể tạo ticket lúc này. Vui lòng thử lại sau.")


CREATE_SUPPORT_TICKET_SCHEMA = {
    "type": "function", "function": {
        "name": "create_support_ticket",
        "description": "Create a support ticket only when the signed-in user explicitly requests it. Never invent an order ID.",
        "parameters": {"type": "object", "properties": {
            "category": {"type": "string", "enum": ["advisory", "negotiation", "technical", "attack_flagged", "other"]},
            "note": {"type": "string", "maxLength": 2000}, "order_id": {"type": "string"},
        }, "required": ["category", "note"]},
    },
}
