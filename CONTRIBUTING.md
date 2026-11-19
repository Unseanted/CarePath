# Contributing to CarePath

This repository is a **hackathon prototype**. Contributions that improve safety, clarity, or evaluation quality are welcome.

## Principles

1. **Clinical decisions stay in the rules engine** — do not move triage logic into prompts or free-form LLM output.
2. **No diagnostic language** in user-facing copy.
3. **Consent before sensitive questions** must remain enforced.
4. **Tests required** for rules and assessment flow changes.
5. **Do not commit secrets** (tokens, real phone numbers, production keys).

## Local workflow

```bash
cd backend
pip install -r requirements.txt
make test
make eval
```

## Clinical changes

Updates to `app/rules/pathways.py` or `app/rules/engine.py` should:

- Bump or annotate `RULES_VERSION`
- Update synthetic cases if behaviour changes
- Be reviewed against `docs/Clinician_Review_Checklist.md`

## Pull requests

Please include:

- What changed and why
- Test output (`make test` / `make eval`)
- Any impact on privacy or clinical safety
