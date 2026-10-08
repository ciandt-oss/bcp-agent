"""Unit tests for OpenRouter and HuggingFace provider configurations via get_provider()."""

import logging
import pytest
from unittest.mock import patch, MagicMock

from bcp.llm_providers import get_provider
from bcp.simple_llm_provider import SimpleLLMProvider
from bcp.logger import setup_logger


@pytest.fixture
def logger():
    return setup_logger(logging.DEBUG)


# --- OpenRouter: get_provider() returns SimpleLLMProvider with correct config ---

def test_get_provider_openrouter(logger, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-key")
    monkeypatch.setenv("OPENROUTER_MODEL_NAME", "anthropic/claude-3.5-sonnet")
    provider = get_provider("openrouter", logger)
    assert isinstance(provider, SimpleLLMProvider)
    assert provider.model == "anthropic/claude-3.5-sonnet"
    assert provider.api_key == "sk-or-test-key"
    assert provider.base_url == "https://openrouter.ai/api/v1"


def test_get_provider_openrouter_default_model(logger, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-key")
    monkeypatch.delenv("OPENROUTER_MODEL_NAME", raising=False)
    provider = get_provider("openrouter", logger)
    assert provider.model == "openai/gpt-6-luna"


def test_get_provider_openrouter_extra_headers(logger, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-key")
    monkeypatch.setenv("OPENROUTER_SITE_URL", "https://myapp.com")
    monkeypatch.setenv("OPENROUTER_APP_TITLE", "BCP Calc")
    provider = get_provider("openrouter", logger)
    assert provider.extra_headers.get("HTTP-Referer") == "https://myapp.com"
    assert provider.extra_headers.get("X-Title") == "BCP Calc"


def test_get_provider_openrouter_no_extra_headers(logger, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-key")
    monkeypatch.delenv("OPENROUTER_SITE_URL", raising=False)
    monkeypatch.delenv("OPENROUTER_APP_TITLE", raising=False)
    provider = get_provider("openrouter", logger)
    assert "HTTP-Referer" not in provider.extra_headers
    assert "X-Title" not in provider.extra_headers


# --- HuggingFace: get_provider() returns SimpleLLMProvider with correct config ---

def test_get_provider_huggingface(logger, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "hf-test-token")
    monkeypatch.setenv("HF_MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")
    provider = get_provider("huggingface", logger)
    assert isinstance(provider, SimpleLLMProvider)
    assert provider.model == "meta-llama/Llama-3.3-70B-Instruct"
    assert provider.api_key == "hf-test-token"
    assert provider.base_url == "https://router.huggingface.co/v1"


def test_get_provider_huggingface_default_model(logger, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "hf-test-token")
    monkeypatch.delenv("HF_MODEL_NAME", raising=False)
    provider = get_provider("huggingface", logger)
    assert provider.model == "zai-org/GLM-5.2:novita"


# --- OpenRouter: invoke() sends correct URL and auth ---

@patch("bcp.simple_llm_provider.httpx.post")
def test_openrouter_invoke_calls_correct_url(mock_post, logger, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-key")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Response from OpenRouter"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = get_provider("openrouter", logger)
    provider.invoke("Hello")

    call_args = mock_post.call_args
    url = call_args[0][0]
    assert "openrouter.ai/api/v1/chat/completions" in url


@patch("bcp.simple_llm_provider.httpx.post")
def test_openrouter_invoke_uses_bearer_token(mock_post, logger, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-my-key")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Response"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = get_provider("openrouter", logger)
    provider.invoke("Hello")

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer sk-or-my-key"


@patch("bcp.simple_llm_provider.httpx.post")
def test_openrouter_invoke_includes_extra_headers(mock_post, logger, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-key")
    monkeypatch.setenv("OPENROUTER_SITE_URL", "https://myapp.com")
    monkeypatch.setenv("OPENROUTER_APP_TITLE", "BCP Calc")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Response"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = get_provider("openrouter", logger)
    provider.invoke("Hello")

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]
    assert headers["HTTP-Referer"] == "https://myapp.com"
    assert headers["X-Title"] == "BCP Calc"


# --- HuggingFace: invoke() sends correct URL and auth ---

@patch("bcp.simple_llm_provider.httpx.post")
def test_huggingface_invoke_calls_correct_url(mock_post, logger, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "hf-test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Response from HuggingFace"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = get_provider("huggingface", logger)
    provider.invoke("Hello")

    call_args = mock_post.call_args
    url = call_args[0][0]
    assert "router.huggingface.co/v1/chat/completions" in url


@patch("bcp.simple_llm_provider.httpx.post")
def test_huggingface_invoke_uses_bearer_token(mock_post, logger, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "hf-my-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Response"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = get_provider("huggingface", logger)
    provider.invoke("Hello")

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer hf-my-token"
