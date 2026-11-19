"""
Conversation manager – orchestrates the full CarePath patient journey.

Flow:
  1. Welcome + assessment consent
  2. Pathway selection
  3. Structured questions (state machine)
  4. Rules evaluation
  5. Explainable recommendation + simulated providers
  6. Optional reminder consent / close

All clinical decisions come from the rules engine.
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.security import hash_phone
from app.models.schemas import Pathway, AssessmentStatus
from app.rules.engine import evaluate
from app.services import assessment as assess_svc
from app.services.providers import match_providers, format_provider_list
from app.services.whatsapp import (
    send_text,
    welcome_message,
    pathway_choice_message,
    recommendation_message,
)

logger = logging.getLogger("carepath.conversation")

# In-memory session store for the prototype (replace with DB in production)
_SESSIONS: dict[str, Any] = {}


def _get_or_create_session(phone: str) -> dict:
    uid = hash_phone(phone)
    if uid not in _SESSIONS:
        _SESSIONS[uid] = {
            "user_id": uid,
            "phone": phone,
            "assessment": None,
            "last_decision": None,
        }
    return _SESSIONS[uid]


async def handle_incoming_message(msg: dict, value: dict) -> None:
    """
    Entry point for every inbound WhatsApp message.
    Expected Meta message shape (simplified).
    """
    from_number = msg.get("from")
    if not from_number:
        return

    text = ""
    if msg.get("type") == "text":
        text = (msg.get("text") or {}).get("body", "").strip()
    elif msg.get("type") == "interactive":
        interactive = msg.get("interactive") or {}
        text = (
            (interactive.get("button_reply") or {}).get("id")
            or (interactive.get("list_reply") or {}).get("id")
            or ""
        )

    if not text:
        return

    session = _get_or_create_session(from_number)
    reply = await process_message(session, text)
    if reply:
        await send_text(from_number, reply)


async def process_message(session: dict, text: str) -> str:
    """
    Pure conversation processor – used by both WhatsApp webhook and demo/CLI.
    Returns the reply text to send to the user.
    """
    raw = text.strip()
    lower = raw.lower()
    assessment = session.get("assessment")

    # Global exit / restart
    if lower in ("stop", "exit", "quit", "cancel"):
        if assessment:
            assessment.status = AssessmentStatus.WITHDRAWN
        return (
            "You have left the CarePath assessment. "
            "You can message again any time to restart. Take care."
        )

    if lower in ("restart", "start", "hi", "hello", "hey") and (
        assessment is None
        or assessment.status
        in (
            AssessmentStatus.NOT_STARTED,
            AssessmentStatus.WITHDRAWN,
            AssessmentStatus.ABANDONED,
            AssessmentStatus.COMPLETED,
        )
    ):
        session["assessment"] = assess_svc.new_assessment(session["user_id"])
        session["last_decision"] = None
        return welcome_message()

    # New or restarted session
    if assessment is None or assessment.status in (
        AssessmentStatus.NOT_STARTED,
        AssessmentStatus.WITHDRAWN,
        AssessmentStatus.ABANDONED,
    ):
        session["assessment"] = assess_svc.new_assessment(session["user_id"])
        session["last_decision"] = None
        return welcome_message()

    state = session["assessment"]

    # --- Consent gate ---
    if state.status == AssessmentStatus.AWAITING_CONSENT:
        if lower in ("yes", "y", "ok", "agree", "i agree", "continue"):
            state = assess_svc.apply_consent_assessment(state, True)
            session["assessment"] = state
            return pathway_choice_message()
        if lower in ("no", "n", "nope"):
            state = assess_svc.apply_consent_assessment(state, False)
            session["assessment"] = state
            return (
                "Understood. No information has been stored for an assessment. "
                "Message again if you change your mind."
            )
        return "Please reply *YES* to continue with a private assessment, or *NO* to exit."

    # --- Pathway selection ---
    if state.status == AssessmentStatus.AWAITING_PATHWAY:
        mapping = {
            "1": Pathway.GENERAL,
            "2": Pathway.FERTILITY,
            "3": Pathway.SYMPTOMS,
            "4": Pathway.FIND_PROFESSIONAL,
            "general": Pathway.GENERAL,
            "fertility": Pathway.FERTILITY,
            "symptoms": Pathway.SYMPTOMS,
            "find": Pathway.FIND_PROFESSIONAL,
        }
        pathway = mapping.get(lower)
        if not pathway:
            return pathway_choice_message()
        state = assess_svc.set_pathway(state, pathway)
        session["assessment"] = state
        q = assess_svc.current_question(state)
        if q:
            return (
                f"You selected: *{pathway.value.replace('_', ' ')}*.\n\n"
                f"{q['prompt']}"
            )
        return "Something went wrong loading questions. Please reply STOP and try again."

    # --- In-progress assessment ---
    if state.status == AssessmentStatus.IN_PROGRESS:
        state, err = assess_svc.record_answer(state, raw)
        session["assessment"] = state
        if err:
            q = assess_svc.current_question(state)
            prompt = q["prompt"] if q else ""
            return f"{err}\n\n{prompt}"

        if state.status == AssessmentStatus.COMPLETED:
            return await _finalise(session, state)

        q = assess_svc.current_question(state)
        if q:
            return q["prompt"]
        return "Assessment complete."

    # --- After recommendation ---
    if state.status == AssessmentStatus.COMPLETED:
        if lower in ("remind", "reminder", "yes remind"):
            state.consent_reminders = True
            session["assessment"] = state
            return (
                "Optional follow-up reminder noted (prototype only – "
                "no real reminder will be sent yet).\n\n"
                "Reply *DONE* when finished, or *RESTART* to begin a new assessment."
            )
        if lower in ("done", "finish", "thanks", "thank you"):
            return (
                "Thank you for using CarePath. "
                "This service does not diagnose conditions. Take care.\n\n"
                "Reply *RESTART* any time to begin again."
            )
        return (
            "Assessment complete. Reply *DONE* to finish, "
            "*REMIND* for an optional follow-up reminder (prototype only), "
            "or *RESTART* to start over."
        )

    return welcome_message()


async def _finalise(session: dict, state) -> str:
    """Run rules engine and return explainable recommendation."""
    decision = evaluate(state)
    state.rules_version = decision.rules_version
    session["assessment"] = state
    session["last_decision"] = decision

    # Best-effort persistence + referral record (non-fatal if DB unavailable)
    try:
        from uuid import uuid4
        from app.db.session import async_session_factory
        from app.services import persistence as pers
        from app.services.providers import match_providers
        async with async_session_factory() as db:
            await pers.ensure_user(db, state.user_id, state.user_id)
            await pers.save_assessment(db, state, decision)
            matched = match_providers(decision, limit=1)
            provider_id = matched[0].provider_id if matched else None
            await pers.save_referral(
                db,
                referral_id=str(uuid4()),
                assessment_id=state.assessment_id,
                user_id=state.user_id,
                decision_id=decision.decision_id,
                provider_id=provider_id,
                status="requested" if not decision.red_flag else "urgent_flagged",
            )
            await db.commit()
    except Exception as exc:
        logger.debug("Persistence skipped: %s", exc)

    providers = match_providers(decision)
    provider_text = format_provider_list(providers)
    return recommendation_message(decision, provider_text)


def reset_session(phone: str) -> None:
    uid = hash_phone(phone)
    _SESSIONS.pop(uid, None)


def get_session_snapshot(phone: str) -> dict | None:
    uid = hash_phone(phone)
    return _SESSIONS.get(uid)
