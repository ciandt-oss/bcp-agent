"""
BedrockProvider — Native AWS Bedrock LLM provider.

Calls the AWS Bedrock Converse API directly via httpx, authenticating with a
bearer token from aws_bedrock_token_generator (auto-cached/refreshed) or from
the AWS_BEARER_TOKEN_BEDROCK env var.

Auth behavior:
- AWS_BEARER_TOKEN_BEDROCK env var set → uses it directly (long-term key or pre-set token)
- Not set → calls provide_token() from aws_bedrock_token_generator before each request
  (handles caching and auto-refresh of short-term tokens)

API reference:
- Endpoint: POST https://bedrock-runtime.{region}.amazonaws.com/model/{modelId}/converse
- Auth: Authorization: Bearer {token}
- Request: {"messages": [...], "inferenceConfig": {...}, "additionalModelRequestFields": {...}}
- Response: {"output": {"message": {"content": [{"text": "..."}]}}}

Reasoning model handling:
- For reasoning models (gpt-5+, gpt-6, o-series), temperature is omitted from
  inferenceConfig (not accepted when reasoning is on) and reasoning_effort="none"
  is passed via additionalModelRequestFields to disable reasoning for determinism.
  If the model doesn't support this field, Bedrock silently ignores it.
- For non-reasoning models, temperature and maxTokens are sent normally.

This provider inherits from LLMProvider for interface compatibility.
"""

import logging
import os
from typing import Optional

import httpx

from .llm_providers import LLMProvider
from .model_utils import is_reasoning_model


class BedrockProvider(LLMProvider):
    """
    Native AWS Bedrock provider using the Converse API.

    Uses httpx directly (no boto3) and authenticates via bearer token from
    aws_bedrock_token_generator or the AWS_BEARER_TOKEN_BEDROCK env var.
    """

    def __init__(self, logger: logging.Logger,
                 model_name: str = "openai.gpt-5.6-luna",
                 region: Optional[str] = None,
                 temperature: float = 0, max_tokens: int = 4096,
                 timeout: float = 300):
        """
        Initialize the BedrockProvider.

        Args:
            logger: The logger instance
            model_name: Bedrock model ID (e.g. "openai.gpt-5.6-luna")
            region: AWS region (falls back to AWS_BEDROCK_REGION env var, then "us-east-1")
            temperature: Sampling temperature (default: 0 for deterministic output)
            max_tokens: Maximum tokens to generate (default: 4096)
            timeout: Request timeout in seconds (default: 300)
        """
        super().__init__(logger)
        self.model_name = model_name
        self.region = region or os.environ.get("AWS_BEDROCK_REGION", "us-east-1")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.url = f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{model_name}/converse"
        self.logger.info(f"BedrockProvider: model={model_name}, region={self.region}")

    def _get_token(self) -> str:
        """Get a bearer token — from env var or aws_bedrock_token_generator."""
        static_token = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")
        if static_token:
            return static_token

        from aws_bedrock_token_generator import provide_token
        return provide_token()

    def get_model(self):
        """Not used — BedrockProvider does not use langchain models."""
        raise NotImplementedError(
            "BedrockProvider does not use langchain models. Use invoke() directly."
        )

    def invoke(self, prompt: str) -> str:
        """
        Send a prompt to the Bedrock Converse API and return the response text.

        Args:
            prompt: The rendered prompt to send to the LLM

        Returns:
            The LLM response as a string

        Raises:
            httpx.HTTPStatusError: On HTTP error responses (4xx, 5xx)
            httpx.ReadTimeout: On timeout
            Exception: On other errors
        """
        token = self._get_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        inference_config = {}
        if not is_reasoning_model(self.model_name):
            inference_config["temperature"] = self.temperature
        inference_config["maxTokens"] = self.max_tokens
        payload = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": inference_config,
        }

        # For reasoning models, pass reasoning_effort via additionalModelRequestFields
        # (the Converse API doesn't support reasoning_effort in inferenceConfig).
        # This attempts to disable reasoning for maximum determinism, matching the
        # behavior of other providers. If the model doesn't support it, Bedrock
        # silently ignores the field — no HTTP 400.
        if is_reasoning_model(self.model_name):
            payload["additionalModelRequestFields"] = {"reasoning_effort": "none"}

        self.logger.debug(
            f"Sending prompt to {self.url} (model={self.model_name}, "
            f"prompt_len={len(prompt)}, region={self.region})"
        )

        try:
            response = httpx.post(self.url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            content_blocks = data.get("output", {}).get("message", {}).get("content", [])
            if not content_blocks:
                raise ValueError("No content found in Bedrock response")

            text_parts = []
            for block in content_blocks:
                if "text" in block:
                    text_parts.append(block["text"])

            if not text_parts:
                raise ValueError("No text content found in Bedrock response blocks")

            content = "".join(text_parts)
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
            self.logger.error(f"Bedrock LLM call failed: {e}")
            raise
