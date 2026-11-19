# CarePath – Privacy by Design Mapping

Maps prototype controls to the Challenge emphasis on privacy, consent, and responsible AI.

| Challenge expectation | CarePath control | Where implemented |
|----------------------|------------------|-------------------|
| Explicit consent before sensitive collection | Multi-stage consent gate; assessment questions blocked until `YES` | `conversation.py`, `assessment.py` |
| Data minimisation | Structured answers only; no free-text diagnosis fields; phone stored as HMAC hash | `security.hash_phone`, schemas |
| User control / withdrawal | `STOP` / `NO` withdraws; mid-flow exit supported | Conversation state machine |
| Separate consents | Assessment, share-with-provider, reminders tracked independently | `AssessmentState` flags + `ConsentORM` |
| Purpose limitation | Data used only for navigation / triage / referral tracking | Product design + disclaimer text |
| Auditability | Rules version + decision_id on every clinical outcome | `rules/engine.py` |
| Screening ≠ diagnosis | Fixed disclaimer on every recommendation | `ClinicalDecision.screening_disclaimer` |
| No diagnostic AI claims | LLM (if any) cannot override rules; current prototype uses no LLM for decisions | Architecture separation |
| Clinician visibility with least privilege | Clinician API requires `X-API-Key`; user IDs truncated in responses | `api/clinician.py` |
| Retention | Prototype stores only active assessment state; production must define explicit retention + deletion | Deployment Notes §5 |

**User-facing privacy statements (prototype)**

- Welcome message explains the service does not diagnose and requests consent before assessment.
- Recommendation always includes the screening disclaimer.
- Optional reminders require a separate affirmative reply.

**Residual risks (acknowledged)**

- WhatsApp device-side access (linked devices, notifications) is outside app control.
- Meta processes message content under its own terms.
- Synthetic evaluation does not prove real-world privacy performance.

*This document is part of the CarePath submission package for the Future Health Digital Innovation Challenge 2026.*
