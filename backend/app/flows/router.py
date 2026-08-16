"""Flow router: detects which guided flow a message triggers and dispatches."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..triage.config import TriageConfig, load_triage_config
from . import bitlocker, mfa_reset, password_reset

if TYPE_CHECKING:
    pass

FLOW_REGISTRY: dict[str, dict] = {
    password_reset.FLOW_NAME: {
        "name": "Password Reset",
        "label": "🔑 Password Reset",
        "detect": password_reset.detect,
        "start": password_reset.start,
        "process": password_reset.process,
    },
    bitlocker.FLOW_NAME: {
        "name": "BitLocker Recovery",
        "label": "🔐 BitLocker Recovery Key",
        "detect": bitlocker.detect,
        "start": bitlocker.start,
        "process": bitlocker.process,
    },
    mfa_reset.FLOW_NAME: {
        "name": "MFA Reset",
        "label": "📱 MFA Reset",
        "detect": mfa_reset.detect,
        "start": mfa_reset.start,
        "process": mfa_reset.process,
    },
}


def detect_flow(text: str) -> tuple[str | None, dict | None]:
    """Return (flow_key, flow_meta) for the first flow whose triggers match, else None."""
    for key, meta in FLOW_REGISTRY.items():
        if meta["detect"](text):
            return key, meta
    return None, None


def start_flow(key: str) -> dict:
    meta = FLOW_REGISTRY[key]
    state = meta["start"]()
    state["flow"] = key
    return state


def process_flow(key: str, user_input: str, state: dict, config: TriageConfig | None = None) -> dict:
    config = config or load_triage_config()
    meta = FLOW_REGISTRY[key]
    return meta["process"](user_input, state, config)


def flow_meta(key: str) -> dict | None:
    return FLOW_REGISTRY.get(key)
