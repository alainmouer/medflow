"""Tests for prescription workflow (sign / send / cancel) and billing CRUD."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.models import Tenant, User, Patient, Episode, Prescription, Billing


@pytest.fixture
def sample_data(db_session: Session) -> tuple[Tenant, User, User, Patient, Episode]:
    tenant = Tenant(name="Test", slug="test", specialty="Test")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    hp = get_password_hash("medflow2026")
    doctor = User(tenant_id=tenant.id, email="doc@test.com", hashed_password=hp, full_name="Doc", role="doctor")
    ipa = User(tenant_id=tenant.id, email="ipa@test.com", hashed_password=hp, full_name="IPA", role="ipa")
    db_session.add_all([doctor, ipa])
    patient = Patient(tenant_id=tenant.id, last_name="Martin", first_name="Luc")
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    episode = Episode(tenant_id=tenant.id, patient_id=patient.id, status="collected", chief_complaint="Test")
    db_session.add(episode)
    db_session.commit()
    db_session.refresh(episode)
    db_session.refresh(doctor)
    db_session.refresh(ipa)
    return tenant, doctor, ipa, patient, episode


def _get_token(client: TestClient, email: str) -> str:
    return client.post("/api/auth/login", data={"username": email, "password": "medflow2026"}).json()["access_token"]


# ---------------------------------------------------------------------------
# Prescription workflow
# ---------------------------------------------------------------------------

def test_prescription_sign_creates_hash(client: TestClient, sample_data: tuple):
    tenant, doctor, _, _, episode = sample_data
    token = _get_token(client, doctor.email)
    r = client.post("/api/prescriptions", json={"episode_id": episode.id, "medications": "Aspirin"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    pres_id = r.json()["id"]
    sign = client.post(f"/api/prescriptions/{pres_id}/sign", headers={"Authorization": f"Bearer {token}"})
    assert sign.status_code == 200
    data = sign.json()
    assert data["status"] == "signed"
    assert data["signature_hash"] is not None
    assert len(data["signature_hash"]) == 64


def test_prescription_send_requires_signed(client: TestClient, sample_data: tuple):
    tenant, doctor, _, _, episode = sample_data
    token = _get_token(client, doctor.email)
    r = client.post("/api/prescriptions", json={"episode_id": episode.id, "medications": "Paracetamol"}, headers={"Authorization": f"Bearer {token}"})
    pres_id = r.json()["id"]
    # send before sign -> 409
    send = client.post(f"/api/prescriptions/{pres_id}/send", headers={"Authorization": f"Bearer {token}"})
    assert send.status_code == 409
    # sign first
    client.post(f"/api/prescriptions/{pres_id}/sign", headers={"Authorization": f"Bearer {token}"})
    send2 = client.post(f"/api/prescriptions/{pres_id}/send", json={"sent_to_email": "patient@test.com"}, headers={"Authorization": f"Bearer {token}"})
    assert send2.status_code == 200
    assert send2.json()["status"] == "sent"
    assert send2.json()["sent_to_email"] == "patient@test.com"


def test_prescription_cancel(client: TestClient, sample_data: tuple):
    tenant, doctor, _, _, episode = sample_data
    token = _get_token(client, doctor.email)
    r = client.post("/api/prescriptions", json={"episode_id": episode.id, "medications": "Doliprane"}, headers={"Authorization": f"Bearer {token}"})
    pres_id = r.json()["id"]
    cancel = client.post(f"/api/prescriptions/{pres_id}/cancel?cancellation_reason=erreur", headers={"Authorization": f"Bearer {token}"})
    assert cancel.status_code == 200
    data = cancel.json()
    assert data["status"] == "cancelled"
    assert data["cancellation_reason"] == "erreur"
    assert data["cancelled_by"] is not None


# ---------------------------------------------------------------------------
# Billing
# ---------------------------------------------------------------------------

def test_billing_crud(client: TestClient, sample_data: tuple):
    _, doctor, _, _, episode = sample_data
    token = _get_token(client, doctor.email)
    # create
    r = client.post("/api/billings", json={"episode_id": episode.id, "acts_total": 55.0}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    b_id = r.json()["id"]
    # list
    lst = client.get("/api/billings", headers={"Authorization": f"Bearer {token}"})
    assert lst.status_code == 200
    assert len(lst.json()) == 1
    # get
    g = client.get(f"/api/billings/{b_id}", headers={"Authorization": f"Bearer {token}"})
    assert g.status_code == 200
    assert g.json()["acts_total"] == 55.0
    # update
    up = client.patch(f"/api/billings/{b_id}", json={"acts_total": 60.0}, headers={"Authorization": f"Bearer {token}"})
    assert up.status_code == 200
    assert up.json()["acts_total"] == 60.0


def test_billing_validate_and_export(client: TestClient, sample_data: tuple):
    _, doctor, _, _, episode = sample_data
    token = _get_token(client, doctor.email)
    r = client.post("/api/billings", json={"episode_id": episode.id, "acts_total": 100.0}, headers={"Authorization": f"Bearer {token}"})
    b_id = r.json()["id"]
    # export before validate -> 409
    exp = client.post(f"/api/billings/{b_id}/export", headers={"Authorization": f"Bearer {token}"})
    assert exp.status_code == 409
    # validate
    val = client.post(f"/api/billings/{b_id}/validate", headers={"Authorization": f"Bearer {token}"})
    assert val.status_code == 200
    assert val.json()["status"] == "validated"
    assert val.json()["validated_by"] is not None
    # export
    exp2 = client.post(f"/api/billings/{b_id}/export", headers={"Authorization": f"Bearer {token}"})
    assert exp2.status_code == 200
    assert exp2.json()["status"] == "exported"
    assert exp2.json()["exported_at"] is not None
    # update after export -> 409
    up = client.patch(f"/api/billings/{b_id}", json={"acts_total": 120.0}, headers={"Authorization": f"Bearer {token}"})
    assert up.status_code == 409


def test_billing_validate_denied_for_ipa(client: TestClient, sample_data: tuple):
    _, _, ipa, _, episode = sample_data
    token = _get_token(client, ipa.email)
    r = client.post("/api/billings", json={"episode_id": episode.id}, headers={"Authorization": f"Bearer {token}"})
    b_id = r.json()["id"]
    val = client.post(f"/api/billings/{b_id}/validate", headers={"Authorization": f"Bearer {token}"})
    assert val.status_code == 403
