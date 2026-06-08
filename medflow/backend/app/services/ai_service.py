"""AI Service abstraction with multi-provider support and fallback logic."""
from __future__ import annotations

import enum
import logging
import os
import time
from typing import Callable

logger = logging.getLogger("medflow.ai")


class AIProvider(enum.Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    MISTRAL = "mistral"
    MOCK = "mock"


class AIProviderError(Exception):
    """Raised when a provider call fails."""

    pass


class AIProviderClient:
    """Base interface for an AI provider client."""

    def generate(self, prompt: str, *, temperature: float = 0.3, max_tokens: int = 1024) -> str:
        raise NotImplementedError


class OpenAIClient(AIProviderClient):
    """OpenAI GPT client (lazy import to avoid hard dependency)."""

    def __init__(self, api_key: str | None = None) -> None:
        import openai  # noqa: PLC0415 lazy import

        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def generate(self, prompt: str, *, temperature: float = 0.3, max_tokens: int = 1024) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise AIProviderError(f"OpenAI generation failed: {exc}") from exc


class AnthropicClient(AIProviderClient):
    """Anthropic Claude client."""

    def __init__(self, api_key: str | None = None) -> None:
        import anthropic  # noqa: PLC0415 lazy import

        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))

    def generate(self, prompt: str, *, temperature: float = 0.3, max_tokens: int = 1024) -> str:
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text if response.content else ""
        except Exception as exc:
            raise AIProviderError(f"Anthropic generation failed: {exc}") from exc


class GeminiClient(AIProviderClient):
    """Google Gemini client."""

    def __init__(self, api_key: str | None = None) -> None:
        import google.generativeai as genai  # noqa: PLC0415 lazy import

        genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate(self, prompt: str, *, temperature: float = 0.3, max_tokens: int = 1024) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
            )
            return response.text or ""
        except Exception as exc:
            raise AIProviderError(f"Gemini generation failed: {exc}") from exc


class MistralClient(AIProviderClient):
    """Self-hosted or API Mistral client."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        from openai import OpenAI  # noqa: PLC0415 lazy import

        self.client = OpenAI(
            api_key=api_key or os.getenv("MISTRAL_API_KEY"),
            base_url=base_url or os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1"),
        )

    def generate(self, prompt: str, *, temperature: float = 0.3, max_tokens: int = 1024) -> str:
        try:
            response = self.client.chat.completions.create(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise AIProviderError(f"Mistral generation failed: {exc}") from exc


class MockClient(AIProviderClient):
    """Mock client for dev/tests — returns deterministic responses."""

    def generate(self, prompt: str, *, temperature: float = 0.3, max_tokens: int = 1024) -> str:
        if "completeness" in prompt.lower():
            return '{"clinical_complete_percent": 72.5, "missing_fields": ["emergency_contact"], "recommendations": ["Add emergency contact details"]}'
        if "prescription" in prompt.lower() or "médicament" in prompt.lower():
            return '{"medications": "Paracétamol 500mg", "dosage": "1 comprimé toutes les 6h", "duration": "5 jours", "instructions": "À prendre avec un repas", "warnings": "Déconseillé en cas d\'insuffisance hépatique"}'
        return "{\"analysis\": \"Données cliniques reçues. Aucune anomalie détectée.\"}"


# Mapping of provider enum to client constructor
_CLIENT_MAP: dict[AIProvider, Callable[[], AIProviderClient]] = {
    AIProvider.OPENAI: lambda: OpenAIClient(),
    AIProvider.ANTHROPIC: lambda: AnthropicClient(),
    AIProvider.GEMINI: lambda: GeminiClient(),
    AIProvider.MISTRAL: lambda: MistralClient(),
    AIProvider.MOCK: lambda: MockClient(),
}


class AIService:
    """Orchestrate LLM calls with failover across configured providers."""

    def __init__(
        self,
        priority: list[AIProvider] | None = None,
        retries_per_provider: int = 1,
        backoff_seconds: float = 1.0,
    ) -> None:
        self.priority = priority or self._default_priority()
        self.retries = retries_per_provider
        self.backoff = backoff_seconds
        self._clients: dict[AIProvider, AIProviderClient] = {}

    @staticmethod
    def _default_priority() -> list[AIProvider]:
        """Read provider priority from config or env var AI_PROVIDER_PRIORITY."""
        raw = os.environ.get("AI_PROVIDER_PRIORITY", "mock")
        names = [name.strip().lower() for name in raw.split(",") if name.strip()]
        providers = []
        for name in names:
            try:
                providers.append(AIProvider(name))
            except ValueError:
                logger.warning("Unknown AI provider '%s' in priority list", name)
        if not providers:
            providers = [AIProvider.MOCK]
        return providers

    def _get_client(self, provider: AIProvider) -> AIProviderClient:
        if provider not in self._clients:
            builder = _CLIENT_MAP.get(provider)
            if builder is None:
                raise AIProviderError(f"No client builder for provider {provider.value}")
            self._clients[provider] = builder()
        return self._clients[provider]

    def generate(self, prompt: str, *, temperature: float = 0.3, max_tokens: int = 1024) -> str:
        """Generate text with automatic failover across configured providers.

        Args:
            prompt: The prompt to send.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in response.

        Returns:
            Generated text string.

        Raises:
            AIProviderError: if all providers fail.
        """
        last_error: Exception | None = None

        for provider in self.priority:
            for attempt in range(1, self.retries + 1):
                try:
                    client = self._get_client(provider)
                    logger.debug("Attempting generation with %s (attempt %d)", provider.value, attempt)
                    result = client.generate(prompt, temperature=temperature, max_tokens=max_tokens)
                    logger.info("Generation succeeded via %s", provider.value)
                    return result
                except AIProviderError as exc:
                    last_error = exc
                    logger.warning("Provider %s attempt %d failed: %s", provider.value, attempt, exc)
                    if attempt < self.retries:
                        time.sleep(self.backoff * attempt)
                except Exception as exc:
                    last_error = exc
                    logger.warning("Provider %s attempt %d unexpected error: %s", provider.value, attempt, exc)

        raise AIProviderError(
            f"All providers failed ({[p.value for p in self.priority]}). Last: {last_error}"
        ) from last_error


def get_ai_service() -> AIService:
    """FastAPI dependency factory for AIService."""
    return AIService()
