"""Unit tests for the deterministic rules engine – product safety critical."""

from datetime import datetime, timezone
from app.models.schemas import (
    AssessmentState,
    AssessmentStatus,
    AssessmentAnswer,
    Pathway,
    TriageCategory,
)
from app.rules.engine import evaluate, RULES_VERSION


def _make(answers: dict, pathway: Pathway = Pathway.GENERAL) -> AssessmentState:
    return AssessmentState(
        assessment_id="test-1",
        user_id="user-test",
        pathway=pathway,
        status=AssessmentStatus.COMPLETED,
        answers=[
            AssessmentAnswer(question_id=k, value=v, answered_at=datetime.now(timezone.utc))
            for k, v in answers.items()
        ],
        completed_at=datetime.now(timezone.utc),
        rules_version=RULES_VERSION,
    )


def test_no_risk_signals_returns_education():
    decision = evaluate(_make({"age_band": "25_34", "trying_to_conceive": "no"}))
    assert decision.triage == TriageCategory.EDUCATION
    assert decision.red_flag is False
    assert decision.rules_version == RULES_VERSION
    assert "not a medical diagnosis" in decision.screening_disclaimer.lower() or "not a diagnosis" in decision.next_step_summary.lower()


def test_red_flag_severe_pain_forces_urgent():
    decision = evaluate(_make({"severe_pain": True, "age_band": "25_34"}, Pathway.SYMPTOMS))
    assert decision.triage == TriageCategory.URGENT
    assert decision.red_flag is True
    assert any("urgent" in f.lower() or "warning" in f.lower() for f in decision.explanation_factors)


def test_red_flag_fever_forces_urgent():
    decision = evaluate(_make({"fever_with_pain": True}, Pathway.SYMPTOMS))
    assert decision.triage == TriageCategory.URGENT
    assert decision.red_flag is True


def test_multiple_signals_suggest_specialist():
    decision = evaluate(
        _make(
            {
                "age_band": "45_plus",
                "prior_semen_test": "abnormal",
                "duration_trying": "gt_12m",
            },
            Pathway.FERTILITY,
        )
    )
    assert decision.triage == TriageCategory.SPECIALIST
    assert decision.red_flag is False


def test_fertility_pathway_with_one_signal_primary_care():
    decision = evaluate(
        _make({"age_band": "35_44", "trying_to_conceive": "yes"}, Pathway.FERTILITY)
    )
    assert decision.triage in (TriageCategory.PRIMARY_CARE, TriageCategory.SPECIALIST)


def test_decision_always_carries_rules_version_and_disclaimer():
    decision = evaluate(_make({}))
    assert decision.rules_version
    assert decision.decision_id
    assert decision.screening_disclaimer
    assert len(decision.explanation_factors) >= 1
