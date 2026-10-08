"""Unit tests for model_utils — reasoning model detection and chat param building."""

import pytest
from bcp.model_utils import is_reasoning_model, build_chat_params


# --- is_reasoning_model ---

@pytest.mark.parametrize("model", [
    "gpt-5-nano",
    "gpt-5",
    "gpt-5.6",
    "gpt-6-luna",
    "gpt-6-sol",
    "gpt-6-astra",
    "openai.gpt-5.6-luna",
    "openai/gpt-6-luna",
    "o1",
    "o1-mini",
    "o3",
    "o3-mini",
    "o4",
    "o4-mini",
])
def test_is_reasoning_model_true(model):
    assert is_reasoning_model(model) is True


@pytest.mark.parametrize("model", [
    "gpt-4o",
    "gpt-4o-mini",
    "claude-sonnet-4-6",
    "anthropic.claude-sonnet-4-6",
    "llama3.1:8b",
    "Qwen/Qwen3.8-27B:novita",
    "zai-org/GLM-5.2:novita",
    "mistral-small",
])
def test_is_reasoning_model_false(model):
    assert is_reasoning_model(model) is False


# --- build_chat_params ---

def test_build_chat_params_reasoning_model():
    payload = build_chat_params(
        model="gpt-6-luna",
        temperature=0,
        max_tokens=4096,
        messages=[{"role": "user", "content": "Hello"}],
    )
    assert payload["model"] == "gpt-6-luna"
    assert payload["messages"] == [{"role": "user", "content": "Hello"}]
    assert payload["stream"] is False
    assert payload["reasoning_effort"] == "none"
    assert payload["temperature"] == 0
    assert payload["max_completion_tokens"] == 4096
    assert "max_tokens" not in payload


def test_build_chat_params_non_reasoning_model():
    payload = build_chat_params(
        model="gpt-4o",
        temperature=0,
        max_tokens=2048,
        messages=[{"role": "user", "content": "Hello"}],
    )
    assert payload["model"] == "gpt-4o"
    assert payload["temperature"] == 0
    assert payload["max_tokens"] == 2048
    assert payload["stream"] is False


def test_build_chat_params_stream_true():
    payload = build_chat_params(
        model="gpt-6-luna",
        temperature=0,
        max_tokens=4096,
        messages=[{"role": "user", "content": "Hello"}],
        stream=True,
    )
    assert payload["stream"] is True


def test_build_chat_params_claude():
    payload = build_chat_params(
        model="claude-sonnet-4-6",
        temperature=0,
        max_tokens=4096,
        messages=[{"role": "user", "content": "Hello"}],
    )
    assert payload["temperature"] == 0
    assert payload["max_tokens"] == 4096
