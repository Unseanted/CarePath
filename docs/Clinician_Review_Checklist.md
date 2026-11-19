# CarePath Clinician Review Checklist

**Purpose:** Structured review of the provisional questionnaire and rules engine before any real-world pilot.  
**Rules version under review:** `2026-11-prototype-v0.1`  
**Files:** `app/rules/pathways.py`, `app/rules/engine.py`

---

## A. Overall clinical safety

| # | Check | Pass / Fail / N/A | Reviewer notes |
|---|-------|-------------------|----------------|
| A1 | Product clearly states it does **not** diagnose conditions | | |
| A2 | Screening vs diagnosis distinction is explicit in every recommendation | | |
| A3 | Red-flag conditions are comprehensive enough for the intended pathway | | |
| A4 | Urgent pathway language is unambiguous and action-oriented | | |
| A5 | No fertility prediction, scoring, or “probability of conception” claims | | |
| A6 | Out-of-scope / limitations messaging is adequate | | |

## B. Question bank (`pathways.py`)

| # | Check | Pass / Fail / N/A | Reviewer notes |
|---|-------|-------------------|----------------|
| B1 | Every question is clinically justified for triage / navigation | | |
| B2 | Age bands are appropriate for the target population | | |
| B3 | Duration-of-trying thresholds align with local referral guidelines | | |
| B4 | Red-flag questions (severe pain, sudden swelling, fever + pain) are correctly specified | | |
| B5 | Wording is neutral, non-stigmatising, and culturally appropriate | | |
| B6 | Optional vs required questions are correctly marked | | |
| B7 | Multi-select options for known conditions are clinically sensible | | |
| B8 | Missing questions that should be added (list below) | | |

**Suggested additions / removals:**


## C. Rules engine (`engine.py`)

| # | Check | Pass / Fail / N/A | Reviewer notes |
|---|-------|-------------------|----------------|
| C1 | Red-flag → URGENT mapping is mandatory and cannot be overridden | | |
| C2 | Signal counting thresholds (education / primary / specialist) are clinically reasonable | | |
| C3 | Age alone does not over-escalate young healthy users | | |
| C4 | Abnormal prior semen test is weighted appropriately | | |
| C5 | Explanation factors are accurate and non-alarmist | | |
| C6 | Recommended service types match local care pathways | | |
| C7 | Rules version string is recorded on every decision | | |

**Threshold changes requested:**


## D. Referral & escalation

| # | Check | Pass / Fail / N/A | Reviewer notes |
|---|-------|-------------------|----------------|
| D1 | Urgent cases are directed to emergency / urgent care language | | |
| D2 | Specialist vs primary-care distinction is clinically meaningful | | |
| D3 | Simulated directory is clearly labelled (not real clinics) | | |
| D4 | User is never told a diagnosis has been made | | |

## E. Privacy & consent (clinical perspective)

| # | Check | Pass / Fail / N/A | Reviewer notes |
|---|-------|-------------------|----------------|
| E1 | Sensitive questions only appear after explicit assessment consent | | |
| E2 | User can withdraw mid-flow | | |
| E3 | Data minimisation is evident (no free-text diagnosis fields) | | |

## F. Sign-off

| Role | Name | Date | Signature / approval |
|------|------|------|----------------------|
| Clinical reviewer (lead) | | | |
| Second clinical reviewer (optional) | | | |
| Product / technical owner | | | |

**Decision:** ☐ Approved for synthetic evaluation only ☐ Approved for closed pilot (with conditions) ☐ Requires rework

**Conditions / rework items:**


---

*This checklist is part of the CarePath submission package for the Future Health Digital Innovation Challenge 2026.*
