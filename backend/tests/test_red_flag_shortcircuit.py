"""Early red-flag short-circuit behaviour."""

from app.services import assessment as assess_svc
from app.models.schemas import AssessmentStatus, Pathway
from app.rules.engine import evaluate
from app.models.schemas import TriageCategory


def test_severe_pain_short_circuits_to_completed():
    state = assess_svc.new_assessment("user-rf")
    state = assess_svc.apply_consent_assessment(state, True)
    state = assess_svc.set_pathway(state, Pathway.SYMPTOMS)

    # age
    state, err = assess_svc.record_answer(state, "2")
    assert err is None
    assert state.status == AssessmentStatus.IN_PROGRESS

    # trying
    state, err = assess_svc.record_answer(state, "3")
    assert err is None

    # severe pain = yes → should complete immediately
    state, err = assess_svc.record_answer(state, "1")
    assert err is None
    assert state.status == AssessmentStatus.COMPLETED
    assert state.current_question_id is None

    decision = evaluate(state)
    assert decision.triage == TriageCategory.URGENT
    assert decision.red_flag is True


def test_no_short_circuit_when_pain_is_no():
    state = assess_svc.new_assessment("user-rf2")
    state = assess_svc.apply_consent_assessment(state, True)
    state = assess_svc.set_pathway(state, Pathway.SYMPTOMS)

    state, _ = assess_svc.record_answer(state, "2")  # age
    state, _ = assess_svc.record_answer(state, "3")  # trying
    state, err = assess_svc.record_answer(state, "2")  # severe pain = no
    assert err is None
    assert state.status == AssessmentStatus.IN_PROGRESS
    assert state.current_question_id is not None
