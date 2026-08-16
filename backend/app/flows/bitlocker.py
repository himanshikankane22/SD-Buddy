"""Guided BitLocker recovery key flow.

Mirrors production: identity validation, device ownership verification,
retrieve key from Entra/Intune (mock), deliver over secure channel, confirm.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..integrations.azure import AzureMock
from .security import IdentityCheck

if TYPE_CHECKING:
    from ..triage.config import TriageConfig

FLOW_NAME = "bitlocker"

TRIGGERS = (
    "bitlocker",
    "recovery key",
    "recovery key needed",
    "enter recovery key",
    "bitlocker key",
    "drive is locked",
    "locked drive",
    "recovery screen",
)

AUTO_STEPS = {"retrieve"}


def detect(text: str) -> bool:
    t = text.lower()
    return any(trig in t for trig in TRIGGERS)


def start() -> dict:
    return {
        "flow": FLOW_NAME,
        "step": "identity",
        "identity": {"employee_code": "", "answers": {}, "attempts": 0, "passed": False, "field_index": 0},
        "device_name": "",
        "device_verified": False,
        "key_result": None,
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
        state["step"] = "device"
        return {
            "messages": [
                "Identity verified. Now I need to verify the device.",
                "Please tell me the **device name** (e.g. JDE-LT-10452-01). "
                "It's usually shown on the recovery screen, or findable in Settings → System → About.",
            ],
            "requires_input": True,
        }

    return {"messages": [_identity_next_question(state)], "requires_input": True}


def _step_device(user_input: str, state: dict, config: TriageConfig) -> dict:
    state["device_name"] = user_input.strip()
    emp_code = state["identity"].get("employee_code", "")
    az = AzureMock()
    verification = az.verify_device_ownership(state["device_name"], emp_code)

    if not verification.get("success"):
        return {
            "messages": [
                "I couldn't verify that this device belongs to you. "
                "For security I cannot release a recovery key. "
                "Please double-check the device name, or call the Service Desk. Escalating this ticket."
            ],
            "cancel": True,
        }

    state["device_verified"] = True
    state["step"] = "retrieve"
    return {
        "messages": [
            f"Device **{verification['device_name']}** (serial {verification['serial_number']}) "
            "is registered to you. Retrieving the recovery key from Microsoft Entra ID..."
        ],
        "requires_input": False,
    }


def _step_retrieve(state: dict, config: TriageConfig) -> dict:
    az = AzureMock()
    key_result = az.get_bitlocker_key(state["device_name"])
    state["key_result"] = key_result

    if not key_result.get("success"):
        return {
            "messages": [
                "No recovery key was found for that device in Entra ID. "
                "This may mean the key wasn't escrowed. Escalating to the Endpoint team."
            ],
            "cancel": True,
        }

    state["step"] = "confirm"
    return {
        "messages": [
            "✅ Recovery key found. The **Key ID** on your recovery screen should match:\n"
            f"**`{key_result['key_id']}`**\n\n"
            "⚠️ **Security notice:** the 48-digit key will be shared over a **secure channel** "
            "(phone / secure mail), never over this chat. In this demo, the full key is shown "
            "only in the ticket draft.",
            "Please unlock the drive with the key and confirm your device boots to Windows "
            "(type 'done' / 'unlocked' when ready).",
        ],
        "requires_input": True,
    }


def _step_confirm(user_input: str | None, state: dict, config: TriageConfig) -> dict:
    state["step"] = "done"
    msgs = [
        "Great — glad the drive is unlocked. A few tips:\n"
        "- The key is now 'used'; your IT team may rotate it automatically.\n"
        "- If you're asked for the key again soon, your device may have a TPM/BIOS issue — report it.\n"
        "- Your ticket is ready in the panel. Anything else?"
    ]
    ticket = {
        "record_type": "Incident",
        "short_description": "BitLocker recovery — user locked out of encrypted drive",
        "category": "Endpoint",
        "impact": "medium",
        "urgency": "high",
        "priority": config.priority_for("medium", "high"),
        "caller": state["identity"].get("employee_code", ""),
        "description": (
            "User could not unlock BitLocker-encrypted drive. Identity verified, device ownership "
            "verified, recovery key retrieved from Entra ID and shared over a secure channel. "
            "Device confirmed unlocked."
        ),
        "resolution_path": "Recovery key shared securely via Entra ID; key ID logged; confirm unlock.",
        "flow": FLOW_NAME,
    }
    state["ticket"] = ticket
    return {"messages": msgs, "ticket": ticket}


_STEP_HANDLERS = {
    "identity": _step_identity,
    "device": _step_device,
    "retrieve": _step_retrieve,
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
