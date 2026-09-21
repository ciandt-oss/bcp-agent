"""
SimpleLLMProvider — Primary LLM provider using httpx directly.

Calls any OpenAI-compatible Chat Completions endpoint via httpx, bypassing the
openai SDK which has compatibility issues with local gateways (Flow, Ollama, etc.).

This is the recommended provider for all OpenAI-compatible endpoints. It works
reliably with:
- OpenAI direct (api.openai.com) — with real API key
- Flow gateway (local) — without auth header (placeholder key)
- Ollama (local) — without auth header
- vLLM, LM Studio, LiteLLM — any OpenAI-compatible endpoint

Auth header behavior:
- Real API key (e.g. sk-...) → sends Authorization: Bearer <key>
- Placeholder key ("test-key", "dummy", "none", "") → omits Authorization header

This provider inherits from LLMProvider for interface compatibility.
"""

import logging
import os
from typing import Optional

import httpx

from .llm_providers import LLMProvider


# API keys that are considered placeholders — no auth header is sent for these
PLACEHOLDER_KEYS = {"", "test-key", "dummy", "none", "none", "placeholder", "fake"}


class SimpleLLMProvider(LLMProvider):
    """
    Primary LLM provider for OpenAI-compatible endpoints.

    Uses httpx directly instead of the openai SDK, which avoids compatibility
    issues with local gateways that hang on Authorization headers with fake tokens.

    Recommended for: Flow gateway, Ollama, vLLM, LM Studio, LiteLLM, and OpenAI direct.
    """

    def __init__(self, logger: logging.Logger, model: str = "mistral-small-2503",
                 api_key: Optional[str] = None, base_url: Optional[str] = None,
                 temperature: float = 0, max_tokens: int = 4096, timeout: float = 300):
        """
        Initialize the SimpleLLMProvider.

        Args:
            logger: The logger instance
            model: Model name (e.g. "mistral-small-2503", "gpt-4o", "llama3.1:8b")
            api_key: API key for the endpoint. Placeholders ("test-key", "dummy", "")
                     will omit the Authorization header. Falls back to OPENAI_API_KEY env var.
            base_url: Endpoint base URL (e.g. "http://127.0.0.1:8788/v1").
                      Falls back to OPENAI_BASE_URL env var, then "https://api.openai.com/v1".
            temperature: Sampling temperature (default: 0 for deterministic output)
            max_tokens: Maximum tokens to generate (default: 4096)
            timeout: Request timeout in seconds (default: 300)
        """
        super().__init__(logger)
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = (
            base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        ).rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.logger.info(f"SimpleLLMProvider: model={model}, base_url={self.base_url}")

    def get_model(self):
        """Not used — SimpleLLMProvider does not use langchain models."""
        raise NotImplementedError(
            "SimpleLLMProvider does not use langchain models. Use invoke() directly."
        )

    def _should_send_auth(self) -> bool:
        """Check if the API key is real (not a placeholder)."""
        return bool(self.api_key) and self.api_key.lower() not in PLACEHOLDER_KEYS

    def invoke(self, prompt: str) -> str:
        """
        Send a prompt to the LLM and return the response text.

        Args:
            prompt: The rendered prompt to send to the LLM

        Returns:
            The LLM response as a string

        Raises:
            httpx.HTTPStatusError: On HTTP error responses (4xx, 5xx)
            httpx.ReadTimeout: On timeout
            Exception: On other errors
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        headers = {"Content-Type": "application/json"}
        if self._should_send_auth():
            headers["Authorization"] = f"Bearer {self.api_key}"

        self.logger.debug(
            f"Sending prompt to {url} (model={self.model}, prompt_len={len(prompt)}, auth={'yes' if 'Authorization' in headers else 'no'})"
        )

        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            self.logger.debug(f"LLM response received (len={len(content)})")
            return content
        except httpx.HTTPStatusError as e:
            self.logger.error(
                f"HTTP error {e.response.status_code}: {e.response.text[:200]}"
            )
            raise
        except httpx.ReadTimeout:
            self.logger.error(f"Request timed out after {self.timeout}s")
            raise
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
