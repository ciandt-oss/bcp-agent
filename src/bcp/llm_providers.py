"""
LLM Providers for BCP Calculator

This module provides a unified interface for different LLM providers.

Recommended model: mistral-small-2503 with temperature=0. This combination was
tested with the 13-dimensions pipeline and produces the lowest Coefficient of
Variation (CV) across repeated executions. All provider defaults use this model
and temperature unless overridden via environment variables.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List, Iterator

from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda
from pydantic import Field, model_validator
import requests


class LLMProvider(ABC):
    """Base abstract class for LLM providers."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize the LLM provider.
        
        Args:
            logger: The logger instance
        """
        self.logger = logger
    
    @abstractmethod
    def get_model(self) -> BaseLanguageModel:
        """
        Get the LLM model for this provider.
        
        Returns:
            The LLM model
        """
        pass
    
    def invoke(self, prompt: str) -> str:
        """
        Invoke the LLM with a prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM response as a string
        """
        self.logger.debug("Sending prompt to LLM")
        chain = self.get_model() | StrOutputParser()
        response = chain.invoke(prompt)
        self.logger.debug("Received response from LLM")
        return response


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, logger: logging.Logger, model_name: str = "mistral-small-2503", temperature: float = 0):
        """
        Initialize the OpenAI provider.

        Args:
            logger: The logger instance
            model_name: The name of the OpenAI model to use
            temperature: The temperature parameter for the model
        """
        super().__init__(logger)
        self.model_name = model_name
        self.temperature = temperature
        self.base_url = os.environ.get("OPENAI_BASE_URL")
        self.logger.info(f"Initialized OpenAI provider with model {model_name}")

    def get_model(self) -> BaseLanguageModel:
        """
        Get the OpenAI model.

        Returns:
            The OpenAI model
        """
        kwargs = {"model": self.model_name, "temperature": self.temperature}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return ChatOpenAI(**kwargs)


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider implementation."""

    def __init__(self, logger: logging.Logger, model_name: str = "mistral-small-2503", temperature: float = 0):
        """
        Initialize the Claude provider.

        Args:
            logger: The logger instance
            model_name: The name of the Claude model to use
            temperature: The temperature parameter for the model
        """
        super().__init__(logger)
        self.model_name = model_name
        self.temperature = temperature
        self.base_url = os.environ.get("ANTHROPIC_BASE_URL")
        self.logger.info(f"Initialized Claude provider with model {model_name}")

    def get_model(self) -> BaseLanguageModel:
        """
        Get the Claude model.

        Returns:
            The Claude model
        """
        kwargs = {"model": self.model_name, "temperature": self.temperature}
        if self.base_url:
            kwargs["anthropic_api_url"] = self.base_url
        return ChatAnthropic(**kwargs)


class FlowLiteLLMChatModel(BaseChatModel):
    """Custom implementation for Flow's LiteLLM Proxy Chat Completions API.

    Inherits directly from BaseChatModel and targets the FlowLiteLLM proxy
    instead of the legacy AI Orchestrator.

    Key characteristics:
    - URL: {base_url}/v1/chat/completions (calls /v1/chat/completions directly)
    - Auth header: FlowToken (not Authorization: Bearer)
    - Payload: temperature/max_tokens omitted for gpt-5/nano reasoning models
    - Auth: Azure AD B2C OAuth2 client_credentials grant (NOT auth-engine-api)
    """

    base_url: str
    flow_tenant: Optional[str]
    flow_agent: Optional[str]
    model_name: str
    temperature: float
    max_tokens: int
    api_key: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    @model_validator(mode='before')
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that the environment is properly set up for LiteLLM."""
        values["model_name"] = values.get("model_name") or "mistral-small-2503"
        values["temperature"] = values.get("temperature") or 0.0
        values["max_tokens"] = values.get("max_tokens") or 4096
        values["base_url"] = values.get("base_url") or "https://flow.ciandt.com/flow-litellm"
        return values

    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "flow-litellm"

    def _convert_messages_to_flow_format(self, messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        """Convert LangChain messages to Flow API format."""
        flow_messages = []
        for message in messages:
            if message.type == "human":
                flow_messages.append({"role": "user", "content": message.content})
            elif message.type == "ai":
                flow_messages.append({"role": "assistant", "content": message.content})
            elif message.type == "system":
                flow_messages.append({"role": "system", "content": message.content})
            else:
                flow_messages.append({"role": "user", "content": str(message.content)})
        return flow_messages

    def _generate(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any
    ) -> ChatResult:
        """Generate completion from FlowLiteLLM Proxy API."""
        flow_messages = self._convert_messages_to_flow_format(messages)

        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        flow_tenant = self.flow_tenant
        flow_agent = self.flow_agent
        api_key = self.api_key
        base_url = self.base_url
        max_tokens = self.max_tokens
        temperature = self.temperature
        model_name = self.model_name

        if flow_tenant:
            headers["FlowTenant"] = flow_tenant
        if flow_agent:
            headers["FlowAgent"] = flow_agent
        headers["FlowChannel"] = "bcp"
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        url = f"{base_url}/v1/chat/completions"

        model_lower = model_name.lower()
        if "gpt-5" in model_lower or "nano" in model_lower:
            payload = {
                "model": model_name,
                "messages": flow_messages,
            }
        else:
            payload = {
                "model": model_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": flow_messages,
            }

        if stop:
            payload["stop"] = stop

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if "choices" in data and len(data["choices"]) > 0:
                message_content = data["choices"][0]["message"]["content"]
                chat_generation = ChatGeneration(message=AIMessage(content=message_content))
                return ChatResult(generations=[chat_generation])
            else:
                raise ValueError("No message content found in response")
        except Exception as e:
            raise RuntimeError(f"Error calling FlowLiteLLM API: {str(e)}")

    def _stream(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any
    ) -> Iterator[Dict[str, Any]]:
        """Stream completion from FlowLiteLLM API (not implemented)."""
        raise NotImplementedError("Streaming not implemented for FlowLiteLLMChatModel")


class FlowLiteLLMProvider(LLMProvider):
    """Flow LiteLLM proxy provider implementation.

    Uses the FlowLiteLLM proxy with a JWT token sent as Authorization: Bearer header.
    The token is provided via FLOW_LITELLM_TOKEN_JWT env var.
    """

    def __init__(self,
                 logger: logging.Logger,
                 model_name: str = "mistral-small-2503",
                 temperature: float = 0,
                 max_tokens: int = 4096):
        """
        Initialize the Flow LiteLLM provider.

        Args:
            logger: The logger instance
            model_name: The name of the model to use
            temperature: The temperature parameter for the model
            max_tokens: Maximum tokens to generate
        """
        super().__init__(logger)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = os.environ.get("FLOW_LLM_LITE_HOST")
        self.flow_tenant = os.environ.get("FLOW_TENANT", "flowteam")
        self.flow_agent = os.environ.get("FLOW_AGENT", "bcp-opensource")
        self.api_key = os.environ.get("FLOW_LITELLM_TOKEN_JWT", "")
        self.logger.info(f"Initialized Flow LiteLLM provider with model {model_name}")

        if not self.api_key:
            raise RuntimeError(
                "FLOW_LITELLM_TOKEN_JWT env var not set. "
                "Provide the JWT token for the Flow LiteLLM proxy."
            )

    def get_model(self) -> BaseLanguageModel:
        """
        Get the Flow LiteLLM model.

        Returns:
            The Flow LiteLLM model
        """
        return FlowLiteLLMChatModel(
            base_url=self.base_url,
            model_name=self.model_name,
            flow_tenant=self.flow_tenant,
            flow_agent=self.flow_agent,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.api_key,
        )


def get_provider(provider_name: str, logger: logging.Logger) -> LLMProvider:
    """
    Get the LLM provider based on the provider name.

    The 'openai' provider now uses SimpleLLMProvider (httpx-based) as the default,
    which works reliably with both OpenAI direct and local gateways (Flow, Ollama, etc.).
    The langchain-based OpenAIProvider is still available but not the default.

    Args:
        provider_name: The name of the provider ('openai', 'claude', 'flow-openai', 'flow-bedrock')
        logger: The logger instance

    Returns:
        The LLM provider

    Raises:
        ValueError: If the provider name is not supported
    """
    provider_name = provider_name.lower()

    if provider_name == "openai":
        from .simple_llm_provider import SimpleLLMProvider
        model_name = os.environ.get("OPENAI_MODEL_NAME", "mistral-small-2503")
        return SimpleLLMProvider(logger, model=model_name)
    elif provider_name == "claude":
        model_name = os.environ.get("ANTHROPIC_MODEL_NAME", "mistral-small-2503")
        return ClaudeProvider(logger, model_name=model_name)
    elif provider_name == "flow-openai":
        model_name = os.environ.get("FLOW_MODEL_NAME", "mistral-small-2503")
        max_tokens = int(os.environ.get("FLOW_MAX_TOKENS", "4096"))
        return FlowLiteLLMProvider(logger, model_name=model_name, max_tokens=max_tokens)
    elif provider_name == "flow-bedrock":
        model_name = os.environ.get("FLOW_BEDROCK_MODEL_NAME", "mistral-small-2503")
        max_tokens = int(os.environ.get("FLOW_BEDROCK_MAX_TOKENS", "1000"))
        temperature = float(os.environ.get("FLOW_BEDROCK_TEMPERATURE", "0"))
        return FlowLiteLLMProvider(logger, model_name=model_name, max_tokens=max_tokens)
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")
