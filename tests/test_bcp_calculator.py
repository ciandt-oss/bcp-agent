#!/usr/bin/env python3
"""
Test script for the BCP Calculator — 13 Dimensions Pipeline

This script tests the BCP Calculator with sample user stories,
producing per-dimension breakdowns and summary CSV reports.
"""

import os
import logging
import json
import argparse
import csv
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from dotenv import load_dotenv
from bcp import BCPCalculator, setup_logger


DIMENSIONS = [
    "business_rules",
    "interface_elements",
    "solution_variabilities",
    "domain_entities",
    "new_domain_entities",
    "roles_permissions",
    "boundaries",
    "background_processes",
    "notifications",
    "audits",
    "nfr",
]


def main():
    parser = argparse.ArgumentParser(
        description="Test the BCP 13-Dimensions Calculator with sample user stories."
    )
    parser.add_argument(
        "--executions",
        type=int,
        default=1,
        help="Number of times to execute BCP calculation for each story (default: 1)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["openai", "claude", "flow-litellm"],
        help="LLM provider to use (default: openai)"
    )
    args = parser.parse_args()

    load_dotenv()

    logger = setup_logger(logging.DEBUG)
    logger.info("Starting BCP 13-Dimensions Calculator test")

    test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if not os.path.isdir(test_data_dir):
        logger.error(f"Test data directory not found: {test_data_dir}")
        return

    test_stories = sorted([f for f in os.listdir(test_data_dir) if f.endswith(".md")])
    if not test_stories:
        logger.error(f"No test stories found in {test_data_dir}")
        return

    calculator = BCPCalculator(logger, provider_name=args.provider)

    csv_rows = []
    csv_header = ["story", "execution"]
    csv_header += [f"dim_{d}" for d in DIMENSIONS]
    csv_header += ["total_bcp", "complexity_maturity", "invest_maturity"]

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_path, exist_ok=True)

    for story_file in test_stories:
        story_path = os.path.join(test_data_dir, story_file)
        logger.info(f"Testing with story: {story_file}")

        try:
            with open(story_path, 'r', encoding='utf-8') as file:
                story_content = file.read()

            results_list = []

            for i in range(args.executions):
                logger.info(f"Execution {i+1}/{args.executions} for {story_file}")
                results = calculator.calculate_bcp(story_content)
                results_list.append(results)

                logger.info(f"Total BCP: {results['total_bcp']}")
                logger.info(f"Breakdown: {results['breakdown']}")
                logger.info(f"Maturity: {results['maturity']}")

                row = [story_file, i + 1]
                breakdown = results.get("breakdown", {})
                for dim in DIMENSIONS:
                    row.append(breakdown.get(dim, ""))
                row.append(results.get("total_bcp", ""))
                maturity = results.get("maturity", {})
                row.append(maturity.get("complexity", ""))
                row.append(maturity.get("invest", ""))
                csv_rows.append(row)

            output_file = os.path.join(
                output_path,
                f"{os.path.splitext(story_file)[0]}_results.json"
            )
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(results_list, file, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {output_file}")

        except Exception as e:
            logger.error(f"Error processing {story_file}: {str(e)}")

    csv_output_path = os.path.join(
        output_path,
        f"bcp_13d_results-{datetime.now().strftime('_%Y%m%d_%H%M%S')}.csv"
    )
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_header)
        writer.writerows(csv_rows)
    logger.info(f"CSV summary written to {csv_output_path}")


if __name__ == "__main__":
    main()
