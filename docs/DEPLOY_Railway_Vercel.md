# CarePath — Deploy Notes (Railway + Vercel)

Ship a public demo URL for judges without local setup.

```
Frontend (Vercel)  →  https://carepath-xxx.vercel.app
        │
        │  NEXT_PUBLIC_API_URL
        ▼
Backend  (Railway) →  https://carepath-api-xxx.up.railway.app
```

---

## A. Backend on Railway

1. Push the `CarePath` repo to GitHub (or deploy from CLI).
2. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**  
   - Root directory: `backend`
3. **Variables** (Settings → Variables):

| Variable | Value |
|----------|--------|
| `CAREPATH_USE_SQLITE` | `1` |
| `DEBUG` | `true` |
| `SECRET_KEY` | long random string |
| `CORS_ORIGINS` | `https://YOUR-VERCEL-APP.vercel.app,http://localhost:3000` |
| `CLINICIAN_API_KEY` | change from default |
| `TELEGRAM_BOT_TOKEN` | optional, from BotFather |
| `PORT` | Railway sets this — don’t hardcode |

4. **Start command** (if not auto-detected):

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Generate a public domain: Settings → Networking → **Generate domain**.  
   Example: `https://carepath-api-production.up.railway.app`

6. Test:  
   `https://YOUR-RAILWAY-URL/health` → should return JSON `status: ok`

### Telegram on Railway (optional)

After the API is public:

```bash
# From any machine with the token, once:
curl -X POST "https://YOUR-RAILWAY-URL/telegram/set-webhook?public_base_url=https://YOUR-RAILWAY-URL"
```

Or keep using long-poll locally for demos; webhook is better for always-on.

---

## B. Frontend on Vercel

1. [vercel.com](https://vercel.com) → **Add New Project** → import the same GitHub repo.
2. **Root directory:** `frontend`
3. Framework: **Next.js** (auto)
4. **Environment variable:**

| Name | Value |
|------|--------|
| `NEXT_PUBLIC_API_URL` | `https://YOUR-RAILWAY-URL` (no trailing slash) |

5. Deploy.
6. Copy the Vercel URL, e.g. `https://carepath-web.vercel.app`

7. **Update Railway CORS** so it includes the real Vercel URL, then redeploy backend if needed.

---

## C. CORS checklist

Backend `CORS_ORIGINS` must list the exact frontend origin:

```env
CORS_ORIGINS=https://carepath-web.vercel.app,http://localhost:3000
```

No trailing slash. After changing, restart/redeploy the API.

---

## D. Local → production parity test

```bash
# Health
curl -s https://YOUR-RAILWAY-URL/health

# Chat
curl -s -X POST https://YOUR-RAILWAY-URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo-judge-1","text":"hello","channel":"web"}'
```

You should see the consent welcome message in JSON.

---

## E. Free-tier gotchas

| Platform | Watch for |
|----------|-----------|
| Railway | Sleep on free tier after idle — hit `/health` before the demo |
| Vercel | `NEXT_PUBLIC_*` is baked in at **build** time — change URL → redeploy frontend |
| SQLite on Railway | Ephemeral filesystem: data resets on redeploy (fine for prototype) |
| Cold start | First request after sleep may take 5–10s — open the site once before presenting |

**Pre-demo ritual:** open the live URL once, send `hello`, confirm a reply, then start the pitch.

---

## F. Minimal GitHub layout for deploy

```
CarePath/
  backend/     ← Railway root
  frontend/    ← Vercel root
  docs/
  pitch/
  README.md
```

Do not set the monorepo root as the only app unless you configure both services with correct subdirectories.

---

## G. Emergency backup (no deploy)

If cloud deploy fails on demo day:

1. Run backend + frontend locally  
2. Use **ngrok** for the API only if needed: `ngrok http 8000`  
3. Point `NEXT_PUBLIC_API_URL` at the ngrok HTTPS URL and restart `npm run dev`  
4. Or screen-share localhost — judges accept this for hackathons  

---

## H. Demo URLs to put on the pitch slide

```
Web app:  https://……vercel.app
API:      https://……railway.app/health
Telegram: @YourCarePathBot (if live)
```

---

*Prototype only · Not medical advice · Rules version 2026-11-prototype-v0.1*
