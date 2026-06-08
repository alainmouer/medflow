"""Unit tests for urgency triage engine."""
from __future__ import annotations

import pytest

from app.services.urgency_triage import (
    score_urgency,
    _score_vital,
    _score_consciousness,
    _score_keywords,
    TriageScore,
)


class TestScoreVital:
    def test_heart_rate_normal(self):
        pts, flag = _score_vital("heart_rate", 72)
        assert pts == 0
        assert flag is None

    def test_heart_rate_critical_high(self):
        pts, flag = _score_vital("heart_rate", 200)
        assert pts == 20
        assert "heart_rate:200.0" == flag

    def test_heart_rate_warning_high(self):
        pts, flag = _score_vital("heart_rate", 145)
        assert pts == 10
        assert "heart_rate:145.0" == flag

    def test_oxygen_saturation_critical_low(self):
        pts, flag = _score_vital("oxygen_saturation", 80)
        assert pts == 25
        assert "oxygen_saturation:80.0" == flag

    def test_none_value(self):
        pts, flag = _score_vital("heart_rate", None)
        assert pts == 0
        assert flag is None


class TestScoreConsciousness:
    def test_alert(self):
        pts, flag = _score_consciousness("Alert")
        assert pts == 0
        assert flag == "consciousness:alert"

    def test_unresponsive(self):
        pts, flag = _score_consciousness("Unresponsive")
        assert pts == 25
        assert flag == "consciousness:unresponsive"

    def test_none(self):
        pts, flag = _score_consciousness(None)
        assert pts == 0
        assert flag is None


class TestScoreKeywords:
    def test_p1_keyword(self):
        pts, level = _score_keywords("Arret cardiaque")
        assert pts == 30
        assert level == "P1"

    def test_p2_keyword(self):
        pts, level = _score_keywords("Douleur thoracique")
        assert pts == 20
        assert level == "P2"

    def test_p4_keyword(self):
        pts, level = _score_keywords("Maux de tête")
        assert pts == 5
        assert level == "P4"

    def test_p5_keyword(self):
        pts, level = _score_keywords("Renouvellement ordonnance")
        assert pts == 0
        assert level == "P5"

    def test_mixed_takes_highest(self):
        pts, level = _score_keywords("Douleur thoracique et renouvellement")
        assert pts == 20
        assert level == "P2"

    def test_none(self):
        pts, level = _score_keywords(None)
        assert pts == 0
        assert level == "P5"


class TestScoreUrgency:
    def test_p1_from_vitals(self):
        result = score_urgency({
            "heart_rate": 200,
            "oxygen_saturation": 80,
            "consciousness_level": "unresponsive",
        })
        assert result.priority == "P1"
        assert result.score >= 50
        assert "heart_rate:200.0" in result.flags
        assert "oxygen_saturation:80.0" in result.flags

    def test_p2_from_keywords(self):
        result = score_urgency({
            "heart_rate": 72,
            "pain_scale": 8,
            "chief_complaint": "Dyspnée aiguë",
        })
        assert result.priority == "P2"
        assert result.score >= 35
        assert "keyword:P2" in result.flags

    def test_p5_healthy(self):
        result = score_urgency({
            "heart_rate": 72,
            "blood_pressure_systolic": 120,
            "temperature": 36.8,
            "chief_complaint": "Renouvellement ordonnance",
        })
        assert result.priority == "P5"
        assert result.score == 0

    def test_p3_borderline(self):
        result = score_urgency({
            "heart_rate": 110,
            "temperature": 38.5,
            "chief_complaint": "Fièvre",
        })
        assert result.priority == "P3"
        assert result.score >= 20

    def test_p4_from_pain(self):
        result = score_urgency({
            "pain_scale": 4,
        })
        assert result.priority == "P4"
        assert result.score >= 5

    def test_pain_scale_warning(self):
        result = score_urgency({
            "pain_scale": 9,
        })
        assert result.score >= 20
        assert "pain_scale:9.0" in result.flags

    def test_consciousness_escalation(self):
        result = score_urgency({
            "consciousness_level": "unresponsive",
        })
        assert result.score == 25
        assert "consciousness:unresponsive" in result.flags

    def test_glucose_critical(self):
        result = score_urgency({
            "glucose": 1.5,
        })
        assert result.score >= 20
        assert "glucose:1.5" in result.flags

    def test_return_type(self):
        result = score_urgency({})
        assert isinstance(result, TriageScore)
        assert result.priority in ("P1", "P2", "P3", "P4", "P5")
        assert isinstance(result.score, int)
        assert isinstance(result.flags, list)
