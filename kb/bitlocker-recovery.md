# KB-002 | BitLocker Recovery Key Retrieval

> Audience: L1 Service Desk | Owner: Endpoint Management / Intune | Source: Microsoft Learn — BitLocker recovery process, Intune docs
> Why it happens: device fails to auto-unlock (TPM / secure boot policy change, BIOS update, unauthorized access attempt, hardware change). Windows shows a recovery screen with a 48-digit key prompt.

## Symptom
User's encrypted work laptop asks for a BitLocker recovery key at boot and they do not have it saved.

## Self-service first (if available)
Before involving L1, the user can retrieve the key themselves:
- **Company Portal website/app** → Devices → select device → **Get recovery key**.
- Key format: 48 characters in 8 groups of 6, separated by dashes, e.g. `123456-789012-345678-901234-567890-123456-789012-345678`.

## L1 resolution (Entra / Intune retrieval)
1. Verify identity (use the standard security questions, KB-001).
2. **Verify device ownership**: ask for device name / serial number (shown on the recovery screen, plus the Key ID). Cross-check the device is registered to this employee in the endpoint inventory.
3. Navigate Entra admin center / Intune: **Devices → All devices → select device → Recovery keys** (or Monitor → Recovery keys).
4. Match the **Key ID** shown on the user's recovery screen to the correct key (a device can have several keys).
5. Copy the 48-digit key and **share it over a secure channel only** (voice call / secure mail). Never paste it in chat.
6. Ask the user to enter the key, confirm the device unlocks and boots to Windows.
7. If the key is not found in Entra: check AD DS via BitLocker Recovery Password Viewer (RSAT) for domain-joined devices, or escalate to L2 Endpoint.
8. Document key ID used, device, and outcome on the ticket.

## Escalation
- No key available in Entra/AD → possible broken escrow → escalate to Endpoint/L2; establish emergency recovery path.
- Repeated recovery prompts on the same device → likely TPM/BIOS issue → escalate.

## Prevention
- Audit all devices have BitLocker keys escrowed to Entra ID.
- Ensure Intune policy "Save BitLocker recovery information to Entra ID" is enabled.
- Rotate recovery keys after use (Entra supports automatic rotation).

## Demo notes
This runbook is driven by the guided **BitLocker flow** in the chatbot (identity + device ownership verification, mock key retrieval).