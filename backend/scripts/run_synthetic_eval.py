#!/usr/bin/env python3
"""
Run the synthetic case suite against the rules engine and print a summary
suitable for the Evaluation Report Template.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.models.schemas import AssessmentState, AssessmentStatus, AssessmentAnswer, Pathway
from app.rules.engine import evaluate, RULES_VERSION

FIXTURE = ROOT / "tests" / "fixtures" / "synthetic_cases.json"


def main() -> None:
    cases = json.loads(FIXTURE.read_text())
    print(f"CarePath synthetic evaluation  |  rules={RULES_VERSION}")
    print(f"Cases: {len(cases)}\n")

    passed = 0
    failed = []

    for case in cases:
        answers = [
            AssessmentAnswer(question_id=k, value=v, answered_at=datetime.now(timezone.utc))
            for k, v in case["answers"].items()
        ]
        state = AssessmentState(
            assessment_id=case["id"],
            user_id="synthetic",
            pathway=Pathway(case["pathway"]),
            status=AssessmentStatus.COMPLETED,
            answers=answers,
            completed_at=datetime.now(timezone.utc),
        )
        decision = evaluate(state)

        triage_ok = decision.triage.value == case["expected_triage"]
        flag_ok = decision.red_flag == case["expected_red_flag"]
        ok = triage_ok and flag_ok

        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed.append(case["id"])

        print(f"[{status}] {case['id']}: {case['description']}")
        print(f"         expected triage={case['expected_triage']} red_flag={case['expected_red_flag']}")
        print(f"         got      triage={decision.triage.value} red_flag={decision.red_flag}")
        print(f"         factors: {decision.explanation_factors}")
        print()

    print("=" * 60)
    print(f"Result: {passed}/{len(cases)} passed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)
    print("All synthetic cases passed.")
    print("\nReminder: these rules are provisional and require clinician review.")


if __name__ == "__main__":
    main()
