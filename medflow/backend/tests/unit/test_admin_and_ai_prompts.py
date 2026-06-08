"""Tests for admin users CRUD and AI prompts."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from app.models.models import Tenant, User, AISystemPrompt


def _get_token(client: TestClient, email: str) -> str:
    return client.post("/api/auth/login", data={"username": email, "password": "medflow2026"}).json()["access_token"]


def test_admin_list_users(client: TestClient, db_session):
    tenant = Tenant(name="Test", slug="test-admin", specialty="Test")
    db_session.add(tenant)
    db_session.commit()
    hp = get_password_hash("medflow2026")
    admin = User(tenant_id=tenant.id, email="admin@test.com", hashed_password=hp, full_name="Admin", role="admin")
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    token = _get_token(client, admin.email)
    r = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_admin_create_user(client: TestClient, db_session):
    tenant = Tenant(name="Test", slug="test-create", specialty="Test")
    db_session.add(tenant)
    db_session.commit()
    hp = get_password_hash("medflow2026")
    admin = User(tenant_id=tenant.id, email="admin2@test.com", hashed_password=hp, full_name="Admin", role="admin")
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    token = _get_token(client, admin.email)
    r = client.post("/api/admin/users", json={
        "email": "newuser@test.com",
        "password": "password12345",
        "full_name": "New User",
        "role": "doctor",
        "specialty": "Cardio",
    }, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    assert r.json()["email"] == "newuser@test.com"
    assert r.json()["tenant_id"] is not None


def test_ai_prompts_crud(client: TestClient, db_session):
    tenant = Tenant(name="Test", slug="test-ai", specialty="Test")
    db_session.add(tenant)
    db_session.commit()
    hp = get_password_hash("medflow2026")
    doctor = User(tenant_id=tenant.id, email="docai@test.com", hashed_password=hp, full_name="Doc", role="doctor")
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    token = _get_token(client, doctor.email)
    # create
    r = client.post("/api/ai-prompts", json={"name": "cardio-v1", "version": "1.0.0", "prompt_text": "Analyze cardiac..."}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    pid = r.json()["id"]
    # list
    lst = client.get("/api/ai-prompts", headers={"Authorization": f"Bearer {token}"})
    assert lst.status_code == 200
    assert len(lst.json()) == 1
    # update
    up = client.patch(f"/api/ai-prompts/{pid}", json={"version": "1.1.0"}, headers={"Authorization": f"Bearer {token}"})
    assert up.status_code == 200
    assert up.json()["version"] == "1.1.0"
    # delete
    dl = client.delete(f"/api/ai-prompts/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert dl.status_code == 204


def test_ai_prompt_rbac_denied_for_ipa(client: TestClient, db_session):
    tenant = Tenant(name="Test", slug="test-ai-rbac", specialty="Test")
    db_session.add(tenant)
    db_session.commit()
    hp = get_password_hash("medflow2026")
    ipa = User(tenant_id=tenant.id, email="ipaai@test.com", hashed_password=hp, full_name="IPA", role="ipa")
    db_session.add(ipa)
    db_session.commit()
    db_session.refresh(ipa)
    token = _get_token(client, ipa.email)
    r = client.get("/api/ai-prompts", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
