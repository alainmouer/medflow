"""Tests for messaging and PDF export."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from app.models.models import Tenant, User, Patient, Episode, Prescription


def _get_token(client: TestClient, email: str) -> str:
    return client.post("/api/auth/login", data={"username": email, "password": "pass"}).json()["access_token"]


def test_messaging_lifecycle(client: TestClient, db_session):
    tenant = Tenant(name="Test", slug="test-msg", specialty="Test")
    db_session.add(tenant)
    db_session.commit()
    hp = get_password_hash("pass")
    doc = User(tenant_id=tenant.id, email="docmsg@test.com", hashed_password=hp, full_name="Doc", role="doctor")
    ipa = User(tenant_id=tenant.id, email="ipamsg@test.com", hashed_password=hp, full_name="IPA", role="ipa")
    db_session.add_all([doc, ipa])
    db_session.commit()
    db_session.refresh(doc)
    db_session.refresh(ipa)

    doc_token = _get_token(client, doc.email)

    # Doc sends to IPA
    r = client.post("/api/messages", json={
        "recipient_id": ipa.id,
        "subject": "Test",
        "body": "Hello IPA",
    }, headers={"Authorization": f"Bearer {doc_token}"})
    assert r.status_code == 200
    msg_id = r.json()["id"]

    # IPA checks inbox
    ipa_token = _get_token(client, ipa.email)
    inbox = client.get("/api/messages/inbox", headers={"Authorization": f"Bearer {ipa_token}"})
    assert inbox.status_code == 200
    assert len(inbox.json()) == 1
    assert inbox.json()[0]["is_read"] is False

    # IPA marks as read
    read = client.patch(f"/api/messages/{msg_id}/read", headers={"Authorization": f"Bearer {ipa_token}"})
    assert read.status_code == 200
    assert read.json()["is_read"] is True

    # Doc checks sent
    sent = client.get("/api/messages/sent", headers={"Authorization": f"Bearer {doc_token}"})
    assert sent.status_code == 200
    assert len(sent.json()) == 1


def test_pdf_export_endpoint(client: TestClient, db_session):
    tenant = Tenant(name="Test", slug="test-pdf", specialty="Test")
    db_session.add(tenant)
    db_session.commit()
    hp = get_password_hash("pass")
    doc = User(tenant_id=tenant.id, email="docpdf@test.com", hashed_password=hp, full_name="Doc", role="doctor")
    db_session.add(doc)
    patient = Patient(tenant_id=tenant.id, last_name="Martin", first_name="Luc")
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    episode = Episode(tenant_id=tenant.id, patient_id=patient.id, status="collected", chief_complaint="Pain")
    db_session.add(episode)
    db_session.commit()
    db_session.refresh(episode)
    pres = Prescription(tenant_id=tenant.id, episode_id=episode.id, medications="Aspirin", status="draft")
    db_session.add(pres)
    db_session.commit()

    token = _get_token(client, doc.email)
    r = client.get(f"/api/exports/episodes/{episode.id}/pdf", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert "attachment" in r.headers["content-disposition"]


def test_mssante_stub_returns_501(client: TestClient, db_session):
    tenant = Tenant(name="Test", slug="test-stub", specialty="Test")
    db_session.add(tenant)
    db_session.commit()
    hp = get_password_hash("pass")
    doc = User(tenant_id=tenant.id, email="docstub@test.com", hashed_password=hp, full_name="Doc", role="doctor")
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    token = _get_token(client, doc.email)
    r = client.post("/api/messages/external/mssante/send", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 501
    assert "Non implémenté" in r.json()["detail"]
