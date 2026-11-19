"""
Assessment state machine.
Manages pathway selection, ordered questions, pause/resume, and completion.
"""

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Optional

from app.models.schemas import (
    AssessmentState,
    AssessmentStatus,
    AssessmentAnswer,
    Pathway,
)
from app.rules.pathways import get_questions_for_pathway, PATHWAY_LABELS


def new_assessment(user_id: str) -> AssessmentState:
    return AssessmentState(
        assessment_id=str(uuid4()),
        user_id=user_id,
        status=AssessmentStatus.AWAITING_CONSENT,
        started_at=datetime.now(timezone.utc),
    )


def apply_consent_assessment(state: AssessmentState, granted: bool) -> AssessmentState:
    state.consent_assessment = granted
    if granted:
        state.status = AssessmentStatus.AWAITING_PATHWAY
    else:
        state.status = AssessmentStatus.WITHDRAWN
    return state


def set_pathway(state: AssessmentState, pathway: Pathway) -> AssessmentState:
    state.pathway = pathway
    state.status = AssessmentStatus.IN_PROGRESS
    questions = get_questions_for_pathway(pathway)
    if questions:
        state.current_question_id = questions[0]["id"]
    return state


def current_question(state: AssessmentState) -> Optional[dict]:
    if not state.pathway or not state.current_question_id:
        return None
    questions = get_questions_for_pathway(state.pathway)
    for q in questions:
        if q["id"] == state.current_question_id:
            return q
    return None


def record_answer(state: AssessmentState, raw_value: str) -> tuple[AssessmentState, Optional[str]]:
    """
    Record answer for current question and advance.
    Returns (updated_state, error_message_or_None).
    """
    q = current_question(state)
    if not q:
        return state, "No active question."

    parsed, err = _parse_answer(q, raw_value)
    if err:
        return state, err

    state.answers.append(
        AssessmentAnswer(
            question_id=q["id"],
            value=parsed,
            answered_at=datetime.now(timezone.utc),
        )
    )

    # Early red-flag short-circuit: if this answer triggers a red flag,
    # complete the assessment immediately so urgent triage can run.
    if q.get("red_flag_if") is not None and parsed == q.get("red_flag_if"):
        state.current_question_id = None
        state.status = AssessmentStatus.COMPLETED
        state.completed_at = datetime.now(timezone.utc)
        return state, None

    # Advance to next unanswered required question
    questions = get_questions_for_pathway(state.pathway)  # type: ignore
    answered_ids = {a.question_id for a in state.answers}
    next_q = None
    for candidate in questions:
        if candidate["id"] not in answered_ids:
            if candidate.get("required", True) or candidate["id"] not in answered_ids:
                next_q = candidate
                break

    if next_q:
        state.current_question_id = next_q["id"]
    else:
        state.current_question_id = None
        state.status = AssessmentStatus.COMPLETED
        state.completed_at = datetime.now(timezone.utc)

    return state, None


def _parse_answer(q: dict, raw: str) -> tuple[Any, Optional[str]]:
    raw = (raw or "").strip().lower()
    qtype = q.get("type", "text")

    if qtype == "text":
        return raw or "none", None

    options = q.get("options") or {}
    # Accept numeric key or value
    if raw in options:
        return options[raw], None
    for k, v in options.items():
        if str(v).lower() == raw or k == raw:
            return v, None

    # Multi-choice (comma-separated numbers)
    if qtype == "choice_multi":
        parts = [p.strip() for p in raw.replace(" ", "").split(",") if p.strip()]
        values = []
        for p in parts:
            if p in options:
                values.append(options[p])
            else:
                return None, f"Please reply with valid option number(s). Options: {', '.join(options.keys())}"
        return values or ["none"], None

    return None, f"Please reply with a valid option number. Options: {', '.join(options.keys())}"
