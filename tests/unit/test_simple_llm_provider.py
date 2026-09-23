import logging
import os
from unittest.mock import patch, MagicMock

import pytest
import httpx

from bcp.simple_llm_provider import SimpleLLMProvider, PLACEHOLDER_KEYS
from bcp.logger import setup_logger


@pytest.fixture
def logger():
    return setup_logger(logging.DEBUG)


@pytest.fixture
def mock_response():
    """Create a mock httpx.Response with a valid Chat Completions JSON body."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "choices": [{"message": {"content": "LLM response text"}}]
    }
    resp.raise_for_status = MagicMock()
    return resp


# --- Initialization ---

def test_init_defaults(logger):
    provider = SimpleLLMProvider(logger, model="mistral-small-2503")
    assert provider.model == "mistral-small-2503"
    assert provider.temperature == 0
    assert provider.max_tokens == 4096
    assert provider.timeout == 300


def test_init_with_custom_base_url(logger):
    provider = SimpleLLMProvider(logger, model="llama3", base_url="http://localhost:11434/v1")
    assert provider.base_url == "http://localhost:11434/v1"


def test_init_with_env_vars(logger, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-real-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://gateway.local/v1")
    provider = SimpleLLMProvider(logger, model="gpt-4o")
    assert provider.api_key == "sk-real-key"
    assert provider.base_url == "http://gateway.local/v1"


def test_init_strips_trailing_slash(logger):
    provider = SimpleLLMProvider(logger, model="test", base_url="http://localhost:8080/v1/")
    assert provider.base_url == "http://localhost:8080/v1"


def test_inherits_from_llm_provider(logger):
    from bcp.llm_providers import LLMProvider
    provider = SimpleLLMProvider(logger, model="test")
    assert isinstance(provider, LLMProvider)


# --- Auth header behavior ---

def test_should_send_auth_with_real_key(logger):
    provider = SimpleLLMProvider(logger, model="test", api_key="sk-real-key-12345")
    assert provider._should_send_auth() is True


def test_should_not_send_auth_with_placeholder_keys(logger):
    for placeholder in PLACEHOLDER_KEYS:
        provider = SimpleLLMProvider(logger, model="test", api_key=placeholder)
        assert provider._should_send_auth() is False, f"Failed for placeholder: '{placeholder}'"


def test_should_not_send_auth_with_empty_key(logger):
    provider = SimpleLLMProvider(logger, model="test", api_key="")
    assert provider._should_send_auth() is False


def test_should_not_send_auth_with_none_key(logger, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = SimpleLLMProvider(logger, model="test")
    assert provider._should_send_auth() is False


# --- invoke() ---

@patch("bcp.simple_llm_provider.httpx.post")
def test_invoke_returns_response_text(mock_post, logger, mock_response):
    mock_post.return_value = mock_response
    provider = SimpleLLMProvider(logger, model="mistral-small-2503", base_url="http://localhost:8080/v1", api_key="test-key")
    result = provider.invoke("Test prompt")
    assert result == "LLM response text"


@patch("bcp.simple_llm_provider.httpx.post")
def test_invoke_sends_auth_header_with_real_key(mock_post, logger, mock_response):
    mock_post.return_value = mock_response
    provider = SimpleLLMProvider(logger, model="gpt-4o", base_url="https://api.openai.com/v1", api_key="sk-real-key")
    provider.invoke("Test prompt")
    call_kwargs = mock_post.call_args
    headers = call_kwargs.kwargs.get("headers", {})
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer sk-real-key"


@patch("bcp.simple_llm_provider.httpx.post")
def test_invoke_omits_auth_header_with_placeholder_key(mock_post, logger, mock_response):
    mock_post.return_value = mock_response
    provider = SimpleLLMProvider(logger, model="mistral-small-2503", base_url="http://localhost:8080/v1", api_key="test-key")
    provider.invoke("Test prompt")
    call_kwargs = mock_post.call_args
    headers = call_kwargs.kwargs.get("headers", {})
    assert "Authorization" not in headers


@patch("bcp.simple_llm_provider.httpx.post")
def test_invoke_sends_correct_payload(mock_post, logger, mock_response):
    mock_post.return_value = mock_response
    provider = SimpleLLMProvider(logger, model="mistral-small-2503", base_url="http://localhost:8080/v1", api_key="test-key", temperature=0, max_tokens=2048)
    provider.invoke("My prompt text")
    call_kwargs = mock_post.call_args
    json_payload = call_kwargs.kwargs.get("json", {})
    assert json_payload["model"] == "mistral-small-2503"
    assert json_payload["messages"] == [{"role": "user", "content": "My prompt text"}]
    assert json_payload["temperature"] == 0
    assert json_payload["max_tokens"] == 2048
    assert json_payload["stream"] is False


@patch("bcp.simple_llm_provider.httpx.post")
def test_invoke_calls_correct_url(mock_post, logger, mock_response):
    mock_post.return_value = mock_response
    provider = SimpleLLMProvider(logger, model="test", base_url="http://localhost:8080/v1", api_key="test-key")
    provider.invoke("prompt")
    call_args = mock_post.call_args
    assert call_args.args[0] == "http://localhost:8080/v1/chat/completions"


# --- Error handling ---

@patch("bcp.simple_llm_provider.httpx.post")
def test_invoke_raises_on_http_error(mock_post, logger):
    mock_post.return_value = MagicMock(
        status_code=500,
        text="Internal Server Error",
        raise_for_status=MagicMock(side_effect=httpx.HTTPStatusError(
            "500 Internal Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500, text="Internal Server Error")
        ))
    )
    provider = SimpleLLMProvider(logger, model="test", api_key="test-key")
    with pytest.raises(httpx.HTTPStatusError):
        provider.invoke("prompt")


@patch("bcp.simple_llm_provider.httpx.post")
def test_invoke_raises_on_timeout(mock_post, logger):
    mock_post.side_effect = httpx.ReadTimeout("Request timed out")
    provider = SimpleLLMProvider(logger, model="test", api_key="test-key")
    with pytest.raises(httpx.ReadTimeout):
        provider.invoke("prompt")


@patch("bcp.simple_llm_provider.httpx.post")
def test_invoke_raises_on_connection_error(mock_post, logger):
    mock_post.side_effect = httpx.ConnectError("Connection refused")
    provider = SimpleLLMProvider(logger, model="test", api_key="test-key")
    with pytest.raises(httpx.ConnectError):
        provider.invoke("prompt")


# --- get_model() ---

def test_get_model_raises_not_implemented(logger):
    provider = SimpleLLMProvider(logger, model="test")
    with pytest.raises(NotImplementedError):
        provider.get_model()
