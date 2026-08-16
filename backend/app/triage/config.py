"""Triage configuration loader (priority matrix, keywords, categories).

Reads backend/config/triage.yaml so rules can be tuned without code changes.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from ..config import get_settings


class TriageConfig:
    def __init__(self, data: dict) -> None:
        self.data = data
        self.matrix = data.get("matrix", {})
        self.priorities = data.get("priorities", {})
        self.major_keywords = [k.lower() for k in data.get("major_incident_keywords", [])]
        self.incident_hints = [k.lower() for k in data.get("incident_hints", [])]
        self.request_hints = [k.lower() for k in data.get("service_request_hints", [])]
        self.categories = data.get("categories", [])

    def priority_for(self, impact: str, urgency: str) -> str:
        impact = (impact or "").lower()
        urgency = (urgency or "").lower()
        level = self.matrix.get(impact, {}).get(urgency)
        if level is None:
            return "P3"
        return level

    def priority_meta(self, priority: str) -> dict:
        return self.priorities.get(priority, {})

    def is_major(self, text: str) -> bool:
        t = text.lower()
        return any(kw in t for kw in self.major_keywords)


@lru_cache(maxsize=1)
def load_triage_config() -> TriageConfig:
    path = Path(get_settings().triage_config)
    if not path.exists():
        # fall back to default location if run from another cwd
        alt = Path(__file__).resolve().parent.parent.parent / "config" / "triage.yaml"
        path = alt
    with path.open(encoding="utf-8") as fh:
        return TriageConfig(yaml.safe_load(fh))
