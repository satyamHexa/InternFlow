"""Azure OpenAI async client with automatic retry logic.

The client is lazily initialised so the app can start without credentials —
endpoints that need AI will raise ``AIServiceUnavailableError`` at call time.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import openai
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

# Exceptions that merit a retry (transient Azure / network issues)
_RETRYABLE = (
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.RateLimitError,
    openai.InternalServerError,
)

_RETRY_POLICY = dict(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(_RETRYABLE),
    reraise=True,
)


class AIServiceUnavailableError(Exception):
    """Raised when Azure OpenAI credentials are not configured."""


class AzureOpenAIClient:
    """Thin async wrapper around the official OpenAI SDK (v1.x).

    All public methods retry up to 3 times with exponential back-off
    on transient errors before propagating the exception.
    """

    def __init__(self) -> None:
        self._client: openai.AsyncAzureOpenAI | None = None

    # ── Configuration ───────────────────────────────────────────────────

    @property
    def is_configured(self) -> bool:
        return bool(settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT)

    def _get_client(self) -> openai.AsyncAzureOpenAI:
        if not self.is_configured:
            raise AIServiceUnavailableError(
                "Azure OpenAI credentials are not configured. "
                "Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in your .env file."
            )
        if self._client is None:
            self._client = openai.AsyncAzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_version=settings.AZURE_OPENAI_API_VERSION,
            )
        return self._client

    # ── Core completion helpers ─────────────────────────────────────────

    async def _raw_completion(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: dict | None = None,
    ) -> str:
        """Single attempt — called inside the retry loop."""
        client = self._get_client()
        kwargs: dict[str, Any] = dict(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if response_format:
            kwargs["response_format"] = response_format

        response = await client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        logger.debug(
            "OpenAI tokens used: prompt=%s completion=%s",
            response.usage.prompt_tokens if response.usage else "?",
            response.usage.completion_tokens if response.usage else "?",
        )
        return content

    async def chat_text(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.4,
        max_tokens: int = 2048,
    ) -> str:
        """Call GPT and return raw text. Retries on transient errors."""
        try:
            async for attempt in AsyncRetrying(**_RETRY_POLICY):
                with attempt:
                    return await self._raw_completion(
                        messages, temperature=temperature, max_tokens=max_tokens
                    )
        except RetryError as exc:
            logger.error("OpenAI chat_text failed after retries: %s", exc)
            raise
        # unreachable but satisfies type checkers
        raise RuntimeError("Unreachable")  # pragma: no cover

    async def chat_json(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> dict:
        """Call GPT in JSON mode and return a parsed dict. Retries on transient errors.

        Uses ``response_format={"type": "json_object"}`` to guarantee the model
        emits valid JSON.  Falls back to manual JSON extraction on decode errors.
        """
        raw = ""
        try:
            async for attempt in AsyncRetrying(**_RETRY_POLICY):
                with attempt:
                    raw = await self._raw_completion(
                        messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_format={"type": "json_object"},
                    )
        except RetryError as exc:
            logger.error("OpenAI chat_json failed after retries: %s", exc)
            raise

        return self._parse_json(raw)

    # ── JSON extraction helpers ─────────────────────────────────────────

    @staticmethod
    def _parse_json(raw: str) -> dict:
        """Parse JSON from a model response, stripping markdown fences if present."""
        text = raw.strip()
        # Strip ```json ... ``` fences that models sometimes emit despite instructions
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(
                line for line in lines if not line.startswith("```")
            ).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning("Could not parse JSON from model response: %s", exc)
            logger.debug("Raw response: %s", raw[:500])
            return {}


# Module-level singleton
azure_openai_client = AzureOpenAIClient()
