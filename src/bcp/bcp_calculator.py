"""
BCP Calculator — 13 Dimensions Pipeline (V2 Decomposed)

Orchestrates the BCP (Business Complexity Points) calculation using a decomposed
pipeline with 14 cells across 3 execution waves:

  Wave 1: 10 functional dimension cells + 1 NFR cell (parallel)
  Wave 2: 1 aggregator cell (depends on 10 functional scores)
  Wave 3: 2 maturity evaluation cells (depend on aggregator + NFR)

Total BCP = functional_aggregator.score + nfr_scoring.score
"""

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional

from .prompt_handler import PromptHandler
from .formula_evaluator import FormulaEvaluator
from .logger import StepLogger


FUNCTIONAL_DIMENSIONS: List[Dict[str, str]] = [
    {
        "name": "business_rules",
        "display": "Business Rules",
        "prompt": "thirteen/functional/business-rules.md",
        "formula": "sum(scores_extracted)",
    },
    {
        "name": "interface_elements",
        "display": "Interface Elements",
        "prompt": "thirteen/functional/interface-elements.md",
        "formula": "ceil(count(static_elements)/5)*static_weight + ceil(count(dynamic_elements)/5)*dynamic_weight",
    },
    {
        "name": "solution_variabilities",
        "display": "Solution Variabilities",
        "prompt": "thirteen/functional/solution-variabilities.md",
        "formula": "dimension_solution_variabilities",
    },
    {
        "name": "domain_entities",
        "display": "Domain Entities",
        "prompt": "thirteen/functional/domain-entities.md",
        "formula": "dimension_domain_entities",
    },
    {
        "name": "new_domain_entities",
        "display": "New Domain Entities",
        "prompt": "thirteen/functional/new-domain-entities.md",
        "formula": "2*ceil(count(block_a_modified)/3) + 5*ceil(count(block_b_new)/3)",
    },
    {
        "name": "roles_permissions",
        "display": "Roles & Permissions",
        "prompt": "thirteen/functional/roles-permissions.md",
        "formula": "dimension_roles_permissions",
    },
    {
        "name": "boundaries",
        "display": "Boundaries",
        "prompt": "thirteen/functional/boundaries.md",
        "formula": "sum(scores_extracted)",
    },
    {
        "name": "background_processes",
        "display": "Background Processes",
        "prompt": "thirteen/functional/background-processes.md",
        "formula": "dimension_background_processes",
    },
    {
        "name": "notifications",
        "display": "Notifications",
        "prompt": "thirteen/functional/notifications.md",
        "formula": "count(notification_events)",
    },
    {
        "name": "audits",
        "display": "Audits",
        "prompt": "thirteen/functional/audits.md",
        "formula": "count(audited_entities)",
    },
]

NFR_CELL = {
    "name": "nfr_scoring",
    "display": "NFR BCP (3 dimensions)",
    "prompt": "thirteen/nfr-scoring.md",
    "formula": "dimension_quality_attributes + dimension_security_compliance + dimension_user_experience_accessibility",
}

AGGREGATOR_CELL = {
    "name": "functional_aggregator",
    "display": "Functional Aggregator",
    "prompt": "thirteen/functional/aggregator.md",
}

MATURITY_CELLS = [
    {
        "name": "complexity_maturity",
        "display": "Complexity Maturity",
        "prompt": "thirteen/complexity-maturity.md",
    },
    {
        "name": "invest_maturity",
        "display": "INVEST Maturity",
        "prompt": "thirteen/invest-maturity.md",
    },
]

# Aggregator formula: sum of all 10 functional dimension scores (as bindings)
AGGREGATOR_FORMULA = " + ".join(f"dim_{d['name']}" for d in FUNCTIONAL_DIMENSIONS)


class BCPCalculator:
    """
    Calculator for Business Complexity Points (BCP) using the 13-dimensions
    decomposed pipeline (V2).
    """

    def __init__(
        self,
        logger: logging.Logger,
        provider_name: str = "openai",
        prompt_handler: PromptHandler | None = None,
        max_workers: int = 5,
    ):
        """
        Initialize the BCP calculator.

        Args:
            logger: The logger instance
            provider_name: The name of the LLM provider to use
            prompt_handler: Optional PromptHandler for dependency injection (testing)
            max_workers: Maximum number of parallel threads per wave
        """
        self.logger = logger
        self.provider_name = provider_name
        self.prompt_handler = prompt_handler or PromptHandler(logger, provider_name=provider_name)
        self.formula_evaluator = FormulaEvaluator(logger)
        self.max_workers = max_workers

    def calculate_bcp(self, story_content: str) -> Dict[str, Any]:
        """
        Calculate the Business Complexity Points (BCP) for a user story
        using the 13-dimensions decomposed pipeline.

        Args:
            story_content: The content of the user story

        Returns:
            A dictionary containing cell results, dimension breakdown,
            maturity scores, and the total BCP
        """
        self.logger.info("Starting BCP 13-dimensions calculation")

        story_lines = story_content.strip().split("\n")
        story_name = story_lines[0].strip() if story_lines else "Unnamed Story"

        story_vars = PromptHandler.prepare_story_variables(story_content)

        results: Dict[str, Any] = {
            "story_name": story_name,
            "cells": {},
            "breakdown": {},
            "maturity": {},
            "total_bcp": 0,
        }

        # --- Wave 1: 10 functional cells + NFR cell (parallel) ---
        wave1_cells = [
            (f"functional_{d['name']}", d["display"], d["prompt"], d["formula"])
            for d in FUNCTIONAL_DIMENSIONS
        ]
        wave1_cells.append(
            (NFR_CELL["name"], NFR_CELL["display"], NFR_CELL["prompt"], NFR_CELL["formula"])
        )

        wave1_results = self._execute_wave(
            wave1_cells, story_vars, bindings=None, wave_name="Wave 1"
        )

        results["cells"].update(wave1_results["cells"])

        # Extract functional scores for aggregator bindings
        aggregator_bindings: Dict[str, Any] = {}
        functional_scores: Dict[str, float] = {}
        for d in FUNCTIONAL_DIMENSIONS:
            cell_name = f"functional_{d['name']}"
            cell_result = wave1_results["cells"].get(cell_name, {})
            score = cell_result.get("score", 0)
            aggregator_bindings[f"dim_{d['name']}"] = score
            functional_scores[d["name"]] = score

        nfr_result = wave1_results["cells"].get("nfr_scoring", {})
        nfr_score = nfr_result.get("score", 0)

        # Populate breakdown from Wave 1
        for d in FUNCTIONAL_DIMENSIONS:
            results["breakdown"][d["name"]] = functional_scores.get(d["name"], 0)
        results["breakdown"]["nfr"] = nfr_score

        # --- Wave 2: aggregator cell (depends on 10 functional scores) ---
        aggregator_result = self._execute_cell(
            cell_name=AGGREGATOR_CELL["name"],
            display_name=AGGREGATOR_CELL["display"],
            prompt_file=AGGREGATOR_CELL["prompt"],
            story_vars=story_vars,
            bindings=aggregator_bindings,
            formula=AGGREGATOR_FORMULA,
            is_aggregator=True,
        )

        results["cells"][AGGREGATOR_CELL["name"]] = aggregator_result
        aggregator_score = aggregator_result.get("score", 0)

        # --- Wave 3: 2 maturity cells (depend on aggregator + NFR) ---
        maturity_bindings: Dict[str, Any] = {
            "functional_scoring": json.dumps(aggregator_result.get("raw_output", {}), ensure_ascii=False),
            "nfr_scoring": json.dumps(nfr_result.get("raw_output", {}), ensure_ascii=False),
        }

        wave3_cells = [
            (mc["name"], mc["display"], mc["prompt"], None) for mc in MATURITY_CELLS
        ]
        wave3_results = self._execute_wave(
            wave3_cells, story_vars, bindings=maturity_bindings, wave_name="Wave 3"
        )

        results["cells"].update(wave3_results["cells"])

        for mc in MATURITY_CELLS:
            cell_result = wave3_results["cells"].get(mc["name"], {})
            score = cell_result.get("score", 0)
            maturity_key = "complexity" if "complexity" in mc["name"] else "invest"
            results["maturity"][maturity_key] = score

        # --- Total BCP ---
        results["total_bcp"] = aggregator_score + nfr_score

        self.logger.info(
            f"BCP 13-dimensions calculation completed. "
            f"Total BCP: {results['total_bcp']} "
            f"(functional: {aggregator_score}, nfr: {nfr_score})"
        )
        return results

    def _execute_wave(
        self,
        cells: List[tuple],
        story_vars: Dict[str, Any],
        bindings: Optional[Dict[str, Any]],
        wave_name: str,
    ) -> Dict[str, Any]:
        """
        Execute a wave of cells in parallel using ThreadPoolExecutor.

        Args:
            cells: List of (name, display, prompt_file, formula) tuples
            story_vars: Story variables dict
            bindings: Optional binding values to inject into prompts
            wave_name: Name for logging

        Returns:
            Dict with 'cells' key containing results per cell name
        """
        self.logger.info(f"{wave_name}: executing {len(cells)} cells in parallel")
        wave_results: Dict[str, Any] = {"cells": {}}

        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(cells))) as executor:
            futures = {}
            for cell_name, display_name, prompt_file, formula in cells:
                future = executor.submit(
                    self._execute_cell,
                    cell_name=cell_name,
                    display_name=display_name,
                    prompt_file=prompt_file,
                    story_vars=story_vars,
                    bindings=bindings,
                    formula=formula,
                )
                futures[future] = cell_name

            for future in as_completed(futures):
                cell_name = futures[future]
                try:
                    result = future.result()
                    wave_results["cells"][cell_name] = result
                    step_logger = StepLogger(self.logger, cell_name)
                    step_logger.info(
                        f"Completed with score: {result.get('score', 'N/A')}"
                    )
                except Exception as e:
                    self.logger.error(f"{wave_name} — cell '{cell_name}' failed: {str(e)}")
                    wave_results["cells"][cell_name] = {
                        "score": 0,
                        "raw_output": {"error": str(e)},
                    }

        return wave_results

    def _execute_cell(
        self,
        cell_name: str,
        display_name: str,
        prompt_file: str,
        story_vars: Dict[str, Any],
        bindings: Optional[Dict[str, Any]] = None,
        formula: Optional[str] = None,
        is_aggregator: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute a single pipeline cell: load prompt, render, invoke LLM, parse, score.

        Args:
            cell_name: Unique cell identifier
            display_name: Human-readable name
            prompt_file: Relative path to the prompt template
            story_vars: Story variables dict
            bindings: Optional binding values for the prompt template
            formula: Optional scoreFormula to evaluate against the LLM output
            is_aggregator: If True, use bindings directly as the score source
                           (aggregator already has scores in its output from bindings)

        Returns:
            Dict with 'score' (number) and 'raw_output' (parsed LLM response)
        """
        step_logger = StepLogger(self.logger, cell_name)
        step_logger.info(f"Processing cell: {display_name}")

        # For the aggregator, bindings are injected as Jinja2 variables in the prompt
        # The prompt template uses {{dim_business_rules}} etc.
        prompt_bindings = bindings if is_aggregator else bindings

        raw_output = self.prompt_handler.process_prompt(
            prompt_file=prompt_file,
            variables=story_vars,
            bindings=prompt_bindings,
        )

        # Evaluate score
        score = 0
        if formula:
            try:
                if is_aggregator:
                    # Aggregator: evaluate formula using binding values
                    score = self.formula_evaluator.evaluate(
                        formula=formula, output={}, bindings=bindings or {}
                    )
                else:
                    score = self.formula_evaluator.evaluate(
                        formula=formula, output=raw_output, bindings=bindings or {}
                    )
            except Exception as e:
                step_logger.warning(f"Score formula evaluation failed: {str(e)}")
                # Try to get score directly from the output
                if isinstance(raw_output, dict) and "score" in raw_output:
                    score = raw_output["score"]
                    step_logger.info(f"Using 'score' field from output: {score}")
        elif isinstance(raw_output, dict) and "score" in raw_output:
            score = raw_output["score"]

        step_logger.info(f"Cell completed. Score: {score}")
        return {"score": score, "raw_output": raw_output}
