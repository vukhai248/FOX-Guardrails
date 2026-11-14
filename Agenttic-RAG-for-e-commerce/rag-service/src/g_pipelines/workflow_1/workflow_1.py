from configs.setting import settings
from configs.GetConfig import config
import uuid
import os
import operator
from typing import TypedDict, Literal, Optional, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from src.LLMService import LLMService
from src.e_agents.guardrail_call import GuardrailCall
from src.e_agents.rejection_call import RejectionCall
from src.e_agents.master_agent import MasterAgent

from src.d_tools import(
    product_search,
    product_compare,
    policy_search,
    order_lookup
)

from src.d_tools import (
    PRODUCT_SEARCH_SCHEMA,
    PRODUCT_COMPARE_SCHEMA,
    POLICY_SEARCH_SCHEMA,
    ORDER_LOOKUP_SCHEMA
)

from src.f_prompts import (
    FULL_MASTER_PROMPT,
    FULL_REJECTION_PROMPT
)

from app.core.security import verify_supabase_jwt

from src.f_prompts.skills import load_skill, list_skills
from src.d_tools.product_reviews import product_reviews, PRODUCT_REVIEWS_SCHEMA
from src.d_tools.support_ticket import create_support_ticket, CREATE_SUPPORT_TICKET_SCHEMA
from src.guard_client import build_context, guard_input, guard_output

#=================================================

available_tools = {
    "product_search": product_search,
    "product_compare": product_compare,
    "policy_search": policy_search,
    "order_lookup": order_lookup,
    "product_reviews": product_reviews,
    "create_support_ticket": create_support_ticket,
}

tools_schema = [
    PRODUCT_SEARCH_SCHEMA,
    PRODUCT_COMPARE_SCHEMA,
    POLICY_SEARCH_SCHEMA,
    ORDER_LOOKUP_SCHEMA,
    PRODUCT_REVIEWS_SCHEMA,
    CREATE_SUPPORT_TICKET_SCHEMA,
]

#=================================================

def select_skill(query: str) -> tuple[str, str]:
    """Chọn skill markdown phù hợp với câu hỏi. Có thể thay bằng LLM-call nhẹ sau này."""
    q = (query or "").lower()
    def selected(name):
        return name, load_skill(name) or ""
    if any(k in q for k in ["ticket", "tạo phiếu", "chuyển nhân viên"]):
        return selected("account/support_ticket")
    if any(k in q for k in ["đánh giá", "review", "mọi người nói gì", "có tốt không"]):
        return selected("product/reviews")
    # Order / account
    if any(k in q for k in ["đơn hàng", "order", "tra đơn", "mua hàng"]):
        return selected("account/order_lookup")
    # Policy
    if any(k in q for k in ["chính sách", "đổi trả", "bảo hành", "trả góp", "giao hàng", "vận chuyển"]):
        return selected("policy/policy_search")
    # Compare (named products)
    if any(k in q for k in ["so sánh", "nên chọn", "hay hơn"]):
        return selected("product/compare" if load_skill("product/compare") else "product/single_spec")
    # Ambiguous / vague
    if any(k in q for k in ["tư vấn", "gợi ý", "nên mua", "máy nào", "con nào", "tầm giá"]):
        return selected("product/ambiguous")
    # Single specific spec / price / stock
    if any(k in q for k in ["bao nhiêu", "giá", "tồn kho", "chip", "ram", "pin", "màn hình", "camera", "bộ nhớ"]):
        return selected("product/single_spec")
    # Default: ambiguous / general guidance
    return selected("product/ambiguous")



#=================================================

llm_service = LLMService(settings, config)
guardrail_call = GuardrailCall(llm_service, config)
rejection_call = RejectionCall(llm_service, config)
master_agent = MasterAgent(llm_service, config)

#=================================================

class RetrievedChunk(TypedDict):
    content: str
    source: str
    score: float
    chunk_type: str

class AgentState(TypedDict):

    # 1. INput user
    user_query: str
    session_id: str

    # 2. Auth
    user_token: Optional[str]
    user_id: Optional[str]
    is_authenticated: bool

    # 3. Guardrail & Quality
    risk_level: Optional[str]               # "low" | "medium" | "high"
    relevance_score: float                   # Dùng cho self-check Corrective RAG

    # 4. Router (Định tuyến)
    intent: str                              # Kết quả phân loại: 'product', 'policy', 'account', 'support'
    skill_name: str
    selected_agent: Optional[str]            # Quyết định Nút xử lý tiếp theo

    # 5. Retrieval & Tools
    retrieved_context: list[RetrievedChunk]
    tool_calls_used: Annotated[list[dict], operator.add]  # ⚡ Reducer cộng dồn lịch sử tool calls (mỗi dict = {tool, args, response?})
    turn_tool_calls: list[dict]
    guard_decision_ids: list[str]
    guard: dict                              # FOX verdict on the input: action, decision_id, flags
    guard_harden: Optional[str]              # FOX "review": system reminder added for this turn
    iteration_count: int                     # Đếm số lần lặp chống infinite loop

    # 6. Hội thoại
    messages: Annotated[list, add_messages]  # ⚡ Reducer cộng dồn tin nhắn
    conversation_state: dict

    # 7. Output
    final_answer: Optional[str]
    cited_sources: list[str]
    ticket_id: Optional[str]
    show_popup: bool
    loop_exhausted: bool

    # 8. Thống kê
    input_tokens: Annotated[int, operator.add]
    output_tokens: Annotated[int, operator.add]
    latency: Annotated[float, operator.add]
    total_tokens: Annotated[int, operator.add]
    

#=================================================

def receive_node(state: AgentState) -> dict:
    query = state.get("user_query", "").strip()
    token = state.get("user_token")
    user_id = None

    if token:
        user_id = verify_supabase_jwt(token)
    
    is_authenticated = True if user_id else False
 
    return {
        "user_id": user_id,
        "is_authenticated": is_authenticated,
        "loop_exhausted": False,
        "skill_name": "",
        "intent": "",
        "turn_tool_calls": [],
        "guard_decision_ids": [],
        "user_query": query  
    }

#=================================================

def _fox_verdict(text) -> dict:
    """FOX verdict carried by GuardedText (plain str when the guard is off or mocked)."""
    return {"action": getattr(text, "action", "allow"), "decision_id": getattr(text, "decision_id", None),
            "flags": list(getattr(text, "flags", ()))}


def guardrail_node(state: AgentState) -> dict:
    ctx = build_context(session_id=state.get("session_id"), user_id=state.get("user_id"))
    query = guard_input(state["user_query"], ctx)
    verdict = _fox_verdict(query)
    fox = {"guard": verdict, "guard_harden": getattr(query, "harden_prompt_text", None),
           "guard_decision_ids": [verdict["decision_id"]] if verdict["decision_id"] else []}
    query = str(query) if isinstance(query, str) else query  # plain str in graph state (checkpointer)
    if verdict["action"] == "block":
        # FOX refused: `query` is already the refusal text; no LLM sees the attack (legacy guard included).
        return {**fox, "risk_level": "attack", "show_popup": True, "user_query": query,
                "latency": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    result = ({"risk_level": "safe", "latency": 0, "tokens": {"input": 0, "output": 0}}
              if os.getenv("LEGACY_LLM_GUARDRAIL", "on").lower() == "off"
              else guardrail_call.invoke(query))
    risk_level = result["risk_level"]
    
    # Chỉ lưu tin nhắn khi KHÔNG phải attack
    if risk_level != "attack":
        return {
            **fox,
            "risk_level": risk_level,
            "user_query": query,
            "show_popup": False,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "latency": result["latency"],
            "input_tokens": result["tokens"]["input"],
            "output_tokens": result["tokens"]["output"],
            "total_tokens": result["tokens"]["input"] + result["tokens"]["output"]
        }
    else:
        # Attack → KHÔNG lưu
        return {
            **fox,
            "risk_level": risk_level,
            "show_popup": True,
            "user_query": query,
            "latency": result["latency"],
            "input_tokens": result["tokens"]["input"],
            "output_tokens": result["tokens"]["output"],
            "total_tokens": result["tokens"]["input"] + result["tokens"]["output"]
        }

#=================================================

def rejection_node(state: AgentState) -> dict:
    """
    [NODE] Rejection Agent (Từ chối):
    - Chỉ chạy khi risk_level == "needs_ticket"
    - Trả về câu từ chối lịch sự
    - KHÔNG lưu tin nhắn vào messages (đã lưu ở guardrail_node)
    """
    
    query = state["user_query"]
    if (state.get("guard") or {}).get("action") == "block":
        # FOX already wrote the refusal; do not send the attack to the rejection LLM.
        return {"final_answer": query, "show_popup": True, "input_tokens": 0, "output_tokens": 0,
                "total_tokens": 0, "latency": 0}

    result = rejection_call.invoke(query)

    return {
        "final_answer": guard_output(result["content"], build_context(session_id=state.get("session_id"), user_id=state.get("user_id"))),
        "show_popup": True,
        "input_tokens": result["tokens"]["input"],
        "output_tokens": result["tokens"]["output"],
        "total_tokens": result["tokens"]["input"] + result["tokens"]["output"],
        "latency": result["latency"]
    }
    

#=================================================

def master_node(state: AgentState) -> dict:
    """
    [NODE 3] Master Agent (Tư duy):
    - Chỉ chạy khi risk_level != "attack"
    - Build messages: system prompt + lịch sử tool calls được inject giữa các lượt hội thoại
      (mỗi lượt user sau lượt 1 sẽ nhìn thấy tool/tham số đã gọi ở lượt trước)
    - messages chỉ lưu user query và assistant final answer
    - tool_calls_used: list[dict] lưu lịch sử tool calls theo thứ tự lượt hội thoại
    """
    import json

    def _fmt_search_context(record):
        """Tóm tắt bộ lọc product_search đã dùng ở lượt trước, dùng skill common/multi_turn_context.md."""
        if not record or record.get("tool") != "product_search":
            return ""
        args = record.get("args", {})
        queries = args.get("queries", [])
        if not queries:
            return ""
        q = queries[0]
        out = str(record.get("output", ""))
        n_items = 0
        if "Dòng:" in out:
            n_items = out.count("Dòng:")
        elif "Product:" in out:
            n_items = out.count("Product:")
        summary = f"{n_items} dòng" if "Dòng:" in out else (f"{n_items} sản phẩm" if "Product:" in out else "kết quả")
        skill = load_skill("common/multi_turn_context") or ""
        return skill.format(
            previous_query=json.dumps(q, ensure_ascii=False),
            result_summary=summary
        )

    tool_history = state.get("tool_calls_used") or []
    last_search_record = None
    for rec in reversed(tool_history):
        if rec.get("tool") == "product_search":
            last_search_record = rec
            break

    full_messages = [{"role": "system", "content": FULL_MASTER_PROMPT}]
    if state.get("guard_harden"):
        full_messages.append({"role": "system", "content": state["guard_harden"]})
    user_count = 0
    for msg in state["messages"]:
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "type", "")
        if role == "user":
            user_count += 1
            if user_count > 1 and last_search_record:
                note = _fmt_search_context(last_search_record)
                if note:
                    full_messages.append({"role": "system", "content": note})
        full_messages.append(msg)

    auth_context = {
        "user_id": state.get("user_id"),
        "user_token": state.get("user_token")
    }

    user_query = state.get("user_query", "")
    skill_name, skill_text = select_skill(user_query)
    if skill_text:
        print(f"🧩 Injected skill: {skill_name}")

    result = master_agent.invoke(
        messages=full_messages,
        available_tools=available_tools,
        tools_schema=tools_schema,
        auth_context=auth_context,
        skill=skill_text,
        guard_ctx={"session_id": state.get("session_id"), "user_id": state.get("user_id"), "intent": skill_name},
    )

    new_tool_records = result.get("tool_context") or []

    assistant_msg = {
        "role": "assistant",
        # Restored PII must not re-enter the LLM context next turn (see master_agent).
        "content": result.get("history_content", result["content"])
    }

    conversation_state = state.get("conversation_state") or {}
    found_new_search = False
    for rec in reversed(new_tool_records):
        if rec.get("tool") == "product_search":
            conversation_state["last_product_search"] = rec
            found_new_search = True
            break
    if not found_new_search and last_search_record:
        conversation_state["last_product_search"] = last_search_record

    output_id = result.get("output_decision_id")
    return {
        "final_answer": result["content"],
        "guard_decision_ids": [*(state.get("guard_decision_ids") or []), *([output_id] if output_id else [])],
        "skill_name": skill_name,
        "intent": skill_name,
        "messages": [assistant_msg],
        "loop_exhausted": result.get("loop_exhausted", False),
        "tool_calls_used": new_tool_records,
        "turn_tool_calls": new_tool_records,
        "conversation_state": conversation_state,
        "input_tokens": result["tokens"]["input"],
        "output_tokens": result["tokens"]["output"],
        "total_tokens": result["tokens"]["input"] + result["tokens"]["output"],
        "latency": result["latency"]
    }


#=================================================  

builder = StateGraph(AgentState)

builder.add_node("receive_node", receive_node)
builder.add_node("guardrail_node", guardrail_node)
builder.add_node("rejection_node", rejection_node)
builder.add_node("master_node", master_node)

def route_after_guardrail(state: AgentState) -> str:
    """Hàm quyết định Nút tiếp theo dựa vào kết quả của Guardrail"""
    risk = state.get("risk_level", "safe")
    
    if risk == "attack":
        return "rejection_node"
    else:    
        return "master_node"


builder.add_edge(START, "receive_node")
builder.add_edge("receive_node", "guardrail_node")
builder.add_conditional_edges(
    "guardrail_node",
    route_after_guardrail,
    {
        "rejection_node": "rejection_node", 
        "master_node": "master_node"       
    }
)
builder.add_edge("rejection_node", END)
builder.add_edge("master_node", END)

memory = MemorySaver()
app = builder.compile(checkpointer=memory)
