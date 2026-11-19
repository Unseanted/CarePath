"""
Deterministic clinical rules engine for CarePath.

All clinical decisions MUST come from this module.
The conversation layer and any LLM are never allowed to invent or override thresholds.

RULES_VERSION is recorded on every decision for auditability.
These rules are provisional and require clinician review before real-world use.
"""

from typing import Any
from uuid import uuid4

from app.models.schemas import (
    AssessmentState,
    ClinicalDecision,
    TriageCategory,
    Pathway,
)
from app.core.config import settings

RULES_VERSION = settings.RULES_VERSION

# Explicit red-flag question IDs (must match pathways.py)
RED_FLAG_QUESTION_IDS = {"severe_pain", "sudden_swelling", "fever_with_pain"}


def _answers_dict(assessment: AssessmentState) -> dict[str, Any]:
    return {a.question_id: a.value for a in assessment.answers}


def _has_red_flag(answers: dict[str, Any]) -> bool:
    """Any true value on a red-flag question triggers urgent path."""
    for qid in RED_FLAG_QUESTION_IDS:
        val = answers.get(qid)
        if val is True or val == "yes" or val == 1:
            return True
    return False


def _risk_signal_count(answers: dict[str, Any]) -> int:
    """Count modest risk signals (not red flags). Provisional logic."""
    count = 0
    age = answers.get("age_band")
    if age in ("35_44", "45_plus"):
        count += 1
    if answers.get("prior_semen_test") == "abnormal":
        count += 2
    if answers.get("duration_trying") == "gt_12m":
        count += 1
    known = answers.get("known_condition")
    if known:
        if isinstance(known, list):
            if any(k in ("varicocele", "prior_infection_or_injury", "hormone_condition") for k in known):
                count += 1
        elif known in ("varicocele", "prior_infection_or_injury", "hormone_condition"):
            count += 1
    if answers.get("lifestyle_smoking") == "yes":
        count += 1
    return count


def _build_factors(answers: dict[str, Any], red_flag: bool) -> list[str]:
    factors: list[str] = []
    if red_flag:
        factors.append("One or more urgent warning signs were reported.")
        return factors

    age = answers.get("age_band")
    if age in ("35_44", "45_plus"):
        factors.append("Age-related factor noted.")
    if answers.get("prior_semen_test") == "abnormal":
        factors.append("Previous abnormal or unclear test result mentioned.")
    if answers.get("duration_trying") == "gt_12m":
        factors.append("Duration of trying to conceive exceeds 12 months.")
    known = answers.get("known_condition")
    if known and known != "none":
        factors.append("Relevant medical or anatomical history noted.")
    if answers.get("lifestyle_smoking") == "yes":
        factors.append("Current tobacco use reported.")

    if not factors:
        factors.append("No elevated risk signals identified in the information provided.")
    return factors


def _service_types(triage: TriageCategory) -> list[str]:
    return {
        TriageCategory.EDUCATION: ["general_information"],
        TriageCategory.PRIMARY_CARE: ["primary_care", "gp"],
        TriageCategory.SPECIALIST: ["andrology", "urology", "fertility_clinic"],
        TriageCategory.URGENT: ["urgent_care", "emergency"],
        TriageCategory.OUT_OF_SCOPE: ["clinician_direct"],
    }.get(triage, ["clinician_direct"])


def _summary(triage: TriageCategory) -> str:
    return {
        TriageCategory.EDUCATION: (
            "Based on the information shared, general reproductive health information "
            "appears appropriate at this stage. This is not a diagnosis."
        ),
        TriageCategory.PRIMARY_CARE: (
            "A discussion with a primary care clinician is a suitable next step. "
            "This service does not diagnose conditions."
        ),
        TriageCategory.SPECIALIST: (
            "Seeing a reproductive health specialist (andrology/urology or fertility service) "
            "is recommended based on the factors identified. This is a navigation suggestion, not a diagnosis."
        ),
        TriageCategory.URGENT: (
            "The information provided includes warning signs that require prompt medical attention. "
            "Please seek urgent care or emergency services without delay."
        ),
        TriageCategory.OUT_OF_SCOPE: (
            "This concern is outside the scope of the current assessment. "
            "Please speak with a qualified healthcare professional."
        ),
    }[triage]


def evaluate(assessment: AssessmentState) -> ClinicalDecision:
    """
    Produce a ClinicalDecision from a completed AssessmentState.
    This is the single source of clinical truth for the prototype.
    """
    answers = _answers_dict(assessment)
    red_flag = _has_red_flag(answers)

    if red_flag:
        triage = TriageCategory.URGENT
    else:
        signals = _risk_signal_count(answers)
        pathway = assessment.pathway

        if pathway == Pathway.FIND_PROFESSIONAL:
            triage = TriageCategory.PRIMARY_CARE
        elif signals >= 3 or (pathway == Pathway.FERTILITY and signals >= 2):
            triage = TriageCategory.SPECIALIST
        elif signals >= 1 or pathway in (Pathway.FERTILITY, Pathway.SYMPTOMS):
            triage = TriageCategory.PRIMARY_CARE
        else:
            triage = TriageCategory.EDUCATION

    factors = _build_factors(answers, red_flag)

    return ClinicalDecision(
        triage=triage,
        explanation_factors=factors,
        next_step_summary=_summary(triage),
        recommended_service_types=_service_types(triage),
        red_flag=red_flag,
        rules_version=RULES_VERSION,
        decision_id=str(uuid4()),
    )
