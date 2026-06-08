"""Base connector interface for interoperability stubs."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    """Abstract interface for all external health system connectors.

    Implementations should override the methods below and handle:
    - Authentication / credential refresh
    - Payload serialization (HL7 FHIR, CDA, CI-SIS, DICOM)
    - Retry policy with exponential backoff
    - Audit logging into external_integration_logs
    """

    connector_type: str = "base"

    @abstractmethod
    async def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Send data to the external system."""
        ...

    @abstractmethod
    async def receive(self, identifier: str) -> dict[str, Any]:
        """Receive / pull data from the external system."""
        ...

    @abstractmethod
    async def healthcheck(self) -> bool:
        """Return True if the external system is reachable."""
        ...
