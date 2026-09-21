#!/usr/bin/env python3
"""
BCP Calculator - Command Line Interface

This script provides a CLI for calculating Business Complexity Points (BCP)
of user stories using the 13-dimensions decomposed pipeline and multiple LLM providers.
"""

import argparse
import json
import logging
import sys
import os
from typing import Dict, Any
from dotenv import load_dotenv

from bcp import BCPCalculator, setup_logger

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate Business Complexity Points (BCP) for a user story."
    )
    parser.add_argument(
        "story_file",
        type=str,
        help="Path to the user story markdown file"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Path to save the output results (default: print to stdout)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "claude", "flow-openai", "flow-bedrock"],
        default="openai",
        help="LLM provider to use (default: openai)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Maximum parallel threads per wave (default: 5)"
    )
    return parser.parse_args()

def read_story_file(file_path: str, logger: logging.Logger) -> str:
    """Read content from a story file."""
    if not os.path.isfile(file_path):
        logger.error(f"Story file not found: {file_path}")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading story file: {str(e)}")
        sys.exit(1)

def calculate_bcp_for_story(story_content: str, provider: str, logger: logging.Logger, max_workers: int = 5) -> Dict[str, Any]:
    """Calculate BCP for a given story."""
    try:
        calculator = BCPCalculator(logger, provider_name=provider, max_workers=max_workers)
        return calculator.calculate_bcp(story_content)
    except Exception as e:
        logger.error(f"Error calculating BCP: {str(e)}")
        sys.exit(1)

def save_or_print_results(results: Dict[str, Any], output_format: str, output_file: str = None, logger: logging.Logger = None) -> None:
    """Save results to file or print to stdout."""
    formatted_results = format_results_json(results) if output_format == "json" else format_results_text(results)

    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(formatted_results)
            if logger:
                logger.info(f"Results saved to {output_file}")
        except Exception as e:
            if logger:
                logger.error(f"Error saving results to {output_file}: {str(e)}")
            sys.exit(1)
    else:
        print(formatted_results)

def main():
    """Main entry point for the BCP Calculator CLI."""
    load_dotenv()
    args = parse_arguments()

    log_level = getattr(logging, args.log_level)
    logger = setup_logger(log_level)

    story_content = read_story_file(args.story_file, logger)
    results = calculate_bcp_for_story(story_content, args.provider, logger, args.max_workers)
    save_or_print_results(results, args.format, args.output_file, logger)

def format_results_json(results: Dict[str, Any]) -> str:
    """Format the results as JSON for the 13-dimensions pipeline output."""
    json_output = {
        "story_name": results.get("story_name", "Unknown"),
        "total_bcp": results.get("total_bcp", 0),
        "breakdown": results.get("breakdown", {}),
        "maturity": results.get("maturity", {}),
        "cells": {},
    }

    cells = results.get("cells", {})
    for cell_name, cell_result in cells.items():
        if isinstance(cell_result, dict):
            raw = cell_result.get("raw_output", {})
            json_output["cells"][cell_name] = {
                "score": cell_result.get("score", 0),
                "summary": raw.get("summary", "") if isinstance(raw, dict) else "",
                "classification": raw.get("classification", "") if isinstance(raw, dict) else "",
            }
        else:
            json_output["cells"][cell_name] = {"raw_response": str(cell_result)}

    return json.dumps(json_output, indent=2, ensure_ascii=False)

def format_results_text(results: Dict[str, Any]) -> str:
    """Format the results as text."""
    output = []

    output.append("=== BCP 13 DIMENSIONS — RESULTS ===")
    output.append(f"Story: {results.get('story_name', 'Unknown')}")
    output.append("")

    output.append("=== DIMENSION BREAKDOWN ===")
    breakdown = results.get("breakdown", {})
    for dim, score in breakdown.items():
        output.append(f"  {dim}: {score}")
    output.append("")

    output.append("=== MATURITY ===")
    maturity = results.get("maturity", {})
    output.append(f"  Complexity Maturity: {maturity.get('complexity', 'N/A')}")
    output.append(f"  INVEST Maturity: {maturity.get('invest', 'N/A')}")
    output.append("")

    output.append("=== CELL DETAILS ===")
    cells = results.get("cells", {})
    for cell_name, cell_result in cells.items():
        score = cell_result.get("score", "N/A") if isinstance(cell_result, dict) else "N/A"
        output.append(f"  {cell_name}: score={score}")
    output.append("")

    output.append("=== TOTAL BCP ===")
    output.append(f"  Total: {results.get('total_bcp', 0)}")
    output.append("")

    return "\n".join(output)

if __name__ == "__main__":
    main()
