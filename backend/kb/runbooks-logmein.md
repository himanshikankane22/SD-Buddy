# KB-010 | Runbook: LogMeIn Remote Support Sessions

> Audience: L1 Service Desk | Owner: Service Desk Manager | Source: LogMeIn security practices (256-bit SSL, consent-first)

## When to use
- User needs on-screen help you cannot script (Nexthink covered in KB-009).
- Demonstrating a fix, guiding the user, or troubleshooting something interactive.
- Unattended support: with prior authorization for managed devices.

## Session etiquette & security
1. **Always get consent**: the user initiates/accepts the session (they must permit Remote Control, File Transfer, etc.). The user can end the session at any time.
2. **Identify yourself and state purpose** before connecting. Confirm you're speaking to the verified caller (KB-001 identity check already done at intake).
3. Sessions are **256-bit SSL encrypted**; do not disable any security prompts.
4. **Never ask for or accept passwords** in the session chat — temp credentials are handled per policy (different channel).
5. **Stay in scope**: do not browse personal folders, emails, or unrelated apps. Work only on the reported issue.
6. **End the session cleanly**: tell the user you are disconnecting, confirm the issue is resolved, and ensure the session applet is gone from their machine.

## During the session
- Narrate what you're doing so the user understands and learns.
- If you must reboot the machine, warn first and (if needed) set Reboot & Reconnect so the session resumes.
- Keep the ServiceNow ticket updated with observations as you go.

## After the session
- Confirm resolution with the user.
- Add session notes (what was done, root cause if identified) to the ticket.
- If the fix was a workaround or the root cause is unknown → hand off to L2 with full context.

## Escalation
- You cannot establish/see the screen, or the issue is beyond L1 scope → escalate to L2, keep the ticket updated.
- Anything suspicious (malware, unusual popups) → stop, treat as security, follow the security incident path.

## Demo notes
In the demo the chatbot guides the user/agent through the consent + secure-session steps; no real remote tool is launched.