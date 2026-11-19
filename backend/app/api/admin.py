"""
Internal demo endpoints – allow exercising the full journey without WhatsApp.
Not for production exposure.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.config import settings
from app.services.conversation import (
    process_message,
    reset_session,
    get_session_snapshot,
    _get_or_create_session,
)

router = APIRouter()


class DemoMessage(BaseModel):
    from_number: str = Field(default="demo-user-001", description="Simulated WhatsApp number")
    text: str = Field(..., description="User message text")


@router.post("/demo/message")
async def demo_message(payload: DemoMessage):
    """Simulate an inbound WhatsApp text message and return the reply text."""
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Demo endpoints only available when DEBUG=true")

    session = _get_or_create_session(payload.from_number)
    reply = await process_message(session, payload.text)

    assessment = session.get("assessment")
    decision = session.get("last_decision")

    return {
        "reply": reply,
        "session": {
            "status": assessment.status.value if assessment else None,
            "pathway": assessment.pathway.value if assessment and assessment.pathway else None,
            "answers_count": len(assessment.answers) if assessment else 0,
            "current_question_id": assessment.current_question_id if assessment else None,
            "consent_assessment": assessment.consent_assessment if assessment else False,
        },
        "decision": {
            "triage": decision.triage.value if decision else None,
            "red_flag": decision.red_flag if decision else None,
            "rules_version": decision.rules_version if decision else None,
        }
        if decision
        else None,
    }


@router.post("/demo/reset")
async def demo_reset(from_number: str = "demo-user-001"):
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Demo endpoints only available when DEBUG=true")
    reset_session(from_number)
    return {"status": "reset", "from_number": from_number}


@router.get("/demo/session/{from_number}")
async def demo_session(from_number: str):
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Demo endpoints only available when DEBUG=true")
    snap = get_session_snapshot(from_number)
    if not snap or not snap.get("assessment"):
        return {"session": None}
    a = snap["assessment"]
    d = snap.get("last_decision")
    return {
        "user_id": a.user_id,
        "status": a.status.value,
        "pathway": a.pathway.value if a.pathway else None,
        "answers": [{"q": x.question_id, "v": x.value} for x in a.answers],
        "current_question_id": a.current_question_id,
        "consent_assessment": a.consent_assessment,
        "consent_reminders": a.consent_reminders,
        "decision": {
            "triage": d.triage.value,
            "red_flag": d.red_flag,
            "factors": d.explanation_factors,
            "summary": d.next_step_summary,
        }
        if d
        else None,
    }
