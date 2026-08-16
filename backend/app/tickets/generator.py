"""ServiceNow-style ticket draft generation and submission."""
from __future__ import annotations

from ..integrations.servicenow import Ticket, get_servicenow
from ..triage.config import load_triage_config


def build_ticket_draft(
    *,
    description: str,
    record_type: str = "Incident",
    category: str = "Other",
    impact: str = "low",
    urgency: str = "low",
    channel: str = "chat",
    caller: str = "",
    priority: str | None = None,
) -> dict:
    """Build a ticket draft dict (not yet persisted)."""
    config = load_triage_config()
    if priority is None:
        priority = config.priority_for(impact, urgency)
    meta = config.priority_meta(priority)
    major = config.is_major(description) or meta.get("major_incident", False)
    if major:
        # Major incidents are always P1 regardless of the matrix inputs.
        priority = "P1"
        meta = config.priority_meta(priority)

    return {
        "record_type": record_type,
        "short_description": _short_description(description),
        "category": category,
        "impact": impact,
        "urgency": urgency,
        "priority": priority,
        "priority_name": meta.get("name", ""),
        "response_sla": meta.get("response_sla", ""),
        "resolution_sla": meta.get("resolution_sla", ""),
        "major_incident": major,
        "description": description,
        "contact_channel": channel,
        "caller": caller,
    }


def submit_ticket(draft: dict) -> Ticket:
    """Persist the draft into the mock ServiceNow store."""
    sn = get_servicenow()
    allowed = {
        "short_description", "category", "impact", "urgency", "priority",
        "contact_channel", "caller", "description", "notes",
    }
    payload = {k: v for k, v in draft.items() if k in allowed}
    if draft["record_type"] == "Service Request":
        return sn.create_request(**payload)
    return sn.create_incident(**payload)


def _short_description(description: str, limit: int = 80) -> str:
    text = " ".join(description.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."
