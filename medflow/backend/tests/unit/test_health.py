"""Unit tests for health and auth endpoints."""
from __future__ import annotations

from fastapi import status


def test_health(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] is not None


def test_tenant_creation_requires_admin(client):
    """Unauthenticated request to create_tenant returns 401."""
    payload = {
        "name": "Cabinet Test",
        "slug": "test-cabinet",
        "specialty": "Cardiologie",
        "address": "1 Rue de la Santé",
        "phone": "0123456789",
        "email": "test@medflow.dev",
    }
    response = client.post("/api/admin/tenants", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_interop_stub_returns_501(client):
    response = client.post("/api/interop/carte-vitale/read")
    assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
    assert "VC - Non implemente" in response.json()["detail"]
