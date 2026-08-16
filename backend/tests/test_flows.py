"""Tests for the guided flows (password reset, bitlocker, mfa)."""
import pytest

from app.flows import bitlocker, mfa_reset, password_reset
from app.flows.router import detect_flow
from app.triage.config import load_triage_config


@pytest.fixture
def config():
    return load_triage_config()


# --------------------------------------------------------------------------- #
# Password reset flow
# --------------------------------------------------------------------------- #
def test_password_flow_full_pass(config):
    state = password_reset.start()
    answers = ["JDE-10452", "Ananya Sharma", "Mumbai HO", "+91 98200 45123", "ananya.sharma@jdepeets.demo", "Rajesh Nair"]
    final = None
    for a in answers:
        final = password_reset.process(a, state, config)
        if final.get("done"):
            break
    assert final is not None
    assert final["done"] is True
    assert final.get("ticket") is not None
    assert final["ticket"]["priority"] in {"P1", "P2", "P3", "P4"}
    assert state["identity"]["passed"] is True


def test_password_flow_wrong_answers_fail(config):
    state = password_reset.start()
    # First answer is the employee code (valid), then repeated wrong full name.
    state = password_reset.process("JDE-10452", state, config)["state"]
    out = None
    for _ in range(3):
        out = password_reset.process("Wrong Name", state, config)
        if out.get("cancel"):
            break
    assert out is not None
    assert out["cancel"] is True
    assert "didn't match" in " ".join(out["messages"]).lower() or "records" in " ".join(out["messages"]).lower()


def test_password_flow_detect():
    assert password_reset.detect("I forgot my password, please reset")
    assert not password_reset.detect("my laptop screen is broken")


# --------------------------------------------------------------------------- #
# Bitlocker flow
# --------------------------------------------------------------------------- #
def test_bitlocker_flow(config):
    state = bitlocker.start()
    answers = ["JDE-10452", "Ananya Sharma", "Mumbai HO", "+91 98200 45123", "ananya.sharma@jdepeets.demo", "Rajesh Nair", "JDE-LT-10452-01", "done"]
    final = None
    for a in answers:
        final = bitlocker.process(a, state, config)
        if final.get("done"):
            break
    assert final is not None
    assert final["done"] is True
    assert final.get("ticket") is not None
    assert final["ticket"]["record_type"] == "Incident"


def test_bitlocker_wrong_device_rejected(config):
    state = bitlocker.start()
    state = bitlocker.process("JDE-10452", state, config)["state"]
    state = bitlocker.process("Ananya Sharma", state, config)["state"]
    state = bitlocker.process("Mumbai HO", state, config)["state"]
    state = bitlocker.process("+91 98200 45123", state, config)["state"]
    state = bitlocker.process("ananya.sharma@jdepeets.demo", state, config)["state"]
    state = bitlocker.process("Rajesh Nair", state, config)["state"]
    out = bitlocker.process("WRONG-DEVICE-999", state, config)
    assert out["done"] is True
    assert out.get("cancel") is True


# --------------------------------------------------------------------------- #
# MFA flow
# --------------------------------------------------------------------------- #
def test_mfa_flow_new_phone(config):
    state = mfa_reset.start()
    answers = ["JDE-13340", "Sophie Laurent", "Paris Office", "+33 6 12 34 56 78", "sophie.laurent@jdepeets.demo", "Claire Dubois", "1", "done"]
    final = None
    for a in answers:
        final = mfa_reset.process(a, state, config)
        if final.get("done"):
            break
    assert final is not None
    assert final["done"] is True
    assert final.get("ticket") is not None
    assert state["revoke"] is False


def test_mfa_flow_lost_stolen_revokes_sessions(config):
    state = mfa_reset.start()
    answers = ["JDE-10452", "Ananya Sharma", "Mumbai HO", "+91 98200 45123", "ananya.sharma@jdepeets.demo", "Rajesh Nair", "2", "done"]
    final = None
    for a in answers:
        final = mfa_reset.process(a, state, config)
        if final.get("done"):
            break
    assert final is not None
    assert final["done"] is True
    assert state["revoke"] is True


# --------------------------------------------------------------------------- #
# Router detection
# --------------------------------------------------------------------------- #
def test_router_detects_flows():
    key, meta = detect_flow("I need a password reset")
    assert key == password_reset.FLOW_NAME
    assert meta is not None

    key, _ = detect_flow("bitlocker recovery key please")
    assert key == bitlocker.FLOW_NAME

    key, _ = detect_flow("my mfa authenticator is broken")
    assert key == mfa_reset.FLOW_NAME

    key, _ = detect_flow("how do I connect to the wifi")
    assert key is None
