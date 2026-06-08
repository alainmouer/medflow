"""Urgency triage engine for P1–P5 scoring."""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TriageScore:
    priority: str
    score: int
    flags: list[str]


def _normalize(text: str | None) -> str:
    if not text:
        return ""
    return (
        unicodedata.normalize("NFD", text.lower())
        .encode("ascii", "ignore")
        .decode("ascii")
    )


# ---------------------------------------------------------------------------
# Physiological thresholds
# ---------------------------------------------------------------------------
VITAL_THRESHOLDS: dict[str, list[tuple[tuple[float, float], int]]] = {
    "heart_rate": [
        ((0, 40), 20),
        ((41, 50), 10),
        ((51, 59), 5),
        ((100, 120), 5),
        ((121, 150), 10),
        ((151, 300), 20),
    ],
    "blood_pressure_systolic": [
        ((0, 80), 20),
        ((81, 89), 10),
        ((90, 99), 5),
        ((141, 160), 5),
        ((161, 180), 10),
        ((181, 300), 20),
    ],
    "blood_pressure_diastolic": [
        ((0, 59), 15),
        ((60, 64), 7),
        ((65, 69), 3),
        ((101, 110), 3),
        ((111, 120), 7),
        ((121, 200), 15),
    ],
    "temperature": [
        ((30, 35), 20),
        ((35.1, 35.9), 10),
        ((36, 36.4), 5),
        ((37.3, 38.0), 5),
        ((38.1, 39.0), 10),
        ((39.1, 45.0), 20),
    ],
    "oxygen_saturation": [
        ((0, 84), 25),
        ((85, 89), 15),
        ((90, 94), 5),
    ],
    "respiratory_rate": [
        ((0, 8), 20),
        ((9, 10), 10),
        ((11, 12), 5),
        ((21, 22), 5),
        ((23, 25), 10),
        ((26, 60), 20),
    ],
    "glucose": [
        ((0, 2.7), 20),
        ((2.8, 3.4), 10),
        ((3.5, 3.8), 5),
        ((7.9, 11.0), 5),
        ((11.1, 15.0), 10),
        ((15.1, 50.0), 20),
    ],
    "pain_scale": [
        ((8, 10), 20),
        ((5, 7), 10),
        ((3, 4), 5),
    ],
}


def _score_vital(vital: str, value: float | int | None) -> tuple[int, str | None]:
    if value is None:
        return 0, None
    thresholds = VITAL_THRESHOLDS.get(vital, [])
    check_value = float(value)
    for (low, high), points in thresholds:
        if low <= check_value <= high:
            return points, f"{vital}:{check_value}"
    return 0, None


# ---------------------------------------------------------------------------
# Consciousness level
# ---------------------------------------------------------------------------
CONSCIOUSNESS_SCORES = {
    "alert": 0,
    "verbal": 5,
    "pain": 10,
    "unresponsive": 25,
}


def _score_consciousness(level: str | None) -> tuple[int, str | None]:
    if not level:
        return 0, None
    norm = _normalize(level).strip()
    for key, pts in CONSCIOUSNESS_SCORES.items():
        if key in norm:
            return pts, f"consciousness:{key}"
    return 0, None


# ---------------------------------------------------------------------------
# Keyword matching
# ---------------------------------------------------------------------------
KEYWORDS = {
    "P1": [
        "arrest", "cardiac", "not breathing", "unconscious", "anaphylaxis",
        "cyanosis", "asphyxia", "massive hemorrhage", "trauma grave",
        "no pulse", "arret cardiaque", "pas de pouls", "pas de respiration",
        "inconscient", "anaphylaxie", "cyanose", "asphyxie", "hemorragie massive",
    ],
    "P2": [
        "chest pain", "dyspnea", "severe", "high fever", "seizure",
        "stroke", "malaise", "syncope", "douleur thoracique", "dyspnee",
        "difficulte respiratoire", "convulsion", "avc", "perte de connaissance",
    ],
    "P3": [
        "fever", "vomiting", "abdominal pain", "infection", "fracture",
        "wound", "fièvre", "vomissement", "douleur abdominale", "plaie ouverte",
    ],
    "P4": [
        "minor", "cough", "cold", "headache", "cut", "bruise",
        "toux", "rhume", "maux de tete", "petite coupure", "ecchymose",
        "ecorchure",
    ],
    "P5": [
        "prescription renewal", "certificate", "checkup", "vaccine",
        "appointment", "renouvellement", "certificat", "bilan", "vaccin",
        "rendez-vous", "convocation",
    ],
}


def _score_keywords(chief_complaint: str | None) -> tuple[int, str]:
    text = _normalize(chief_complaint)
    max_score = 0
    matched_level = "P5"
    for level, keywords in KEYWORDS.items():
        for kw in keywords:
            if _normalize(kw) in text:
                pts = {"P1": 30, "P2": 20, "P3": 10, "P4": 5, "P5": 0}[level]
                if pts > max_score:
                    max_score = pts
                    matched_level = level
    return max_score, matched_level


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def score_urgency(data: dict) -> TriageScore:
    """
    Compute triage priority from physiological data and chief complaint.

    Args:
        data: dict with optional keys:
            heart_rate, blood_pressure_systolic, blood_pressure_diastolic,
            temperature, oxygen_saturation, respiratory_rate, glucose,
            pain_scale, consciousness_level, chief_complaint

    Returns:
        TriageScore(priority='P1'..'P5', score=int, flags=list[str])
    """
    total = 0
    flags: list[str] = []

    vitals = [
        "heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic",
        "temperature", "oxygen_saturation", "respiratory_rate",
        "glucose", "pain_scale",
    ]

    for vital in vitals:
        pts, flag = _score_vital(vital, data.get(vital))
        if pts:
            total += pts
            flags.append(flag)  # type: ignore[arg-type]

    pts, flag = _score_consciousness(data.get("consciousness_level"))
    if pts:
        total += pts
        flags.append(flag)  # type: ignore[arg-type]

    kw_score, kw_level = _score_keywords(data.get("chief_complaint"))
    total += kw_score
    if kw_score:
        flags.append(f"keyword:{kw_level}")

    # Final mapping
    if total >= 50:
        priority = "P1"
    elif total >= 35:
        priority = "P2"
    elif total >= 20:
        priority = "P3"
    elif total >= 5:
        priority = "P4"
    else:
        priority = "P5"

    return TriageScore(priority=priority, score=total, flags=flags)
