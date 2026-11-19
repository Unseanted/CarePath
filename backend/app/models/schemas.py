"""
Pydantic schemas for CarePath.
These define the product data contracts used by services and the rules engine.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class ConsentType(str, Enum):
    ASSESSMENT = "assessment"
    SHARE_WITH_PROVIDER = "share_with_provider"
    REMINDERS = "reminders"


class AssessmentStatus(str, Enum):
    NOT_STARTED = "not_started"
    AWAITING_CONSENT = "awaiting_consent"
    AWAITING_PATHWAY = "awaiting_pathway"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    WITHDRAWN = "withdrawn"


class TriageCategory(str, Enum):
    EDUCATION = "education"
    PRIMARY_CARE = "primary_care"
    SPECIALIST = "specialist"
    URGENT = "urgent"
    OUT_OF_SCOPE = "out_of_scope"


class Pathway(str, Enum):
    GENERAL = "general_reproductive_health"
    FERTILITY = "fertility_concerns"
    SYMPTOMS = "symptoms_or_concern"
    FIND_PROFESSIONAL = "find_professional"


class ConsentRecord(BaseModel):
    user_id: str
    consent_type: ConsentType
    granted: bool
    timestamp: datetime
    version: str = "2026-11-v1"


class AssessmentAnswer(BaseModel):
    question_id: str
    value: Any
    answered_at: datetime


class AssessmentState(BaseModel):
    assessment_id: str
    user_id: str
    pathway: Optional[Pathway] = None
    status: AssessmentStatus = AssessmentStatus.NOT_STARTED
    answers: list[AssessmentAnswer] = Field(default_factory=list)
    current_question_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    rules_version: Optional[str] = None
    consent_assessment: bool = False
    consent_share: bool = False
    consent_reminders: bool = False


class ClinicalDecision(BaseModel):
    triage: TriageCategory
    explanation_factors: list[str]
    next_step_summary: str
    recommended_service_types: list[str] = Field(default_factory=list)
    red_flag: bool = False
    rules_version: str
    decision_id: str
    screening_disclaimer: str = (
        "This is a screening and navigation suggestion only. "
        "It is not a medical diagnosis and does not replace advice from a qualified healthcare professional."
    )


class Provider(BaseModel):
    provider_id: str
    name: str
    credentials: str
    services: list[str]
    location: Optional[str] = None
    teleconsultation_available: bool = False
    verified: bool = False  # True only after real credential verification


class ReferralEvent(BaseModel):
    referral_id: str
    assessment_id: str
    user_id: str
    decision_id: str
    provider_id: Optional[str] = None
    status: str  # requested | confirmed | completed | abandoned
    created_at: datetime
    updated_at: datetime


class IncomingMessage(BaseModel):
    from_number: str
    message_id: str
    timestamp: datetime
    text: Optional[str] = None
    interactive_reply: Optional[str] = None
