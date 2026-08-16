# KB-004 | Incident vs Service Request (ITIL Classification)

> Audience: L1 Service Desk | Owner: Service Desk Manager | Source: ITIL 4 Incident / Service Request Management

## Definitions
- **Incident** — an *unplanned interruption* to a service, or a *reduction in quality*. Something that is broken. Goal: restore service ASAP. Example: email down, VPN not connecting, laptop BSOD, "the system is down".
- **Service Request** — a *standard request* for something the user does not yet have (fulfillment). No service disruption. Goal: fulfill per catalog. Example: password reset, new laptop, software install, access to a shared drive, M365 license.

## Classification table
| Criterion | Incident | Service Request |
|---|---|---|
| Nature | Unplanned break/fix | Standard request |
| Disruption | Yes | No |
| SLA type | Restoration time | Fulfillment time |
| Goal | Fix quickly | Fulfill request |
| Example | Teams won't open for whole team | Need Adobe Reader installed |

## Judgment rules for L1
- If a *request* cannot be fulfilled normally (e.g. software install keeps failing) it becomes an **incident**.
- If lockouts happen across **many accounts** at once → incident (possible attack), not a request.
- A "whole system down" report often turns out to be one page failing for one user — screen-share / check first, then classify honestly.

## Categories (examples for this account)
- **Identity & Access**: password reset, account unlock, MFA reset, AD/Entra access.
- **Endpoint**: BitLocker, OneDrive, hardware, BSOD, printer.
- **Collaboration (M365)**: Outlook, Teams, SharePoint, Exchange.
- **ERP**: SAP login, Fiori, roles.
- **Network/Connectivity**: VPN, Wi-Fi, network drives.

## Why it matters
Correct classification sets the correct **SLA clock**, **priority**, **assignee queue**, and **reporting**. Miscategorized requests burn incident-management resources.

## Demo notes
The chatbot triages each conversation as Incident or Service Request using the rules above plus the LLM.