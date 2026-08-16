# KB-009 | Runbook: Nexthink — Endpoint Actions for L1

> Audience: L1 Service Desk | Owner: Digital Employee Experience | Source: Nexthink library packs, internal practice

## What Nexthink is used for at L1
Nexthink gives real-time visibility and **remote actions** on endpoints. L1 uses it to fix common issues without a remote session or a site visit.

## Basic commands / actions
1. **OneDrive reset** — "OneDrive assisted troubleshooting" workflow
   - Verifies the OneDrive install, checks sync state, and resets the OneDrive client.
   - Use when: OneDrive stuck "Processing", not syncing, crashes, files missing.
   - Reduces the longest tail of OneDrive tickets automatically.
2. **gpupdate /force** — run Group Policy refresh remotely
   - Use when: user reports missing printers, no mapped drives, policy changes "not applying".
   - Same effect as an on-machine `gpupdate /force`; often resolves policy-stuck issues without reboot.
3. **Restart OneDrive** — restart the process on the endpoint.
4. **Endpoint status** — last boot, sync state, network health — quick triage before remote session.

## When to use Nexthink vs LogMeIn (KB-010)
- Use **Nexthink** for defined, scriptable fixes (reset, GP refresh, status) — no user interaction needed, fast, auditable.
- Use **LogMeIn** when you need eyes/hands on screen (user reports something odd, needs demonstration, or a fix isn't scriptable).

## Workflow notes
- Trigger the action on the correct device (confirm device name with the user).
- The result/outcome should be noted back on the ServiceNow ticket.
- If an automated workflow detects broader issues (Wi-Fi quality, crashes across many devices) → escalate; it may be an incident, not a single-user issue.

## Prevention / improvement
- Nexthink connectivity-assisted and Zscaler-assisted troubleshooting workflows cut VPN/network diagnosis time.
- Use Nexthink data to spot recurring issues for Problem Management.

## Demo notes
In the demo these actions are simulated by a mock Nexthink runner (see backend integrations).