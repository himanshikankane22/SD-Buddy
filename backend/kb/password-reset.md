# KB-001 | Active Directory Password Reset

> Audience: L1 Service Desk | Owner: Identity Access Management | Source: ITIL Incident Mgmt, Microsoft AD/Entra docs, internal process
> Top call driver — password resets account for 20-50% of help desk calls at most organizations.

## Symptom
User cannot sign in to Windows / corporate apps with a forgotten or expired password, or their AD account is locked.

## Mandatory identity verification (5 security questions)
**Do NOT reset until identity is validated.** Ask ALL of the following and cross-check against the employee master record (HR feed):

1. Employee code
2. Full name (as per records)
3. Primary location
4. Mobile number
5. Email ID
6. Reporting manager's name

Rules:
- If any answer does not match the employee record, do not proceed. Warn once, allow one retry, then refer the caller to verify via a different channel.
- Never reset on a caller's request alone (social-engineering guard).
- Ask questions one at a time; do not reveal which field failed.

## Resolution steps
1. Log the request (call / chat / email / portal) and note the channel.
2. Verify the 5 security questions (above).
3. Pre-check the account in AD: account status (active/locked/disabled), last password change, expiry date. `get_account_status`.
   - If **locked**: note the source of lockouts (event 4740), unlock, then proceed or advise retry.
   - If **disabled**: do not reset — check HR status; refer to onboarding/offboarding process.
4. Reset the password in AD **with "User must change password at next logon"** set. Use a temporary password.
5. **Deliver the temporary password over a different channel** than the one the request came in on (e.g. request by chat → deliver by call). Never send passwords in plain text email.
6. Advise the user: sign out of all devices, sign in on primary machine first, change password at next logon, update saved credentials (phone, mapped drives, Windows Credential Manager) to avoid repeat lockouts.
7. Advise expiry policy: passwords expire after 90 days (configurable); user will be forced to change.

## Escalation
- Multiple accounts locking at the same time → possible brute force / security incident → escalate to Security.
- Reset fails or AD is unavailable → escalate to L2 Identity.
- User cannot receive the temp password on any channel → escalate to L1 supervisor.

## Prevention
- Promote Self-Service Password Reset (SSPR) where available.
- Educate users to update credentials on all devices the day they change a password.
- Track repeat reset requests → feed Problem Management.

## Demo notes
This runbook is driven by the guided **password reset flow** in the chatbot, validated against a seeded mock employee DB.