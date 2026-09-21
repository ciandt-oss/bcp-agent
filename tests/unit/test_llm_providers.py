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
    # Avoid constructing real Flow provider by intercepting constructor
    constructed = {"flow_openai": False}

    class DummyFlowProvider(FlowLiteLLMProvider):
        def __init__(self, *a, **kw):
            constructed["flow_openai"] = True
            # Do not call super to avoid token fetch

    monkeypatch.setattr("bcp.llm_providers.FlowLiteLLMProvider", DummyFlowProvider)

    p = get_provider("flow-openai", logger)
    assert constructed["flow_openai"] is True


# --- FlowLiteLLMChatModel tests ---

def test_flow_litellm_chat_model_llm_type():
    """FlowLiteLLMChatModel returns correct llm_type."""
    model = FlowLiteLLMChatModel(
        base_url="https://example.com/flow-litellm",
        flow_tenant="test-tenant",
        flow_agent="test-agent",
        model_name="mistral-small-2503",
        temperature=0,
        max_tokens=4096,
        api_key="test-token",
    )
    assert model._llm_type() == "flow-litellm"


@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_url_has_no_openai_prefix(mock_post):
    """FlowLiteLLMChatModel calls /v1/chat/completions directly."""
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
        model_name="mistral-small-2503",
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
def test_flow_litellm_uses_flow_token_header(mock_post):
    """FlowLiteLLMChatModel sends FlowToken header, not Authorization: Bearer."""
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
        model_name="mistral-small-2503",
        temperature=0,
        max_tokens=4096,
        api_key="my-token",
    )
    model._generate([HumanMessage(content="hello")])

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]
    assert headers.get("FlowToken") == "my-token"
    assert "Authorization" not in headers


@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_payload_omits_temperature_for_gpt5(mock_post):
    """FlowLiteLLMChatModel omits temperature/max_tokens for gpt-5 models."""
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
    assert "temperature" not in payload
    assert "max_tokens" not in payload


@patch("bcp.llm_providers.requests.post")
def test_flow_litellm_payload_includes_temperature_for_non_gpt5(mock_post):
    """FlowLiteLLMChatModel includes temperature/max_tokens for non-gpt-5 models."""
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
        model_name="mistral-small-2503",
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
def test_flow_litellm_includes_flow_headers(mock_post):
    """FlowLiteLLMChatModel sends FlowTenant and FlowAgent headers."""
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
        model_name="mistral-small-2503",
        temperature=0,
        max_tokens=4096,
        api_key="test-token",
    )
    model._generate([HumanMessage(content="hello")])

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]
    assert headers["FlowTenant"] == "my-tenant"
    assert headers["FlowAgent"] == "my-agent"
