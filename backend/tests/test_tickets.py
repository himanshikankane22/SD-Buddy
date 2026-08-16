"""Tests for ticket generation + the mock ServiceNow store."""
from app.integrations.servicenow import get_servicenow
from app.tickets.generator import build_ticket_draft, submit_ticket


def test_build_draft_defaults():
    draft = build_ticket_draft(description="Email down for everyone")
    assert draft["record_type"] == "Incident"
    assert draft["priority"] == "P1"
    assert draft["major_incident"] is True
    assert draft["short_description"]


def test_build_draft_low_priority():
    draft = build_ticket_draft(
        description="requesting software install",
        record_type="Service Request",
        impact="low",
        urgency="low",
    )
    assert draft["priority"] == "P4"
    assert draft["major_incident"] is False


def test_submit_to_servicenow():
    sn = get_servicenow()
    before = len(sn.list())
    draft = build_ticket_draft(
        description="password reset",
        record_type="Service Request",
        impact="low",
        urgency="medium",
        channel="chat",
    )
    ticket = submit_ticket(draft)
    assert ticket.number.startswith("REQ")
    assert len(sn.list()) == before + 1
    assert sn.get(ticket.number) is not None


def test_short_description_truncation():
    draft = build_ticket_draft(description="x" * 200)
    assert len(draft["short_description"]) <= 80
