"""Guided MFA reset flow.

Mirrors production: identity validation, trigger decision (lost vs compromised),
Require re-register MFA (and revoke sessions if needed), confirm re-registration.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..integrations.azure import AzureMock
from .security import IdentityCheck

if TYPE_CHECKING:
    from ..triage.config import TriageConfig

FLOW_NAME = "mfa_reset"

TRIGGERS = (
    "mfa",
    "multi factor",
    "multifactor",
    "authenticator",
    "2fa",
    "two factor",
    "new phone",
    "lost phone",
    "stolen phone",
    "phone number changed",
    "code rejected",
    "push not received",
    "mfa reset",
)

AUTO_STEPS = {"reset"}


def detect(text: str) -> bool:
    t = text.lower()
    return any(trig in t for trig in TRIGGERS)


def start() -> dict:
    return {
        "flow": FLOW_NAME,
        "step": "identity",
        "identity": {"employee_code": "", "answers": {}, "attempts": 0, "passed": False, "field_index": 0},
        "scenario": None,
        "revoke": False,
        "result": None,
        "ticket": None,
    }


def _identity_next_question(state: dict) -> str:
    check = IdentityCheck(**state["identity"])
    return check.current_question() or ""


def _step_identity(user_input: str, state: dict, config: TriageConfig) -> dict:
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
        return {"messages": [result["message"]], "cancel": True}

    if not result.get("ok"):
        msgs = [result["message"]]
        if not result.get("done"):
            msgs.append(_identity_next_question(state))
        return {"messages": msgs, "requires_input": True}

    if result.get("done") and check.passed:
        state["step"] = "scenario"
        return {
            "messages": [
                "Identity verified. Let's figure out what happened to your MFA so I apply the right reset.",
                "Which best describes your situation?\n"
                "1. **New phone / changed number** — lost access to the Authenticator app\n"
                "2. **Lost or stolen device** — possible security concern\n"
                "3. **Codes rejected / prompts not arriving** — MFA not working but I still have my phone",
            ],
            "requires_input": True,
        }

    return {"messages": [_identity_next_question(state)], "requires_input": True}


def _step_scenario(user_input: str, state: dict, config: TriageConfig) -> dict:
    t = user_input.lower()
    if any(k in t for k in ("1", "new phone", "changed number", "lost access", "new device")):
        state["scenario"] = "new_phone"
        state["revoke"] = False
    elif any(k in t for k in ("2", "lost", "stolen", "compromised", "security")):
        state["scenario"] = "lost_stolen"
        state["revoke"] = True
    elif any(k in t for k in ("3", "rejected", "not arriving", "not working", "prompts")):
        state["scenario"] = "codes_failing"
        state["revoke"] = False
    else:
        return {
            "messages": ["I didn't catch that — please reply 1, 2 or 3, or describe the situation."],
            "requires_input": True,
        }

    state["step"] = "reset"
    return {
        "messages": ["Thanks. I'll now initiate the MFA reset in the Entra admin center..."],
        "requires_input": False,
    }


def _step_reset(state: dict, config: TriageConfig) -> dict:
    az = AzureMock()
    emp_code = state["identity"].get("employee_code", "")
    result = az.require_mfa_rerregistration(emp_code, revoke_sessions=state["revoke"])
    state["result"] = result
    actions = ", ".join(result.get("actions", []))
    msgs = [
        f"✅ **MFA reset initiated** (simulated): **{actions}** for your account. "
        "At your **next sign-in** you'll be prompted to register a new authentication method "
        "(typically the Microsoft Authenticator app)."
    ]
    if state["revoke"]:
        msgs.append(
            "⚠️ Because your device was lost/stolen, sessions were also **revoked** — "
            "you'll be signed out everywhere, which is intentional for security."
        )
    msgs.append(
        "Please sign in and complete the re-registration, then tell me once you're in "
        "(type 'done' when set up)."
    )
    state["step"] = "confirm"
    return {"messages": msgs, "requires_input": True}


def _step_confirm(user_input: str | None, state: dict, config: TriageConfig) -> dict:
    state["step"] = "done"
    msgs = [
        "Excellent — you're re-registered. Final tips:\n"
        "- Review your **Security Info** at https://mysignins.microsoft.com and remove old/unused methods.\n"
        "- Enable Authenticator **backup** so a future phone change is smoother.\n"
        "- Note: this reset does **not** change your password.\n"
        "- Your ticket is ready in the panel. Anything else?"
    ]
    ticket = {
        "record_type": "Service Request",
        "short_description": "MFA re-registration reset",
        "category": "Identity & Access",
        "impact": "low",
        "urgency": "high",
        "priority": config.priority_for("low", "high"),
        "caller": state["identity"].get("employee_code", ""),
        "description": (
            f"User required MFA re-registration. Scenario: {state['scenario']}. "
            "Identity verified; re-registration required (and sessions revoked if device lost/stolen). "
            "User re-registered and confirmed sign-in."
        ),
        "resolution_path": "Require re-register MFA via Entra admin center; user re-registered Authenticator.",
        "flow": FLOW_NAME,
    }
    state["ticket"] = ticket
    return {"messages": msgs, "ticket": ticket}


_STEP_HANDLERS = {
    "identity": _step_identity,
    "scenario": _step_scenario,
    "reset": _step_reset,
    "confirm": _step_confirm,
}


def process(user_input: str, state: dict, config: TriageConfig) -> dict:
    step = state.get("step", "identity")
    handler = _STEP_HANDLERS.get(step, _step_identity)
    result = handler(user_input, state, config)

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
