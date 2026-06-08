"""SQLAlchemy models with tenant_id on every table."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class GUIDMixin:
    """Token UUID column compatible with SQLite and PostgreSQL."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )


class Tenant(Base):
    """Multi-tenant root entity."""

    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    plan: Mapped[str] = mapped_column(String(50), default="internal")  # internal / commercial
    hds_certified: Mapped[bool] = mapped_column(Boolean, default=False)
    settings: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base):
    """Application user with RBAC role."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Patient(Base):
    """Patient entity with multi-tenant isolation."""

    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Episode(Base):
    """Clinical episode tied to a patient visit."""

    __tablename__ = "episodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    patient_id: Mapped[str] = mapped_column(String(36), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    episode_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)
    clinical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    clinical_complete_percent: Mapped[float] = mapped_column(nullable=False, default=0.0)
    intake_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    collected_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    signed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Prescription(Base):
    """Medical prescription tied to an episode. Signing is doctor-only.

    Workflow: draft → signed → sent → cancelled
    """

    __tablename__ = "prescriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    episode_id: Mapped[str] = mapped_column(String(36), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    medications: Mapped[str | None] = mapped_column(Text, nullable=True)
    dosage: Mapped[str | None] = mapped_column(String(200), nullable=True)
    duration: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    warnings: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    signed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    signature_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # SHA-256 hex
    sent_to_email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TriageEntry(Base):
    """Urgency triage entry (P1-P5) linked to an episode or standalone intake."""

    __tablename__ = "triage_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    episode_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    patient_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Vital signs
    heart_rate: Mapped[int | None] = mapped_column(nullable=True)
    blood_pressure_systolic: Mapped[int | None] = mapped_column(nullable=True)
    blood_pressure_diastolic: Mapped[int | None] = mapped_column(nullable=True)
    temperature: Mapped[float | None] = mapped_column(nullable=True)
    oxygen_saturation: Mapped[float | None] = mapped_column(nullable=True)
    respiratory_rate: Mapped[int | None] = mapped_column(nullable=True)
    glucose: Mapped[float | None] = mapped_column(nullable=True)
    pain_scale: Mapped[int | None] = mapped_column(nullable=True)
    consciousness_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Scoring result
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="P5")
    score: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="waiting")
    assigned_to: Mapped[str | None] = mapped_column(String(36), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Appointment(Base):
    """Unified appointment (cabinet, teleconsultation, exam, field-visit link)."""

    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    patient_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    episode_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    assigned_staff_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    appointment_type: Mapped[str] = mapped_column(String(50), nullable=False, default="consultation")
    modality: Mapped[str] = mapped_column(String(50), nullable=False, default="synchronous_presential")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="scheduled")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_min: Mapped[int | None] = mapped_column(nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    video_link: Mapped[str | None] = mapped_column(String(300), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FieldVisit(Base):
    """Field mission (home, EHPAD, clinic) with checklist and episode sync."""

    __tablename__ = "field_visits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    patient_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    episode_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    assigned_staff_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    collection_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="internal_visit")
    location_type: Mapped[str] = mapped_column(String(50), nullable=False, default="home")
    location_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    patient_count: Mapped[int] = mapped_column(nullable=False, default=1)
    is_group_visit: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduled_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    checklist: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    checklist_completion_rate: Mapped[int] = mapped_column(nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Billing(Base):
    """Medical billing / invoice tied to an episode."""

    __tablename__ = "billings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    episode_id: Mapped[str] = mapped_column(String(36), nullable=False)
    patient_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    # Billing data
    ccam_codes: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    acts_total: Mapped[float] = mapped_column(nullable=False, default=0.0)
    # Insurance
    social_security_base: Mapped[float] = mapped_column(nullable=False, default=0.0)
    social_security_paid: Mapped[float] = mapped_column(nullable=False, default=0.0)
    mutuelle_paid: Mapped[float] = mapped_column(nullable=False, default=0.0)
    patient_liability: Mapped[float] = mapped_column(nullable=False, default=0.0)
    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    # Timestamps
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    validated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
# Table audit trail and external_integration_logs will be added in later phases.
