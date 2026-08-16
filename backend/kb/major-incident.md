# KB-006 | Major / Critical Incident Handling

> Audience: L1 Service Desk + Service Desk Manager | Owner: Incident Manager | Source: ITIL 4 Major Incident Management

## Definition
A **Major Incident** is a P1 incident with large business impact (site down, core service outage, security breach) that requires a coordinated response outside normal queues.

## Detection triggers (keywords)
Flag as Major Incident when the report matches **P1** OR contains severity keywords such as:
- "site down", "plant down", "office down"
- "no network", "no internet", "everyone/all users affected"
- "email down for everyone", "Teams down"
- "security breach", "hacked", "ransomware", "phishing + credentials entered"
- "system outage", "SAP down for everyone", "payroll not processing"

## Immediate actions (L1)
1. **Do not resolve alone.** Open the ticket as P1 and raise a **Major Incident** flag.
2. Initiate **bridge call** with Service Desk Manager / Incident Manager / on-call L2.
3. Announce with a **business impact statement** (what is down, who is affected, estimated impact).
4. Set **communication cadence** (e.g. every 30 min) for all stakeholders.
5. Keep a **timeline log** of actions and findings on the ticket.
6. Coordinate with resolver groups (Network, Infrastructure, Security, Microsoft, SAP) via the bridge.
7. Only downgrade/close after service restoration is **verified** and agreed with the Incident Manager.

## Roles
- **L1**: first triage, flag, ticket hygiene, comms to business, log actions.
- **Service Desk Manager / Incident Manager**: owns the bridge, decisions, comms to executives.
- **L2/L3/Resolvers**: technical fix.
- **Security**: any compromise/breach takes precedence; follow incident-response playbook.

## Post-incident
- Root Cause Analysis (RCA) within agreed SLA (e.g. 5 business days).
- Review: was detection correct? What can be prevented / monitored?

## Demo notes
The chatbot auto-flags Major Incidents on P1 + severity keywords and surfaces an escalation banner in the UI.