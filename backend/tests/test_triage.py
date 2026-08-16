"""Tests for the triage engine (type classification + priority matrix)."""
from app.triage.classifier import classify_type
from app.triage.config import load_triage_config
from app.triage.priority import detect_priority, guess_impact_urgency


def test_classify_incident():
    cfg = load_triage_config()
    result = classify_type("Outlook is down for everyone in the office", cfg)
    assert result["type"] == "Incident"


def test_classify_service_request():
    cfg = load_triage_config()
    result = classify_type("I forgot my password and need a reset", cfg)
    assert result["type"] == "Service Request"


def test_priority_matrix_high_high_is_p1():
    cfg = load_triage_config()
    result = detect_priority("high", "high", "email down for all users", cfg)
    assert result["priority"] == "P1"
    assert result["major_incident"] is True


def test_priority_matrix_low_low_is_p4():
    cfg = load_triage_config()
    result = detect_priority("low", "low", "minor printer issue", cfg)
    assert result["priority"] == "P4"
    assert result["major_incident"] is False


def test_major_incident_keywords():
    cfg = load_triage_config()
    assert cfg.is_major("The plant network is down and nobody can work") is True
    assert cfg.is_major("Password reset please") is False


def test_guess_impact_urgency():
    cfg = load_triage_config()
    assert guess_impact_urgency("site down, no network for all users", cfg) == {
        "impact": "high",
        "urgency": "high",
    }
    assert guess_impact_urgency("need a new laptop", cfg) == {"impact": "low", "urgency": "low"}


def test_editable_config_file_exists():
    cfg = load_triage_config()
    assert "matrix" in cfg.data
    assert {"high", "medium", "low"} <= set(cfg.matrix.keys())
