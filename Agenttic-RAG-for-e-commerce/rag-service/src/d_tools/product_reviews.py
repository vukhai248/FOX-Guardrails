import re

from app.core.security import supabase_anon_client
from src.d_tools.tool_result import Segment, ToolResult

_CANDIDATES = 30
_SHOWN = 8
# Storage / RAM sizes and shop suffixes do not change which phone the customer means.
_SIZE = re.compile(r"\b\d+\s*(?:gb|tb)\b")
_PREFIX = re.compile(r"^(?:điện thoại|dien thoai|máy tính bảng|laptop)\s+")


def _model_key(name: str) -> str:
    """'iPhone 16 128GB | Chính hãng VN/A' → 'iphone 16'; 'Điện thoại iPhone 16 Pro Max 256GB' → 'iphone 16 pro max'."""
    base = name.split("|", 1)[0].lower().strip()
    base = _PREFIX.sub("", base)
    base = _SIZE.sub(" ", base)
    return " ".join(base.split())


# Words that make a different model, not a variant (colour, edition text are variants).
_MODEL_WORDS = {"pro", "max", "plus", "ultra", "mini", "fe", "edge", "lite", "air", "se", "neo", "gt", "slim",
                "fold", "flip", "note", "turbo", "prime", "x"}


def _same_model(product_key: str, wanted: str) -> bool:
    """'iphone 15 pro max titan tự nhiên' is the model 'iphone 15 pro max'; 'iphone 16 pro' is not 'iphone 16'."""
    if product_key == wanted:
        return True
    if not product_key.startswith(wanted + " "):
        return False
    extra = product_key[len(wanted):].split()
    return not any(w in _MODEL_WORDS or w.isdigit() for w in extra)


def _search(name: str) -> list[dict]:
    rows = (supabase_anon_client.table("products").select("id,name")
            .ilike("name", f"%{name}%").limit(_CANDIDATES).execute()).data or []
    words = name.split()
    if rows or not 1 < len(words) <= 5:
        return rows
    # "AirPods Pro 2" vs "Apple AirPods Pro Gen 2": every word must appear, in any order.
    query = supabase_anon_client.table("products").select("id,name")
    for word in words:
        query = query.ilike("name", f"%{word}%")
    return query.limit(_CANDIDATES).execute().data or []


def _resolve(name: str) -> tuple[list[int], list[dict]]:
    """Product ids to read, or ([], candidates) when the customer must pick one.

    One name can match many products ("iPhone 16" → 128GB, 256GB, Pro, Plus…). Storage and colour
    variants of the same model are one product for reviews; other models (Pro, Plus) are different."""
    products = _search(name)
    if len(products) == 1:
        return [products[0]["id"]], products
    wanted = _model_key(name)
    same_model = [p for p in products if _same_model(_model_key(p.get("name") or ""), wanted)]
    if same_model:
        return [p["id"] for p in same_model], products
    return [], products


def product_reviews(product_id: int | None = None, product_name: str | None = None, limit: int = 5) -> ToolResult:
    def result(text):
        return ToolResult("product_reviews", text)

    if type(limit) is not int or not 1 <= limit <= 20:
        return result("limit phải từ 1 đến 20.")
    if product_id is not None and (type(product_id) is not int or product_id <= 0):
        return result("Mã sản phẩm không hợp lệ.")
    try:
        if product_id is None:
            if not isinstance(product_name, str) or not product_name.strip():
                return result("Vui lòng chọn sản phẩm cụ thể bằng tên hoặc mã sản phẩm.")
            # No PostgREST filter syntax or wildcard supplied by the model is forwarded.
            name = product_name.strip()
            if len(name) > 200 or any(c in name for c in "%_*\\"):
                return result("Vui lòng chọn tên sản phẩm cụ thể.")
            ids, candidates = _resolve(name)
            if not ids:
                if not candidates:
                    # Never echo the model-supplied name: trusted text is not inspected by the context guard.
                    return result("Không tìm thấy sản phẩm nào khớp tên này.")
                # Give the model something to choose from, instead of a bare "be specific" that it
                # can only answer by retrying the same name (loop until max_turns).
                lines = [f"- product_id={p['id']}: {p['name']}" for p in candidates[:_SHOWN]]
                return result("Tên khớp nhiều sản phẩm khác nhau. Gọi lại product_reviews với product_id "
                              "của đúng sản phẩm khách hỏi, hoặc hỏi khách chọn:\n" + "\n".join(lines))
        else:
            ids = [product_id]
        query = supabase_anon_client.table("reviews").select("id,product_id,rating,comment,created_at")
        query = query.eq("product_id", ids[0]) if len(ids) == 1 else query.in_("product_id", ids)
        reviews = query.order("created_at", desc=True).limit(limit).execute().data or []
        header = ", ".join(str(i) for i in ids)
        trusted = [f"=== PRODUCT REVIEWS: {header} ==="]
        segments = []
        for review in reviews:
            trusted.append(f"Review {review['id']}: {review['rating']}/5 | {review['created_at']}")
            segments.append(Segment("review", str(review["id"]), review.get("comment") or ""))
        if not reviews:
            trusted.append("Chưa có đánh giá.")
        return ToolResult("product_reviews", "\n".join(trusted), segments)
    except Exception:
        return result("Không thể đọc đánh giá lúc này. Vui lòng thử lại sau.")


PRODUCT_REVIEWS_SCHEMA = {
    "type": "function", "function": {
        "name": "product_reviews",
        "description": ("Read latest customer ratings and comments. Pass product_id when known (from "
                        "product_search or a previous product_reviews candidate list); otherwise product_name. "
                        "Storage variants of one model are read together."),
        "parameters": {"type": "object", "properties": {
            "product_id": {"type": "integer"}, "product_name": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
        }, "required": []},
    },
}
