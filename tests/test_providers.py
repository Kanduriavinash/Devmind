import io
import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from devmind.providers import (
    ChatRequest,
    DeterministicFakeProvider,
    OpenAICompatibleProvider,
    ProviderInvalidResponse,
    ProviderRateLimited,
    ProviderRequestFailed,
    ProviderUnavailable,
    complete_json,
)


def _http_error(status):
    return urllib.error.HTTPError("https://provider.invalid", status, "failure", {}, io.BytesIO(b"private body"))


def test_deterministic_fake_provider_returns_queued_responses():
    provider = DeterministicFakeProvider(["first", "second"])
    assert provider.complete("prompt one") == "first"
    assert provider.complete("prompt two") == "second"
    assert provider.prompts == ["prompt one", "prompt two"]


def test_chat_request_validates_prompt_and_temperature():
    with pytest.raises(ValueError, match="non-empty"):
        ChatRequest(" ")
    with pytest.raises(ValueError, match="Temperature"):
        ChatRequest("hello", temperature=3)


def test_provider_returns_normalized_response_and_sends_json_mode():
    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps({
        "model": "local-model",
        "choices": [{"message": {"content": '{"finding": "supported"}'}}],
        "usage": {"prompt_tokens": 8, "completion_tokens": 4},
    }).encode()
    provider = OpenAICompatibleProvider("http://127.0.0.1:11434/v1", model="local-model", max_retries=0)

    with patch("devmind.providers.urllib.request.urlopen", return_value=response) as urlopen:
        parsed = provider.request(ChatRequest("inspect evidence", json_mode=True))

    assert parsed.content == '{"finding": "supported"}'
    assert parsed.model == "local-model"
    assert parsed.prompt_tokens == 8
    sent = json.loads(urlopen.call_args.args[0].data)
    assert sent["response_format"] == {"type": "json_object"}
    assert "think" not in sent


def test_provider_can_disable_model_thinking(monkeypatch):
    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps({
        "model": "local-model",
        "choices": [{"message": {"content": "ready"}}],
    }).encode()
    monkeypatch.setenv("DEVMIND_LLM_DISABLE_THINKING", "true")
    provider = OpenAICompatibleProvider("http://127.0.0.1:11434/v1", model="local-model", max_retries=0)

    with patch("devmind.providers.urllib.request.urlopen", return_value=response) as urlopen:
        assert provider.complete("reply briefly") == "ready"

    assert json.loads(urlopen.call_args.args[0].data)["think"] is False


def test_provider_timeout_can_be_configured_from_environment(monkeypatch):
    monkeypatch.setenv("DEVMIND_LLM_TIMEOUT", "240")
    assert OpenAICompatibleProvider("http://127.0.0.1:11434/v1", model="local-model").timeout == 240
    with pytest.raises(ValueError, match="positive number"):
        monkeypatch.setenv("DEVMIND_LLM_TIMEOUT", "not-a-number")
        OpenAICompatibleProvider("http://127.0.0.1:11434/v1", model="local-model")


def test_provider_retry_count_can_be_disabled_from_environment(monkeypatch):
    monkeypatch.setenv("DEVMIND_LLM_MAX_RETRIES", "0")
    provider = OpenAICompatibleProvider("http://127.0.0.1:11434/v1", model="local-model")
    assert provider.max_retries == 0


def test_provider_retries_rate_limit_and_never_exposes_api_key_in_error():
    response = MagicMock()
    response.__enter__.return_value.read.return_value = b'{"choices":[{"message":{"content":"ok"}}]}'
    provider = OpenAICompatibleProvider("https://provider.invalid/v1", api_key="do-not-leak", model="test", max_retries=1)
    with patch("devmind.providers.urllib.request.urlopen", side_effect=[_http_error(429), response]) as urlopen, patch("devmind.providers.time.sleep"):
        assert provider.complete("hello") == "ok"
    assert urlopen.call_count == 2

    provider.max_retries = 0
    with patch("devmind.providers.urllib.request.urlopen", side_effect=_http_error(401)):
        with pytest.raises(ProviderRequestFailed) as raised:
            provider.complete("hello")
    assert "do-not-leak" not in str(raised.value)


def test_provider_bounds_retry_count_and_classifies_rate_limits():
    provider = OpenAICompatibleProvider("https://provider.invalid/v1", model="test", max_retries=2)
    with patch("devmind.providers.urllib.request.urlopen", side_effect=_http_error(429)) as urlopen, patch("devmind.providers.time.sleep"):
        with pytest.raises(ProviderRateLimited):
            provider.complete("hello")
    assert urlopen.call_count == 3


def test_provider_rejects_invalid_structured_responses():
    class JsonFake(DeterministicFakeProvider):
        def request(self, request):
            assert request.json_mode
            from devmind.providers import ChatResponse

            return ChatResponse(self.complete(request.prompt), "fake")

    assert complete_json(JsonFake('{"ok": true}'), "return JSON") == {"ok": True}
    with pytest.raises(ProviderInvalidResponse, match="JSON"):
        complete_json(JsonFake("not json"), "return JSON")
    with pytest.raises(ProviderInvalidResponse, match="object"):
        complete_json(JsonFake("[1, 2]"), "return JSON")


def test_provider_requires_configuration_and_bounds_retries():
    with pytest.raises(ProviderUnavailable, match="Configure"):
        OpenAICompatibleProvider().complete("hello")
    with pytest.raises(ValueError, match="max_retries"):
        OpenAICompatibleProvider(max_retries=4)
