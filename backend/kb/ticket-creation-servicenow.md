# KB-011 | Ticket Creation in ServiceNow

> Audience: L1 Service Desk | Owner: Service Desk Manager | Source: ServiceNow ITSM practice, internal SOP

## Two record types
- **Incident** (INCNNNNNN) — unplanned break/fix (see KB-004).
- **Service Request** (REQNNNNNN) — catalog fulfillment (see KB-004).

## 4 contact channels (all map to a ticket)
| Channel | Notes |
|---|---|
| **Call** | Identity verified verbally; fast; log during call. |
| **Chat** | Verify identity; never share temp passwords/keys in chat. |
| **Email** | Parse subject/body; confirm details; watch for out-of-office auto-replies. |
| **Portal / Self-service** | User self-logs; chatbot can pre-fill and hand to agent. |

## Fields to capture (minimum)
1. **Caller** — employee code + name (verified).
2. **Category / subcategory** — e.g. Identity & Access → Password Reset.
3. **Record type** — Incident vs Service Request.
4. **Impact** — High / Medium / Low.
5. **Urgency** — High / Medium / Low.
6. **Priority** — derived from matrix (KB-005) → P1–P4.
7. **Short description** — one line, e.g. "Cannot sign in — password expired (AD)".
8. **Description** — full detail: symptoms, error message, device name, what was tried, channel.
9. **Contact channel** — call/chat/email/portal.
10. **Assignment group** — auto by category; escalate if wrong.

## Writing a good description (ABC)
- **Symptom**: exact error text, what the user was doing.
- **Scope**: one user vs many (never guess — "whole system down" often = one page).
- **Attempted**: what L1 already tried (password reset, gpupdate, OneDrive reset, etc.).
- **Impact/urgency rationale**: so priority is defensible.

## SLA & escalation
- Priority sets response/resolution SLA clocks (configurable). Breach risk → escalate to supervisor/incident manager.
- Add **timeline notes** for every action and user contact.

## Demo notes
The chatbot auto-generates a ServiceNow-style ticket draft as a conversation progresses and surfaces it in the ticket panel; the mock ServiceNow store holds it.