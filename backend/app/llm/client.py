"""OpenRouter chat client (OpenAI-compatible API)."""
from __future__ import annotations

import httpx

from ..config import get_settings


class LLMError(RuntimeError):
    """Raised when the LLM call fails."""


class OpenRouterClient:
    """Thin wrapper around the OpenRouter chat completions endpoint."""

    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def available(self) -> bool:
        return self._settings.has_api_key

    def chat(
        self,
        messages: list[dict],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        if not self.available:
            raise LLMError(
                "OPENROUTER_API_KEY is not configured. "
                "Copy .env.example to .env and add your key."
            )

        headers = {
            "Authorization": f"Bearer {self._settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._settings.openrouter_model,
            "messages": messages,
            "temperature": (
                temperature if temperature is not None else self._settings.openrouter_temperature
            ),
            "max_tokens": max_tokens if max_tokens is not None else self._settings.openrouter_max_tokens,
        }
        try:
            with httpx.Client(timeout=self._settings.openrouter_timeout) as client:
                resp = client.post(
                    f"{self._settings.openrouter_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise LLMError(f"Network error talking to OpenRouter: {exc}") from exc

        if resp.status_code != 200:
            raise LLMError(f"OpenRouter API error {resp.status_code}: {resp.text[:400]}")

        try:
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Unexpected OpenRouter response shape: {resp.text[:400]}") from exc
