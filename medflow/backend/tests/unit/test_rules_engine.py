"""Tests for Rules Engine (completeness + safety rules)."""
from __future__ import annotations

import pytest
from datetime import datetime

from app.services.rules_engine import evaluate, evaluate_episode, RuleViolation, RuleResult


def test_empty_data_zero_completeness():
    result = evaluate({})
    assert result.clinical_complete_percent == 0.0
    assert len(result.missing_fields) == 10  # all mandatory fields missing
    assert len(result.violations) == 0  # no data to trigger safety rules


def test_fully_complete_data_hundred_percent():
    data = {
        "chief_complaint": "Douleur thoracique",
        "clinical_notes": "Patient stable, ECG normal",
        "medications": "Aspirine",
        "allergies": "Aucune",
        "dosage": "100mg",
        "duration": "7 jours",
        "date_of_birth": datetime(1980, 5, 20),
        "gender": "M",
        "phone": "0611223344",
        "emergency_contact": "Jean Martin (frère)",
    }
    result = evaluate(data)
    assert result.clinical_complete_percent == 100.0
    assert len(result.missing_fields) == 0
    assert len(result.violations) == 0


def test_partial_completeness():
    data = {
        "chief_complaint": "Fièvre",
        "clinical_notes": "",
        "medications": None,
        "allergies": "Aucune",
        "dosage": "500mg",
        "duration": None,
        "date_of_birth": datetime(1992, 11, 10),
        "gender": "F",
        "phone": None,
        "emergency_contact": None,
    }
    result = evaluate(data)
    # Present: chief_complaint, allergies, dosage, date_of_birth, gender = 5/10 = 50%
    assert result.clinical_complete_percent == 50.0
    assert len(result.missing_fields) == 5


def test_safety_rule_aspirin_allergy():
    data = {
        "chief_complaint": "Douleur thoracique aigue",
        "clinical_notes": "",
        "medications": "",
        "allergies": "aspirine",
        "dosage": "",
        "duration": "",
        "date_of_birth": datetime(1960, 1, 1),
        "gender": "M",
        "phone": "",
        "emergency_contact": "",
    }
    result = evaluate(data)
    violations = [v for v in result.violations if v.severity == "error"]
    assert len(violations) >= 1
    assert any("aspirine" in v.message.lower() for v in violations)


def test_safety_rule_fever_warfarin():
    data = {
        "chief_complaint": "Fièvre et courbatures",
        "clinical_notes": "",
        "medications": "warfarine",
        "allergies": "",
        "dosage": "",
        "duration": "",
        "date_of_birth": datetime(1970, 6, 15),
        "gender": "F",
        "phone": "",
        "emergency_contact": "",
    }
    result = evaluate(data)
    warnings = [v for v in result.violations if v.severity == "warning"]
    assert any("warfarine" in w.message.lower() for w in warnings)


def test_safety_rule_allergy_without_emergency_contact():
    data = {
        "chief_complaint": "Urticaire",
        "clinical_notes": "",
        "medications": "",
        "allergies": "penicilline",
        "dosage": "",
        "duration": "",
        "date_of_birth": datetime(2000, 3, 10),
        "gender": "F",
        "phone": "",
        "emergency_contact": None,
    }
    result = evaluate(data)
    assert any("contact d'urgence" in v.message for v in result.violations)


def test_evaluate_episode_wrapper():
    """Test the convenience wrapper with mock-like objects."""
    class FakeEpisode:
        chief_complaint = "Douleur"
        clinical_notes = "Notes"

    class FakePatient:
        allergies = "Aucune"
        date_of_birth = datetime(1985, 5, 20)
        gender = "M"
        phone = "0611223344"
        emergency_contact = "Contact"

    class FakePrescription:
        medications = "Paracétamol"
        dosage = "500mg"
        duration = "5 jours"
        instructions = "..."
        warnings = "..."

    result = evaluate_episode(FakeEpisode(), FakePatient(), FakePrescription())
    assert result.clinical_complete_percent == 100.0
