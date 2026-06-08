"""Rules Engine for clinical completeness validation and medical safety checks."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("medflow.rules")


@dataclass
class RuleViolation:
    """A single rule violation with actionable metadata."""

    field: str
    severity: str  # error | warning | info
    message: str
    recommendation: str | None = None


@dataclass
class RuleResult:
    """Result of running the rules engine on a clinical record."""

    clinical_complete_percent: float = 0.0
    missing_fields: list[str] = field(default_factory=list)
    violations: list[RuleViolation] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    alerts: list[RuleViolation] = field(default_factory=list)  # high-severity violations


def _has_value(value: Any) -> bool:
    """Check if a field has a meaningful value."""
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    return True


def _check_mandatory_fields(data: dict[str, Any]) -> tuple[float, list[str]]:
    """Calculate completeness percentage and report missing mandatory fields.

    Mandatory fields for a clinical episode:
      1. chief_complaint (motif de consultation)
      2. clinical_notes (compte-rendu / observations)
      3. medications (traitements en cours)
      4. allergies (allergies connues)
      5. dosage / duration (posologie)
      6. patient demographics (date_of_birth, gender, phone)
    """
    mandatory = [
        ("chief_complaint", "Motif de consultation"),
        ("clinical_notes", "Compte-rendu clinique"),
        ("medications", "Traitements en cours"),
        ("allergies", "Allergies connues"),
        ("dosage", "Posologie / dosage"),
        ("duration", "Durée du traitement"),
        ("date_of_birth", "Date de naissance du patient"),
        ("gender", "Sexe du patient"),
        ("phone", "Téléphone du patient"),
        ("emergency_contact", "Contact d'urgence"),
    ]

    present = 0
    missing: list[str] = []

    for key, label in mandatory:
        if _has_value(data.get(key)):
            present += 1
        else:
            missing.append(label)

    total = len(mandatory)
    percent = round((present / total) * 100, 1) if total > 0 else 0.0
    return percent, missing


def _check_safety_rules(data: dict[str, Any]) -> list[RuleViolation]:
    """Evaluate medical safety rules / contre-indications.

    Rules:
      - If chief_complaint contains 'douleur thoracique' AND allergies contains 'aspirine',
        flag a warning (do not give Aspirin).
      - If chief_complaint contains 'fièvre' AND age < 16, flag NSAID caution.
      - If medications contains 'warfarine', flag INR monitoring.
    """
    violations: list[RuleViolation] = []
    complaint = str(data.get("chief_complaint", "")).lower()
    allergies = str(data.get("allergies", "")).lower()
    medications = str(data.get("medications", "")).lower()

    # Rule: Aspirin allergy + chest pain
    if "douleur thoracique" in complaint or "chest pain" in complaint:
        if "aspirine" in allergies or "aspirin" in allergies:
            violations.append(
                RuleViolation(
                    field="allergies",
                    severity="error",
                    message="Patient allergique à l'aspirine avec douleur thoracique.",
                    recommendation="Ne PAS administrer d'aspirine. Évaluer alternative antithrombotique.",
                )
            )

    # Rule: Fever + anticoagulant
    if "fièvre" in complaint or "fever" in complaint:
        if "warfarine" in medications or "warfarin" in medications:
            violations.append(
                RuleViolation(
                    field="medications",
                    severity="warning",
                    message="Fièvre chez patient sous anticoagulant (warfarine).",
                    recommendation="Surveillance accrue du taux d'INR. Éviter les AINS.",
                )
            )

    # Rule: Known allergy present but no emergency contact
    if allergies and "aucune" not in allergies and "none" not in allergies:
        if not _has_value(data.get("emergency_contact")):
            violations.append(
                RuleViolation(
                    field="emergency_contact",
                    severity="warning",
                    message="Allergie déclarée sans contact d'urgence.",
                    recommendation="Saisir un contact d'urgence en cas de réaction allergique grave.",
                )
            )

    return violations


def evaluate(data: dict[str, Any]) -> RuleResult:
    """Run the full rules engine over a clinical data dict.

    The input dict should contain a flattened view of episode + patient + prescription
    fields for evaluation.
    """
    percent, missing = _check_mandatory_fields(data)
    violations = _check_safety_rules(data)

    # Build recommendations from missing fields
    recommendations = [f"Saisir le champ requis : {m}" for m in missing]

    # High-severity violations become alerts
    alerts = [v for v in violations if v.severity == "error"]

    logger.info("Rules engine: completeness=%.1f%% missing=%d violations=%d", percent, len(missing), len(violations))

    return RuleResult(
        clinical_complete_percent=percent,
        missing_fields=missing,
        violations=violations,
        recommendations=recommendations,
        alerts=alerts,
    )


def evaluate_episode(episode: Any, patient: Any, prescription: Any | None = None) -> RuleResult:
    """Convenience wrapper that flattens ORM objects into a dict for evaluate()."""
    data: dict[str, Any] = {
        "chief_complaint": getattr(episode, "chief_complaint", None),
        "clinical_notes": getattr(episode, "clinical_notes", None),
        "medications": getattr(prescription, "medications", None),
        "dosage": getattr(prescription, "dosage", None),
        "duration": getattr(prescription, "duration", None),
        "instructions": getattr(prescription, "instructions", None),
        "warnings": getattr(prescription, "warnings", None),
        "allergies": getattr(patient, "allergies", None),
        "date_of_birth": getattr(patient, "date_of_birth", None),
        "gender": getattr(patient, "gender", None),
        "phone": getattr(patient, "phone", None),
        "emergency_contact": getattr(patient, "emergency_contact", None),
        "emergency_phone": getattr(patient, "emergency_phone", None),
    }
    return evaluate(data)
