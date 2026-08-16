"""Mock Active Directory (AD) integration.

POC stand-in for AD Users & Computers / PowerShell based password resets.
In production this would be a delegated, audited AD write (least privilege),
never a raw bind with a Domain Admin account.
"""
from __future__ import annotations

import random
import string
from datetime import datetime, timedelta

from .users import find_employee

PASSWORD_EXPIRY_DAYS = 90


class ADUserStatus:
    ACTIVE = "active"
    LOCKED = "locked"
    DISABLED = "disabled"


def get_account_status(employee_code: str) -> dict:
    emp = find_employee(employee_code)
    if emp is None:
        return {"found": False, "status": None, "detail": "Employee not found in AD."}
    last_changed = datetime.fromisoformat(emp["password_last_changed"])
    expiry = last_changed + timedelta(days=PASSWORD_EXPIRY_DAYS)
    days_to_expiry = (expiry - datetime.now()).days
    return {
        "found": True,
        "status": emp["ad_account_status"],
        "ad_username": emp["ad_username"],
        "password_last_changed": emp["password_last_changed"],
        "password_expiry": expiry.date().isoformat(),
        "days_to_expiry": days_to_expiry,
        "detail": (
            f"AD account '{emp['ad_username']}' is {emp['ad_account_status']}. "
            f"Password expires on {expiry.date().isoformat()}."
        ),
    }


def reset_password(
    employee_code: str,
    temp_password: str,
) -> dict:
    emp = find_employee(employee_code)
    if emp is None:
        return {"success": False, "detail": "Employee not found."}
    return {
        "success": True,
        "ad_username": emp["ad_username"],
        "temp_password": temp_password,
        "must_change_on_next_logon": True,
        "detail": (
            f"Password reset executed for {emp['ad_username']}. "
            "User must change at next logon."
        ),
    }


def generate_temp_password(length: int = 12) -> str:
    """Generate a compliant-looking temporary password (demo only)."""
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%"
    return "".join(random.SystemRandom().choice(alphabet) for _ in range(length))


def unlock_account(employee_code: str) -> dict:
    emp = find_employee(employee_code)
    if emp is None:
        return {"success": False, "detail": "Employee not found."}
    return {
        "success": True,
        "ad_username": emp["ad_username"],
        "detail": f"Account '{emp['ad_username']}' unlocked.",
    }


class ADMock:
    """Convenience facade over the AD mock functions (demo)."""

    def get_account_status(self, employee_code: str) -> dict:
        return get_account_status(employee_code)

    def reset_password(self, employee_code: str, temp_password: str) -> dict:
        return reset_password(employee_code, temp_password)

    def generate_temp_password(self, length: int = 12) -> str:
        return generate_temp_password(length)

    def unlock_account(self, employee_code: str) -> dict:
        return unlock_account(employee_code)
