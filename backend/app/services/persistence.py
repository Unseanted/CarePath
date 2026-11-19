"""
Lightweight persistence for CarePath sessions and assessments.
Uses the ORM models; works with SQLite (default) or Postgres.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import AssessmentORM, ConsentORM, ReferralORM, UserSession
from app.models.schemas import (
    AssessmentState,
    AssessmentStatus,
    AssessmentAnswer,
    Pathway,
    ClinicalDecision,
    TriageCategory,
)

logger = logging.getLogger("carepath.persistence")


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def ensure_user(session: AsyncSession, user_id: str, phone_hash: str) -> UserSession:
    row = await session.get(UserSession, user_id)
    if row:
        row.updated_at = _now()
        return row
    row = UserSession(id=user_id, phone_hash=phone_hash, created_at=_now(), updated_at=_now())
    session.add(row)
    await session.flush()
    return row


async def save_consent(
    session: AsyncSession,
    user_id: str,
    consent_type: str,
    granted: bool,
    version: str,
) -> None:
    session.add(
        ConsentORM(
            user_id=user_id,
            consent_type=consent_type,
            granted=granted,
            version=version,
            timestamp=_now(),
        )
    )
    await session.flush()


def assessment_to_orm(state: AssessmentState) -> AssessmentORM:
    answers = {a.question_id: a.value for a in state.answers}
    return AssessmentORM(
        id=state.assessment_id,
        user_id=state.user_id,
        pathway=state.pathway.value if state.pathway else None,
        status=state.status.value,
        answers=answers,
        current_question_id=state.current_question_id,
        started_at=state.started_at,
        completed_at=state.completed_at,
        rules_version=state.rules_version,
        consent_assessment=state.consent_assessment,
        consent_share=state.consent_share,
        consent_reminders=state.consent_reminders,
        decision_json=None,
    )


def orm_to_assessment(row: AssessmentORM) -> AssessmentState:
    answers = [
        AssessmentAnswer(
            question_id=k,
            value=v,
            answered_at=_now(),
        )
        for k, v in (row.answers or {}).items()
    ]
    pathway = Pathway(row.pathway) if row.pathway else None
    return AssessmentState(
        assessment_id=row.id,
        user_id=row.user_id,
        pathway=pathway,
        status=AssessmentStatus(row.status),
        answers=answers,
        current_question_id=row.current_question_id,
        started_at=row.started_at,
        completed_at=row.completed_at,
        rules_version=row.rules_version,
        consent_assessment=row.consent_assessment,
        consent_share=row.consent_share,
        consent_reminders=row.consent_reminders,
    )


async def save_assessment(
    session: AsyncSession,
    state: AssessmentState,
    decision: Optional[ClinicalDecision] = None,
) -> None:
    row = await session.get(AssessmentORM, state.assessment_id)
    answers = {a.question_id: a.value for a in state.answers}
    decision_json = None
    if decision:
        decision_json = {
            "triage": decision.triage.value,
            "explanation_factors": decision.explanation_factors,
            "next_step_summary": decision.next_step_summary,
            "recommended_service_types": decision.recommended_service_types,
            "red_flag": decision.red_flag,
            "rules_version": decision.rules_version,
            "decision_id": decision.decision_id,
            "screening_disclaimer": decision.screening_disclaimer,
        }

    if row:
        row.pathway = state.pathway.value if state.pathway else None
        row.status = state.status.value
        row.answers = answers
        row.current_question_id = state.current_question_id
        row.started_at = state.started_at
        row.completed_at = state.completed_at
        row.rules_version = state.rules_version
        row.consent_assessment = state.consent_assessment
        row.consent_share = state.consent_share
        row.consent_reminders = state.consent_reminders
        if decision_json:
            row.decision_json = decision_json
    else:
        orm = assessment_to_orm(state)
        if decision_json:
            orm.decision_json = decision_json
        session.add(orm)

    # Link to user session
    user = await session.get(UserSession, state.user_id)
    if user:
        user.current_assessment_id = state.assessment_id
        user.updated_at = _now()

    await session.flush()


async def load_assessment(session: AsyncSession, assessment_id: str) -> Optional[AssessmentState]:
    row = await session.get(AssessmentORM, assessment_id)
    if not row:
        return None
    return orm_to_assessment(row)


async def load_latest_assessment(session: AsyncSession, user_id: str) -> Optional[AssessmentState]:
    user = await session.get(UserSession, user_id)
    if user and user.current_assessment_id:
        return await load_assessment(session, user.current_assessment_id)
    result = await session.execute(
        select(AssessmentORM)
        .where(AssessmentORM.user_id == user_id)
        .order_by(AssessmentORM.started_at.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    return orm_to_assessment(row) if row else None


async def save_referral(
    session: AsyncSession,
    referral_id: str,
    assessment_id: str,
    user_id: str,
    decision_id: str,
    provider_id: Optional[str] = None,
    status: str = "requested",
) -> None:
    session.add(
        ReferralORM(
            id=referral_id,
            assessment_id=assessment_id,
            user_id=user_id,
            decision_id=decision_id,
            provider_id=provider_id,
            status=status,
            created_at=_now(),
            updated_at=_now(),
        )
    )
    await session.flush()
