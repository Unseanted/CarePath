# CarePath Deployment Notes

**Prototype status:** Local / demo ready. Not production-hardened.

---

## 1. Local quick start (SQLite, no external services)

```bash
unzip carepath_scaffold.zip && cd carepath_scaffold
pip install -r requirements.txt
cp .env.example .env
export CAREPATH_USE_SQLITE=1
make run
# or: uvicorn app.main:app --reload --port 8000
```

- Health: http://localhost:8000/health  
- OpenAPI docs (DEBUG): http://localhost:8000/docs  
- CLI demo (no server): `python scripts/chat_simulator.py`  
- HTTP demo (server running): `python scripts/http_demo.py`

---

## 2. WhatsApp Cloud API setup (for live messaging)

1. Create a Meta Developer app and add the **WhatsApp** product.
2. Create / select a WhatsApp Business test number.
3. In `.env` set:
   ```
   WHATSAPP_VERIFY_TOKEN=<your-chosen-verify-string>
   WHATSAPP_ACCESS_TOKEN=<temporary or system user token>
   WHATSAPP_PHONE_NUMBER_ID=<phone-number-id from Meta>
   ```
4. Expose your local server (e.g. ngrok):
   ```bash
   ngrok http 8000
   ```
5. In Meta webhook configuration:
   - Callback URL: `https://<ngrok-id>.ngrok.io/webhook`
   - Verify token: same as `WHATSAPP_VERIFY_TOKEN`
   - Subscribe to `messages`
6. Send a message from the Meta test phone numbers to your business number.

**Notes**
- Webhook must respond 200 quickly; processing is backgrounded.
- Interactive buttons are supported in code (`send_interactive_buttons`) but the default conversation still uses plain text for maximum compatibility.
- Never commit real tokens to version control.

---

## 3. Optional Postgres

```bash
docker compose up -d db
# in .env:
CAREPATH_USE_SQLITE=0
DATABASE_URL=postgresql+asyncpg://carepath:carepath@localhost:5432/carepath
```

Tables are created on startup via `init_db()` (prototype convenience). Prefer Alembic migrations for production.

---

## 4. Clinician endpoints

Require header: `X-API-Key: <CLINICIAN_API_KEY>`

```
GET /clinician/assessments
GET /clinician/assessments/{id}
GET /clinician/referrals
GET /clinician/metrics/summary
```

Default dev key: `carepath-clinician-dev-key` (change before any shared environment).

---

## 5. Security & privacy checklist before any pilot

- [ ] Rotate `SECRET_KEY` and `CLINICIAN_API_KEY`
- [ ] Disable `DEBUG` (hides `/docs` and relaxes some checks)
- [ ] Confirm WhatsApp webhook signature verification is implemented and enforced
- [ ] Confirm retention / deletion policy is coded and documented
- [ ] Complete clinical review (Clinician_Review_Checklist.md)
- [ ] Legal review of consent wording for the target jurisdiction
- [ ] No real patient data in logs

---

## 6. What is intentionally not production-ready

- In-memory session store is primary for the interactive demo
- Webhook signature verification is a placeholder
- No rate limiting, WAF, or formal authN/Z beyond API key
- Provider directory is simulated
- Clinical rules are provisional

See Strategy Document § limitations and the Evaluation Report for the full boundary statement.
