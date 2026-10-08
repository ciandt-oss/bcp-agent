"""
Model utility functions for model-aware parameter handling.

Reasoning models (GPT-5+, o-series, nano) do not accept the `temperature` parameter
when reasoning is enabled (default: medium). Sending it causes the API to drop or
reject the parameter. This module provides utilities to detect reasoning models
and build request payloads that respect these constraints.

For Anthropic Claude models, determinism is controlled via:
- `temperature=0` — no sampling randomness
- `thinking={"type": "disabled"}` — disables adaptive thinking (always-on by default)
- `reasoning_effort="low"` — minimizes reasoning variation
These are applied by ClaudeProvider and can be overridden via env vars:
- `ANTHROPIC_THINKING` (default: '{"type": "disabled"}')
- `ANTHROPIC_REASONING_EFFORT` (default: 'low')

Reference: https://docs.litellm.ai/blog/gpt_6_sol_luna#notes
"""

# Model name substrings that indicate a reasoning model
# These models have reasoning enabled by default and do not accept `temperature`
# unless `reasoning_effort="none"` is explicitly set.
_REASONING_INDICATORS = ["gpt-5", "gpt-6", "o1", "o3", "o4", "nano"]


def is_reasoning_model(model_name: str) -> bool:
    """Check if a model is a reasoning model that doesn't accept temperature by default.

    Reasoning models include:
    - GPT-5 family (gpt-5, gpt-5-nano, gpt-5.6, etc.)
    - GPT-6 family (gpt-6-luna, gpt-6-sol, gpt-6-astra, etc.)
    - o-series (o1, o1-mini, o3, o3-mini, o4, o4-mini, etc.)
    - nano variants (any model with "nano" in the name)

    Args:
        model_name: The model name/identifier to check

    Returns:
        True if the model is a reasoning model, False otherwise
    """
    model_lower = model_name.lower()
    return any(indicator in model_lower for indicator in _REASONING_INDICATORS)


def build_chat_params(model: str, temperature: float, max_tokens: int,
                      messages: list, stream: bool = False) -> dict:
    """Build a Chat Completions request payload with model-aware parameter handling.

    For reasoning models (gpt-5+, o-series, nano):
      - Sends `reasoning_effort="none"` to disable reasoning for maximum determinism
      - Sends `temperature` alongside it (allowed when reasoning is off)
      - Uses `max_completion_tokens` instead of `max_tokens` (required by reasoning models)

    For non-reasoning models:
      - Includes `temperature` and `max_tokens` as usual

    Reference: https://docs.litellm.ai/blog/gpt_6_sol_luna#notes
    "temperature only applies when reasoning is off, so send reasoning_effort='none'
    alongside it. Without it LiteLLM drops or refuses the parameter."

    Args:
        model: Model name/identifier
        temperature: Sampling temperature (sent with reasoning_effort="none" for reasoning models)
        max_tokens: Maximum tokens to generate (sent as max_completion_tokens for reasoning models)
        messages: List of message dicts for the chat completions API
        stream: Whether to stream the response

    Returns:
        A dict ready to be sent as the JSON body of a POST /chat/completions request
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }
    if is_reasoning_model(model):
        payload["reasoning_effort"] = "none"
        payload["temperature"] = temperature
        payload["max_completion_tokens"] = max_tokens
    else:
        payload["temperature"] = temperature
        payload["max_tokens"] = max_tokens
    return payload
