# KB-003 | MFA Reset (Require Re-Registration) in Microsoft Entra ID

> Audience: L1 Service Desk | Owner: Identity Access Management | Source: Microsoft Entra docs, delegate-by-task (Authentication Administrator)
> Top call driver alongside password resets. Common triggers: lost/stolen phone, new device without Authenticator transfer, outdated phone number, repeated prompt failures, suspected compromise.

## Symptom
User cannot complete MFA sign-in (no push received, code rejected, authenticator app gone, or new phone not set up).

## Pre-requisites (agent)
- The L1 agent's service account needs the **Authentication Administrator** role (least privilege) in Entra ID. Privileged Authentication Administrator is required to reset MFA for other admins.

## Resolution steps
1. Verify identity (standard security questions, KB-001).
2. Determine the trigger — this decides the action:
   - **New phone / lost authenticator / changed number** → `Require re-register MFA`.
   - **Lost/stolen device or suspected compromise** → `Require re-register MFA` **AND** `Revoke MFA sessions` (signs the user out everywhere and invalidates refresh tokens).
3. Entra admin center: **Identity → Users → All users → user → Authentication methods → Require re-register multifactor authentication**.
4. Confirm the action. Tell the user: at next sign-in they will be prompted to register a new method (typically Microsoft Authenticator).
5. Ask the user to sign in and complete re-registration, and confirm they can access Outlook/Teams afterwards.
6. Recommend the user review Security Info and remove any old/unusable methods.
7. Note: MFA reset does NOT change the user's password.
8. If the reset "does not stick": have the user fully sign out, wait ~10 minutes for propagation, retry.

## Escalation
- Reset fails / user cannot complete registration → escalate to L2 Identity.
- Suspicion of account compromise → escalate to Security immediately (treat as incident).

## Prevention
- Encourage users to keep Authenticator backup / cloud backup enabled.
- Consider SSPR so users can self-service some recovery.
- Educate users to verify phone number in Security Info.

## Demo notes
Driven by the guided **MFA reset flow** in the chatbot (identity check + compromised-vs-lost decision branch, mock Entra reset).