"""API routes: health, auth, interop stubs."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.database import get_db
from app.models.models import Tenant, User, Patient, Episode, Prescription, TriageEntry, Appointment, FieldVisit, Billing, AISystemPrompt, Message
from app.schemas.schemas import (
    HealthOut,
    Token,
    TenantCreate,
    TenantOut,
    UserOut,
    UserCreate,
    PatientCreate,
    PatientOut,
    EpisodeCreate,
    EpisodeOut,
    EpisodeUpdate,
    PrescriptionCreate,
    PrescriptionOut,
    PrescriptionUpdate,
    PrescriptionSendRequest,
    AnalysisResult,
    TriageCreate,
    TriageOut,
    TriageStatsOut,
    RuleViolationOut,
    ConfidenceScoreOut,
    TriageUpdate,
    AppointmentCreate,
    AppointmentOut,
    AppointmentUpdate,
    FieldVisitCreate,
    FieldVisitOut,
    FieldVisitUpdate,
    BillingCreate,
    BillingUpdate,
    BillingOut,
    AISystemPromptCreate,
    AISystemPromptUpdate,
    AISystemPromptOut,
    MessageCreate,
    MessageOut,
)
from app.services.ai_service import AIService, get_ai_service
from app.services.rules_engine import evaluate_episode
from app.services.triage_engine import triage_episode
from app.services.urgency_triage import score_urgency
from app.api.ws_triage import manager as triage_ws_manager

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
    except Exception:
        raise credentials_exception  # noqa: B904
    if user_id is None:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()  # noqa: S608
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise credentials_exception
    return user


# -----------------------------------------------------------------------------
# Health
# -----------------------------------------------------------------------------

@router.get("/health", response_model=HealthOut, tags=["system"])
async def health() -> HealthOut:
    return HealthOut(status="healthy", version=settings.VERSION, env="dev")


# -----------------------------------------------------------------------------
# Auth
# -----------------------------------------------------------------------------

@router.post("/api/auth/login", response_model=Token, tags=["auth"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.email == form_data.username).first()  # noqa: S608
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account disabled")
    token = create_access_token({"sub": user.id, "tenant_id": user.tenant_id, "role": user.role})
    return Token(access_token=token)


@router.get("/api/auth/me", response_model=UserOut, tags=["auth"])
async def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)


# -----------------------------------------------------------------------------
# Tenant management (admin only — Phase 2+ hardening)
# -----------------------------------------------------------------------------

@router.post("/api/admin/tenants", response_model=TenantOut, tags=["admin"])
async def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TenantOut:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    existing = db.query(Tenant).filter(Tenant.slug == payload.slug).first()  # noqa: S608
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists")
    tenant = Tenant(**payload.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return TenantOut.model_validate(tenant)


@router.get("/api/admin/tenants", response_model=list[TenantOut], tags=["admin"])
async def list_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TenantOut]:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return [TenantOut.model_validate(t) for t in db.query(Tenant).all()]


# -----------------------------------------------------------------------------
# Admin users
# -----------------------------------------------------------------------------


@router.get("/api/admin/users", response_model=list[UserOut], tags=["admin"])
async def admin_list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserOut]:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return [UserOut.model_validate(u) for u in db.query(User).filter(User.tenant_id == current_user.tenant_id).all()]


@router.post("/api/admin/users", response_model=UserOut, tags=["admin"])
async def admin_create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserOut:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    existing = db.query(User).filter(User.email == payload.email).first()  # noqa: S608
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    from app.core.security import get_password_hash
    user = User(
        tenant_id=current_user.tenant_id,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        specialty=payload.specialty,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.patch("/api/admin/users/{user_id}", response_model=UserOut, tags=["admin"])
async def admin_update_user(
    user_id: str,
    payload: UserCreate,  # reutilise UserCreate en tant que "payload complet"
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserOut:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    user = db.query(User).filter(User.id == user_id, User.tenant_id == current_user.tenant_id).first()  # noqa: S608
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if payload.password:
        from app.core.security import get_password_hash
        user.hashed_password = get_password_hash(payload.password)
    user.email = payload.email
    user.full_name = payload.full_name
    user.role = payload.role
    user.specialty = payload.specialty
    user.tenant_id = current_user.tenant_id
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.delete("/api/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["admin"])
async def admin_delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    user = db.query(User).filter(User.id == user_id, User.tenant_id == current_user.tenant_id).first()  # noqa: S608
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()


# -----------------------------------------------------------------------------
# Patient management (authenticated users with tenant_id)
# -----------------------------------------------------------------------------

@router.post("/api/patients", response_model=PatientOut, tags=["patients"])
async def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PatientOut:
    patient = Patient(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return PatientOut.model_validate(patient)


@router.get("/api/patients", response_model=list[PatientOut], tags=["patients"])
async def list_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PatientOut]:
    patients = db.query(Patient).filter(Patient.tenant_id == current_user.tenant_id).all()
    return [PatientOut.model_validate(p) for p in patients]


@router.get("/api/patients/{patient_id}", response_model=PatientOut, tags=["patients"])
async def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PatientOut:
    patient = db.query(Patient).filter(
        Patient.id == patient_id, Patient.tenant_id == current_user.tenant_id
    ).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return PatientOut.model_validate(patient)


# -----------------------------------------------------------------------------
# Episode management (authenticated users with tenant_id)
# -----------------------------------------------------------------------------

@router.post("/api/episodes", response_model=EpisodeOut, tags=["episodes"])
async def create_episode(
    payload: EpisodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeOut:
    patient = db.query(Patient).filter(
        Patient.id == payload.patient_id, Patient.tenant_id == current_user.tenant_id
    ).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    episode = Episode(tenant_id=current_user.tenant_id, collected_by=current_user.id, **payload.model_dump())
    db.add(episode)
    db.commit()
    db.refresh(episode)
    return EpisodeOut.model_validate(episode)


@router.get("/api/episodes", response_model=list[EpisodeOut], tags=["episodes"])
async def list_episodes(
    patient_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EpisodeOut]:
    query = db.query(Episode).filter(Episode.tenant_id == current_user.tenant_id)
    if patient_id:
        query = query.filter(Episode.patient_id == patient_id)
    episodes = query.all()
    return [EpisodeOut.model_validate(e) for e in episodes]


@router.get("/api/episodes/{episode_id}", response_model=EpisodeOut, tags=["episodes"])
async def get_episode(
    episode_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeOut:
    episode = db.query(Episode).filter(
        Episode.id == episode_id, Episode.tenant_id == current_user.tenant_id
    ).first()
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    return EpisodeOut.model_validate(episode)


@router.patch("/api/episodes/{episode_id}", response_model=EpisodeOut, tags=["episodes"])
async def update_episode(
    episode_id: str,
    payload: EpisodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeOut:
    episode = db.query(Episode).filter(
        Episode.id == episode_id, Episode.tenant_id == current_user.tenant_id
    ).first()
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(episode, field, value)
    db.commit()
    db.refresh(episode)
    return EpisodeOut.model_validate(episode)


# -----------------------------------------------------------------------------
# AI Pipeline — analysis & triage
# -----------------------------------------------------------------------------

@router.post("/api/episodes/{episode_id}/analyze", response_model=AnalysisResult, tags=["ai"])
async def analyze_episode(
    episode_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
) -> AnalysisResult:
    """Run the full AI rules+triage pipeline on an episode.

    Steps:
      1. Load episode + patient + optional prescription.
      2. Run rules engine for completeness & safety.
      3. If completeness >= 70%, run LLM analysis.
      4. Compute confidence score.
      5. Persist clinical_complete_percent to episode.
    """
    # RBAC: only doctor or ipa can run analysis
    if current_user.role not in ("doctor", "ipa"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor or IPA role required")

    episode = db.query(Episode).filter(
        Episode.id == episode_id, Episode.tenant_id == current_user.tenant_id
    ).first()
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")

    patient = db.query(Patient).filter(
        Patient.id == episode.patient_id, Patient.tenant_id == current_user.tenant_id
    ).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    prescription = db.query(Prescription).filter(
        Prescription.episode_id == episode_id, Prescription.tenant_id == current_user.tenant_id
    ).first()

    # Step 2 — Rules engine
    rule_result = evaluate_episode(episode, patient, prescription)

    # Step 3-4 — Triage + optional AI
    patient_summary = (
        f"{patient.first_name} {patient.last_name}, "
        f"né(e) le {patient.date_of_birth}, "
        f"sexe {patient.gender}, "
        f"motif: {episode.chief_complaint or 'non renseigné'}."
    )
    triage = triage_episode(
        episode_id=str(episode.id),
        rule_result=rule_result,
        ai_service=ai_service if rule_result.clinical_complete_percent >= 70.0 else None,
        patient_summary=patient_summary,
    )

    # Step 5 — Persist completeness
    episode.clinical_complete_percent = rule_result.clinical_complete_percent
    if rule_result.clinical_complete_percent >= 70.0 and episode.status == "collected":
        episode.status = "processing"
    db.commit()
    db.refresh(episode)

    return AnalysisResult(
        episode_id=str(episode.id),
        clinical_complete_percent=rule_result.clinical_complete_percent,
        can_process=triage.can_process,
        missing_fields=rule_result.missing_fields,
        violations=[
            RuleViolationOut(
                field=v.field, severity=v.severity, message=v.message, recommendation=v.recommendation
            )
            for v in rule_result.violations
        ],
        recommendations=rule_result.recommendations,
        ai_analysis=triage.ai_analysis,
        confidence=ConfidenceScoreOut(
            score=triage.confidence.score if triage.confidence else 0.0,
            level=triage.confidence.level if triage.confidence else "low",
            risk_category=triage.confidence.risk_category if triage.confidence else None,
            triage_notes=triage.confidence.triage_notes if triage.confidence else [],
            flags=triage.confidence.flags if triage.confidence else [],
        ) if triage.confidence else None,
        next_steps=triage.next_steps,
    )


@router.post("/api/episodes/{episode_id}/sign", response_model=EpisodeOut, tags=["episodes"])
async def sign_episode(
    episode_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeOut:
    """Sign off an episode as a doctor."""
    if current_user.role != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Episode signing is doctor-only")
    episode = db.query(Episode).filter(
        Episode.id == episode_id, Episode.tenant_id == current_user.tenant_id
    ).first()
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    if episode.status == "signed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Episode already signed")
    episode.status = "signed"
    db.commit()
    db.refresh(episode)
    return EpisodeOut.model_validate(episode)


# -----------------------------------------------------------------------------
# Prescription management (doctor-only signing)
# -----------------------------------------------------------------------------


def _require_doctor_or_ipa(user: User) -> None:
    """Raise 403 if user is not doctor or ipa."""
    if user.role not in ("doctor", "ipa"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor or IPA role required")


@router.post("/api/prescriptions", response_model=PrescriptionOut, tags=["prescriptions"])
async def create_prescription(
    payload: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PrescriptionOut:
    _require_doctor_or_ipa(current_user)
    episode = db.query(Episode).filter(
        Episode.id == payload.episode_id, Episode.tenant_id == current_user.tenant_id
    ).first()
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    prescription = Prescription(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        **payload.model_dump(),
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return PrescriptionOut.model_validate(prescription)


@router.get("/api/prescriptions", response_model=list[PrescriptionOut], tags=["prescriptions"])
async def list_prescriptions(
    episode_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PrescriptionOut]:
    query = db.query(Prescription).filter(Prescription.tenant_id == current_user.tenant_id)
    if episode_id:
        query = query.filter(Prescription.episode_id == episode_id)
    return [PrescriptionOut.model_validate(p) for p in query.all()]


@router.get("/api/prescriptions/{prescription_id}", response_model=PrescriptionOut, tags=["prescriptions"])
async def get_prescription(
    prescription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PrescriptionOut:
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id, Prescription.tenant_id == current_user.tenant_id
    ).first()
    if not prescription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    return PrescriptionOut.model_validate(prescription)


@router.patch("/api/prescriptions/{prescription_id}", response_model=PrescriptionOut, tags=["prescriptions"])
async def update_prescription(
    prescription_id: str,
    payload: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PrescriptionOut:
    _require_doctor_or_ipa(current_user)
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id, Prescription.tenant_id == current_user.tenant_id
    ).first()
    if not prescription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    if prescription.signed_by is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot edit a signed prescription")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prescription, field, value)
    db.commit()
    db.refresh(prescription)
    return PrescriptionOut.model_validate(prescription)


@router.post(
    "/api/prescriptions/{prescription_id}/sign",
    response_model=PrescriptionOut,
    tags=["prescriptions"],
)
async def sign_prescription(
    prescription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PrescriptionOut:
    if current_user.role != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Prescription signing is doctor-only")
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id, Prescription.tenant_id == current_user.tenant_id
    ).first()
    if not prescription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    if prescription.signed_by is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Prescription already signed")
    from datetime import datetime, timezone
    import hashlib
    payload = f"{prescription.id}:{prescription.episode_id}:{current_user.id}:{datetime.now(timezone.utc).isoformat()}"
    prescription.signature_hash = hashlib.sha256(payload.encode()).hexdigest()
    prescription.signed_by = current_user.id
    prescription.signed_at = datetime.now(timezone.utc)
    prescription.status = "signed"
    db.commit()
    db.refresh(prescription)
    return PrescriptionOut.model_validate(prescription)


@router.post(
    "/api/prescriptions/{prescription_id}/send",
    response_model=PrescriptionOut,
    tags=["prescriptions"],
)
async def send_prescription(
    prescription_id: str,
    payload: PrescriptionSendRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PrescriptionOut:
    if current_user.role not in ("doctor", "ipa"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor or IPA role required")
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id, Prescription.tenant_id == current_user.tenant_id
    ).first()
    if not prescription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    if prescription.status != "signed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Prescription must be signed before sending")
    if prescription.status == "sent":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Prescription already sent")
    from datetime import datetime, timezone
    prescription.status = "sent"
    prescription.sent_at = datetime.now(timezone.utc)
    if payload and payload.sent_to_email:
        prescription.sent_to_email = payload.sent_to_email
    db.commit()
    db.refresh(prescription)
    return PrescriptionOut.model_validate(prescription)


@router.post(
    "/api/prescriptions/{prescription_id}/cancel",
    response_model=PrescriptionOut,
    tags=["prescriptions"],
)
async def cancel_prescription(
    prescription_id: str,
    cancellation_reason: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PrescriptionOut:
    if current_user.role not in ("doctor", "ipa"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor or IPA role required")
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id, Prescription.tenant_id == current_user.tenant_id
    ).first()
    if not prescription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    if prescription.status == "cancelled":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Prescription already cancelled")
    from datetime import datetime, timezone
    prescription.status = "cancelled"
    prescription.cancelled_by = current_user.id
    prescription.cancelled_at = datetime.now(timezone.utc)
    prescription.cancellation_reason = cancellation_reason
    db.commit()
    db.refresh(prescription)
    return PrescriptionOut.model_validate(prescription)


# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Triage management
# -----------------------------------------------------------------------------


@router.post("/api/triage", response_model=TriageOut, tags=["triage"])
async def create_triage_entry(
    payload: TriageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TriageOut:
    """Create a triage entry with auto-scoring."""
    if current_user.role not in ("doctor", "ipa", "sec"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor, IPA or sec role required")

    data = payload.model_dump()
    result = score_urgency(data)

    entry = TriageEntry(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        priority=result.priority,
        score=result.score,
        **data,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Real-time alert for P1/P2
    if result.priority in ("P1", "P2"):
        import asyncio
        asyncio.create_task(
            triage_ws_manager.broadcast(
                current_user.tenant_id,
                {
                    "type": "triage_alert",
                    "priority": result.priority,
                    "score": result.score,
                    "chief_complaint": data.get("chief_complaint"),
                    "id": str(entry.id),
                },
            )
        )

    return TriageOut.model_validate(entry)


@router.get("/api/triage", response_model=list[TriageOut], tags=["triage"])
async def list_triage_entries(
    status: str | None = None,
    priority: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TriageOut]:
    query = db.query(TriageEntry).filter(TriageEntry.tenant_id == current_user.tenant_id)
    if status:
        query = query.filter(TriageEntry.status == status)
    if priority:
        query = query.filter(TriageEntry.priority == priority)
    return [TriageOut.model_validate(t) for t in query.order_by(TriageEntry.score.desc()).all()]


@router.get("/api/triage/stats/counts", response_model=TriageStatsOut, tags=["triage"])
async def triage_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TriageStatsOut:
    """Return P1-P5 counts for the current tenant."""
    rows = db.query(TriageEntry).filter(TriageEntry.tenant_id == current_user.tenant_id).all()
    counts = {"P1": 0, "P2": 0, "P3": 0, "P4": 0, "P5": 0}
    for r in rows:
        counts[r.priority] = counts.get(r.priority, 0) + 1
    return TriageStatsOut(tenant_id=current_user.tenant_id, counts=counts)


@router.get("/api/triage/{triage_id}", response_model=TriageOut, tags=["triage"])
async def get_triage_entry(
    triage_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TriageOut:
    entry = db.query(TriageEntry).filter(
        TriageEntry.id == triage_id, TriageEntry.tenant_id == current_user.tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Triage entry not found")
    return TriageOut.model_validate(entry)


@router.patch("/api/triage/{triage_id}", response_model=TriageOut, tags=["triage"])
async def update_triage_entry(
    triage_id: str,
    payload: TriageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TriageOut:
    entry = db.query(TriageEntry).filter(
        TriageEntry.id == triage_id, TriageEntry.tenant_id == current_user.tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Triage entry not found")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)
    if any(k in update_data for k in [
        "heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic",
        "temperature", "oxygen_saturation", "respiratory_rate",
        "glucose", "pain_scale", "consciousness_level", "chief_complaint",
    ]):
        recalc = score_urgency({k: getattr(entry, k) for k in [
            "heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic",
            "temperature", "oxygen_saturation", "respiratory_rate",
            "glucose", "pain_scale", "consciousness_level", "chief_complaint",
        ]})
        entry.priority = recalc.priority
        entry.score = recalc.score
    db.commit()
    db.refresh(entry)
    return TriageOut.model_validate(entry)


# -----------------------------------------------------------------------------
# Agenda — appointments & field visits
# -----------------------------------------------------------------------------


@router.post("/api/appointments", response_model=AppointmentOut, tags=["agenda"])
async def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentOut:
    """Create an appointment. Allowed: doctor, ipa, sec."""
    if current_user.role not in ("doctor", "ipa", "sec"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor, IPA or sec role required")
    entry = Appointment(tenant_id=current_user.tenant_id, created_by=current_user.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return AppointmentOut.model_validate(entry)


@router.get("/api/appointments", response_model=list[AppointmentOut], tags=["agenda"])
async def list_appointments(
    date_from: str | None = None,
    date_to: str | None = None,
    status: str | None = None,
    assigned_staff_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AppointmentOut]:
    query = db.query(Appointment).filter(Appointment.tenant_id == current_user.tenant_id)
    if date_from:
        query = query.filter(Appointment.scheduled_at >= date_from)
    if date_to:
        query = query.filter(Appointment.scheduled_at <= date_to)
    if status:
        query = query.filter(Appointment.status == status)
    if assigned_staff_id:
        query = query.filter(Appointment.assigned_staff_id == assigned_staff_id)
    return [AppointmentOut.model_validate(a) for a in query.order_by(Appointment.scheduled_at.asc()).all()]


@router.patch("/api/appointments/{appointment_id}", response_model=AppointmentOut, tags=["agenda"])
async def update_appointment(
    appointment_id: str,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentOut:
    entry = db.query(Appointment).filter(
        Appointment.id == appointment_id, Appointment.tenant_id == current_user.tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    if current_user.role not in ("doctor", "ipa", "sec"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor, IPA or sec role required")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return AppointmentOut.model_validate(entry)


@router.post("/api/field-visits", response_model=FieldVisitOut, tags=["agenda"])
async def create_field_visit(
    payload: FieldVisitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FieldVisitOut:
    """Create a field visit. Allowed: doctor, ipa, sec."""
    if current_user.role not in ("doctor", "ipa", "sec"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor, IPA or sec role required")
    entry = FieldVisit(tenant_id=current_user.tenant_id, created_by=current_user.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return FieldVisitOut.model_validate(entry)


@router.get("/api/field-visits", response_model=list[FieldVisitOut], tags=["agenda"])
async def list_field_visits(
    date_from: str | None = None,
    date_to: str | None = None,
    status: str | None = None,
    assigned_staff_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FieldVisitOut]:
    query = db.query(FieldVisit).filter(FieldVisit.tenant_id == current_user.tenant_id)
    if date_from:
        query = query.filter(FieldVisit.scheduled_start_at >= date_from)
    if date_to:
        query = query.filter(FieldVisit.scheduled_start_at <= date_to)
    if status:
        query = query.filter(FieldVisit.status == status)
    if assigned_staff_id:
        query = query.filter(FieldVisit.assigned_staff_id == assigned_staff_id)
    return [FieldVisitOut.model_validate(v) for v in query.order_by(FieldVisit.scheduled_start_at.asc()).all()]


@router.patch("/api/field-visits/{visit_id}", response_model=FieldVisitOut, tags=["agenda"])
async def update_field_visit(
    visit_id: str,
    payload: FieldVisitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FieldVisitOut:
    entry = db.query(FieldVisit).filter(
        FieldVisit.id == visit_id, FieldVisit.tenant_id == current_user.tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field visit not found")
    if current_user.role not in ("doctor", "ipa", "sec"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor, IPA or sec role required")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return FieldVisitOut.model_validate(entry)


# -----------------------------------------------------------------------------
# Billing
# -----------------------------------------------------------------------------


@router.post("/api/billings", response_model=BillingOut, tags=["billing"])
async def create_billing(
    payload: BillingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillingOut:
    if current_user.role not in ("doctor", "ipa", "sec"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor, IPA or sec role required")
    episode = db.query(Episode).filter(
        Episode.id == payload.episode_id, Episode.tenant_id == current_user.tenant_id
    ).first()
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    entry = Billing(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        **payload.model_dump(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return BillingOut.model_validate(entry)


@router.get("/api/billings", response_model=list[BillingOut], tags=["billing"])
async def list_billings(
    episode_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BillingOut]:
    query = db.query(Billing).filter(Billing.tenant_id == current_user.tenant_id)
    if episode_id:
        query = query.filter(Billing.episode_id == episode_id)
    return [BillingOut.model_validate(b) for b in query.all()]


@router.get("/api/billings/{billing_id}", response_model=BillingOut, tags=["billing"])
async def get_billing(
    billing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillingOut:
    entry = db.query(Billing).filter(
        Billing.id == billing_id, Billing.tenant_id == current_user.tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Billing not found")
    return BillingOut.model_validate(entry)


@router.patch("/api/billings/{billing_id}", response_model=BillingOut, tags=["billing"])
async def update_billing(
    billing_id: str,
    payload: BillingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillingOut:
    entry = db.query(Billing).filter(
        Billing.id == billing_id, Billing.tenant_id == current_user.tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Billing not found")
    if current_user.role not in ("doctor", "ipa", "sec"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor, IPA or sec role required")
    if entry.status == "exported":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Exported billing cannot be modified")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return BillingOut.model_validate(entry)


@router.post("/api/billings/{billing_id}/validate", response_model=BillingOut, tags=["billing"])
async def validate_billing(
    billing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillingOut:
    if current_user.role != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Billing validation is doctor-only")
    entry = db.query(Billing).filter(
        Billing.id == billing_id, Billing.tenant_id == current_user.tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Billing not found")
    if entry.status == "validated":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Billing already validated")
    from datetime import datetime, timezone
    entry.status = "validated"
    entry.validated_by = current_user.id
    entry.validated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(entry)
    return BillingOut.model_validate(entry)


@router.post("/api/billings/{billing_id}/export", response_model=BillingOut, tags=["billing"])
async def export_billing(
    billing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillingOut:
    if current_user.role not in ("doctor", "sec"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor or sec role required")
    entry = db.query(Billing).filter(
        Billing.id == billing_id, Billing.tenant_id == current_user.tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Billing not found")
    if entry.status != "validated":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Billing must be validated before export")
    from datetime import datetime, timezone
    entry.status = "exported"
    entry.exported_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(entry)
    return BillingOut.model_validate(entry)


# -----------------------------------------------------------------------------
# AI System Prompts (admin & doctor only)
# -----------------------------------------------------------------------------


@router.post("/api/ai-prompts", response_model=AISystemPromptOut, tags=["ai-prompts"])
async def create_ai_prompt(
    payload: AISystemPromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AISystemPromptOut:
    if current_user.role not in ("admin", "doctor"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or doctor role required")
    entry = AISystemPrompt(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        **payload.model_dump(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return AISystemPromptOut.model_validate(entry)


@router.get("/api/ai-prompts", response_model=list[AISystemPromptOut], tags=["ai-prompts"])
async def list_ai_prompts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AISystemPromptOut]:
    if current_user.role not in ("admin", "doctor"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or doctor role required")
    items = db.query(AISystemPrompt).filter(AISystemPrompt.tenant_id == current_user.tenant_id).all()
    return [AISystemPromptOut.model_validate(i) for i in items]


@router.patch("/api/ai-prompts/{prompt_id}", response_model=AISystemPromptOut, tags=["ai-prompts"])
async def update_ai_prompt(
    prompt_id: str,
    payload: AISystemPromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AISystemPromptOut:
    if current_user.role not in ("admin", "doctor"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or doctor role required")
    entry = db.query(AISystemPrompt).filter(
        AISystemPrompt.id == prompt_id, AISystemPrompt.tenant_id == current_user.tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI prompt not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return AISystemPromptOut.model_validate(entry)


@router.delete("/api/ai-prompts/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["ai-prompts"])
async def delete_ai_prompt(
    prompt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    if current_user.role not in ("admin", "doctor"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or doctor role required")
    entry = db.query(AISystemPrompt).filter(
        AISystemPrompt.id == prompt_id, AISystemPrompt.tenant_id == current_user.tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI prompt not found")
    db.delete(entry)
    db.commit()


# -----------------------------------------------------------------------------
# Messaging (internal)
# -----------------------------------------------------------------------------

@router.post("/api/messages", response_model=MessageOut, tags=["messaging"])
async def create_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageOut:
    entry = Message(
        tenant_id=current_user.tenant_id,
        sender_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return MessageOut.model_validate(entry)


@router.get("/api/messages/inbox", response_model=list[MessageOut], tags=["messaging"])
async def list_inbox(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MessageOut]:
    items = db.query(Message).filter(
        Message.tenant_id == current_user.tenant_id,
        Message.recipient_id == current_user.id,
    ).order_by(Message.created_at.desc()).all()
    return [MessageOut.model_validate(i) for i in items]


@router.get("/api/messages/sent", response_model=list[MessageOut], tags=["messaging"])
async def list_sent(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MessageOut]:
    items = db.query(Message).filter(
        Message.tenant_id == current_user.tenant_id,
        Message.sender_id == current_user.id,
    ).order_by(Message.created_at.desc()).all()
    return [MessageOut.model_validate(i) for i in items]


@router.patch("/api/messages/{message_id}/read", response_model=MessageOut, tags=["messaging"])
async def mark_message_read(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageOut:
    entry = db.query(Message).filter(
        Message.id == message_id, Message.tenant_id == current_user.tenant_id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    entry.is_read = True
    db.commit()
    db.refresh(entry)
    return MessageOut.model_validate(entry)


# -----------------------------------------------------------------------------
# External messaging stubs (MSSanté CI-SIS) — 501 Not Implemented in VI
# -----------------------------------------------------------------------------

@router.post("/api/messages/external/mssante/send", status_code=status.HTTP_501_NOT_IMPLEMENTED, tags=["messaging"])
async def stub_mssante_send(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return {"detail": "[VI - Non implémenté] Messagerie externe MSSanté CI-SIS réservée pour la VC"}


# -----------------------------------------------------------------------------
# PDF Export
# -----------------------------------------------------------------------------

@router.get("/api/exports/episodes/{episode_id}/pdf", tags=["exports"])
async def export_episode_pdf(
    episode_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("doctor", "ipa"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor or IPA role required")
    episode = db.query(Episode).filter(Episode.id == episode_id, Episode.tenant_id == current_user.tenant_id).first()  # noqa: S608
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    patient = db.query(Patient).filter(Patient.id == episode.patient_id).first()  # noqa: S608
    prescriptions = db.query(Prescription).filter(Prescription.episode_id == episode_id, Prescription.tenant_id == current_user.tenant_id).all()  # noqa: S608
    from app.services.pdf_service import generate_episode_pdf
    import io
    data = {
        "tenant_name": "MedFlow",
        "patient": {"id": patient.id if patient else "", "name": f"{patient.first_name} {patient.last_name}" if patient else ""},
        "episode": {"id": episode.id, "chief_complaint": episode.chief_complaint, "status": episode.status},
        "prescriptions": [{"medications": p.medications, "status": p.status, "signed_by": p.signed_by} for p in prescriptions],
    }
    pdf_bytes, _ = generate_episode_pdf(data)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=episode_{episode_id}.pdf"},
    )


# -----------------------------------------------------------------------------
# Interoperability stubs (Option C) — return 501 Not Implemented in VI
# -----------------------------------------------------------------------------

STUB_ROUTES = [
    "/api/interop/carte-vitale/read",
    "/api/interop/mssante/send",
    "/api/interop/dmp/push",
    "/api/interop/fhir/patient/{patient_id}",
    "/api/interop/dicom/upload",
]


@router.post("/api/interop/carte-vitale/read", status_code=status.HTTP_501_NOT_IMPLEMENTED, tags=["interop"])
async def stub_carte_vitale() -> dict:
    return {"detail": "[VC - Non implemente] Carte Vitale reading not available in VI"}


@router.post("/api/interop/mssante/send", status_code=status.HTTP_501_NOT_IMPLEMENTED, tags=["interop"])
async def stub_mssante() -> dict:
    return {"detail": "[VC - Non implemente] MSSante sending not available in VI"}


@router.post("/api/interop/dmp/push", status_code=status.HTTP_501_NOT_IMPLEMENTED, tags=["interop"])
async def stub_dmp() -> dict:
    return {"detail": "[VC - Non implemente] DMP push not available in VI"}


@router.get("/api/interop/fhir/patient/{patient_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED, tags=["interop"])
async def stub_fhir(patient_id: str) -> dict:
    return {"detail": "[VC - Non implemente] FHIR R4 export not available in VI"}


@router.post("/api/interop/dicom/upload", status_code=status.HTTP_501_NOT_IMPLEMENTED, tags=["interop"])
async def stub_dicom() -> dict:
    return {"detail": "[VC - Non implemente] DICOM upload not available in VI"}

