"""PDF generation service using ReportLab."""
from __future__ import annotations

import io
import hashlib
from datetime import datetime, timezone

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm


def _draw_header(c: canvas.Canvas, title: str, tenant_name: str = "MedFlow") -> None:
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, A4[1] - 2 * cm, title)
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, A4[1] - 2.5 * cm, f"{tenant_name} — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}")
    c.line(2 * cm, A4[1] - 2.7 * cm, A4[0] - 2 * cm, A4[1] - 2.7 * cm)


def _draw_footer(c: canvas.Canvas, page_num: int) -> None:
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, 1 * cm, f"Page {page_num}")


def generate_episode_pdf(episode_data: dict) -> tuple[bytes, str]:
    """Generate a PDF report for an episode.

    Returns (pdf_bytes, sha256_hex).
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, "Rapport d'épisode", episode_data.get("tenant_name", "MedFlow"))
    y = A4[1] - 4 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Informations patient")
    y -= 0.8 * cm
    c.setFont("Helvetica", 10)
    for key, value in episode_data.get("patient", {}).items():
        c.drawString(2 * cm, y, f"{key}: {value}")
        y -= 0.5 * cm
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Détails de l'épisode")
    y -= 0.8 * cm
    c.setFont("Helvetica", 10)
    for key, value in episode_data.get("episode", {}).items():
        c.drawString(2 * cm, y, f"{key}: {value}")
        y -= 0.5 * cm
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Prescriptions associées")
    y -= 0.8 * cm
    c.setFont("Helvetica", 10)
    for pres in episode_data.get("prescriptions", []):
        c.drawString(2 * cm, y, f"- {pres.get('medications', 'N/A')} ({pres.get('status', 'N/A')})")
        y -= 0.5 * cm
    _draw_footer(c, 1)
    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    sha = hashlib.sha256(pdf_bytes).hexdigest()
    return pdf_bytes, sha
