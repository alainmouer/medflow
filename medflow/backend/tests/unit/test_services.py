"""Unit tests for the new AI services (rules_engine + triage_engine)."""
from __future__ import annotations

from datetime import datetime

from app.services.rules_engine import evaluate, evaluate_episode, RuleResult
from app.services.triage_engine import triage_episode, ConfidenceScore
from app.services.ai_service import AIService, AIProvider


class TestRulesEngine:
    def test_validate_all_complete(self):
        data = {
            "chief_complaint": "Contrôle routine",
            "clinical_notes": "Patient stable",
            "medications": "Aucun",
            "allergies": "Aucune",
            "dosage": "N/A",
            "duration": "N/A",
            "date_of_birth": datetime(1990, 1, 1),
            "gender": "M",
            "phone": "0611223344",
            "emergency_contact": "Personne de confiance",
        }
        result = evaluate(data)
        assert result.clinical_complete_percent == 100.0
        assert result.missing_fields == []
        assert result.violations == []

    def test_validate_missing_all(self):
        result = evaluate({})
        assert result.clinical_complete_percent == 0.0
        assert len(result.missing_fields) == 10

    def test_validate_aspirin_allergy_chest_pain(self):
        data = {
            "chief_complaint": "Douleur thoracique",
            "allergies": "aspirine",
            "date_of_birth": datetime(1960, 1, 1),
            "gender": "M",
            "phone": "0611223344",
        }
        result = evaluate(data)
        assert any(v.severity == "error" and "aspirine" in v.message.lower() for v in result.violations)

    def test_validate_fever_warfarin(self):
        data = {
            "chief_complaint": "Fièvre",
            "medications": "warfarine",
            "allergies": "aucune",
            "date_of_birth": datetime(1970, 6, 15),
            "gender": "F",
            "phone": "0611223344",
        }
        result = evaluate(data)
        assert any("warfarine" in v.message.lower() for v in result.violations)

    def test_evaluate_episode_wrapper(self):
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


class TestTriageEngine:
    def test_triage_complete_data(self):
        rule_result = RuleResult(
            clinical_complete_percent=85.0,
            missing_fields=["emergency_phone"],
            violations=[],
            recommendations=["Add emergency_phone"],
            alerts=[],
        )
        service = AIService(priority=[AIProvider.MOCK])
        triage = triage_episode(
            episode_id="ep-123",
            rule_result=rule_result,
            ai_service=service,
            patient_summary="Patient stable, 45 ans",
        )
        assert triage.can_process is True
        assert triage.confidence is not None
        assert triage.confidence.score > 0.5
        assert triage.confidence.level in ("medium", "high")

    def test_triage_incomplete_data(self):
        rule_result = RuleResult(
            clinical_complete_percent=50.0,
            missing_fields=["dosage", "duration", "clinical_notes", "medications", "allergies"],
            violations=[],
            recommendations=[],
            alerts=[],
        )
        triage = triage_episode(
            episode_id="ep-456",
            rule_result=rule_result,
            ai_service=None,
            patient_summary="",
        )
        assert triage.can_process is False
        assert triage.ai_analysis is None
        assert triage.confidence is not None
        assert "Compléter les données cliniques" in triage.next_steps[0]

    def test_triage_with_safety_violation(self):
        from app.services.rules_engine import RuleViolation
        rule_result = RuleResult(
            clinical_complete_percent=75.0,
            missing_fields=["emergency_contact"],
            violations=[
                RuleViolation(
                    field="allergies",
                    severity="error",
                    message="Patient allergique à l'aspirine avec douleur thoracique.",
                    recommendation="Ne PAS administrer d'aspirine.",
                )
            ],
            recommendations=["Add emergency_contact"],
            alerts=[],
        )
        service = AIService(priority=[AIProvider.MOCK])
        triage = triage_episode(
            episode_id="ep-789",
            rule_result=rule_result,
            ai_service=service,
            patient_summary="Patient allergique",
        )
        assert triage.can_process is True
        assert any("1 severe safety violation" in f for f in triage.confidence.flags)
