# CarePath

**Mobile-first reproductive health navigation**  
*Future Health Digital Innovation Challenge 2026 — Male Reproductive Health*

> From a private question to a clinically appropriate next step.

**Channels:** Web chat (live) · Telegram bot · WhatsApp architecture (optional)

[![Prototype](https://img.shields.io/badge/status-prototype-blue)]()
[![Next.js](https://img.shields.io/badge/Next.js-14-black)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)]()

---

## Quick start (demo in ~5 minutes)

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
export CAREPATH_USE_SQLITE=1
uvicorn app.main:app --reload --port 8000
```

Health: http://localhost:8000/health  
Docs: http://localhost:8000/docs  

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.example .env.local         # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open: **http://localhost:3000**

### 3. Telegram bot (optional)

1. Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy token  
2. Put token in `backend/.env`: `TELEGRAM_BOT_TOKEN=...`  
3. Run (no public URL needed):

```bash
cd backend && source .venv/bin/activate
python scripts/run_telegram_poll.py
```

Message your bot: `hello` → full CarePath journey.

---

## Architecture

```
┌─────────────────┐   ┌──────────────────┐
│  Next.js Web    │   │  Telegram Bot    │
│  Chat UI        │   │  (poll/webhook)  │
└────────┬────────┘   └────────┬─────────┘
         │  POST /api/chat     │
         └──────────┬──────────┘
                    ▼
            FastAPI CarePath
         ┌──────────────────────┐
         │ conversation engine  │
         │ assessment state     │
         │ rules engine (v0.1)  │
         │ provider matching    │
         └──────────────────────┘
```

**Clinical decisions never come from an LLM** — only from the versioned rules engine.

---

## Theme

- **Charcoal** `#121212` base  
- **Yellow accent** `#F5C518`  
- Typography: Space Grotesk (display) + Inter (body)  
- GSAP message / hero motion  
- Unsplash clinical backgrounds with dark overlays  

---

## API surface

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness |
| `POST` | `/api/chat` | Web chat message |
| `POST` | `/api/chat/reset` | Reset session |
| `POST` | `/telegram/webhook` | Telegram updates |
| `GET` | `/telegram/me` | Bot identity check |
| `GET/POST` | `/webhook` | WhatsApp (optional) |
| `GET` | `/clinician/*` | Metrics (API key) |

### Chat request body

```json
{ "session_id": "uuid", "text": "hello", "channel": "web" }
```

---

## Tests

```bash
cd backend
pytest tests/ -v
python scripts/run_synthetic_eval.py
```

---

## Repo layout

```
CarePath/
├── backend/          FastAPI + rules + Telegram + chat API
├── frontend/         Next.js 14 + Tailwind + GSAP
├── docs/             Strategy, evaluation, privacy, checklists
├── pitch/            Pitch deck PPTX + PDF
├── README.md
└── LICENSE
```

---

## Environment

**Backend `.env`**

```env
CAREPATH_USE_SQLITE=1
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
TELEGRAM_BOT_TOKEN=
CLINICIAN_API_KEY=carepath-clinician-dev-key
```

**Frontend `.env.local`**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Disclaimer

Prototype for evaluation only. Does **not** diagnose conditions or predict fertility. Clinical rules require qualified review before real-world use.

---

*Deadline target: 20 November 2026 · CarePath team*
