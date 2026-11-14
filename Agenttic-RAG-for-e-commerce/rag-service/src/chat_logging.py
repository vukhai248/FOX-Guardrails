"""Server-only per-turn conversation log, without tool arguments or auth tokens."""
import logging
from datetime import datetime, timedelta, timezone

from app.core.security import supabase_admin_client
from src.guard_client import LogText, build_context, guard_log

logger = logging.getLogger(__name__)


def write_chat_turn(*, session_id, user_id, user_message, agent_message, tool_calls,
                    risk_level, guard_decision_ids) -> bool:
    try:
        if not isinstance(session_id, str) or not 1 <= len(session_id) <= 100:
            raise ValueError("Invalid log session")
        context = build_context(session_id=session_id, user_id=user_id)
        user_log = guard_log(user_message, {**context, "role": "user"})
        agent_log = guard_log(agent_message, {**context, "role": "agent"})
        for prepared in (user_log, agent_log):
            if not isinstance(prepared, LogText) or not isinstance(prepared.message, str):
                raise ValueError("Missing prepared log message")
        decisions = list(dict.fromkeys([*guard_decision_ids, *user_log.decision_ids, *agent_log.decision_ids]))
        if any(not isinstance(decision, str) for decision in decisions):
            raise ValueError("Invalid decision ID")
        names = list(dict.fromkeys(call["tool"] for call in tool_calls
                                  if isinstance(call, dict) and isinstance(call.get("tool"), str)))
        tools = ", ".join(names)[:100] or None
        risk = {"safe": "low", "needs_ticket": "medium", "attack": "high",
                "low": "low", "medium": "medium", "high": "high"}.get(risk_level, "high")
        now = datetime.now(timezone.utc)
        rows = [{"session_id": session_id, "user_id": user_id, "role": role,
                 "message": prepared.message, "tool_used": tools, "risk_level": risk,
                 "guard_decision_ids": decisions,
                 "created_at": (now + timedelta(microseconds=index)).isoformat()}
                for index, (role, prepared) in enumerate((("user", user_log), ("agent", agent_log)))]
    except Exception:
        logger.warning("CHAT_LOG_PREPARE_FAILED")
        return False
    try:
        supabase_admin_client.table("chat_logs").insert(rows).execute()
        return True
    except Exception:
        # The chat may already have created a ticket. Do not fail it and provoke a retry.
        logger.warning("CHAT_LOG_WRITE_FAILED")
        return False
