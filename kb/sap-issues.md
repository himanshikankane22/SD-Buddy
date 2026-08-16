# KB-008 | SAP User Issues — L1 Troubleshooting

> Audience: L1 Service Desk | Owner: SAP Basis / AMS | Source: SAP support practices, SAP Help (SU01)
> SAP logins and access issues are a recurring call driver. L1 scope is limited to user-level fixes; functional blockers go to L2/L3.

## L1 scope (what we can do)
- SAP **user lock / unlock**
- SAP **password reset**
- Login/Fiori tile visibility guidance
- Basic role/authorization verification (read-only)

## L1 out-of-scope (escalate)
- Functional blockers (order entry, billing, postings errors)
- Fiori app performance / tile configuration problems
- Role/authorization *changes* (requires authorization team + approvals)
- Any issue affecting multiple users or an entire module → treat as incident

## Resolution steps

### 1. User locked out of SAP ("User is locked" / multiple wrong attempts)
1. Verify identity (KB-001 questions).
2. Check the lock: often caused by too many wrong login attempts or a service account retrying stale credentials.
3. Unlock via transaction **SU01** → enter username → Lock/Unlock → unlock. Note: L1 requires delegated Basis authorization for this — otherwise escalate.
4. Confirm the user can log in.
5. If it locks again quickly → check for a service/mapped job using the account, or escalate to Basis.

### 2. SAP password reset
1. Verify identity.
2. SU01 → username → Password → set new/initial password → Save.
3. Tell the user the policy: complexity rules, initial password flag (change at first logon), expiry.
4. Never share the password over the same channel the request came in on.

### 3. Fiori / login page issues
- Confirm the URL and that the user is on the corporate network/VPN.
- Clear browser cache; retry in an InPrivate window.
- Check SAP Service Availability notification for planned downtime/patch window.
- Tile missing → likely authorization; verify role in SU01 (read-only) or escalate to Basis/Auth.

## Escalation
- Functional/business process errors → SAP Functional L2 with full ticket context.
- Mass lockouts or SAP availability problems → Major Incident path (KB-006).
- Role changes → authorization team.

## Demo notes
The chatbot can triage SAP issues and route to the right runbook or escalation.