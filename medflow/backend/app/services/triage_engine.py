"""Triage Engine for AI confidence scoring and risk prioritization."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.services.ai_service import AIService, AIProviderError
from app.services.rules_engine import RuleResult

logger = logging.getLogger("medflow.triage")


@dataclass
class ConfidenceScore:
    """Confidence and triage metadata for an AI-generated result."""

    score: float  # 0.0 - 1.0
    level: str  # low | medium | high
    risk_category: str | None = None  # urgent | routine | followup
    triage_notes: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)


@dataclass
class TriageResult:
    """Combined triage output: rules + LLM + confidence."""

    episode_id: str
    clinical_complete_percent: float
    can_process: bool  # True if completeness >= 70%
    rule_result: RuleResult
    ai_analysis: str | None = None
    confidence: ConfidenceScore | None = None
    next_steps: list[str] = field(default_factory=list)


def _calculate_confidence(
    completeness: float,
    rule_violations: list[Any],
    ai_response_length: int,
) -> ConfidenceScore:
    """Heuristic confidence score based on completeness, safety, and output coherence.

    Scoring logic:
      - Completeness contributes up to 0.40
      - No severe violations contributes up to 0.30
      - AI response length (proxy for detail) contributes up to 0.30
    """
    score = 0.0
    flags: list[str] = []

    # Completeness weight
    score += min(completeness / 100.0, 1.0) * 0.40

    # Safety weight: penalise errors heavily
    error_count = sum(1 for v in rule_violations if getattr(v, "severity", "") == "error")
    if error_count == 0:
        score += 0.30
    else:
        score += max(0.0, 0.30 - (error_count * 0.15))
        flags.append(f"{error_count} severe safety violation(s) detected")

    # Coherence weight (response length proxy)
    if ai_response_length > 200:
        score += 0.30
    elif ai_response_length > 50:
        score += 0.15
    else:
        flags.append("AI response too short — low coherence")

    # Clamp and determine level
    score = round(max(0.0, min(1.0, score)), 2)
    if score >= 0.75:
        level = "high"
    elif score >= 0.45:
        level = "medium"
    else:
        level = "low"

    # Risk category
    if completeness < 50 or error_count > 0:
        risk = "urgent"
    elif completeness < 80:
        risk = "followup"
    else:
        risk = "routine"

    return ConfidenceScore(
        score=score,
        level=level,
        risk_category=risk,
        triage_notes=[f"Confidence derived from completeness ({completeness}%) and {len(rule_violations)} safety checks"],
        flags=flags,
    )


def triage_episode(
    episode_id: str,
    rule_result: RuleResult,
    ai_service: AIService | None,
    patient_summary: str,
) -> TriageResult:
    """Run the full triage pipeline: rules + optional LLM enrichment + confidence scoring.

    Args:
        episode_id: The episode UUID.
        rule_result: Already-computed rules engine result.
        ai_service: AIService instance for LLM calls.
        patient_summary: Brief text summary of patient context for the LLM.

    Returns:
        TriageResult with all metadata.
    """
    can_process = rule_result.clinical_complete_percent >= 70.0
    ai_analysis: str | None = None
    confidence: ConfidenceScore | None = None
    next_steps: list[str] = []

    # If completeness is decent, ask the LLM for enrichment / prescription draft
    if can_process:
        prompt = (
            f"Contexte patient : {patient_summary}\n"
            f"Complétude clinique : {rule_result.clinical_complete_percent}%.\n"
            f"Champs manquants : {rule_result.missing_fields}.\n"
            f"Violations de sécurité : {[v.message for v in rule_result.violations]}.\n\n"
            "En tant qu'assistant médical, fournis une analyse concise (max 300 mots) :\n"
            "1. Évaluation du risque clinique\n"
            "2. Suggestions de prescriptions ou examens complémentaires\n"
            "3. Points d'attention pour le médecin signataire\n"
            "Réponds en français dans un JSON structuré si possible."
        )
        try:
            ai_analysis = ai_service.generate(prompt, temperature=0.2, max_tokens=800)
            next_steps.append("Validation côte-à-côte par le médecin signataire requise")
            next_steps.append("Vérifier les allergies et interactions médicamenteuses")
        except AIProviderError as exc:
            logger.error("AI generation failed for episode %s: %s", episode_id, exc)
            ai_analysis = "[Analyse IA indisponible — passez en mode validation manuelle]"
            next_steps.append("Analyse IA indisponible — validation manuelle obligatoire")
    else:
        next_steps.append("Compléter les données cliniques avant traitement IA")
        if rule_result.missing_fields:
            next_steps.extend([f"Ajouter: {m}" for m in rule_result.missing_fields[:3]])

    # Compute confidence
    response_len = len(ai_analysis) if ai_analysis else 0
    confidence = _calculate_confidence(
        completeness=rule_result.clinical_complete_percent,
        rule_violations=rule_result.violations,
        ai_response_length=response_len,
    )

    # Add next steps from confidence flags
    if confidence.flags:
        next_steps.extend(confidence.flags)

    return TriageResult(
        episode_id=episode_id,
        clinical_complete_percent=rule_result.clinical_complete_percent,
        can_process=can_process,
        rule_result=rule_result,
        ai_analysis=ai_analysis,
        confidence=confidence,
        next_steps=list(dict.fromkeys(next_steps)),  # dedupe while preserving order
    )
