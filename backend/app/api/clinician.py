"""
Protected clinician endpoints (in-memory primary for prototype reliability).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Header, Depends
from app.core.config import settings
from app.services.conversation import _SESSIONS

router = APIRouter()


async def require_clinician_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    expected = settings.CLINICIAN_API_KEY
    if expected and x_api_key != expected:
        if not (settings.DEBUG and not x_api_key):
            raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
    return True


@router.get("/assessments")
async def list_assessments(limit: int = Query(20, ge=1, le=100), _: bool = Depends(require_clinician_key)):
    items = []
    for sess in list(_SESSIONS.values())[:limit]:
        a = sess.get("assessment")
        d = sess.get("last_decision")
        if not a:
            continue
        items.append({
            "assessment_id": a.assessment_id,
            "user_id": a.user_id[:8] + "…",
            "pathway": a.pathway.value if a.pathway else None,
            "status": a.status.value,
            "answers_count": len(a.answers),
            "rules_version": a.rules_version,
            "decision": {
                "triage": d.triage.value,
                "red_flag": d.red_flag,
                "factors": d.explanation_factors,
            } if d else None,
            "source": "memory",
        })
    return {"count": len(items), "assessments": items}


@router.get("/metrics/summary")
async def metrics_summary(_: bool = Depends(require_clinician_key)):
    total = completed = withdrawn = urgent = specialist = primary = education = 0
    for sess in _SESSIONS.values():
        a = sess.get("assessment")
        d = sess.get("last_decision")
        if not a:
            continue
        total += 1
        if a.status.value == "completed":
            completed += 1
        if a.status.value == "withdrawn":
            withdrawn += 1
        if d:
            t = d.triage.value
            if t == "urgent":
                urgent += 1
            elif t == "specialist":
                specialist += 1
            elif t == "primary_care":
                primary += 1
            elif t == "education":
                education += 1
    return {
        "total_assessments": total,
        "completed": completed,
        "withdrawn": withdrawn,
        "by_triage": {
            "urgent": urgent,
            "specialist": specialist,
            "primary_care": primary,
            "education": education,
        },
        "rules_version": settings.RULES_VERSION,
    }
