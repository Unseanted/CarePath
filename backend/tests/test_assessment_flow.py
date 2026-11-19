"""Tests for assessment state machine and consent gates."""

from app.services import assessment as assess_svc
from app.models.schemas import AssessmentStatus, Pathway


def test_new_assessment_starts_at_consent():
    state = assess_svc.new_assessment("user-1")
    assert state.status == AssessmentStatus.AWAITING_CONSENT
    assert state.consent_assessment is False


def test_consent_granted_moves_to_pathway():
    state = assess_svc.new_assessment("user-1")
    state = assess_svc.apply_consent_assessment(state, True)
    assert state.status == AssessmentStatus.AWAITING_PATHWAY
    assert state.consent_assessment is True


def test_consent_denied_withdraws():
    state = assess_svc.new_assessment("user-1")
    state = assess_svc.apply_consent_assessment(state, False)
    assert state.status == AssessmentStatus.WITHDRAWN


def test_pathway_starts_questions():
    state = assess_svc.new_assessment("user-1")
    state = assess_svc.apply_consent_assessment(state, True)
    state = assess_svc.set_pathway(state, Pathway.GENERAL)
    assert state.status == AssessmentStatus.IN_PROGRESS
    assert state.current_question_id is not None
    q = assess_svc.current_question(state)
    assert q is not None
    assert "prompt" in q


def test_answering_advances_and_completes():
    state = assess_svc.new_assessment("user-1")
    state = assess_svc.apply_consent_assessment(state, True)
    state = assess_svc.set_pathway(state, Pathway.FIND_PROFESSIONAL)  # short path

    # Answer the single age_band question
    state, err = assess_svc.record_answer(state, "2")
    assert err is None
    assert state.status == AssessmentStatus.COMPLETED
    assert len(state.answers) == 1
    assert state.answers[0].value == "25_34"
