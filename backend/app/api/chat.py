"""
Web chat API – primary channel for the CarePath prototype.
Uses the same conversation processor as WhatsApp / Telegram.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.conversation import (
    process_message,
    reset_session,
    get_session_snapshot,
    _get_or_create_session,
)

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=8, max_length=128, description="Stable client session id")
    text: str = Field(..., min_length=1, max_length=2000)
    channel: str = Field(default="web", description="web | telegram | demo")


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    status: str | None = None
    pathway: str | None = None
    answers_count: int = 0
    current_question_id: str | None = None
    triage: str | None = None
    red_flag: bool | None = None
    quick_replies: list[str] = Field(default_factory=list)


def _quick_replies_for(status: str | None, reply: str) -> list[str]:
    """Suggest tappable replies for the web UI."""
    if not status or status in ("not_started", "awaiting_consent"):
        return ["YES", "NO"]
    if status == "awaiting_pathway":
        return ["1", "2", "3", "4"]
    if status == "completed":
        return ["DONE", "REMIND", "RESTART"]
    if status == "in_progress":
        # Numeric options are common; keep light defaults
        return ["1", "2", "3", "4"]
    return []


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """
    Send a user message and receive the CarePath reply.
    session_id should be a UUID stored in the browser (localStorage).
    """
    channel_key = f"{payload.channel}:{payload.session_id}"
    session = _get_or_create_session(channel_key)
    reply = await process_message(session, payload.text)

    assessment = session.get("assessment")
    decision = session.get("last_decision")
    status = assessment.status.value if assessment else None
    pathway = assessment.pathway.value if assessment and assessment.pathway else None

    return ChatResponse(
        reply=reply or "",
        session_id=payload.session_id,
        status=status,
        pathway=pathway,
        answers_count=len(assessment.answers) if assessment else 0,
        current_question_id=assessment.current_question_id if assessment else None,
        triage=decision.triage.value if decision else None,
        red_flag=decision.red_flag if decision else None,
        quick_replies=_quick_replies_for(status, reply or ""),
    )


@router.post("/reset")
async def chat_reset(session_id: str, channel: str = "web"):
    channel_key = f"{channel}:{session_id}"
    reset_session(channel_key)
    return {"status": "reset", "session_id": session_id}


@router.get("/session/{session_id}")
async def chat_session(session_id: str, channel: str = "web"):
    channel_key = f"{channel}:{session_id}"
    snap = get_session_snapshot(channel_key)
    if not snap or not snap.get("assessment"):
        return {"session": None}
    a = snap["assessment"]
    d = snap.get("last_decision")
    return {
        "status": a.status.value,
        "pathway": a.pathway.value if a.pathway else None,
        "answers_count": len(a.answers),
        "triage": d.triage.value if d else None,
        "red_flag": d.red_flag if d else None,
    }
