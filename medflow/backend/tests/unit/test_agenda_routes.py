"""Unit tests for agenda REST endpoints."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from app.main import create_app
from app.db.database import Base, engine, get_db
from app.models.models import Tenant, User, Appointment, FieldVisit
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
def doctor_auth_headers(client, doctor_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "doctor@test.com", "password": "TestPassphrase123!"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Appointments
# ---------------------------------------------------------------------------

class TestCreateAppointment:
    def test_create_appointment(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        response = client.post(
            "/api/appointments",
            headers=doctor_auth_headers,
            json={
                "appointment_type": "consultation",
                "modality": "synchronous_presential",
                "scheduled_at": "2026-06-15T10:00:00",
                "duration_min": 30,
                "location": "Cabinet A",
                "notes": "Première consultation",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["appointment_type"] == "consultation"
        assert data["modality"] == "synchronous_presential"
        assert data["status"] == "scheduled"
        assert data["tenant_id"] == tenant.id

    def test_create_appointment_unauthenticated(self, client):
        response = client.post(
            "/api/appointments",
            json={"appointment_type": "consultation"},
        )
        assert response.status_code == 401

    def test_create_appointment_admin_forbidden(self, client, db_session, tenant):
        # Create admin user and login
        admin = User(
            tenant_id=tenant.id,
            email="admin@test.com",
            hashed_password=get_password_hash("TestPassphrase123!"),
            full_name="Admin User",
            role="admin",
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        resp = client.post(
            "/api/auth/login",
            data={"username": "admin@test.com", "password": "TestPassphrase123!"},
        )
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/appointments",
            headers=headers,
            json={"appointment_type": "consultation"},
        )
        assert response.status_code == 403


class TestListAppointments:
    def test_list_empty(self, client, doctor_auth_headers):
        response = client.get("/api/appointments", headers=doctor_auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_with_entries(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        a1 = Appointment(
            tenant_id=tenant.id,
            created_by=doctor_user.id,
            appointment_type="consultation",
            modality="synchronous_presential",
            status="scheduled",
            scheduled_at=datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc),
        )
        a2 = Appointment(
            tenant_id=tenant.id,
            created_by=doctor_user.id,
            appointment_type="exam",
            modality="synchronous_presential",
            status="confirmed",
            scheduled_at=datetime(2026, 6, 16, 14, 0, tzinfo=timezone.utc),
        )
        db_session.add_all([a1, a2])
        db_session.commit()

        response = client.get("/api/appointments", headers=doctor_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["appointment_type"] == "consultation"  # ordered by date asc

    def test_list_filter_status(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        a1 = Appointment(
            tenant_id=tenant.id, created_by=doctor_user.id,
            appointment_type="consultation", modality="synchronous_presential",
            status="scheduled", scheduled_at=datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc),
        )
        a2 = Appointment(
            tenant_id=tenant.id, created_by=doctor_user.id,
            appointment_type="exam", modality="synchronous_presential",
            status="confirmed", scheduled_at=datetime(2026, 6, 16, 14, 0, tzinfo=timezone.utc),
        )
        db_session.add_all([a1, a2])
        db_session.commit()

        response = client.get("/api/appointments?status=confirmed", headers=doctor_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "confirmed"


class TestUpdateAppointment:
    def test_patch_status(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        a = Appointment(
            tenant_id=tenant.id, created_by=doctor_user.id,
            appointment_type="consultation", modality="synchronous_presential",
            status="scheduled", scheduled_at=datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc),
        )
        db_session.add(a)
        db_session.commit()
        db_session.refresh(a)

        response = client.patch(
            f"/api/appointments/{a.id}",
            headers=doctor_auth_headers,
            json={"status": "confirmed"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"

    def test_patch_not_found(self, client, doctor_auth_headers):
        response = client.patch(
            "/api/appointments/nonexistent-id",
            headers=doctor_auth_headers,
            json={"status": "confirmed"},
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Field Visits
# ---------------------------------------------------------------------------

class TestCreateFieldVisit:
    def test_create_field_visit(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        response = client.post(
            "/api/field-visits",
            headers=doctor_auth_headers,
            json={
                "collection_mode": "internal_visit",
                "location_type": "home",
                "location_address": "123 Rue de la Sante",
                "scheduled_start_at": "2026-06-15T10:00:00",
                "scheduled_end_at": "2026-06-15T11:00:00",
                "notes": "Collecte cardio",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["collection_mode"] == "internal_visit"
        assert data["location_type"] == "home"
        assert data["status"] == "draft"
        assert data["tenant_id"] == tenant.id

    def test_create_field_visit_unauthenticated(self, client):
        response = client.post(
            "/api/field-visits",
            json={"collection_mode": "internal_visit"},
        )
        assert response.status_code == 401


class TestListFieldVisits:
    def test_list_empty(self, client, doctor_auth_headers):
        response = client.get("/api/field-visits", headers=doctor_auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_with_entries(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        v1 = FieldVisit(
            tenant_id=tenant.id, created_by=doctor_user.id,
            collection_mode="internal_visit", location_type="home",
            status="draft", scheduled_start_at=datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc),
        )
        v2 = FieldVisit(
            tenant_id=tenant.id, created_by=doctor_user.id,
            collection_mode="internal_visit", location_type="ehpad",
            status="scheduled", scheduled_start_at=datetime(2026, 6, 16, 14, 0, tzinfo=timezone.utc),
        )
        db_session.add_all([v1, v2])
        db_session.commit()

        response = client.get("/api/field-visits", headers=doctor_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_filter_status(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        v1 = FieldVisit(
            tenant_id=tenant.id, created_by=doctor_user.id,
            collection_mode="internal_visit", location_type="home",
            status="draft", scheduled_start_at=datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc),
        )
        v2 = FieldVisit(
            tenant_id=tenant.id, created_by=doctor_user.id,
            collection_mode="internal_visit", location_type="ehpad",
            status="scheduled", scheduled_start_at=datetime(2026, 6, 16, 14, 0, tzinfo=timezone.utc),
        )
        db_session.add_all([v1, v2])
        db_session.commit()

        response = client.get("/api/field-visits?status=scheduled", headers=doctor_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "scheduled"


class TestUpdateFieldVisit:
    def test_patch_status(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        v = FieldVisit(
            tenant_id=tenant.id, created_by=doctor_user.id,
            collection_mode="internal_visit", location_type="home",
            status="draft", scheduled_start_at=datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc),
        )
        db_session.add(v)
        db_session.commit()
        db_session.refresh(v)

        response = client.patch(
            f"/api/field-visits/{v.id}",
            headers=doctor_auth_headers,
            json={"status": "in_progress"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    def test_patch_not_found(self, client, doctor_auth_headers):
        response = client.patch(
            "/api/field-visits/nonexistent-id",
            headers=doctor_auth_headers,
            json={"status": "completed"},
        )
        assert response.status_code == 404

    def test_patch_checklist_completion(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        v = FieldVisit(
            tenant_id=tenant.id, created_by=doctor_user.id,
            collection_mode="internal_visit", location_type="home",
            status="in_progress", checklist_completion_rate=0,
            scheduled_start_at=datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc),
        )
        db_session.add(v)
        db_session.commit()
        db_session.refresh(v)

        response = client.patch(
            f"/api/field-visits/{v.id}",
            headers=doctor_auth_headers,
            json={"checklist_completion_rate": 75, "status": "in_progress"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["checklist_completion_rate"] == 75
