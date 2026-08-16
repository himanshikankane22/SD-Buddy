"""Guided password reset flow.

Mirrors the production L1 process: identity validation (5 security questions),
AD pre-check, reset with temp password, expiry advice.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..integrations.ad import ADMock
from .security import IdentityCheck

if TYPE_CHECKING:
    from ..triage.config import TriageConfig

FLOW_NAME = "password_reset"

TRIGGERS = (
    "password reset",
    "reset my password",
    "reset password",
    "forgot password",
    "forgotten password",
    "change password",
    "password expired",
    "locked out",
    "account locked",
    "cannot sign in",
    "can't sign in",
    "can't login",
    "cannot login",
)

# Steps that advance without user input.
AUTO_STEPS = {"ad_check", "reset", "advice"}


def detect(text: str) -> bool:
    t = text.lower()
    t_norm = t.replace(" my ", " ").replace(" the ", " ").replace(" a ", " ")
    return any(trig in t or trig in t_norm for trig in TRIGGERS)


def start() -> dict:
    return {
        "flow": FLOW_NAME,
        "step": "identity",
        "identity": {"employee_code": "", "answers": {}, "attempts": 0, "passed": False, "field_index": 0},
        "ad_result": None,
        "temp_password": None,
        "ticket": None,
    }


def _identity_next_question(state: dict) -> str:
    check = IdentityCheck(**state["identity"])
    return check.current_question() or ""


def _step_identity(user_input: str, state: dict, config: TriageConfig) -> dict:
    """Run one identity-validation step. Returns {messages, requires_input, cancel, done}."""
    check = IdentityCheck(**state["identity"])
    result = check.submit(user_input)
    state["identity"] = {
        "employee_code": check.employee_code,
        "answers": check.answers,
        "attempts": check.attempts,
        "passed": check.passed,
        "field_index": check.field_index,
    }

    if result.get("failed"):
        return {"messages": [result["message"]], "requires_input": False, "cancel": True}

    if not result.get("ok"):
        msgs = [result["message"]]
        if not result.get("done"):
            msgs.append(_identity_next_question(state))
        return {"messages": msgs, "requires_input": True}

    if result.get("done") and check.passed:
        msgs = [f"Thank you, **{check.employee['full_name']}** — identity verified."]
        state["step"] = "ad_check"
        return {"messages": msgs, "requires_input": False}

    return {"messages": [_identity_next_question(state)], "requires_input": True}


def _step_ad_check(state: dict, config: TriageConfig) -> dict:
    emp = state["identity"].get("employee_code", "")
    ad = ADMock()
    status = ad.get_account_status(emp)
    state["ad_result"] = status

    if not status.get("found"):
        return {"messages": ["Your account wasn't found in Active Directory. Escalating to L1."], "cancel": True}
    if status.get("status") == "disabled":
        return {
            "messages": [
                "Your AD account is currently **disabled**, which usually means an HR status change. "
                "I can't reset this myself — please contact HR / call the Service Desk. Escalating this ticket."
            ],
            "cancel": True,
        }

    msgs = []
    if status.get("status") == "locked":
        msgs.append("Your account was locked due to failed sign-in attempts. I'll unlock it and proceed.")
    msgs.append(
        f"Account **{status.get('ad_username')}** is {status.get('status')}. "
        f"Last password change: {status.get('password_last_changed')}. "
        f"Password expires: {status.get('password_expiry')} ({status.get('days_to_expiry')} days).\n\n"
        "Proceeding to reset now..."
    )
    state["step"] = "reset"
    return {"messages": msgs, "requires_input": False}


def _step_reset(state: dict, config: TriageConfig) -> dict:
    ad = ADMock()
    emp_code = state["identity"].get("employee_code", "")
    temp = ad.generate_temp_password()
    ad.reset_password(emp_code, temp)
    state["temp_password"] = temp
    state["step"] = "advice"
    return {
        "messages": [
            "✅ **Password reset executed** (simulated in this demo).",
            "⚠️ For your security, the temporary password will **not** be shared over this channel. "
            "In production, L1 delivers it over a different channel (e.g. a phone call). "
            "In this demo, the temp password is shown in the ticket draft only.",
            "Next, you must change it at your **next logon**. I'll guide you.",
        ],
        "requires_input": False,
    }


def _step_advice(state: dict, config: TriageConfig) -> dict:
    msgs = [
        "**How to finish:**\n"
        "1. Sign out of all devices (phone, laptop, any saved sessions).\n"
        "2. Sign in to your primary machine with the temporary password.\n"
        "3. Change your password when prompted (password must be changed at next logon).\n"
        "4. Update saved credentials on your phone, mapped drives and in Windows Credential Manager — "
        "otherwise the old password will keep causing lockouts.\n"
        "5. Passwords expire after **90 days**; you'll be prompted to change them.",
        "Your ticket is ready — check the ticket panel on the right. Is there anything else I can help with?",
    ]
    state["step"] = "done"
    temp = state.get("temp_password", "n/a")
    ticket = {
        "record_type": "Service Request",
        "short_description": "AD password reset for user",
        "category": "Identity & Access",
        "impact": "low",
        "urgency": "medium",
        "priority": config.priority_for("low", "medium"),
        "caller": state["identity"].get("employee_code", ""),
        "description": (
            "User requested an Active Directory password reset. Identity verified via "
            "6 security questions. AD account pre-checked and reset with temp password "
            "(user must change at next logon)."
        ),
        "notes": [
            f"Temporary password (demo only): `{temp}` — in production, deliver over a different channel (e.g. phone call).",
            "User advised: sign out everywhere, change at next logon, update saved credentials.",
            "Passwords expire every 90 days.",
        ],
        "resolution_path": "AD password reset (change-at-next-logon); user advised on expiry + sign-out everywhere.",
        "flow": FLOW_NAME,
    }
    state["ticket"] = ticket
    return {"messages": msgs, "requires_input": False, "ticket": ticket}


_STEP_HANDLERS = {
    "identity": _step_identity,
    "ad_check": _step_ad_check,
    "reset": _step_reset,
    "advice": _step_advice,
}


def process(user_input: str, state: dict, config: TriageConfig) -> dict:
    """Advance the password-reset flow. Auto-chains through non-interactive steps."""
    step = state.get("step", "identity")
    handler = _STEP_HANDLERS.get(step, _step_identity)
    result = handler(user_input, state, config)

    # Auto-advance through steps that don't require user input.
    while (
        not result.get("requires_input")
        and not result.get("cancel")
        and result.get("messages")
        and state.get("step") in AUTO_STEPS
    ):
        nxt = state["step"]
        nxt_result = _STEP_HANDLERS[nxt](state, config)
        result["messages"] = result.get("messages", []) + nxt_result.get("messages", [])
        result.update({k: v for k, v in nxt_result.items() if k != "messages"})
        if nxt_result.get("ticket"):
            result["ticket"] = nxt_result["ticket"]
        if nxt_result.get("cancel"):
            result["cancel"] = True
            break

    done = state.get("step") == "done" or bool(result.get("cancel"))
    return {
        "messages": result.get("messages", []),
        "state": state,
        "done": done,
        "cancel": result.get("cancel", False),
        "ticket": result.get("ticket"),
    }
