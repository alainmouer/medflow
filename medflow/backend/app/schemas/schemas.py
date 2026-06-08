"""Pydantic schemas for request/response validation."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class TenantBase(BaseModel):
    name: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=100)
    specialty: str | None = Field(None, max_length=100)
    address: str | None = None
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = Field(None, max_length=100)


class TenantCreate(TenantBase):
    pass


class TenantOut(TenantBase):
    id: str
    is_active: bool
    plan: str
    hds_certified: bool
    settings: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=100)
    full_name: str = Field(..., max_length=100)
    role: str = Field(..., max_length=50)
    specialty: str | None = Field(None, max_length=100)
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=12, max_length=128)
    tenant_id: str


class UserOut(UserBase):
    id: str
    tenant_id: str
    mfa_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class HealthOut(BaseModel):
    status: str
    version: str
    env: str


# -----------------------------------------------------------------------------
# Patient schemas
# -----------------------------------------------------------------------------

class PatientBase(BaseModel):
    external_id: str | None = Field(None, max_length=100)
    last_name: str = Field(..., max_length=100)
    first_name: str = Field(..., max_length=100)
    date_of_birth: datetime | None = None
    gender: str | None = Field(None, max_length=20)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = Field(None, max_length=100)
    address: str | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = Field(None, max_length=20)
    allergies: str | None = None


class PatientCreate(PatientBase):
    pass


class PatientOut(PatientBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# -----------------------------------------------------------------------------
# Episode schemas
# -----------------------------------------------------------------------------

class EpisodeBase(BaseModel):
    patient_id: str
    episode_type: str | None = Field(None, max_length=50)
    chief_complaint: str | None = None
    clinical_notes: str | None = None
    clinical_complete_percent: float = 0.0
    intake_method: str | None = Field(None, max_length=50)


class EpisodeCreate(EpisodeBase):
    pass


class EpisodeUpdate(BaseModel):
    status: str | None = None
    chief_complaint: str | None = None
    clinical_notes: str | None = None
    clinical_complete_percent: float | None = None
    intake_method: str | None = None


class EpisodeOut(EpisodeBase):
    id: str
    tenant_id: str
    status: str
    collected_by: str | None = None
    signed_by: str | None = None
    signed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# -----------------------------------------------------------------------------
# Prescription schemas
# -----------------------------------------------------------------------------

class PrescriptionBase(BaseModel):
    episode_id: str
    medications: str | None = None
    dosage: str | None = Field(None, max_length=200)
    duration: str | None = Field(None, max_length=100)
    instructions: str | None = None
    warnings: str | None = None


class PrescriptionCreate(PrescriptionBase):
    pass


class PrescriptionUpdate(BaseModel):
    medications: str | None = None
    dosage: str | None = None
    duration: str | None = None
    instructions: str | None = None
    warnings: str | None = None


class PrescriptionOut(PrescriptionBase):
    id: str
    tenant_id: str
    status: str
    created_by: str | None = None
    signed_by: str | None = None
    signed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# -----------------------------------------------------------------------------
# AI / Pipeline schemas
# -----------------------------------------------------------------------------

class RuleViolationOut(BaseModel):
    field: str
    severity: str
    message: str
    recommendation: str | None = None


class ConfidenceScoreOut(BaseModel):
    score: float
    level: str
    risk_category: str | None = None
    triage_notes: list[str]
    flags: list[str]


class AnalysisResult(BaseModel):
    episode_id: str
    clinical_complete_percent: float
    can_process: bool
    missing_fields: list[str]
    violations: list[RuleViolationOut]
    recommendations: list[str]
    ai_analysis: str | None = None
    confidence: ConfidenceScoreOut | None = None
    next_steps: list[str]


class PipelineRequest(BaseModel):
    episode_id: str
    run_ai_analysis: bool = True


# -----------------------------------------------------------------------------
# Triage schemas
# -----------------------------------------------------------------------------

class TriageBase(BaseModel):
    episode_id: str | None = None
    patient_id: str | None = None
    chief_complaint: str | None = None
    heart_rate: int | None = Field(None, ge=0, le=300)
    blood_pressure_systolic: int | None = Field(None, ge=0, le=300)
    blood_pressure_diastolic: int | None = Field(None, ge=0, le=200)
    temperature: float | None = Field(None, ge=30.0, le=45.0)
    oxygen_saturation: float | None = Field(None, ge=0.0, le=100.0)
    respiratory_rate: int | None = Field(None, ge=0, le=60)
    glucose: float | None = Field(None, ge=0.0, le=50.0)
    pain_scale: int | None = Field(None, ge=0, le=10)
    consciousness_level: str | None = Field(None, max_length=20)
    notes: str | None = None


class TriageCreate(TriageBase):
    pass


class TriageUpdate(BaseModel):
    chief_complaint: str | None = None
    heart_rate: int | None = Field(None, ge=0, le=300)
    blood_pressure_systolic: int | None = Field(None, ge=0, le=300)
    blood_pressure_diastolic: int | None = Field(None, ge=0, le=200)
    temperature: float | None = Field(None, ge=30.0, le=45.0)
    oxygen_saturation: float | None = Field(None, ge=0.0, le=100.0)
    respiratory_rate: int | None = Field(None, ge=0, le=60)
    glucose: float | None = Field(None, ge=0.0, le=50.0)
    pain_scale: int | None = Field(None, ge=0, le=10)
    consciousness_level: str | None = Field(None, max_length=20)
    status: str | None = None
    assigned_to: str | None = None
    notes: str | None = None


class TriageOut(TriageBase):
    id: str
    tenant_id: str
    priority: str
    score: int
    status: str
    assigned_to: str | None = None
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TriageStatsOut(BaseModel):
    tenant_id: str
    counts: dict[str, int]


# -----------------------------------------------------------------------------