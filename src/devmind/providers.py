"""Replaceable chat model providers with bounded, secret-safe error handling."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class ProviderUnavailable(RuntimeError):
    """Raised when configuration or the provider prevents a model response."""


class ProviderRateLimited(ProviderUnavailable):
    """Raised when the provider continues returning rate-limit responses."""


class ProviderRequestFailed(ProviderUnavailable):
    """Raised for non-retryable HTTP and transport failures."""


class ProviderInvalidResponse(ProviderUnavailable):
    """Raised when a provider response is missing or malformed."""


@dataclass(frozen=True)
class ChatRequest:
    """Validated request options independent of a specific model service."""

    prompt: str
    temperature: float = 0.0
    json_mode: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValueError("Chat prompt must be a non-empty string.")
        if not 0 <= self.temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2.")


@dataclass(frozen=True)
class ChatResponse:
    """Normalized model content and optional usage values."""

    content: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class ChatProvider:
    """Provider interface; `complete` keeps compatibility with existing agents."""

    def complete(self, prompt: str) -> str:
        raise NotImplementedError

    def request(self, request: ChatRequest) -> ChatResponse:
        """Default adapter for simple providers that implement only `complete`."""
        return ChatResponse(content=self.complete(request.prompt), model="unknown")


class DeterministicFakeProvider(ChatProvider):
    """Queue-backed fake for repeatable tests; it never calls a model service."""

    def __init__(self, responses: list[str] | str):
        self._responses = [responses] if isinstance(responses, str) else list(responses)
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self._responses:
            raise ProviderUnavailable("Fake provider has no queued response.")
        response = self._responses.pop(0)
        if not isinstance(response, str):
            raise ProviderInvalidResponse("Fake provider response must be text.")
        return response


class OpenAICompatibleProvider(ChatProvider):
    """OpenAI-compatible chat adapter with bounded retries and response checks."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ):
        self.base_url = (base_url or os.getenv("DEVMIND_LLM_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("DEVMIND_LLM_API_KEY", "")
        self.model = model or os.getenv("DEVMIND_LLM_MODEL", "")
        if timeout is None:
            try:
                timeout = float(os.getenv("DEVMIND_LLM_TIMEOUT", "45"))
            except ValueError as exc:
                raise ValueError("DEVMIND_LLM_TIMEOUT must be a positive number of seconds.") from exc
        if timeout <= 0:
            raise ValueError("Provider timeout must be positive.")
        if max_retries is None:
            try:
                max_retries = int(os.getenv("DEVMIND_LLM_MAX_RETRIES", "2"))
            except ValueError as exc:
                raise ValueError("DEVMIND_LLM_MAX_RETRIES must be an integer from 0 to 3.") from exc
        if not 0 <= max_retries <= 3:
            raise ValueError("Provider max_retries must be between 0 and 3.")
        self.timeout = timeout
        self.max_retries = max_retries

    def complete(self, prompt: str) -> str:
        """Return assistant text, raising a typed error on unavailable/invalid output."""
        return self.request(ChatRequest(prompt)).content

    def request(self, request: ChatRequest) -> ChatResponse:
        if not self.base_url or not self.model:
            raise ProviderUnavailable("Configure DEVMIND_LLM_BASE_URL and DEVMIND_LLM_MODEL to enable model requests.")
        url = self.base_url if self.base_url.endswith("/chat/completions") else self.base_url + "/chat/completions"
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": request.temperature,
        }
        disable_thinking = os.getenv("DEVMIND_LLM_DISABLE_THINKING", "").strip().lower()
        if disable_thinking in {"1", "true", "yes", "on"}:
            body["think"] = False
        if request.json_mode:
            body["response_format"] = {"type": "json_object"}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        encoded_body = json.dumps(body).encode("utf-8")
        last_error: ProviderUnavailable | None = None
        for attempt in range(self.max_retries + 1):
            http_request = urllib.request.Request(url, data=encoded_body, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(http_request, timeout=self.timeout) as response:
                    payload = json.loads(response.read(4_000_001))
                return _parse_chat_response(payload, default_model=self.model)
            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    last_error = ProviderRateLimited("Model provider rate limit persisted after bounded retries.")
                    retryable = True
                elif 500 <= exc.code <= 599:
                    last_error = ProviderRequestFailed(f"Model provider returned HTTP {exc.code}.")
                    retryable = True
                else:
                    raise ProviderRequestFailed(f"Model provider returned HTTP {exc.code}.") from exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = ProviderRequestFailed(f"Model request failed due to {type(exc).__name__}.")
                retryable = True
            except (json.JSONDecodeError, ProviderInvalidResponse) as exc:
                raise ProviderInvalidResponse("Model provider returned malformed or incomplete response data.") from exc
            if not retryable or attempt >= self.max_retries:
                assert last_error is not None
                raise last_error
            time.sleep(min(0.25 * (2**attempt), 1.0))
        raise ProviderUnavailable("Model provider did not return a response.")


def complete_json(provider: ChatProvider, prompt: str) -> dict[str, Any]:
    """Request a JSON object and validate its shape before agent code consumes it."""
    response = provider.request(ChatRequest(prompt=prompt, json_mode=True))
    try:
        value = json.loads(response.content)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ProviderInvalidResponse("Model response was not valid JSON.") from exc
    if not isinstance(value, dict):
        raise ProviderInvalidResponse("Structured model response must be a JSON object.")
    return value


def _parse_chat_response(payload: Any, *, default_model: str) -> ChatResponse:
    if not isinstance(payload, dict):
        raise ProviderInvalidResponse("Model response must be a JSON object.")
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderInvalidResponse("Model response did not contain a chat completion.") from exc
    if not isinstance(content, str) or not content.strip():
        raise ProviderInvalidResponse("Model response content must be a non-empty string.")
    usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}
    return ChatResponse(
        content=content,
        model=str(payload.get("model") or default_model),
        prompt_tokens=_optional_int(usage.get("prompt_tokens")),
        completion_tokens=_optional_int(usage.get("completion_tokens")),
    )


def _optional_int(value: Any) -> int | None:
    return value if isinstance(value, int) and value >= 0 else None
