import logging
import json
import pytest

from bcp.prompt_handler import PromptHandler
from bcp.logger import setup_logger


class FakeProvider:
    def __init__(self, response_text):
        self.response_text = response_text

    def invoke(self, prompt: str) -> str:
        return self.response_text


@pytest.fixture
def logger():
    return setup_logger(logging.DEBUG)


def test_render_prompt(logger):
    handler = PromptHandler(logger, provider_name="openai")
    template = "Hello {{ name }}"
    rendered = handler.render_prompt(template, {"name": "World"})
    assert rendered == "Hello World"


def test_prepare_story_variables():
    story_content = "Login Feature\nAs a user I want to log in."
    vars = PromptHandler.prepare_story_variables(story_content)
    assert "story" in vars
    assert vars["story"]["key"] == "Login Feature"
    assert vars["story"]["summary"] == "Login Feature"
    assert "Login Feature" in vars["story"]["description"]
    assert "As a user" in vars["story"]["description"]


def test_prepare_story_variables_empty():
    vars = PromptHandler.prepare_story_variables("")
    assert vars["story"]["key"] == "Unnamed Story"
    assert vars["story"]["summary"] == "Unnamed Story"


def test_load_prompt_subdirectory(logger):
    """Verify that prompt files in subdirectories can be loaded."""
    handler = PromptHandler(logger, provider_name="openai")
    # This should load from prompts/thirteen/functional/business-rules.md
    content = handler.load_prompt("thirteen/functional/business-rules.md")
    assert "business" in content.lower() or "rule" in content.lower()
    assert len(content) > 100


def test_process_prompt_with_story_dict(logger, monkeypatch):
    """Test that story dict variables are rendered correctly in prompts."""
    response = '{"score": 5, "dimension": "business_rules"}'
    handler = PromptHandler(logger, provider_name="openai")
    handler.provider = FakeProvider(response)
    monkeypatch.setattr(handler, "load_prompt", lambda f: "Story: {{ story.summary }}\nDesc: {{ story.description }}")
    
    story_vars = PromptHandler.prepare_story_variables("My Story\nContent here")
    out = handler.process_prompt("any", story_vars)
    assert out["score"] == 5


def test_process_prompt_with_bindings(logger, monkeypatch):
    """Test that binding values are injected into the prompt template."""
    response = '{"score": 10, "dimension": "aggregator"}'
    handler = PromptHandler(logger, provider_name="openai")
    handler.provider = FakeProvider(response)
    monkeypatch.setattr(handler, "load_prompt", lambda f: "BR: {{ dim_business_rules }} IE: {{ dim_interface_elements }}")
    
    bindings = {"dim_business_rules": 5, "dim_interface_elements": 8}
    out = handler.process_prompt("aggregator", {}, bindings=bindings)
    assert out["score"] == 10


def test_process_prompt_codeblock_json(logger, monkeypatch):
    response = '```json\n{\n  "score": 5,\n  "dimension": "test"\n}\n```'
    handler = PromptHandler(logger, provider_name="openai")
    handler.provider = FakeProvider(response)
    monkeypatch.setattr(handler, "load_prompt", lambda f: "X")
    out = handler.process_prompt("any", {})
    assert out["score"] == 5
    assert out["dimension"] == "test"


def test_process_prompt_plain_json(logger, monkeypatch):
    response = '{\n  "score": 7,\n  "dimension": "test"\n}'
    handler = PromptHandler(logger, provider_name="openai")
    handler.provider = FakeProvider(response)
    monkeypatch.setattr(handler, "load_prompt", lambda f: "X")
    out = handler.process_prompt("any", {})
    assert out["score"] == 7


def test_process_prompt_json_array(logger, monkeypatch):
    response = '[{"Rule": "R1", "Score": 3}, {"Rule": "R2", "Score": 5}]'
    handler = PromptHandler(logger, provider_name="openai")
    handler.provider = FakeProvider(response)
    monkeypatch.setattr(handler, "load_prompt", lambda f: "X")
    out = handler.process_prompt("any", {})
    assert "items" in out
    assert len(out["items"]) == 2


def test_process_prompt_raw_text(logger, monkeypatch):
    response = "No JSON here"
    handler = PromptHandler(logger, provider_name="openai")
    handler.provider = FakeProvider(response)
    monkeypatch.setattr(handler, "load_prompt", lambda f: "X")
    out = handler.process_prompt("any", {})
    assert out["raw_response"] == "No JSON here"


def test_extract_json_variants(logger):
    handler = PromptHandler(logger, provider_name="openai")
    s1 = '```json\n{"score":1}\n```'
    assert handler._extract_json_from_response(s1) == '{"score":1}'
    s2 = '```\n{"score":2}\n```'
    assert handler._extract_json_from_response(s2) == '{"score":2}'
    s3 = "no json"
    assert handler._extract_json_from_response(s3) is None


def test_extract_balanced_json():
    # Simple object
    assert PromptHandler._extract_balanced_json('prefix {"a": 1} suffix') == '{"a": 1}'
    # Nested object
    assert PromptHandler._extract_balanced_json('{"a": {"b": 2}}') == '{"a": {"b": 2}}'
    # Array
    assert PromptHandler._extract_balanced_json('[1, 2, 3]') == '[1, 2, 3]'
    # String with braces inside
    assert PromptHandler._extract_balanced_json('{"a": "hello {world}"}') == '{"a": "hello {world}"}'
    # No JSON
    assert PromptHandler._extract_balanced_json("no json here") is None
