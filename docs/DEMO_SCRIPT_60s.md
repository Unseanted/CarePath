# CarePath — 60-Second Demo Script

**Goal:** Show a working product: consent → assessment → deterministic triage → next step.  
**Channels:** Web chat (primary) or Telegram.  
**Time:** ~60–75 seconds if practiced once.

---

## Before you start (30 seconds setup)

1. Backend running: `http://localhost:8000/health` → `ok`
2. Frontend running: `http://localhost:3000`
3. Browser ready; optional second tab for Telegram
4. Say one line first:

> “CarePath turns a private question into an appropriate next step — without diagnosing. Web chat is live; Telegram works the same way; WhatsApp architecture is ready when Meta is.”

---

## Path A — Fertility → specialist (~35 seconds)

| # | You do | You say (optional voiceover) |
|---|--------|------------------------------|
| 1 | Open **localhost:3000** — chat loads welcome | “User lands in a private chat. No new app.” |
| 2 | Tap **Yes, continue** | “Explicit consent before any sensitive questions.” |
| 3 | Tap **2 · Fertility** | “Pathway: fertility concerns.” |
| 4 | Tap **3** (age 35–44) | “Structured questions — not free-form chat.” |
| 5 | Tap **1** (trying to conceive: yes) | |
| 6 | Tap **3** (>12 months) | |
| 7 | Tap **2** (prior test abnormal) | “Rules engine evaluates — not an LLM diagnosis.” |
| 8 | Point at recommendation | “Specialist pathway suggested, factors listed, screening disclaimer fixed. Simulated providers only.” |

**Expected on screen**
- Triage: **specialist**
- Factors: age, duration, prior abnormal test
- Disclaimer: not a diagnosis

---

## Path B — Urgent red flag (~25 seconds)

| # | You do | You say |
|---|--------|---------|
| 1 | Tap **Reset** (header) | “New session — red-flag path.” |
| 2 | Tap **Yes, continue** | |
| 3 | Tap **3 · Symptoms** | |
| 4 | Tap **2** (age 25–34) | |
| 5 | Tap **3** (prefer not to say on trying) | |
| 6 | Tap **1** (severe pain = yes) | “Red flag short-circuits the questionnaire.” |
| 7 | Point at urgent message | “Immediate urgent-care language. No ‘it’s probably fine’.” |

**Expected on screen**
- Triage: **urgent**
- Red-flag styling / emergency pathway language

---

## Optional 10-second close

> “Same clinical core on Telegram with a bot token. WhatsApp stays the long-term channel; Meta verification does not block this demo.”

If Telegram is running: show one message `hello` → same consent text.

---

## Exact web taps (cheat sheet)

### Fertility
```
YES → 2 → 3 → 1 → 3 → 2
```

### Urgent
```
Reset → YES → 3 → 2 → 3 → 1
```

### Education (if asked)
```
YES → 1 → 2 → 2 → 4 → 2
```
(Expected: education / low-intensity next step)

---

## If something breaks live

| Problem | Fix |
|---------|-----|
| Chat says backend unreachable | Restart API on :8000; check `NEXT_PUBLIC_API_URL` |
| No quick-reply buttons | Type `YES` / `2` / etc. in the input |
| Stuck mid-flow | Header **Reset** |
| Judges ask “is this WhatsApp?” | “Channel-agnostic core; web + Telegram live for reliability.” |

---

## One-sentence product claim (memorise)

> CarePath does not diagnose infertility — it helps men take the next appropriate healthcare action, privately, with explainable rules and red-flag safety.
