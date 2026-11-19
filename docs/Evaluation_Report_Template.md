# CarePath Evaluation Report Template
**Future Health Digital Innovation Challenge 2026 – Male Reproductive Health**

**Prototype version:** [e.g. 0.1.0-hackathon]  
**Date:** [YYYY-MM-DD]  
**Evaluation set:** Synthetic patient suite (N = ___)  
**Rules engine version:** [hash / tag]  

---

## 1. Mapping to Challenge “Your solution should” requirements

| # | Required attribute | How tested | Result / observation | Evidence location |
|---|--------------------|------------|----------------------|-------------------|
| 1 | Earlier, explainable risk identification (screening ≠ diagnosis) | Synthetic cases with known risk signals; inspect explanation text and decision label | | Section 3 + case logs |
| 2 | Culturally trusted experience | Language review of prompts & responses; absence of family-status assumptions | | Conversation transcripts |
| 3 | Lower-friction assessment | End-to-end WhatsApp flow completion rate; pause/resume correctness | | Journey metrics |
| 4 | Safe triage and referral | Red-flag cases force urgent path; non-urgent cases never escalate incorrectly | | Confusion matrix / triage accuracy |
| 5 | Privacy by design | Consent stages enforced; no unauthorised data fields collected; deletion path exercised | | Consent & data audit |
| 6 | Demonstrable value | Assessment completion, time-to-recommendation, referral appropriateness | | Aggregate metrics table |

---

## 2. Synthetic Case Suite Design

Cases are constructed to exercise:

- Normal / low-risk pathways
- Moderate risk signals requiring primary-care or specialist navigation
- Explicit red-flag scenarios (urgent)
- Edge cases: incomplete answers, out-of-scope questions, withdrawal of consent mid-flow
- Cultural / linguistic sensitivity checks (neutral language, no assumed fertility goals)

Each case carries a gold-label expected triage category and expected next-step type.

**Minimum recommended set size for submission:** 20–30 labelled cases covering all triage buckets and at least 5 red-flag variants.

---

## 3. Primary Metrics (to be filled after test run)

| Metric | Definition | Target (prototype) | Observed |
|--------|------------|--------------------|----------|
| Assessment completion rate | Users who finish structured assessment / started | ≥ 80 % on synthetic | |
| Triage accuracy | Correct category vs gold label | ≥ 90 % | |
| Red-flag sensitivity | True positives / all red-flag cases | 100 % | |
| Red-flag false-positive rate | Incorrect urgent labels on non-urgent cases | Low | |
| Referral appropriateness | Recommended service type matches clinical expectation | ≥ 90 % | |
| Explanation coverage | Every recommendation includes the factors that drove it | 100 % | |
| Consent enforcement | Sensitive questions blocked without prior consent | 100 % | |
| Data-minimisation check | No extraneous sensitive fields collected | Pass | |

---

## 4. Safety & Responsible AI Checks

- [ ] LLM never overrides rules-engine decision
- [ ] All clinical thresholds come from versioned rules file
- [ ] Out-of-scope user statements produce limitation acknowledgement + clinician route
- [ ] No fertility “score” or diagnostic language appears in any output
- [ ] Human-oversight / escalation message present and reachable
- [ ] Conversation logs contain no unauthorised partner-identifying data

---

## 5. Limitations Statement (include in submission)

- Clinical rules are provisional and require review/approval by qualified clinicians before any real-world use.
- Provider directory is simulated / limited for the prototype.
- Evaluation uses synthetic cases only; real-user performance, cultural acceptance and referral completion rates are unknown.
- WhatsApp itself is outside our control; device previews and linked devices remain user-side risks.
- No claim is made of diagnostic accuracy, fertility prediction or clinical outcome improvement.

---

## 6. Next Steps Toward Pilot

1. Clinical review of questionnaire and rules.
2. Formal privacy / DPIA-style assessment for target jurisdiction.
3. Partnership discussions with clinics / andrology services.
4. Controlled pilot with explicit consent and human oversight.
5. Measurement of real referral completion and user trust.

---

*This template is part of the CarePath prototype submission package. Fill observed columns and attach case-level logs / confusion matrix as appendices.*
