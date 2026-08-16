"""Mock Microsoft Entra ID / Intune integration.

POC stand-in for the Entra admin center + Intune device blades used to
retrieve BitLocker recovery keys and reset MFA.
In production these map to Microsoft Graph endpoints with scoped permissions
(e.g. BitlockerKey.Read.All, AuthenticationAdministrator role).
"""
from __future__ import annotations

from .users import find_device_by_name


def get_bitlocker_key(device_name: str) -> dict:
    dev = find_device_by_name(device_name)
    if dev is None:
        return {
            "success": False,
            "detail": (
                "No BitLocker recovery key found for that device name. "
                "Confirm the exact device name (e.g. from the recovery screen) "
                "or check whether the device is enrolled in Intune."
            ),
        }
    return {
        "success": True,
        "device_name": dev["device_name"],
        "serial_number": dev["serial_number"],
        "employee_code": dev["employee_code"],
        "key_id": dev["key_id"],
        "bitlocker_recovery_key": dev["bitlocker_recovery_key"],
        "status": dev["status"],
        "detail": (
            f"Recovery key found for {dev['device_name']} in Entra ID. "
            "Share over a secure channel only."
        ),
    }


def verify_device_ownership(device_name: str, employee_code: str) -> dict:
    dev = find_device_by_name(device_name)
    if dev is None:
        return {
            "success": False,
            "detail": "Device not found in the endpoint inventory.",
        }
    owned = dev["employee_code"].strip().upper() == employee_code.strip().upper()
    return {
        "success": owned,
        "device_name": dev["device_name"],
        "serial_number": dev["serial_number"],
        "employee_code": dev["employee_code"],
        "detail": (
            "Device ownership verified."
            if owned
            else "Device is not registered to this employee. Do NOT share the key."
        ),
    }


def require_mfa_rerregistration(employee_code: str, revoke_sessions: bool = False) -> dict:
    from .users import find_employee

    emp = find_employee(employee_code)
    if emp is None:
        return {"success": False, "detail": "Employee not found in Entra ID."}
    actions = ["Require re-register MFA"]
    if revoke_sessions:
        actions.append("Revoke MFA sessions")
    return {
        "success": True,
        "employee_code": emp["employee_code"],
        "upn": emp["email_id"],
        "actions": actions,
        "detail": (
            f"MFA reset initiated for {emp['email_id']} ({', '.join(actions)}). "
            "User will be prompted to register a new method at next sign-in."
        ),
    }


class AzureMock:
    """Facade over the Entra/Intune mocks (demo)."""

    def get_bitlocker_key(self, device_name: str) -> dict:
        return get_bitlocker_key(device_name)

    def verify_device_ownership(self, device_name: str, employee_code: str) -> dict:
        return verify_device_ownership(device_name, employee_code)

    def require_mfa_rerregistration(self, employee_code: str, revoke_sessions: bool = False) -> dict:
        return require_mfa_rerregistration(employee_code, revoke_sessions)
