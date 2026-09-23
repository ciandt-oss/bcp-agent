"""
Prompt Handler for BCP Calculator

This module handles loading and processing prompts for the BCP Calculator.
Supports the 13-dimensions pipeline with subdirectory-based prompt loading,
story dict variables, pipeline bindings, and robust JSON extraction.
"""

import os
import json
import logging
import re
from typing import Dict, Any, Optional

from jinja2 import Template

from .llm_providers import LLMProvider, get_provider


class PromptHandler:
    """
    Handler for loading and processing prompts.
    """

    def __init__(self, logger: logging.Logger, provider_name: str = "openai"):
        """
        Initialize the prompt handler.

        Args:
            logger: The logger instance
            provider_name: The name of the LLM provider to use ('openai' or 'claude')
        """
        self.logger = logger
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.prompts_dir = os.path.join(current_dir, "prompts")
        self.provider = get_provider(provider_name, logger)

    def load_prompt(self, prompt_file: str) -> str:
        """
        Load a prompt template from file.

        Supports relative paths with subdirectories (e.g. 'thirteen/functional/business-rules.md').

        Args:
            prompt_file: The relative path of the prompt template within the prompts directory

        Returns:
            The prompt template content
        """
        prompt_path = os.path.join(self.prompts_dir, prompt_file)
        self.logger.debug(f"Loading prompt from {prompt_path}")

        try:
            with open(prompt_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Error loading prompt {prompt_file}: {str(e)}")
            raise

    def render_prompt(self, prompt_template: str, variables: Dict[str, Any]) -> str:
        """
        Render a prompt template with variables using Jinja2.

        Args:
            prompt_template: The prompt template content
            variables: The variables to render in the template

        Returns:
            The rendered prompt
        """
        self.logger.debug(f"Rendering prompt with variables: {list(variables.keys())}")

        try:
            template = Template(prompt_template)
            return template.render(**variables)
        except Exception as e:
            self.logger.error(f"Error rendering prompt: {str(e)}")
            raise

    @staticmethod
    def prepare_story_variables(story_content: str) -> Dict[str, Any]:
        """
        Parse raw story content into the dict structure expected by 13-dimensions prompts.

        The prompts use {{story.key}}, {{story.summary}}, and {{story.description}}.
        The first non-empty line is used as both key and summary; the full content
        (including the first line) is used as description.

        Args:
            story_content: Raw user story text

        Returns:
            A dict with 'story' key containing sub-keys: key, summary, description
        """
        lines = story_content.strip().split("\n")
        first_line = lines[0].strip() if lines and lines[0].strip() else "Unnamed Story"

        return {
            "story": {
                "key": first_line,
                "summary": first_line,
                "description": story_content.strip(),
            }
        }

    def process_prompt(
        self,
        prompt_file: str,
        variables: Dict[str, Any],
        bindings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a prompt with the LLM.

        Args:
            prompt_file: The relative path of the prompt template
            variables: The variables to render in the template (including 'story' dict)
            bindings: Optional pipeline binding values to inject (e.g. dim_business_rules, functional_scoring)

        Returns:
            The parsed response from the LLM as a dict
        """
        self.logger.info(f"Processing prompt: {prompt_file}")

        prompt_template = self.load_prompt(prompt_file)

        render_vars = dict(variables)
        if bindings:
            render_vars.update(bindings)

        rendered_prompt = self.render_prompt(prompt_template, render_vars)

        response = self.provider.invoke(rendered_prompt)

        return self._parse_response(response)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response into a Python dict.

        Tries multiple strategies: direct JSON parse, markdown code blocks,
        and regex extraction for JSON objects/arrays.

        Args:
            response: The raw response string from the LLM

        Returns:
            Parsed JSON as a dict, or {"raw_response": response} on failure
        """
        if not response or not response.strip():
            self.logger.warning("Empty response from LLM")
            return {"raw_response": ""}

        stripped = response.strip()

        # Strategy 1: direct JSON parse
        try:
            result = json.loads(stripped)
            if isinstance(result, (dict, list)):
                return result if isinstance(result, dict) else {"items": result}
        except json.JSONDecodeError:
            pass

        # Strategy 2: extract from ```json code blocks
        json_content = self._extract_json_from_response(response)
        if json_content:
            try:
                result = json.loads(json_content)
                if isinstance(result, (dict, list)):
                    return result if isinstance(result, dict) else {"items": result}
            except json.JSONDecodeError:
                pass

        # Strategy 3: find largest balanced JSON object or array
        json_str = self._extract_balanced_json(stripped)
        if json_str:
            try:
                result = json.loads(json_str)
                if isinstance(result, (dict, list)):
                    return result if isinstance(result, dict) else {"items": result}
            except json.JSONDecodeError:
                pass

        self.logger.warning("Response is not valid JSON, returning raw text")
        return {"raw_response": response}

    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """
        Extract JSON content from markdown code blocks.

        Args:
            response: The raw response from the LLM

        Returns:
            The extracted JSON string or None if no JSON found
        """
        # ```json ... ```
        match = re.search(r"```json\s*\n(.*?)\n```", response, re.DOTALL)
        if match:
            return match.group(1).strip()

        # ``` ... ``` containing JSON
        match = re.search(r"```\s*\n(\{.*?\}|\[.*?\])\s*\n```", response, re.DOTALL)
        if match:
            return match.group(1).strip()

        return None

    @staticmethod
    def _extract_balanced_json(text: str) -> Optional[str]:
        """
        Find the first balanced JSON object or array in a string.

        Scans for '{' or '[' and tracks bracket depth to find the matching close.

        Args:
            text: The text to search

        Returns:
            The extracted JSON string or None
        """
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start_idx = text.find(start_char)
            if start_idx == -1:
                continue

            depth = 0
            in_string = False
            escape_next = False

            for i in range(start_idx, len(text)):
                ch = text[i]

                if escape_next:
                    escape_next = False
                    continue

                if ch == "\\":
                    escape_next = True
                    continue

                if ch == '"':
                    in_string = not in_string
                    continue

                if in_string:
                    continue

                if ch == start_char:
                    depth += 1
                elif ch == end_char:
                    depth -= 1
                    if depth == 0:
                        return text[start_idx : i + 1]

        return None
