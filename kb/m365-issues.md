# KB-007 | Microsoft 365 (M365) Common Issues — L1 Troubleshooting

> Audience: L1 Service Desk | Owner: Collaboration Services | Source: Microsoft troubleshooting docs, internal KB
> M365 (Outlook, Teams, OneDrive, SharePoint, Exchange) is a frequent call driver.

## 1. Outlook — email not syncing / profile issues
- Restart Outlook in **safe mode** (`outlook.exe /safe`) to rule out add-ins.
- Check the account is not set to Work Offline (bottom-right of status bar).
- Run **Microsoft SaRA** (Support and Recovery Assistant) → Outlook diagnostics.
- Rebuild the profile or re-add the account only if the above fail.
- Check Service Health dashboard for an Exchange Online incident before deep troubleshooting.

## 2. Microsoft Teams — can't join / calls drop / camera & mic
- Check Teams app version; recommend update.
- Clear Teams cache: close Teams, delete `%appdata%\Microsoft\Teams` cache folders, restart.
- Test audio/video device permissions in Windows + browser.
- Check Service Health for Teams issues (broad outages → incident, escalate).

## 3. OneDrive — files not syncing / stuck "Processing"
- Check sync status in OneDrive system tray.
- **Reset OneDrive** (L1 can use Nexthink action — see KB-009; or manually `%localappdata%\Microsoft\OneDrive\onedrive.exe /reset`).
- Check file path length / unsupported characters; verify storage quota.
- Confirm the user signs into the correct work/school account.
- If files show as "orphaned", use OneDrive known-folder-move guidance.

## 4. Sign-in problems / "your password has expired"
- Confirm the account is active and password not expired (see KB-001).
- Rule out cached credentials: sign out everywhere, retry on primary machine.
- Check browser/autofill not supplying stale credentials.
- If MFA loop → see KB-003.

## 5. Office apps crashing / slow
- Online Repair via Control Panel → Programs → Office → Change → Online Repair.
- Disable add-ins; run SaRA.
- Check device resources (CPU/RAM/disk) and network.

## 6. License / activation errors
- Verify license in M365 Admin Center → Users → active user → licenses.
- Ask user to sign out of Office apps, then sign back in.
- Escalate to L2 if license shows assigned but activation still fails.

## Escalation
- Service-wide outages (Exchange/Teams/SharePoint) → treat as incident; check Service Health; escalate.
- Persistent sync failures / data loss risk → escalate to L2 Collaboration.

## Demo notes
Useful for free-form chat Q&A; for OneDrive specifically the chatbot can offer the Nexthink OneDrive-reset path.