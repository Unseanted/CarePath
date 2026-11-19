# CarePath Evaluation Report
**Future Health Digital Innovation Challenge 2026 – Male Reproductive Health**

**Prototype version:** 0.1.0-hackathon  
**Date:** 2026-11-03  
**Evaluation set:** Synthetic patient suite (N = 10)  
**Rules engine version:** `2026-11-prototype-v0.1`

---

## 1. Summary metrics

| Metric | Observed |
|--------|----------|
| Cases run | 10 |
| Triage + red-flag accuracy | **10/10** (100%) |
| Red-flag sensitivity | **3/3** (target 100%) |
| Rules version recorded on every decision | Yes |
| Screening disclaimer present | Yes |

## 2. Mapping to Challenge “Your solution should” requirements

| # | Required attribute | How tested | Result |
|---|--------------------|------------|--------|
| 1 | Earlier, explainable risk identification | Synthetic cases with known signals; inspect factors + disclaimer | Pass – factors listed; screening ≠ diagnosis |
| 2 | Culturally trusted experience | Neutral language in prompts & recommendations; no family-status assumptions | Pass – reviewed in message templates |
| 3 | Lower-friction assessment | End-to-end CLI / demo journey completion | Pass – consent → pathway → questions → result |
| 4 | Safe triage and referral | Red-flag cases force urgent; non-urgent never escalate incorrectly | Pass – 100% red-flag sensitivity |
| 5 | Privacy by design | Consent gate enforced before sensitive questions | Pass – unit tests for consent states |
| 6 | Demonstrable value | Assessment completion, triage accuracy, referral matching | Pass – metrics above |

## 3. Case-level results

### `case-edu-01` – PASS
- **Description:** Young adult, no risk signals, general pathway
- **Pathway:** `general_reproductive_health`
- **Expected:** triage=`education`, red_flag=False
- **Got:** triage=`education`, red_flag=False
- **Factors:** ['No elevated risk signals identified in the information provided.']
- **Summary:** Based on the information shared, general reproductive health information appears appropriate at this stage. This is not a diagnosis.

### `case-edu-02` – PASS
- **Description:** Under 25, general, minimal history
- **Pathway:** `general_reproductive_health`
- **Expected:** triage=`education`, red_flag=False
- **Got:** triage=`education`, red_flag=False
- **Factors:** ['No elevated risk signals identified in the information provided.']
- **Summary:** Based on the information shared, general reproductive health information appears appropriate at this stage. This is not a diagnosis.

### `case-urgent-01` – PASS
- **Description:** Severe testicular pain – must escalate
- **Pathway:** `symptoms_or_concern`
- **Expected:** triage=`urgent`, red_flag=True
- **Got:** triage=`urgent`, red_flag=True
- **Factors:** ['One or more urgent warning signs were reported.']
- **Summary:** The information provided includes warning signs that require prompt medical attention. Please seek urgent care or emergency services without delay.

### `case-urgent-02` – PASS
- **Description:** Fever with scrotal pain
- **Pathway:** `symptoms_or_concern`
- **Expected:** triage=`urgent`, red_flag=True
- **Got:** triage=`urgent`, red_flag=True
- **Factors:** ['One or more urgent warning signs were reported.']
- **Summary:** The information provided includes warning signs that require prompt medical attention. Please seek urgent care or emergency services without delay.

### `case-urgent-03` – PASS
- **Description:** Sudden swelling
- **Pathway:** `symptoms_or_concern`
- **Expected:** triage=`urgent`, red_flag=True
- **Got:** triage=`urgent`, red_flag=True
- **Factors:** ['One or more urgent warning signs were reported.']
- **Summary:** The information provided includes warning signs that require prompt medical attention. Please seek urgent care or emergency services without delay.

### `case-specialist-01` – PASS
- **Description:** Older age + abnormal prior test + long trying duration
- **Pathway:** `fertility_concerns`
- **Expected:** triage=`specialist`, red_flag=False
- **Got:** triage=`specialist`, red_flag=False
- **Factors:** ['Age-related factor noted.', 'Previous abnormal or unclear test result mentioned.', 'Duration of trying to conceive exceeds 12 months.']
- **Summary:** Seeing a reproductive health specialist (andrology/urology or fertility service) is recommended based on the factors identified. This is a navigation suggestion, not a diagnosis.

### `case-specialist-02` – PASS
- **Description:** Multiple risk signals on general pathway
- **Pathway:** `general_reproductive_health`
- **Expected:** triage=`specialist`, red_flag=False
- **Got:** triage=`specialist`, red_flag=False
- **Factors:** ['Age-related factor noted.', 'Relevant medical or anatomical history noted.', 'Current tobacco use reported.']
- **Summary:** Seeing a reproductive health specialist (andrology/urology or fertility service) is recommended based on the factors identified. This is a navigation suggestion, not a diagnosis.

### `case-primary-01` – PASS
- **Description:** Moderate signal on fertility pathway
- **Pathway:** `fertility_concerns`
- **Expected:** triage=`primary_care`, red_flag=False
- **Got:** triage=`primary_care`, red_flag=False
- **Factors:** ['Age-related factor noted.']
- **Summary:** A discussion with a primary care clinician is a suitable next step. This service does not diagnose conditions.

### `case-primary-02` – PASS
- **Description:** Find professional pathway defaults toward primary care
- **Pathway:** `find_professional`
- **Expected:** triage=`primary_care`, red_flag=False
- **Got:** triage=`primary_care`, red_flag=False
- **Factors:** ['No elevated risk signals identified in the information provided.']
- **Summary:** A discussion with a primary care clinician is a suitable next step. This service does not diagnose conditions.

### `case-primary-03` – PASS
- **Description:** Single age signal on general pathway
- **Pathway:** `general_reproductive_health`
- **Expected:** triage=`primary_care`, red_flag=False
- **Got:** triage=`primary_care`, red_flag=False
- **Factors:** ['Age-related factor noted.']
- **Summary:** A discussion with a primary care clinician is a suitable next step. This service does not diagnose conditions.

## 4. Safety & Responsible AI checks

- [x] LLM never overrides rules-engine decision (no LLM in clinical path)
- [x] All clinical thresholds come from versioned rules file
- [x] Out-of-scope / limitations acknowledged in user-facing text
- [x] No fertility “score” or diagnostic language in outputs
- [x] Human-oversight / urgent escalation message present
- [x] Red-flag short-circuit implemented (assessment completes on urgent sign)

## 5. Limitations statement

- Clinical rules are **provisional** and require review/approval by qualified clinicians before any real-world use.
- Provider directory is **simulated** for the prototype.
- Evaluation uses **synthetic cases only**; real-user performance is unknown.
- WhatsApp device previews and linked devices remain user-side risks outside our control.
- No claim is made of diagnostic accuracy, fertility prediction, or clinical outcome improvement.

## 6. Next steps toward pilot

1. Clinical review of questionnaire and rules (see Clinician Review Checklist).
2. Formal privacy / data-protection assessment for the target jurisdiction.
3. Partnership discussions with clinics / andrology services.
4. Controlled pilot with explicit consent and human oversight.
5. Measurement of real referral completion and user trust.

---
*Generated by `scripts/generate_eval_report.py` on 2026-11-03T11:55:40.261556+00:00*