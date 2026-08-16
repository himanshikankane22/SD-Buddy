"""Incident vs Service Request classifier (rule-based with configurable hints)."""
from __future__ import annotations

from .config import TriageConfig


def classify_type(text: str, config: TriageConfig) -> dict:
    """Classify a contact description as Incident or Service Request.

    Returns a dict with type, hints found, and confidence.
    """
    t = text.lower()
    incident_hits = [h for h in config.incident_hints if h in t]
    request_hits = [h for h in config.request_hints if h in t]

    # A locked/forgotten password reset is typically a Service Request,
    # even though "locked" also appears in incident hints.
    explicit_request = any(h in t for h in ("password reset", "forgot password", "mfa reset", "new laptop"))

    score = len(incident_hits) - len(request_hits)
    if explicit_request:
        record_type = "Service Request"
        confidence = 0.9
    elif score > 0:
        record_type = "Incident"
        confidence = min(0.95, 0.55 + 0.1 * score)
    elif score < 0:
        record_type = "Service Request"
        confidence = min(0.95, 0.55 + 0.1 * abs(score))
    else:
        record_type = "Incident"
        confidence = 0.5

    return {
        "type": record_type,
        "confidence": round(confidence, 2),
        "incident_hints": incident_hits,
        "request_hints": request_hits,
    }
