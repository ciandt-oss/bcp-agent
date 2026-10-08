import logging
import pytest
from unittest.mock import patch, MagicMock

from bcp.llm_providers import (
    get_provider, OpenAIProvider, ClaudeProvider,
    FlowLiteLLMProvider,
)
from bcp.llm_providers import FlowLiteLLMChatModel
from bcp.simple_llm_provider import SimpleLLMProvider
from bcp.logger import setup_logger
from langchain_core.messages import HumanMessage

@pytest.fixture
def logger():
    return setup_logger(logging.DEBUG)


def test_get_provider_basic(logger):
    p = get_provider("openai", logger)
    assert isinstance(p, SimpleLLMProvider)
    p = get_provider("claude", logger)
    assert isinstance(p, ClaudeProvider)


def test_get_provider_flow_mapping(logger, monkeypatch):
    constructed = {"flow_openai": False}

    class DummyFlowProvider(FlowLiteLLMProvider):
        def __init__(self, *a, **kw):
            constructed["flow_openai"] = True

    monkeypatch.setattr("bcp.llm_providers.FlowLiteLLMProvider", DummyFlowProvider)

    p = get_provider("flow-openai", logger)
    assert constructed["flow_openai"] is True


def test_flow_litellm_requires_jwt_token(logger, monkeypatch):
    monkeypatch.delenv("FLOW_LITELLM_TOKEN_JWT", raising=False)
    with pytest.raises(RuntimeError, match="FLOW_LITELLM_TOKEN_JWT"):
        FlowLiteLLMProvider(logger)


def test_flow_litellm_uses_jwt_token(logger, monkeypatch):
    monkeypatch.setenv("FLOW_LITELLM_TOKEN_JWT", "my-jwt-token")
    monkeypatch.setenv("FLOW_LLM_LITE_HOST", "https://example.com/flow-litellm")
    provider = FlowLiteLLMProvider(logger)
    assert provider.api_key == "my-jwt-token"


# --- FlowLiteLLMChatModel tests ---

def test_flow_litellm_chat_model_llm_type():
    model = FlowLiteLLMChatModel(
        base_url="https://example.com/flow-litellm",
        flow_tenant="test-tenant",
        flow_agent="test-agent",
        model_name="gpt-6-luna",
        temperature=0,
        max_tokens=4096,
        api_key="test-token",
    )
    assert model._llm_type() == "flow-litellm"


@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_url_has_no_openai_prefix(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "test response"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    model = FlowLiteLLMChatModel(
        base_url="https://example.com/flow-litellm",
        flow_tenant="test-tenant",
        flow_agent="test-agent",
        model_name="gpt-6-luna",
        temperature=0,
        max_tokens=4096,
        api_key="test-token",
    )
    model._generate([HumanMessage(content="hello")])

    call_args = mock_post.call_args
    url = call_args[0][0]
    assert "/v1/chat/completions" in url
    assert "/v1/openai" not in url


@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_uses_authorization_bearer(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "test response"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    model = FlowLiteLLMChatModel(
        base_url="https://example.com/flow-litellm",
        flow_tenant="test-tenant",
        flow_agent="test-agent",
        model_name="gpt-6-luna",
        temperature=0,
        max_tokens=4096,
        api_key="my-jwt-token",
    )
    model._generate([HumanMessage(content="hello")])

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]
    assert headers.get("Authorization") == "Bearer my-jwt-token"
    assert "FlowToken" not in headers


@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_includes_flow_channel(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "test response"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    model = FlowLiteLLMChatModel(
        base_url="https://example.com/flow-litellm",
        flow_tenant="test-tenant",
        flow_agent="test-agent",
        model_name="gpt-6-luna",
        temperature=0,
        max_tokens=4096,
        api_key="test-token",
    )
    model._generate([HumanMessage(content="hello")])

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]
    assert headers.get("FlowChannel") == "bcp"


@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_payload_includes_model(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "test response"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    model = FlowLiteLLMChatModel(
        base_url="https://example.com/flow-litellm",
        flow_tenant="test-tenant",
        flow_agent="test-agent",
        model_name="gpt-6-luna",
        temperature=0,
        max_tokens=4096,
        api_key="test-token",
    )
    model._generate([HumanMessage(content="hello")])

    call_args = mock_post.call_args
    payload = call_args[1]["json"]
    assert payload["model"] == "gpt-6-luna"


@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_payload_omits_temperature_for_gpt5(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "test response"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    model = FlowLiteLLMChatModel(
        base_url="https://example.com/flow-litellm",
        flow_tenant="test-tenant",
        flow_agent="test-agent",
        model_name="gpt-5-nano",
        temperature=0,
        max_tokens=4096,
        api_key="test-token",
    )
    model._generate([HumanMessage(content="hello")])

    call_args = mock_post.call_args
    payload = call_args[1]["json"]
    assert payload["reasoning_effort"] == "none"
    assert payload["temperature"] == 0
    assert payload["max_completion_tokens"] == 4096
    assert "max_tokens" not in payload
    assert payload["model"] == "gpt-5-nano"


@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_payload_includes_temperature_for_non_reasoning(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "test response"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    model = FlowLiteLLMChatModel(
        base_url="https://example.com/flow-litellm",
        flow_tenant="test-tenant",
        flow_agent="test-agent",
        model_name="gpt-4o",
        temperature=0,
        max_tokens=4096,
        api_key="test-token",
    )
    model._generate([HumanMessage(content="hello")])

    call_args = mock_post.call_args
    payload = call_args[1]["json"]
    assert payload["temperature"] == 0
    assert payload["max_tokens"] == 4096


@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_payload_omits_temperature_for_gpt6(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "test response"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    model = FlowLiteLLMChatModel(
        base_url="https://example.com/flow-litellm",
        flow_tenant="test-tenant",
        flow_agent="test-agent",
        model_name="gpt-6-luna",
        temperature=0,
        max_tokens=4096,
        api_key="test-token",
    )
    model._generate([HumanMessage(content="hello")])

    call_args = mock_post.call_args
    payload = call_args[1]["json"]
    assert payload["reasoning_effort"] == "none"
    assert payload["temperature"] == 0
    assert payload["max_completion_tokens"] == 4096
    assert "max_tokens" not in payload
    assert payload["model"] == "gpt-6-luna"


@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_includes_flow_headers(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "test response"}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    model = FlowLiteLLMChatModel(
        base_url="https://example.com/flow-litellm",
        flow_tenant="my-tenant",
        flow_agent="my-agent",
        model_name="gpt-6-luna",
        temperature=0,
        max_tokens=4096,
        api_key="test-token",
    )
    model._generate([HumanMessage(content="hello")])

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]
    assert headers["FlowTenant"] == "my-tenant"
    assert headers["FlowAgent"] == "my-agent"


# --- 400 fallback for reasoning models that don't support reasoning_effort="none" ---

@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_400_fallback_removes_reasoning_effort_and_temperature(mock_post):
    """When a reasoning model rejects reasoning_effort='none' with HTTP 400, the retry
    should remove reasoning_effort, temperature, and revert max_completion_tokens to max_tokens."""
    import copy

    # Capture payloads at call time (the code mutates the dict in-place for retry)
    captured_payloads = []

    def capture_and_respond(*args, **kwargs):
        captured_payloads.append(copy.deepcopy(kwargs.get("json", {})))
        call_index = len(captured_payloads) - 1
        if call_index == 0:
            bad_response = MagicMock()
            bad_response.status_code = 400
            bad_response.text = '{"error": "reasoning_effort none not supported"}'
            return bad_response
        else:
            good_response = MagicMock()
            good_response.status_code = 200
            good_response.json.return_value = {
                "choices": [{"message": {"content": "test response"}}]
            }
            good_response.raise_for_status = MagicMock()
            return good_response

    mock_post.side_effect = capture_and_respond

    model = FlowLiteLLMChatModel(
        base_url="https://example.com/flow-litellm",
        flow_tenant="test-tenant",
        flow_agent="test-agent",
        model_name="gpt-6-astra",
        temperature=0,
        max_tokens=4096,
        api_key="test-token",
    )
    model._generate([HumanMessage(content="hello")])

    # Verify two calls were made
    assert len(captured_payloads) == 2

    # First call should have reasoning_effort, temperature, max_completion_tokens
    first_payload = captured_payloads[0]
    assert first_payload["reasoning_effort"] == "none"
    assert first_payload["temperature"] == 0
    assert first_payload["max_completion_tokens"] == 4096

    # Second call (retry) should NOT have reasoning_effort or temperature,
    # and max_completion_tokens should be reverted to max_tokens
    second_payload = captured_payloads[1]
    assert "reasoning_effort" not in second_payload
    assert "temperature" not in second_payload
    assert "max_completion_tokens" not in second_payload
    assert second_payload["max_tokens"] == 4096
