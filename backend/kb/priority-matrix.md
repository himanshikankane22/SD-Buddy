# KB-005 | Priority Matrix (Impact × Urgency)

> Audience: L1 Service Desk | Owner: Service Desk Manager | Source: ITIL 4 Priority Matrix, config/triage.yaml (editable)

## Concepts
- **Impact** — how wide the disruption is: how many users / whether a critical business service or revenue process is affected. (High / Medium / Low)
- **Urgency** — how fast it must be resolved: time-sensitivity (deadlines, payroll, blocked critical user). (High / Medium / Low)
- **Priority** — derived from Impact × Urgency via the matrix. Sets the response/resolution SLA and escalation path.

## Matrix (default in config/triage.yaml)
| Impact \ Urgency | High | Medium | Low |
|---|---|---|---|
| **High** | P1 | P2 | P2 |
| **Medium** | P2 | P3 | P3 |
| **Low** | P3 | P4 | P4 |

## Priority definitions
- **P1 (Critical)** — whole site / core service down, critical business process blocked, security breach. Immediate response, Major Incident process, exec communication.
- **P2 (High)** — significant impact, one department or business-critical single user blocked, or medium impact with high urgency. Fast escalation.
- **P3 (Medium)** — single user with workaround, medium/medium. Normal queue.
- **P4 (Low)** — minor inconvenience, low/low. Standard fulfillment.

## Pitfalls to avoid
- Loud/frustrated user ≠ high impact. Judge on facts.
- Don't over-prioritize: if everything is P1, nothing is P1 → SLA breaches and burnout.
- Confuse impact and urgency: a 1-user payroll problem at month-end is high *urgency* but low *impact* → still P2.

## Worked examples
- Company-wide email outage during business hours → Impact High × Urgency High → **P1**.
- Payroll system blocked for one user before salary processing → Impact Low × Urgency High → **P2**.
- CRM slow for one sales user, still usable → Impact Medium × Urgency Medium → **P3**.
- Reporting dashboard for one occasional user → Impact Low × Urgency Low → **P4**.

## Demo notes
The matrix is loaded from `backend/config/triage.yaml`; edit that file to change rules without touching code.