"""Tests for AI Service (fallback, retry, provider cycling)."""
from __future__ import annotations

import pytest

from app.services.ai_service import (
    AIService,
    AIProvider,
    AIProviderError,
    AIProviderClient,
    MockClient,
)


class FailingClient(AIProviderClient):
    """Always fails for testing fallback."""

    def generate(self, prompt: str, *, temperature: float = 0.3, max_tokens: int = 1024) -> str:
        raise AIProviderError("Simulated failure")


class FixedResponseClient(AIProviderClient):
    """Returns a fixed response for testing."""

    def __init__(self, response: str) -> None:
        self.response = response

    def generate(self, prompt: str, *, temperature: float = 0.3, max_tokens: int = 1024) -> str:
        return self.response


def test_mock_client_returns_deterministic_response():
    client = MockClient()
    result = client.generate("Check completeness of clinical data")
    assert "clinical_complete_percent" in result
    assert "72.5" in result

    result2 = client.generate("prescription for patient")
    assert "Paracétamol" in result2


def test_ai_service_default_priority_uses_mock():
    service = AIService()
    assert service.priority == [AIProvider.MOCK]
    result = service.generate("completeness test")
    assert "clinical_complete_percent" in result


def test_ai_service_fallback_on_provider_failure(monkeypatch):
    service = AIService(
        priority=[AIProvider.OPENAI, AIProvider.MOCK],
        retries_per_provider=1,
    )
    # Inject a failing client for OpenAI
    service._clients[AIProvider.OPENAI] = FailingClient()
    service._clients[AIProvider.MOCK] = MockClient()

    result = service.generate("completeness test")
    assert "clinical_complete_percent" in result


def test_ai_service_raises_when_all_providers_fail():
    service = AIService(
        priority=[AIProvider.OPENAI, AIProvider.ANTHROPIC],
        retries_per_provider=1,
    )
    service._clients[AIProvider.OPENAI] = FailingClient()
    service._clients[AIProvider.ANTHROPIC] = FailingClient()

    with pytest.raises(AIProviderError, match="All providers failed"):
        service.generate("any prompt")


def test_ai_service_priority_order_respected():
    service = AIService(
        priority=[AIProvider.MOCK, AIProvider.OPENAI],
        retries_per_provider=1,
    )
    service._clients[AIProvider.MOCK] = FixedResponseClient("mock-wins")
    service._clients[AIProvider.OPENAI] = FixedResponseClient("openai-wins")

    result = service.generate("test")
    assert result == "mock-wins"


def test_ai_service_retries_then_fails():
    service = AIService(
        priority=[AIProvider.OPENAI],
        retries_per_provider=2,
        backoff_seconds=0.01,  # fast for tests
    )
    service._clients[AIProvider.OPENAI] = FailingClient()

    with pytest.raises(AIProviderError):
        service.generate("test")
