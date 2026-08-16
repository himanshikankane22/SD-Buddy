# SD Buddy — Service Desk L1 Copilot

An enterprise **L1 service desk chatbot** that acts as the first point of contact for end users
and assists L1 agents. It guides users through real service desk workflows (password reset,
BitLocker recovery, MFA reset), triages every contact (Incident vs. Service Request, priority,
Major Incident detection), retrieves answers from a curated knowledge base, and drafts a
ServiceNow-style ticket — all in one conversation.

> Portfolio project for a TCS onboarding technical survey, modelled on real JDE Peets L1
> service desk work (HCL). All backend integrations are **simulated** with seeded data.

**Author:** Junior Endpoint Support Analyst — hands-on L1 engineer experience on the
Intune/endpoint management team (device enrolment, compliance, BitLocker, and
remediation).

## Demo

- Open **http://localhost:5173** with both servers running (see below).
- Try the quick actions, or type one of these:
  - `I forgot my password, please reset`
  - `My laptop needs a BitLocker recovery key`
  - `My Authenticator app stopped working, reset my MFA`
  - `The entire office network is down, all users affected` (triggers Major Incident / P1)

### Demo identities (mock AD)

| Employee code | Name | Location | Device | BitLocker key ID |
|---|---|---|---|---|
| `JDE-10452` | Ananya Sharma | Mumbai HO | `JDE-LT-10452-01` | `4290b6c0-b17a-497a-8552-272cc30e80d4` |
| `JDE-10877` | Marcus De Vries | Amsterdam HO | — | — |
| `JDE-12011` | Priya Patel | Mumbai HO | — | — |
| `JDE-13340` | Sophie Laurent | Paris HO | — | — |
| `JDE-14198` | Tom Miller | London HO | — | — |
| `JDE-15566` | Elena Rodriguez | Madrid HO | — | — |

Security questions asked in a flow (answer as the chosen user): employee code, full name,
primary location, mobile number, email ID, reporting manager's name. For **Ananya Sharma** the
manager is `Rajesh Nair`.

## Features

- **Two personas** — End User and L1 Agent (different system prompts, tone and behaviour).
- **Four contact channels** — Call, Chat, Email, ServiceNow Portal (stamped onto the ticket).
- **Guided flows** — password reset, BitLocker recovery, MFA reset; each with a 6-field
  identity validation, step-by-step UI progress and auto-advancing internal steps.
- **Security-first behaviour** — temp passwords and BitLocker keys are never sent over the
  same channel in the conversation; they appear only in the (demo) ticket.
- **Triage engine** — rule-based Incident vs. Service Request classification + configurable
  Impact × Urgency → Priority matrix with SLA targets and Major Incident detection.
- **RAG knowledge base** — pure-Python TF-IDF retrieval over 12 markdown runbooks/articles,
  no external vector DB.
- **LLM with graceful fallback** — OpenRouter-backed chat answers, but a deterministic
  rule-based fallback answers when the LLM is unavailable.
- **Live ticket draft** — ServiceNow-style ticket (REQ/INC number, category, priority, caller,
  notes) built as the conversation progresses.

## Architecture

```
Browser (React + Vite)
   │  /api, /health  (vite proxy)
   ▼
FastAPI (app/main.py)
   ├── Sessions (in-memory)
   ├── Flow router ── password_reset / bitlocker / mfa_reset
   ├── Triage engine ── classifier + priority matrix + major detection
   ├── RAG (TF-IDF) ── kb/*.md
   ├── LLM client (OpenRouter) ── with rule-based fallback
   └── Ticket generator ── ServiceNow mock
```

See [docs/architecture.md](docs/architecture.md) for the deep dive, data flow and
interview Q&A.

## Project structure

```
project2/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, routes, orchestration
│   │   ├── config.py          # settings (.env)
│   │   ├── sessions.py        # in-memory session store
│   │   ├── llm/               # OpenRouter client + prompts
│   │   ├── integrations/      # AD, Azure/Intune, ServiceNow, Nexthink (mocks)
│   │   ├── rag/               # markdown loader + TF-IDF index
│   │   ├── triage/            # classifier, priority, major-incident
│   │   ├── flows/             # password_reset, bitlocker, mfa_reset, security
│   │   └── tickets/           # ServiceNow-style draft generation
│   ├── tests/                 # pytest suite (25 tests)
│   └── pyproject.toml         # pytest + ruff config
├── kb/                        # knowledge base markdown (RAG source)
├── frontend/                  # React + Vite + TypeScript chat UI
└── .env.example               # env template (copy to .env, add key)
```

## Quick start

### 1. Backend

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings python-dotenv httpx PyYAML pytest ruff
cp ..\.env.example ..\.env   # then set OPENROUTER_API_KEY
python -m uvicorn app.main:app --reload
```

The app runs on http://localhost:8000 (docs at `/docs`). Without an API key it falls back
to deterministic rule-based answers (status shows `llm_configured: false`).

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dev server proxies `/api` to the backend.

### 3. Tests & lint

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest      # 25 tests
.\.venv\Scripts\ruff.exe check app tests  # lint

cd ..\frontend
npm run typecheck && npm run build        # TS + production build
npm run lint
```

## API overview

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | App + LLM status |
| POST | `/api/session` | Create session `{role, channel}` |
| GET | `/api/session/{id}` | Session state, flow, ticket |
| POST | `/api/chat` | Main chat `{session_id, message, role, channel}` |
| POST | `/api/ticket` | Force a ticket draft from a message |
| GET | `/api/kb` | Knowledge base index |
| GET | `/api/triage/config` | Loaded triage rules |
| POST | `/api/agent/nexthink` | Nexthink mock actions (L1) |

## Config

- `.env` — `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, app name, CORS origins.
- `backend/config/triage.yaml` — priority matrix, SLA targets, Major Incident keywords,
  Incident vs. SR rules. Editable without code.

## Notes / caveats

- All enterprise integrations are mocked with seeded JSON data — no real credentials or data.
- The OpenRouter key in `.env` is yours; it is git-ignored. Rotate if it leaks.
- Sessions and ticket stores are in-memory (reset on restart).
- `git init` was deferred: git is not on PATH on this machine. `.gitignore` is already in place.