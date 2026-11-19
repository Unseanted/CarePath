"""Edge cases: invalid answers, mid-flow withdrawal, multi-select, restart."""

from app.services import assessment as assess_svc
from app.services.conversation import process_message, reset_session, _get_or_create_session
from app.models.schemas import AssessmentStatus, Pathway
import asyncio


def test_invalid_answer_rejects_and_stays_on_question():
    state = assess_svc.new_assessment("edge-1")
    state = assess_svc.apply_consent_assessment(state, True)
    state = assess_svc.set_pathway(state, Pathway.GENERAL)
    q_before = state.current_question_id

    state, err = assess_svc.record_answer(state, "not-a-valid-option")
    assert err is not None
    assert "valid option" in err.lower() or "option" in err.lower()
    assert state.current_question_id == q_before
    assert state.status == AssessmentStatus.IN_PROGRESS
    assert len(state.answers) == 0


def test_multi_select_known_condition():
    state = assess_svc.new_assessment("edge-2")
    state = assess_svc.apply_consent_assessment(state, True)
    state = assess_svc.set_pathway(state, Pathway.GENERAL)

    # age
    state, err = assess_svc.record_answer(state, "2")
    assert err is None
    # trying
    state, err = assess_svc.record_answer(state, "2")
    assert err is None
    # known_condition multi-select: varicocele + prior infection
    state, err = assess_svc.record_answer(state, "1,2")
    assert err is None
    assert state.answers[-1].value == ["varicocele", "prior_infection_or_injury"]


async def _run_withdrawal():
    phone = "edge-withdraw"
    reset_session(phone)
    session = _get_or_create_session(phone)

    r1 = await process_message(session, "hello")
    assert "consent" in r1.lower() or "yes" in r1.lower()

    r2 = await process_message(session, "yes")
    assert "1." in r2 or "pathway" in r2.lower() or "general" in r2.lower()

    r3 = await process_message(session, "1")  # general pathway
    assert r3  # first question

    r4 = await process_message(session, "stop")
    assert "left" in r4.lower() or "exit" in r4.lower() or "stop" in r4.lower() or "care" in r4.lower()

    a = session["assessment"]
    assert a.status == AssessmentStatus.WITHDRAWN


def test_mid_flow_withdrawal():
    asyncio.get_event_loop().run_until_complete(_run_withdrawal())


async def _run_restart():
    phone = "edge-restart"
    reset_session(phone)
    session = _get_or_create_session(phone)

    await process_message(session, "hello")
    await process_message(session, "yes")
    await process_message(session, "1")
    await process_message(session, "stop")

    # Restart
    r = await process_message(session, "restart")
    assert "consent" in r.lower() or "yes" in r.lower() or "welcome" in r.lower()
    a = session["assessment"]
    assert a.status == AssessmentStatus.AWAITING_CONSENT


def test_restart_after_withdrawal():
    asyncio.get_event_loop().run_until_complete(_run_restart())
