"""Unit tests for triage REST endpoints."""
from __future__ import annotations

import pytest

from app.main import create_app
from app.db.database import Base, engine, get_db
from app.models.models import Tenant, User, Patient, Episode, TriageEntry
from app.core.security import get_password_hash


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = next(get_db())
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def tenant(db_session):
    t = Tenant(name="Test Tenant", slug="test-tenant")
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


@pytest.fixture(scope="function")
def admin_user(db_session, tenant):
    u = User(
        tenant_id=tenant.id,
        email="admin@test.com",
        hashed_password=get_password_hash("TestPassphrase123!"),
        full_name="Admin User",
        role="admin",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture(scope="function")
def doctor_user(db_session, tenant):
    u = User(
        tenant_id=tenant.id,
        email="doctor@test.com",
        hashed_password=get_password_hash("TestPassphrase123!"),
        full_name="Doctor User",
        role="doctor",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture(scope="function")
def sec_user(db_session, tenant):
    u = User(
        tenant_id=tenant.id,
        email="sec@test.com",
        hashed_password=get_password_hash("TestPassphrase123!"),
        full_name="Sec User",
        role="sec",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture(scope="function")
def auth_headers(client, admin_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@test.com", "password": "TestPassphrase123!"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def doctor_auth_headers(client, doctor_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "doctor@test.com", "password": "TestPassphrase123!"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def sec_auth_headers(client, sec_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "sec@test.com", "password": "TestPassphrase123!"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCreateTriage:
    def test_create_triage_doctor(self, client, doctor_auth_headers, db_session, tenant):
        response = client.post(
            "/api/triage",
            headers=doctor_auth_headers,
            json={
                "chief_complaint": "Douleur thoracique",
                "heart_rate": 110,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "P3"
        assert data["score"] >= 20
        assert data["tenant_id"] == tenant.id
        assert data["status"] == "waiting"

    def test_create_triage_sec(self, client, sec_auth_headers, db_session, tenant):
        response = client.post(
            "/api/triage",
            headers=sec_auth_headers,
            json={
                "chief_complaint": "Fièvre",
                "temperature": 38.5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] in ("P2", "P3")

    def test_create_triage_admin_forbidden(self, client, auth_headers):
        response = client.post(
            "/api/triage",
            headers=auth_headers,
            json={"chief_complaint": "Test"},
        )
        assert response.status_code == 403

    def test_create_triage_unauthenticated(self, client):
        response = client.post(
            "/api/triage",
            json={"chief_complaint": "Test"},
        )
        assert response.status_code == 401

    def test_create_triage_p1(self, client, doctor_auth_headers, db_session, tenant):
        response = client.post(
            "/api/triage",
            headers=doctor_auth_headers,
            json={
                "chief_complaint": "Arrêt cardiaque",
                "heart_rate": 200,
                "oxygen_saturation": 80,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "P1"
        assert data["score"] >= 70

    def test_create_triage_minimal(self, client, doctor_auth_headers):
        response = client.post(
            "/api/triage",
            headers=doctor_auth_headers,
            json={},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "P5"
        assert data["score"] == 0


class TestListTriage:
    def test_list_triage(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        t1 = TriageEntry(
            tenant_id=tenant.id,
            created_by=doctor_user.id,
            priority="P1",
            score=80,
            status="waiting",
        )
        t2 = TriageEntry(
            tenant_id=tenant.id,
            created_by=doctor_user.id,
            priority="P3",
            score=30,
            status="in_progress",
        )
        db_session.add_all([t1, t2])
        db_session.commit()

        response = client.get("/api/triage", headers=doctor_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # should be ordered by score desc
        assert data[0]["priority"] == "P1"
        assert data[1]["priority"] == "P3"

    def test_list_triage_filter_status(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        t1 = TriageEntry(
            tenant_id=tenant.id, created_by=doctor_user.id,
            priority="P1", score=80, status="waiting",
        )
        t2 = TriageEntry(
            tenant_id=tenant.id, created_by=doctor_user.id,
            priority="P3", score=30, status="in_progress",
        )
        db_session.add_all([t1, t2])
        db_session.commit()

        response = client.get("/api/triage?status=waiting", headers=doctor_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "waiting"

    def test_list_triage_filter_priority(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        t1 = TriageEntry(
            tenant_id=tenant.id, created_by=doctor_user.id,
            priority="P1", score=80, status="waiting",
        )
        t2 = TriageEntry(
            tenant_id=tenant.id, created_by=doctor_user.id,
            priority="P3", score=30, status="in_progress",
        )
        db_session.add_all([t1, t2])
        db_session.commit()

        response = client.get("/api/triage?priority=P1", headers=doctor_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "P1"


class TestTriageCounts:
    def test_counts(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        for _ in range(3):
            db_session.add(TriageEntry(
                tenant_id=tenant.id, created_by=doctor_user.id,
                priority="P1", score=80, status="waiting",
            ))
        for _ in range(2):
            db_session.add(TriageEntry(
                tenant_id=tenant.id, created_by=doctor_user.id,
                priority="P2", score=50, status="waiting",
            ))
        db_session.commit()

        response = client.get("/api/triage/stats/counts", headers=doctor_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["counts"]["P1"] == 3
        assert data["counts"]["P2"] == 2
        assert data["counts"]["P5"] == 0


class TestUpdateTriage:
    def test_patch_status(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        t = TriageEntry(
            tenant_id=tenant.id, created_by=doctor_user.id,
            priority="P3", score=40, status="waiting",
        )
        db_session.add(t)
        db_session.commit()
        db_session.refresh(t)

        response = client.patch(
            f"/api/triage/{t.id}",
            headers=doctor_auth_headers,
            json={"status": "in_progress", "assigned_to": doctor_user.id},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["assigned_to"] == doctor_user.id
        assert data["priority"] == "P3"  # unchanged

    def test_patch_recalc_score(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        t = TriageEntry(
            tenant_id=tenant.id, created_by=doctor_user.id,
            priority="P5", score=0, status="waiting",
            heart_rate=72,
        )
        db_session.add(t)
        db_session.commit()
        db_session.refresh(t)

        response = client.patch(
            f"/api/triage/{t.id}",
            headers=doctor_auth_headers,
            json={
                "heart_rate": 200,
                "oxygen_saturation": 80,
                "consciousness_level": "unresponsive",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "P1"
        assert data["score"] >= 50

    def test_patch_not_found(self, client, doctor_auth_headers):
        response = client.patch(
            "/api/triage/nonexistent-id",
            headers=doctor_auth_headers,
            json={"status": "done"},
        )
        assert response.status_code == 404


class TestGetTriage:
    def test_get_triage(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        t = TriageEntry(
            tenant_id=tenant.id, created_by=doctor_user.id,
            priority="P2", score=60, status="waiting",
        )
        db_session.add(t)
        db_session.commit()
        db_session.refresh(t)

        response = client.get(f"/api/triage/{t.id}", headers=doctor_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == t.id
        assert data["priority"] == "P2"

    def test_get_triage_not_found(self, client, doctor_auth_headers):
        response = client.get("/api/triage/nonexistent-id", headers=doctor_auth_headers)
        assert response.status_code == 404
