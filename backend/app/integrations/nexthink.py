"""Mock Nexthink integration.

POC stand-in for Nexthink endpoint actions commonly used by L1 (OneDrive
reset, Group Policy refresh, endpoint diagnostics). In production these map
to Nexthink remote actions / library-pack workflows (NQL + Act).
"""
from __future__ import annotations

from enum import Enum


class NexthinkAction(str, Enum):
    ONEDRIVE_RESET = "onedrive_reset"
    GPUPDATE_FORCE = "gpupdate_force"
    RESTART_ONEDRIVE = "restart_onedrive"
    ENDPOINT_STATUS = "endpoint_status"


# Action -> human readable description of what L1 would trigger
ACTION_DETAILS = {
    NexthinkAction.ONEDRIVE_RESET: (
        "Trigger 'OneDrive assisted troubleshooting' workflow: verify install, "
        "check sync state, then reset the OneDrive client."
    ),
    NexthinkAction.GPUPDATE_FORCE: "Run gpupdate /force on the endpoint to re-apply Group Policy.",
    NexthinkAction.RESTART_ONEDRIVE: "Restart the OneDrive process on the endpoint.",
    NexthinkAction.ENDPOINT_STATUS: "Collect endpoint status: last boot, sync state, network health.",
}


class NexthinkMock:
    """Simulated remote-action runner for Nexthink (demo)."""

    def run(self, action: str, device_name: str) -> dict:
        try:
            act = NexthinkAction(action)
        except ValueError:
            return {
                "success": False,
                "detail": f"Unknown Nexthink action '{action}'.",
            }
        return {
            "success": True,
            "action": act.value,
            "device_name": device_name,
            "detail": ACTION_DETAILS[act],
            "note": (
                "Simulated in the demo — in production this triggers a Nexthink "
                "remote action and the result lands back on the ServiceNow ticket."
            ),
        }

    def list_actions(self) -> list[str]:
        return [a.value for a in NexthinkAction]


_nexthink = NexthinkMock()


def get_nexthink() -> NexthinkMock:
    return _nexthink
