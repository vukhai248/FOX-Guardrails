import sys
import asyncio
from pathlib import Path
from uuid import uuid4

# Thêm thư mục gốc của rag-service vào sys.path để tránh lỗi import module configs
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from configs.setting import settings
from src.guard_client import build_context, guard_output
from src.chat_logging import write_chat_turn
from src.health import service_health

# Import compiled LangGraph Workflow 1
from src.g_pipelines.workflow_1.workflow_1 import app as workflow_app

app = FastAPI(
    title="Agentic RAG E-Commerce Backend",
    description="Dịch vụ Backend RAG hỗ trợ tư vấn sản phẩm, so sánh thông số và tra cứu đơn hàng.",
    version="1.0.0",
    debug=settings.DEBUG
)

# Cấu hình CORS để frontend Next.js có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = Field(default=None, max_length=100)
    user_token: Optional[str] = None

class GuardResponse(BaseModel):
    action: str = "allow"
    decision_id: Optional[str] = None
    flags: List[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    tool_used: Optional[str] = None
    sources: List[str] = []
    session_id: str
    guard: GuardResponse = Field(default_factory=GuardResponse)

@app.get("/health")
def health_check():
    return service_health()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, authorization: Optional[str] = Header(None)):
    try:
        from app.core.security import verify_supabase_jwt
        
        # Giải mã token từ Header Authorization hoặc fallback từ Body request
        user_id = None
        user_token = None
        if authorization:
            if authorization.startswith("Bearer "):
                user_token = authorization[7:]
            else:
                user_token = authorization
        elif request.user_token:
            user_token = request.user_token

        if user_token:
            user_id = verify_supabase_jwt(user_token)

        # Gọi Workflow 1 (LangGraph) với user_query, session_id, user_token
        session_id = request.session_id or str(uuid4())
        thread_id = f"{user_id or 'anon'}:{session_id}"
        run_config = {"configurable": {"thread_id": thread_id}}
        
        result = workflow_app.invoke(
            {
                "user_query": request.message,
                "session_id": session_id,
                "user_token": user_token,
            },
            config=run_config
        )

        # Trích xuất kết quả từ Agent State
        final_answer = result.get("final_answer")
        if not final_answer:
            final_answer = guard_output("Xin lỗi, tôi không thể xử lý yêu cầu này.",
                                        build_context(session_id=session_id, user_id=user_id))
        cited_sources = result.get("cited_sources") or []
        
        # Tổng hợp tool_used từ lịch sử tool calls
        tool_calls = result.get("tool_calls_used") or []
        tool_used = ", ".join([t.get("tool", "") for t in tool_calls if t.get("tool")]) or None

        await asyncio.to_thread(write_chat_turn,
            session_id=session_id, user_id=user_id, user_message=request.message,
            agent_message=final_answer, tool_calls=result.get("turn_tool_calls") or [],
            risk_level=result.get("risk_level") or "safe",
            guard_decision_ids=result.get("guard_decision_ids") or [],
        )

        verdict = result.get("guard") or {}
        return ChatResponse(
            reply=final_answer,
            tool_used=tool_used,
            sources=cited_sources,
            session_id=session_id,
            guard=GuardResponse(action=verdict.get("action") or "allow", decision_id=verdict.get("decision_id"),
                                flags=list(verdict.get("flags") or [])),
        )
    except Exception as e:
        print(f"[ERROR] Chat endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Chạy server dựa trên cấu hình trong file .env
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
