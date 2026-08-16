# SD Buddy — Architecture & Design Notes

Deep dive behind the Service Desk L1 Copilot, written as engineering documentation.

---

## 1. System overview

```
┌────────────────────────────── Browser (React + Vite) ─────────────────────────────┐
│  RoleToggle   ChannelSelector   ChatWindow   FlowWizard   PriorityBanner          │
│  TicketPanel (ServiceNow-style draft, live)                                       │
└──────────────────────────────────────┬────────────────────────────────────────────┘
                                       │  /api/*, /health  (Vite dev proxy → :8000)
┌──────────────────────────────────────▼────────────────────────────────────────────┐
│                            FastAPI  (app/main.py)                                 │
│                                                                                   │
│  POST /api/chat ──► SessionStore ──► ┌─ Guided Flow router (active flow?)         │
│                                       │     password_reset │ bitlocker │ mfa_reset │
│                                       ├─ Triage engine (every message)            │
│                                       │     Incident/SR · priority · major?       │
│                                       ├─ RAG retriever (TF-IDF over backend/kb/*.md) │
│                                       ├─ LLM client (OpenRouter, fallback if off) │
│                                       └─ Ticket generator ─► ServiceNow mock      │
│                                                                                   │
│  Mocks: ADMock │ AzureMock │ ServiceNowMock │ NexthinkMock (seeded JSON)          │
└───────────────────────────────────────────────────────────────────────────────────┘
```

**Design principles**

1. **Flows beat free-form chat.** A guided flow is a deterministic, step-based state
   machine. For well-understood, high-risk processes (password reset) we never trust the
   LLM to improvise — it must follow the exact steps with validation.
2. **Triage on every message.** Every utterance is classified (Incident vs. Service
   Request) and scored (Impact × Urgency → Priority) so the ticket draft stays coherent
   and Major Incidents surface immediately.
3. **RAG + LLM, not just LLM.** Answers come from a curated KB first (deterministic,
   explainable, controllable), with the LLM used to shape the final answer. No vector DB —
   TF-IDF is intentionally simple and dependency-free.
4. **LLM as an enhancement, not a single point of failure.** If the API key is missing or
   the call fails, a rule-based fallback still answers.
5. **Deterministic data paths for anything auditable** (identity, tickets, priority),
   LLM only for natural-language shaping.

---

## 2. Request lifecycle (POST /api/chat)

1. Load session (or 404). Update `role` / `channel`.
2. Append user message to history; cache caller.
3. **Triage** the latest message → `{record_type, impact, urgency, priority, major_incident, SLAs}`.
4. If a **flow is active** → `process_flow(flow_key, user_input, flow_state)`.
   - Handlers return `messages` + `requires_input`. Steps marked `AUTO_STEPS` chain
     without user input (e.g. identity-check → AD pre-check → reset → advice).
   - `cancel` or `done` clears the flow; `done` also finalizes the ticket.
   - `state` is a plain dict (JSON-safe) — persisted on the session.
5. Else **detect a new flow** from the message; if matched, start it and return the intro.
6. Else **free-form**: RAG-retrieve KB context → build chat messages → call LLM; on any
   LLM failure use `_fallback_answer`.
7. Return `{session_id, reply, history, flow, ticket, triage, llm_used, major_incident}`.

---

## 3. Triage engine

`backend/app/triage/` — rules live in `backend/config/triage.yaml` (editable without code).

- **Classifier** (Incident vs. Service Request): keyword/pattern based. "It's broken",
  "outage", "error", "can't" → Incident. "reset", "new", "renew", "access to", "order" →
  Service Request. Returns a confidence score.
- **Priority matrix** (config-driven):

  | Impact \ Urgency | high | medium | low |
  |---|---|---|---|
  | **high** | P1 | P2 | P2 |
  | **medium** | P2 | P3 | P3 |
  | **low** | P3 | P4 | P4 |

- **Major Incident**: any P1, or an explicit override via severity keywords
  ("site down", "office network is down", "all users", "data breach", "outage"). Major
  incidents are forced to P1 and get a red banner + escalation note in the UI.

---

## 4. Guided flows

Each flow is a small state machine registered in `flows/router.py`:

```
detect(message) → flow_key      # intent detection
start(flow_key) → initial_state
process(user_input, state)      # advance one step (may auto-chain)
```

### Password reset
1. **Identity** — collect 6 validation fields (employee code, full name, primary
   location, mobile number, email ID, reporting manager). Compare against the mock AD
   store; 3 wrong answers abort with a referral to ServiceNow HR.
2. **AD pre-check** — account status (locked/expired/disabled).
3. **Reset** — generate temp password, mark "must change at next logon".
4. **Advice** — sign out everywhere, update saved credentials, 90-day expiry.
5. **Security rule**: the temp password is **never** sent in the chat; it is delivered
   over a different channel and only surfaced in the (demo) ticket notes.

### BitLocker recovery
1. Identity (6 fields, same validator).
2. **Device verification** — user provides their device tag/name; match against the
   Entra/Intune mock device register.
3. **Retrieve key** — pull the 48-digit recovery key from the mock Azure AD store; hand
   over on the call channel only, never in chat/email.
4. **Confirm** — user confirms the key worked; close with resolution notes.

### MFA reset
1. Identity (6 fields).
2. **Scenario** — 1 = new phone, 2 = lost/stolen (revoke sessions), 3 = codes failing.
3. **Action** — depending on scenario: require re-registration, revoke sessions, etc.
4. **Confirm** — user confirms re-registration; ticket finalized.

Shared `flows/security.py` holds the `IdentityCheck` validator — pure logic, unit-tested.

---

## 5. RAG pipeline (dependency-free TF-IDF)

`backend/app/rag/`

- **Loader**: reads `backend/kb/*.md`, splits on `##` headings into `KBSection(source, title, body)`.
- **Index**: tokenize → lowercase → stopwords → frequency → TF-IDF weighting.
- **Retrieve**: cosine-ish similarity of query against sections; returns top-k with scores.
- **Format**: top sections are rendered as a compact context block for the LLM prompt.

Why TF-IDF and not embeddings? (a) zero external services/deps — runs offline; (b) fully
explainable in an interview; (c) plenty for a small curated KB. Swappable: replace the
retriever with `sentence-transformers` + FAISS later without touching callers.

---

## 6. LLM layer

`backend/app/llm/`

- `client.py` — minimal OpenRouter wrapper (`POST https://openrouter.ai/api/v1/chat/completions`)
  using `httpx`. Exposes `.available` and `chat(messages, max_tokens)`.
- `prompts.py` — two personas:
  - **End User**: friendly, short, guides step-by-step, never asks for secrets.
  - **L1 Agent**: runbook-oriented, includes KB article names, suggests ServiceNow
    category, flags escalation conditions.
- `make_chat_messages(role, history, kb_context)` assembles the conversation.
- **Fallback**: `_fallback_answer` in `main.py` produces a deterministic answer (triage +
  top KB hit + escalation offer) when the LLM is off/unreachable — the demo never looks
  broken.

---

## 7. Integrations (mocks)

| Integration | Module | Production equivalent |
|---|---|---|
| AD | `integrations/ad.py` | Active Directory / Entra ID user management |
| Azure/Intune | `integrations/azure.py` | Entra ID BitLocker key, device register, MFA policies |
| ServiceNow | `integrations/servicenow.py` | ServiceNow Table API (`incident`/`sc_req_item`) |
| Nexthink | `integrations/nexthink.py` | Nexthink Experience/Runbooks queries |

Each exposes a small, clearly-named interface so the real API can be swapped in without
touching flow logic. Seed data lives in `backend/app/data/` (`employees.json`,
`bitlocker_keys.json`).

---

## 8. Tickets

`backend/app/tickets/generator.py`

- `build_ticket_draft` — turns a conversation into a ServiceNow-style dict with
  `short_description`, `category`, `impact`, `urgency`, `priority`, SLAs, `major_incident`,
  `contact_channel`, `caller`. Forced to **P1** when major.
- `submit_ticket` — persists into the mock store, returns an enriched dict
  (`INC000001` / `REQ000001` numbering). Whitelist of payload fields guards against
  injecting unexpected keys.

---

## 9. Frontend

React 18 + Vite + TypeScript, no UI framework (custom CSS, dark theme).

- `types.ts` mirrors the API contracts (ChatResponse, FlowSnapshot, Ticket, Triage).
- `api.ts` thin fetch wrappers.
- `App.tsx` owns state; components are presentational.
- **FlowWizard** renders flow label, step counter and a progress bar; during identity
  validation it shows `identity_progress/identity_total` (6).
- **PriorityBanner** appears when `major_incident` (P1) — red, pulsing.
- **TicketPanel** shows the live ServiceNow-style draft with a "Copy JSON" button.
- Channel/role switches are reflected in the backend session on every send.

---

## 10. Testing strategy

- **Backend (pytest, 25 tests)** — triage matrix + major detection, flow state machines
  (happy path, wrong answers, cancel, auto-advance), ticket generation (P1 forcing, field
  whitelist), RAG retrieval over the real KB.
- **Lint** — ruff (`E,F,W,I,UP,B,SIM`) clean; ESLint (react-hooks, typescript-eslint) clean.
- **Types/build** — `tsc --noEmit` clean; `vite build` produces a production bundle.
- **E2E** — full flows exercised over the live HTTP API (password reset, BitLocker, MFA,
  Major Incident) with the LLM live.

Run: `pytest` and `ruff check app tests` in `backend/`; `npm run typecheck && npm run build`
and `npm run lint` in `frontend/`.

---

## 11. Interview Q&A (demo talking points)

**Q. How do you keep the bot safe for password resets?**
A. Identity is validated against the directory with 6 fields before any action. Sensitive
values (temp password, BitLocker key) are never echoed on the same channel — they're
delivered via a different channel and only noted in the ticket. There's a bounded number of
validation attempts, then a human hand-off.

**Q. Why a flow state machine instead of pure LLM?**
A. High-risk processes need deterministic guarantees: exact steps, validation, audit trail.
The LLM is great at natural language but can hallucinate steps. Flows give control and
reproducibility; the LLM handles everything else.

**Q. What if the LLM is down?**
A. The bot degrades gracefully to a rule-based fallback (triage + KB top hit + escalation
offer). A demo never looks broken, and L1 can still work.

**Q. Why TF-IDF instead of embeddings?**
A. Zero dependencies, offline, explainable, and plenty for a small curated KB. The
retriever is an interface, so it can be swapped for embeddings + FAISS without changing
callers.

**Q. How would you take this to production?**
A. Replace mocks with real APIs behind the same interfaces; persist sessions and tickets
in a database; add real SSO; evaluate the LLM with an eval set; add rate limiting,
logging/PII redaction, and human-in-the-loop approval for sensitive actions; move RAG to
real embeddings with versioned KB.

**Q. What did you measure / how would you?**
A. Today: test coverage, latency of the RAG+LLM path, ticket field accuracy. In
production: containment rate (% of chats resolved without escalation), handle time, user
satisfaction, LLM answer acceptance, and drift in KB relevance over time.

---

## 12. Known limitations

- In-memory sessions and ticket store (data resets on restart).
- Mock identity/device data — real integrations are stubbed behind clean interfaces.
- Single-user demo context; no auth beyond the persona toggle.
- No persistent history or audit DB.
- TF-IDF misses synonyms/semantics (acceptable for the KB size).
