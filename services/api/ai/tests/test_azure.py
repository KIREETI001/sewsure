"""Azure clients tested with a fake transport. No network, no credentials."""

import json

import pytest

from ai import live_check
from ai.azure_http import urllib_transport
from ai.errors import ModelError, ModelTimeout
from ai.model_client import AzureFoundryClient, ModelRequest
from ai.safety import AzurePromptShieldsScreen

ENV = [
    "SEWSURE_AI_FOUNDRY_ENDPOINT",
    "SEWSURE_AI_FOUNDRY_DEPLOYMENT",
    "SEWSURE_AI_FOUNDRY_API_KEY",
    "SEWSURE_CONTENT_SAFETY_ENDPOINT",
    "SEWSURE_CONTENT_SAFETY_API_KEY",
]
FAKE_KEY = "unit-test-not-a-real-key"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ENV:
        monkeypatch.delenv(name, raising=False)


class FakeTransport:
    def __init__(self, status=200, body=None, exc=None):
        self.status, self.body, self.exc, self.calls = status, body, exc, []

    def __call__(self, url, headers, body, timeout):
        self.calls.append((url, headers, json.loads(body), timeout))
        if self.exc:
            raise self.exc
        return self.status, json.dumps(self.body).encode()


def request(stage="D"):
    return ModelRequest(stage, "system", {"inspiration_text": "cropped"}, "name", "v0")


def completion(text):
    return {
        "choices": [{"message": {"content": text}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 20},
    }


def test_foundry_requires_env():
    with pytest.raises(ModelError) as e:
        AzureFoundryClient()
    assert e.value.code == "MODEL_NOT_CONFIGURED"
    assert not AzureFoundryClient.configured()


def test_foundry_request_and_response(monkeypatch):
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_ENDPOINT", "https://example.invalid/")
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_DEPLOYMENT", "dep1")
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_API_KEY", FAKE_KEY)
    monkeypatch.setenv("SEWSURE_AI_PRICE_IN_PER_1K", "0.01")
    monkeypatch.setenv("SEWSURE_AI_PRICE_OUT_PER_1K", "0.03")
    t = FakeTransport(body=completion('{"proposals": []}'))
    resp = AzureFoundryClient(transport=t).complete(request())
    url, headers, body, _ = t.calls[0]
    assert url.startswith("https://example.invalid/openai/deployments/dep1/chat/completions")
    assert headers["api-key"] == FAKE_KEY and "Authorization" not in headers
    assert body["response_format"]["type"] == "json_schema"
    assert "proposals" in body["response_format"]["json_schema"]["schema"]["properties"]
    assert body["temperature"] == 0
    assert resp.text == '{"proposals": []}' and resp.deployment == "dep1"
    assert (resp.input_tokens, resp.output_tokens) == (100, 20)
    assert resp.cost_usd == pytest.approx(0.001 + 0.0006)


@pytest.mark.parametrize("status", [429, 500, 503, 401])
def test_foundry_http_errors_are_model_errors_without_body_text(monkeypatch, status):
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_DEPLOYMENT", "d")
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_API_KEY", FAKE_KEY)
    t = FakeTransport(status=status, body={"error": FAKE_KEY})
    with pytest.raises(ModelError) as e:
        AzureFoundryClient(transport=t).complete(request())
    assert e.value.code == f"AZURE_HTTP_{status}" and FAKE_KEY not in str(e.value)


def test_foundry_timeout_and_bad_response(monkeypatch):
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_DEPLOYMENT", "d")
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_API_KEY", FAKE_KEY)
    with pytest.raises(ModelTimeout):
        AzureFoundryClient(transport=FakeTransport(exc=ModelTimeout())).complete(request())
    with pytest.raises(ModelError) as e:
        AzureFoundryClient(transport=FakeTransport(body={"choices": []})).complete(request())
    assert e.value.code == "AZURE_BAD_RESPONSE"


def test_shields_blocks_and_allows(monkeypatch):
    monkeypatch.setenv("SEWSURE_CONTENT_SAFETY_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("SEWSURE_CONTENT_SAFETY_API_KEY", FAKE_KEY)
    attack = FakeTransport(body={"userPromptAnalysis": {"attackDetected": True}})
    ok = FakeTransport(body={"userPromptAnalysis": {"attackDetected": False}})
    v = AzurePromptShieldsScreen(transport=attack).screen("text")
    assert not v.allowed and v.reason == "PROMPT_ATTACK_SUSPECTED"
    assert AzurePromptShieldsScreen(transport=ok).screen("text").allowed
    url, headers, body, _ = attack.calls[0]
    assert "text:shieldPrompt" in url and headers["Ocp-Apim-Subscription-Key"] == FAKE_KEY
    assert body == {"userPrompt": "text", "documents": []}


def test_shields_never_allows_without_an_answer(monkeypatch):
    monkeypatch.setenv("SEWSURE_CONTENT_SAFETY_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("SEWSURE_CONTENT_SAFETY_API_KEY", FAKE_KEY)
    for t in (FakeTransport(status=503, body={}), FakeTransport(body={"unexpected": 1})):
        with pytest.raises(ModelError):
            AzurePromptShieldsScreen(transport=t).screen("hello")
    with pytest.raises(ModelError) as e:
        AzurePromptShieldsScreen()  # no endpoint configured (autouse fixture cleared env)
    assert e.value.code == "SAFETY_NOT_CONFIGURED"


def test_live_check_skips_cleanly_without_credentials(capsys):
    assert live_check.main() == 0
    out = capsys.readouterr().out
    assert "SKIP foundry" in out and "SKIP prompt_shields" in out


def test_live_check_reports_pass_with_fake_services(monkeypatch, capsys):
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_DEPLOYMENT", "d")
    monkeypatch.setenv("SEWSURE_AI_FOUNDRY_API_KEY", FAKE_KEY)
    monkeypatch.setenv("SEWSURE_CONTENT_SAFETY_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("SEWSURE_CONTENT_SAFETY_API_KEY", FAKE_KEY)

    attrs = json.dumps(
        {
            "crop_length": "cropped",
            "waist_shaping": "none",
            "sleeve_style": "unchanged",
            "closure_preservation": True,
        }
    )
    props = json.dumps(
        {
            "proposals": [
                {"recipe_id": "woven_shirt_crop_v1", "parameters": {"crop_level": "cropped"}}
            ]
        }
    )
    replies = iter([completion(attrs), completion(props)])
    foundry = lambda url, h, b, t: (200, json.dumps(next(replies)).encode())  # noqa: E731

    def shields(url, headers, body, timeout):
        attack = "Ignore all previous" in json.loads(body)["userPrompt"]
        return 200, json.dumps({"userPromptAnalysis": {"attackDetected": attack}}).encode()

    monkeypatch.setattr(
        live_check,
        "AzureFoundryClient",
        lambda: AzureFoundryClient(transport=foundry),
    )
    monkeypatch.setattr(live_check, "AzurePromptShieldsScreen", _ShieldsFactory(shields))
    assert live_check.main() == 0
    out = capsys.readouterr().out
    assert "PASS foundry" in out and "PASS prompt_shields" in out
    assert FAKE_KEY not in out and "example.invalid" not in out


class _ShieldsFactory:
    def __init__(self, transport):
        self._t = transport

    def configured(self):
        return True

    def __call__(self):
        return AzurePromptShieldsScreen(transport=self._t)


def test_default_transport_refuses_nothing_at_import():
    assert callable(urllib_transport)  # importing the module made no network call
