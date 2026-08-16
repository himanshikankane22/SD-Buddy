"""Identity validation used by all guided flows.

Validates the user against a seeded mock employee database using the same
5 security questions the L1 team asks in production.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..integrations.users import find_employee

VALIDATION_FIELDS = [
    ("employee_code", "employee code"),
    ("full_name", "full name"),
    ("primary_location", "primary location"),
    ("mobile_number", "mobile number"),
    ("email_id", "email ID"),
    ("reporting_manager", "reporting manager's name"),
]


@dataclass
class IdentityCheck:
    employee_code: str = ""
    answers: dict = field(default_factory=dict)
    attempts: int = 0
    passed: bool = False
    employee: dict | None = None
    field_index: int = 0

    def __post_init__(self) -> None:
        # Re-resolve the employee record whenever employee_code is present
        # (needed because state is serialized to plain dicts between turns).
        if self.employee is None and self.employee_code:
            self.employee = find_employee(self.employee_code)

    @property
    def next_field(self) -> tuple[str, str] | None:
        if self.field_index >= len(VALIDATION_FIELDS):
            return None
        return VALIDATION_FIELDS[self.field_index]

    def current_question(self) -> str | None:
        nxt = self.next_field
        if nxt is None:
            return None
        if nxt[0] == "employee_code":
            return "To verify your identity, please confirm your **employee code** (e.g. JDE-XXXXX)."
        return f"Please confirm your **{nxt[1]}** (as per your HR record)."

    def submit(self, answer: str) -> dict:
        """Process one answer. Returns {ok, message, done, failed}."""
        nxt = self.next_field
        if nxt is None:
            return {"ok": True, "done": True, "failed": False, "message": ""}

        field_key, _label = nxt
        if field_key == "employee_code":
            self.employee_code = answer.strip().upper()
            self.employee = find_employee(self.employee_code)
            if self.employee is None:
                self.attempts += 1
                if self.attempts >= 3:
                    return {
                        "ok": False,
                        "done": True,
                        "failed": True,
                        "message": (
                            "I couldn't find that employee code after several tries. "
                            "For security, please call the Service Desk so we can verify "
                            "you over a different channel."
                        ),
                    }
                return {
                    "ok": False,
                    "done": False,
                    "failed": False,
                    "message": (
                        "That employee code wasn't found. Please double-check it "
                        "(format is like JDE-10452)."
                    ),
                }
            self.answers[field_key] = self.employee_code
            self.field_index += 1
            return {"ok": True, "done": False, "failed": False, "message": ""}

        if self.employee is None:
            return {"ok": False, "done": True, "failed": True, "message": "No employee record to validate against."}

        expected = (self.employee.get(field_key) or "").strip().lower()
        if answer.strip().lower() == expected:
            self.answers[field_key] = answer.strip()
            self.field_index += 1
            if self.field_index >= len(VALIDATION_FIELDS):
                self.passed = True
                return {
                    "ok": True,
                    "done": True,
                    "failed": False,
                    "message": "Identity verified successfully.",
                }
            return {"ok": True, "done": False, "failed": False, "message": ""}

        self.attempts += 1
        if self.attempts >= 3:
            return {
                "ok": False,
                "done": True,
                "failed": True,
                "message": (
                    "One or more details didn't match our records after several attempts. "
                    "For your security, please call the Service Desk so we can verify you "
                    "over a different channel."
                ),
            }
        return {
            "ok": False,
            "done": False,
            "failed": False,
            "message": "That didn't match our records. Please try again.",
        }


def full_name_from_code(employee_code: str) -> str | None:
    emp = find_employee(employee_code)
    return emp["full_name"] if emp else None
