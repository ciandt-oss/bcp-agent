"""Unit tests for BedrockProvider."""

import logging
import pytest
from unittest.mock import patch, MagicMock

from bcp.bedrock_provider import BedrockProvider
from bcp.logger import setup_logger


@pytest.fixture
def logger():
    return setup_logger(logging.DEBUG)


def test_bedrock_provider_initialization(logger):
    provider = BedrockProvider(logger, model_name="openai.gpt-5.6-luna", region="us-west-2")
    assert provider.model_name == "openai.gpt-5.6-luna"
    assert provider.region == "us-west-2"
    assert "bedrock-runtime.us-west-2.amazonaws.com" in provider.url
    assert "/model/openai.gpt-5.6-luna/converse" in provider.url


def test_bedrock_provider_default_region(logger, monkeypatch):
    monkeypatch.delenv("AWS_BEDROCK_REGION", raising=False)
    provider = BedrockProvider(logger)
    assert provider.region == "us-east-1"


def test_bedrock_provider_region_from_env(logger, monkeypatch):
    monkeypatch.setenv("AWS_BEDROCK_REGION", "eu-central-1")
    provider = BedrockProvider(logger)
    assert provider.region == "eu-central-1"


def test_bedrock_provider_get_model_raises(logger):
    provider = BedrockProvider(logger)
    with pytest.raises(NotImplementedError):
        provider.get_model()


def test_bedrock_provider_token_from_env(logger, monkeypatch):
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "my-static-token")
    provider = BedrockProvider(logger)
    assert provider._get_token() == "my-static-token"


def test_bedrock_provider_token_from_generator(logger, monkeypatch):
    monkeypatch.delenv("AWS_BEARER_TOKEN_BEDROCK", raising=False)
    with patch("aws_bedrock_token_generator.provide_token", return_value="generated-token"):
        provider = BedrockProvider(logger)
        assert provider._get_token() == "generated-token"


@patch("bcp.bedrock_provider.httpx.post")
def test_bedrock_invoke_calls_correct_url(mock_post, logger, monkeypatch):
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "output": {"message": {"content": [{"text": "Hello from Bedrock"}]}}
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = BedrockProvider(logger, model_name="openai.gpt-5.6-luna", region="us-east-1")
    provider.invoke("Hello")

    call_args = mock_post.call_args
    url = call_args[0][0]
    assert "bedrock-runtime.us-east-1.amazonaws.com" in url
    assert "/model/openai.gpt-5.6-luna/converse" in url


@patch("bcp.bedrock_provider.httpx.post")
def test_bedrock_invoke_uses_bearer_token(mock_post, logger, monkeypatch):
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "test-bearer-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "output": {"message": {"content": [{"text": "Response"}]}}
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = BedrockProvider(logger)
    provider.invoke("Hello")

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer test-bearer-token"


@patch("bcp.bedrock_provider.httpx.post")
def test_bedrock_invoke_converse_request_format(mock_post, logger, monkeypatch):
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "output": {"message": {"content": [{"text": "Response"}]}}
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = BedrockProvider(logger, model_name="anthropic.claude-sonnet-4-6", temperature=0, max_tokens=2048)
    provider.invoke("Tell me a joke")

    call_args = mock_post.call_args
    payload = call_args[1]["json"]
    assert payload["messages"] == [{"role": "user", "content": [{"text": "Tell me a joke"}]}]
    assert payload["inferenceConfig"]["temperature"] == 0
    assert payload["inferenceConfig"]["maxTokens"] == 2048


@patch("bcp.bedrock_provider.httpx.post")
def test_bedrock_invoke_parses_response(mock_post, logger, monkeypatch):
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "output": {"message": {"content": [{"text": "The answer is 42"}]}}
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = BedrockProvider(logger)
    result = provider.invoke("What is the answer?")
    assert result == "The answer is 42"


@patch("bcp.bedrock_provider.httpx.post")
def test_bedrock_invoke_parses_multiple_content_blocks(mock_post, logger, monkeypatch):
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "output": {"message": {"content": [
            {"text": "Part 1 "},
            {"text": "Part 2"},
        ]}}
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = BedrockProvider(logger)
    result = provider.invoke("Hello")
    assert result == "Part 1 Part 2"


@patch("bcp.bedrock_provider.httpx.post")
def test_bedrock_invoke_raises_on_empty_content(mock_post, logger, monkeypatch):
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "output": {"message": {"content": []}}
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = BedrockProvider(logger)
    with pytest.raises(ValueError, match="No content found"):
        provider.invoke("Hello")


@patch("bcp.bedrock_provider.httpx.post")
def test_bedrock_invoke_raises_on_missing_content_key(mock_post, logger, monkeypatch):
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {"output": {"message": {}}}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = BedrockProvider(logger)
    with pytest.raises(ValueError, match="No content found"):
        provider.invoke("Hello")


# --- Reasoning model temperature handling ---

@patch("bcp.bedrock_provider.httpx.post")
def test_bedrock_invoke_omits_temperature_for_gpt6(mock_post, logger, monkeypatch):
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "output": {"message": {"content": [{"text": "Response"}]}}
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = BedrockProvider(logger, model_name="openai.gpt-5.6-luna")
    provider.invoke("Hello")

    payload = mock_post.call_args[1]["json"]
    assert "temperature" not in payload["inferenceConfig"]
    assert payload["inferenceConfig"]["maxTokens"] == 4096


@patch("bcp.bedrock_provider.httpx.post")
def test_bedrock_invoke_includes_temperature_for_claude(mock_post, logger, monkeypatch):
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "output": {"message": {"content": [{"text": "Response"}]}}
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    provider = BedrockProvider(logger, model_name="anthropic.claude-sonnet-4-6")
    provider.invoke("Hello")

    payload = mock_post.call_args[1]["json"]
    assert payload["inferenceConfig"]["temperature"] == 0
    assert payload["inferenceConfig"]["maxTokens"] == 4096
