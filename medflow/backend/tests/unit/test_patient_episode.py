"""Unit tests for patient and episode API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.db.database import Base, engine, get_db
from app.models.models import Tenant, User, Patient, Episode
from app.core.security import get_password_hash
from app.models.models import Prescription


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory database for each test."""
    Base.metadata.create_all(bind=engine)
    session = next(get_db())
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden get_db."""
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
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
def ipa_user(db_session, tenant):
    u = User(
        tenant_id=tenant.id,
        email="ipa@test.com",
        hashed_password=get_password_hash("TestPassphrase123!"),
        full_name="IPA User",
        role="ipa",
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
def ipa_auth_headers(client, ipa_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "ipa@test.com", "password": "TestPassphrase123!"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestPatientEndpoints:
    def test_create_patient(self, client, auth_headers):
        response = client.post(
            "/api/patients",
            headers=auth_headers,
            json={
                "last_name": "Dupont",
                "first_name": "Marie",
                "gender": "F",
                "phone": "0601020304",
                "email": "marie.dupont@test.com",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["last_name"] == "Dupont"
        assert data["first_name"] == "Marie"
        assert data["gender"] == "F"
        assert "id" in data
        assert "tenant_id" in data

    def test_create_patient_minimal(self, client, auth_headers):
        response = client.post(
            "/api/patients",
            headers=auth_headers,
            json={"last_name": "Martin", "first_name": "Jean"},
        )
        assert response.status_code == 200
        assert response.json()["last_name"] == "Martin"

    def test_list_patients(self, client, auth_headers, db_session, tenant, admin_user):
        p1 = Patient(tenant_id=tenant.id, last_name="A", first_name="X")
        p2 = Patient(tenant_id=tenant.id, last_name="B", first_name="Y")
        db_session.add_all([p1, p2])
        db_session.commit()
        response = client.get("/api/patients", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_patient(self, client, auth_headers, db_session, tenant, admin_user):
        p = Patient(tenant_id=tenant.id, last_name="Test", first_name="Patient")
        db_session.add(p)
        db_session.commit()
        db_session.refresh(p)
        response = client.get(f"/api/patients/{p.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["last_name"] == "Test"

    def test_get_patient_not_found(self, client, auth_headers):
        response = client.get("/api/patients/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_create_patient_unauthenticated(self, client):
        response = client.post(
            "/api/patients",
            json={"last_name": "X", "first_name": "Y"},
        )
        assert response.status_code == 401


class TestEpisodeEndpoints:
    def test_create_episode(self, client, auth_headers, db_session, tenant, admin_user):
        patient = Patient(tenant_id=tenant.id, last_name="Ep", first_name="Patient")
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)

        response = client.post(
            "/api/episodes",
            headers=auth_headers,
            json={
                "patient_id": patient.id,
                "episode_type": "in_clinic",
                "chief_complaint": "Douleur abdominale",
                "intake_method": "digital",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == patient.id
        assert data["status"] == "pending"
        assert data["collected_by"] == admin_user.id

    def test_create_episode_patient_not_found(self, client, auth_headers):
        response = client.post(
            "/api/episodes",
            headers=auth_headers,
            json={"patient_id": "nonexistent-id", "chief_complaint": "Test"},
        )
        assert response.status_code == 404

    def test_list_episodes(self, client, auth_headers, db_session, tenant, admin_user):
        patient = Patient(tenant_id=tenant.id, last_name="L", first_name="P")
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)

        ep1 = Episode(tenant_id=tenant.id, patient_id=patient.id, status="pending")
        ep2 = Episode(tenant_id=tenant.id, patient_id=patient.id, status="consented")
        db_session.add_all([ep1, ep2])
        db_session.commit()

        response = client.get("/api/episodes", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_episodes_filter_by_patient(
        self, client, auth_headers, db_session, tenant, admin_user
    ):
        p1 = Patient(tenant_id=tenant.id, last_name="P1", first_name="P1")
        p2 = Patient(tenant_id=tenant.id, last_name="P2", first_name="P2")
        db_session.add_all([p1, p2])
        db_session.commit()
        db_session.refresh(p1)
        db_session.refresh(p2)

        ep1 = Episode(tenant_id=tenant.id, patient_id=p1.id, status="pending")
        ep2 = Episode(tenant_id=tenant.id, patient_id=p2.id, status="consented")
        db_session.add_all([ep1, ep2])
        db_session.commit()

        response = client.get(f"/api/episodes?patient_id={p1.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["patient_id"] == p1.id

    def test_update_episode(self, client, auth_headers, db_session, tenant, admin_user):
        patient = Patient(tenant_id=tenant.id, last_name="U", first_name="P")
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)

        ep = Episode(tenant_id=tenant.id, patient_id=patient.id, status="pending")
        db_session.add(ep)
        db_session.commit()
        db_session.refresh(ep)

        response = client.patch(
            f"/api/episodes/{ep.id}",
            headers=auth_headers,
            json={"status": "consented", "chief_complaint": "Updated complaint"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "consented"
        assert data["chief_complaint"] == "Updated complaint"

    def test_get_episode(self, client, auth_headers, db_session, tenant, admin_user):
        patient = Patient(tenant_id=tenant.id, last_name="G", first_name="P")
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)

        ep = Episode(tenant_id=tenant.id, patient_id=patient.id, status="pending")
        db_session.add(ep)
        db_session.commit()
        db_session.refresh(ep)

        response = client.get(f"/api/episodes/{ep.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == ep.id

    def test_get_episode_not_found(self, client, auth_headers):
        response = client.get("/api/episodes/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404


class TestPrescriptionEndpoints:
    def test_create_prescription(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        patient = Patient(tenant_id=tenant.id, last_name="P", first_name="R")
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        ep = Episode(tenant_id=tenant.id, patient_id=patient.id, status="pending")
        db_session.add(ep)
        db_session.commit()
        db_session.refresh(ep)
        response = client.post(
            "/api/prescriptions",
            headers=doctor_auth_headers,
            json={
                "episode_id": ep.id,
                "medications": "Paracetamol 500mg",
                "dosage": "1cp x 3/jour",
                "duration": "5 jours",
                "instructions": "A prendre pendant les repas",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["episode_id"] == ep.id
        assert data["status"] == "draft"
        assert data["created_by"] == doctor_user.id

    def test_create_prescription_episode_not_found(self, client, doctor_auth_headers):
        response = client.post(
            "/api/prescriptions",
            headers=doctor_auth_headers,
            json={"episode_id": "nonexistent-id", "medications": "Test"},
        )
        assert response.status_code == 404

    def test_sign_prescription_doctor_ok(
        self, client, doctor_auth_headers, db_session, tenant, doctor_user
    ):
        patient = Patient(tenant_id=tenant.id, last_name="S", first_name="P")
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        ep = Episode(tenant_id=tenant.id, patient_id=patient.id, status="pending")
        db_session.add(ep)
        db_session.commit()
        db_session.refresh(ep)
        rx = Prescription(tenant_id=tenant.id, episode_id=ep.id, status="draft")
        db_session.add(rx)
        db_session.commit()
        db_session.refresh(rx)
        response = client.post(
            f"/api/prescriptions/{rx.id}/sign", headers=doctor_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "signed"
        assert data["signed_by"] == doctor_user.id

    def test_sign_prescription_admin_forbidden(self, client, auth_headers, db_session, tenant):
        patient = Patient(tenant_id=tenant.id, last_name="F", first_name="P")
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        ep = Episode(tenant_id=tenant.id, patient_id=patient.id, status="pending")
        db_session.add(ep)
        db_session.commit()
        db_session.refresh(ep)
        rx = Prescription(tenant_id=tenant.id, episode_id=ep.id, status="draft")
        db_session.add(rx)
        db_session.commit()
        db_session.refresh(rx)
        response = client.post(
            f"/api/prescriptions/{rx.id}/sign", headers=auth_headers
        )
        assert response.status_code == 403

    def test_sign_prescription_ipa_forbidden(self, client, ipa_auth_headers, db_session, tenant, ipa_user):
        patient = Patient(tenant_id=tenant.id, last_name="I", first_name="P")
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        ep = Episode(tenant_id=tenant.id, patient_id=patient.id, status="pending")
        db_session.add(ep)
        db_session.commit()
        db_session.refresh(ep)
        rx = Prescription(tenant_id=tenant.id, episode_id=ep.id, status="draft")
        db_session.add(rx)
        db_session.commit()
        db_session.refresh(rx)
        response = client.post(
            f"/api/prescriptions/{rx.id}/sign", headers=ipa_auth_headers
        )
        assert response.status_code == 403

    def test_sign_prescription_already_signed(
        self, client, doctor_auth_headers, db_session, tenant, doctor_user
    ):
        patient = Patient(tenant_id=tenant.id, last_name="A", first_name="P")
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        ep = Episode(tenant_id=tenant.id, patient_id=patient.id, status="pending")
        db_session.add(ep)
        db_session.commit()
        db_session.refresh(ep)
        rx = Prescription(tenant_id=tenant.id, episode_id=ep.id, status="signed", signed_by=doctor_user.id)
        db_session.add(rx)
        db_session.commit()
        db_session.refresh(rx)
        response = client.post(
            f"/api/prescriptions/{rx.id}/sign", headers=doctor_auth_headers
        )
        assert response.status_code == 409

    def test_update_signed_prescription_forbidden(self, client, doctor_auth_headers, db_session, tenant, doctor_user):
        patient = Patient(tenant_id=tenant.id, last_name="U", first_name="P")
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        ep = Episode(tenant_id=tenant.id, patient_id=patient.id, status="pending")
        db_session.add(ep)
        db_session.commit()
        db_session.refresh(ep)
        rx = Prescription(tenant_id=tenant.id, episode_id=ep.id, status="signed", signed_by=doctor_user.id)
        db_session.add(rx)
        db_session.commit()
        db_session.refresh(rx)
        response = client.patch(
            f"/api/prescriptions/{rx.id}",
            headers=doctor_auth_headers,
            json={"medications": "Updated"},
        )
        assert response.status_code == 409

    def test_list_prescriptions(
        self, client, auth_headers, db_session, tenant, admin_user
    ):
        patient = Patient(tenant_id=tenant.id, last_name="L", first_name="P")
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        ep = Episode(tenant_id=tenant.id, patient_id=patient.id, status="pending")
        db_session.add(ep)
        db_session.commit()
        db_session.refresh(ep)
        rx1 = Prescription(tenant_id=tenant.id, episode_id=ep.id, status="draft")
        rx2 = Prescription(tenant_id=tenant.id, episode_id=ep.id, status="signed")
        db_session.add_all([rx1, rx2])
        db_session.commit()
        response = client.get("/api/prescriptions", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2