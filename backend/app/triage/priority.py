"""Priority + major-incident detection assembled from the triage config."""
from __future__ import annotations

from .config import TriageConfig, load_triage_config


def detect_priority(
    impact: str,
    urgency: str,
    description: str,
    config: TriageConfig | None = None,
) -> dict:
    """Return a priority assessment dict for a contact/description."""
    config = config or load_triage_config()

    priority = config.priority_for(impact, urgency)
    meta = config.priority_meta(priority)
    major = config.is_major(description) or meta.get("major_incident", False)

    return {
        "impact": impact.lower(),
        "urgency": urgency.lower(),
        "priority": priority,
        "priority_name": meta.get("name", priority),
        "description": meta.get("description", ""),
        "response_sla": meta.get("response_sla", ""),
        "resolution_sla": meta.get("resolution_sla", ""),
        "major_incident": major,
    }


def guess_impact_urgency(description: str, config: TriageConfig | None = None) -> dict:
    """Heuristic impact/urgency guesses from wording (P1-priority wording)."""
    config = config or load_triage_config()
    t = description.lower()

    if config.is_major(t):
        return {"impact": "high", "urgency": "high"}

    high_impact = any(
        kw in t
        for kw in ("all users", "everyone", "site", "plant", "office", "company", "department", "team")
    )
    high_urgency = any(kw in t for kw in ("urgent", "asap", "immediately", "now", "deadline", "blocked", "can't work", "cannot work", "payroll"))

    if high_impact and high_urgency:
        return {"impact": "high", "urgency": "high"}
    if high_impact:
        return {"impact": "high", "urgency": "medium"}
    if high_urgency:
        return {"impact": "low", "urgency": "high"}
    return {"impact": "low", "urgency": "low"}
