import logging
import json
import pytest

from bcp.bcp_calculator import BCPCalculator, FUNCTIONAL_DIMENSIONS, NFR_CELL, AGGREGATOR_FORMULA
from bcp.logger import setup_logger


class FakePromptHandler:
    """Mock PromptHandler that returns canned responses keyed by prompt file path."""

    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def process_prompt(self, prompt_file, variables, bindings=None):
        self.calls.append({"prompt_file": prompt_file, "variables": variables, "bindings": bindings})
        return self._responses.get(prompt_file, {})


@pytest.fixture
def logger():
    return setup_logger(logging.DEBUG)


def _build_wave1_responses():
    """Return canned responses for all Wave 1 cells (10 functional + NFR)."""
    responses = {}
    for d in FUNCTIONAL_DIMENSIONS:
        responses[f"thirteen/functional/{d['prompt'].split('/')[-1]}"] = {
            "score": 5,
            "dimension": d["name"],
            "summary": f"Mocked {d['display']}",
        }
    responses["thirteen/nfr-scoring.md"] = {
        "score": 3,
        "dimension": "nfr_scoring",
        "dimension_quality_attributes": 1,
        "dimension_security_compliance": 1,
        "dimension_user_experience_accessibility": 1,
        "summary": "Mocked NFR",
    }
    return responses


def test_bcp_13d_happy_path(logger):
    """Test that the 13-dimensions pipeline produces correct total BCP."""
    responses = _build_wave1_responses()

    # Override specific cells with known values for predictable math
    responses["thirteen/functional/business-rules.md"] = {
        "summary": "2 rules found",
        "items": ["Rule 1 — Score: 3", "Rule 2 — Score: 5"],
        "scores_extracted": [3, 5],
    }
    responses["thirteen/functional/interface-elements.md"] = {
        "summary": "5 static, 5 dynamic",
        "context": "new",
        "static_elements": ["a", "b", "c", "d", "e"],
        "dynamic_elements": ["x", "y", "z", "w", "v"],
        "static_weight": 3,
        "dynamic_weight": 8,
    }
    responses["thirteen/functional/solution-variabilities.md"] = {
        "score": 3,
        "dimension_solution_variabilities": 3,
        "classification": "M",
    }
    responses["thirteen/functional/domain-entities.md"] = {
        "score": 2,
        "dimension_domain_entities": 2,
    }
    responses["thirteen/functional/new-domain-entities.md"] = {
        "score": 4,
        "block_a_modified": ["e1", "e2", "e3"],
        "block_b_new": [],
    }
    responses["thirteen/functional/roles-permissions.md"] = {
        "score": 3,
        "dimension_roles_permissions": 3,
    }
    responses["thirteen/functional/boundaries.md"] = {
        "summary": "2 boundaries",
        "items": ["Boundary 1 — Score: 2", "Boundary 2 — Score: 3"],
        "scores_extracted": [2, 3],
    }
    responses["thirteen/functional/background-processes.md"] = {
        "score": 5,
        "dimension_background_processes": 5,
    }
    responses["thirteen/functional/notifications.md"] = {
        "summary": "2 events",
        "notification_events": ["event1", "event2"],
    }
    responses["thirteen/functional/audits.md"] = {
        "summary": "1 entity",
        "audited_entities": [{"entity": "User"}],
    }
    responses["thirteen/nfr-scoring.md"] = {
        "score": 3,
        "dimension_quality_attributes": 1,
        "dimension_security_compliance": 1,
        "dimension_user_experience_accessibility": 1,
    }

    # Aggregator response (prompt is rendered with bindings, but output is LLM-generated)
    responses["thirteen/functional/aggregator.md"] = {
        "score": 0,  # will be overridden by formula
        "dimension": "aggregator",
        "dim_business_rules": 8,
        "dim_interface_elements": 11,
        "dim_solution_variabilities": 3,
        "dim_domain_entities": 2,
        "dim_new_domain_entities": 2,
        "dim_roles_permissions": 3,
        "dim_boundaries": 5,
        "dim_background_processes": 5,
        "dim_notifications": 2,
        "dim_audits": 1,
        "total_bcp_functional": 42,
    }

    # Maturity cells
    responses["thirteen/complexity-maturity.md"] = {
        "score": 3,
        "classification": "Meets Basic Standards",
    }
    responses["thirteen/invest-maturity.md"] = {
        "score": 4,
        "classification": "Demonstrates Good Maturity",
    }

    fake = FakePromptHandler(responses)
    calc = BCPCalculator(logger=logger, provider_name="openai", prompt_handler=fake)
    story = "Password Reset\nAs a user I want to reset my password."
    result = calc.calculate_bcp(story)

    # Verify breakdown has all 10 functional + NFR
    assert "business_rules" in result["breakdown"]
    assert "interface_elements" in result["breakdown"]
    assert "solution_variabilities" in result["breakdown"]
    assert "domain_entities" in result["breakdown"]
    assert "new_domain_entities" in result["breakdown"]
    assert "roles_permissions" in result["breakdown"]
    assert "boundaries" in result["breakdown"]
    assert "background_processes" in result["breakdown"]
    assert "notifications" in result["breakdown"]
    assert "audits" in result["breakdown"]
    assert "nfr" in result["breakdown"]

    # Verify individual dimension scores
    assert result["breakdown"]["business_rules"] == 8  # sum([3, 5])
    assert result["breakdown"]["interface_elements"] == 11  # ceil(5/5)*3 + ceil(5/5)*8 = 3+8
    assert result["breakdown"]["solution_variabilities"] == 3
    assert result["breakdown"]["domain_entities"] == 2
    assert result["breakdown"]["new_domain_entities"] == 2  # 2*ceil(3/3) + 5*ceil(0/3) = 2+0
    assert result["breakdown"]["roles_permissions"] == 3
    assert result["breakdown"]["boundaries"] == 5  # sum([2, 3])
    assert result["breakdown"]["background_processes"] == 5
    assert result["breakdown"]["notifications"] == 2  # count(2 events)
    assert result["breakdown"]["audits"] == 1  # count(1 entity)
    assert result["breakdown"]["nfr"] == 3  # 1+1+1

    # Total BCP = aggregator score + NFR score
    expected_aggregator = 8 + 11 + 3 + 2 + 2 + 3 + 5 + 5 + 2 + 1  # = 42
    assert result["total_bcp"] == expected_aggregator + 3  # 42 + 3 = 45

    # Verify maturity scores
    assert result["maturity"]["complexity"] == 3
    assert result["maturity"]["invest"] == 4

    # Verify all 14 cells are present
    assert len(result["cells"]) == 14


def test_bcp_13d_cell_failure_continues(logger):
    """Test that a failing functional cell doesn't halt the pipeline — it scores 0."""
    class ErrorPromptHandler(FakePromptHandler):
        def process_prompt(self, prompt_file, variables, bindings=None):
            if prompt_file == "thirteen/functional/business-rules.md":
                raise RuntimeError("LLM error")
            return super().process_prompt(prompt_file, variables, bindings)

    responses = _build_wave1_responses()
    responses["thirteen/functional/aggregator.md"] = {"score": 0, "dimension": "aggregator"}
    responses["thirteen/complexity-maturity.md"] = {"score": 2}
    responses["thirteen/invest-maturity.md"] = {"score": 2}

    fake = ErrorPromptHandler(responses)
    calc = BCPCalculator(logger=logger, provider_name="openai", prompt_handler=fake)
    story = "Test\nBody"
    result = calc.calculate_bcp(story)

    # business_rules cell should have score=0 due to error
    assert result["cells"]["functional_business_rules"]["score"] == 0
    assert "error" in result["cells"]["functional_business_rules"]["raw_output"]
    # Pipeline should continue — other cells should have scores
    assert result["total_bcp"] > 0


def test_bcp_13d_output_structure(logger):
    """Verify the output structure has all expected top-level keys."""
    responses = _build_wave1_responses()
    responses["thirteen/functional/aggregator.md"] = {"score": 0, "dimension": "aggregator"}
    responses["thirteen/complexity-maturity.md"] = {"score": 3}
    responses["thirteen/invest-maturity.md"] = {"score": 3}

    fake = FakePromptHandler(responses)
    calc = BCPCalculator(logger=logger, provider_name="openai", prompt_handler=fake)
    result = calc.calculate_bcp("My Story\nSome content")

    assert "story_name" in result
    assert "cells" in result
    assert "breakdown" in result
    assert "maturity" in result
    assert "total_bcp" in result
    assert result["story_name"] == "My Story"
