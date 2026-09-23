#!/usr/bin/env python3
"""BCP 13-Dimensions Pipeline utility.

Computes scores from cell JSON outputs, aggregates dimensions,
consolidates story results, and produces final reports.
Standalone — uses only Python stdlib, no external dependencies.
"""

import argparse
import json
import math
import os
import sys


FUNCTIONAL_DIMENSIONS = [
    ("functional_business_rules", "business_rules", "D1", "Business Rules"),
    ("functional_interface_elements", "interface_elements", "D2", "Interface Elements"),
    ("functional_boundaries", "boundaries", "D3", "Boundaries"),
    ("functional_roles_permissions", "roles_permissions", "D4", "Roles & Permissions"),
    ("functional_solution_variabilities", "solution_variabilities", "D5", "Solution Variabilities"),
    ("functional_domain_entities", "domain_entities", "D6", "Domain Entities"),
    ("functional_new_domain_entities", "new_domain_entities", "D7", "New Domain Entities"),
    ("functional_background_processes", "background_processes", "D8", "Background Processes"),
    ("functional_notifications", "notifications", "D9", "Notifications"),
    ("functional_audits", "audits", "D10", "Audits"),
]

NFR_DIMENSIONS = [
    ("dimension_quality_attributes", "D11", "Quality Attributes", "quality_attributes"),
    ("dimension_security_compliance", "D12", "Security & Compliance", "security_compliance"),
    ("dimension_user_experience_accessibility", "D13", "UX & Accessibility", "user_experience_accessibility"),
]

DIM_KEYS = [
    "dim_business_rules",
    "dim_interface_elements",
    "dim_boundaries",
    "dim_roles_permissions",
    "dim_solution_variabilities",
    "dim_domain_entities",
    "dim_new_domain_entities",
    "dim_background_processes",
    "dim_notifications",
    "dim_audits",
]

DIRECT_VALUE_CELLS = {
    "solution_variabilities": "dimension_solution_variabilities",
    "domain_entities": "dimension_domain_entities",
    "roles_permissions": "dimension_roles_permissions",
    "background_processes": "dimension_background_processes",
}

CELLS_WITH_ITEMS = {"business_rules", "boundaries"}


def safe_get(data, key, default=None):
    if not isinstance(data, dict):
        return default
    return data.get(key, default)


def safe_list(data, key):
    val = safe_get(data, key, [])
    return val if isinstance(val, list) else []


def safe_int(data, key, default=0):
    val = safe_get(data, key, default)
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return int(val)
    return default


def safe_str(data, key, default=""):
    val = safe_get(data, key, default)
    return val if isinstance(val, str) else default


def is_failed(raw_output):
    return isinstance(raw_output, dict) and "error" in raw_output


def compute_cell_score(cell_name, output):
    if not isinstance(output, dict) or "error" in output:
        return 0

    if cell_name in ("business_rules", "boundaries"):
        arr = safe_list(output, "scores_extracted")
        return sum(v for v in arr if isinstance(v, (int, float)) and not isinstance(v, bool))

    if cell_name == "interface_elements":
        static = safe_list(output, "static_elements")
        dynamic = safe_list(output, "dynamic_elements")
        sw = safe_int(output, "static_weight")
        dw = safe_int(output, "dynamic_weight")
        return math.ceil(len(static) / 5) * sw + math.ceil(len(dynamic) / 5) * dw

    if cell_name == "new_domain_entities":
        block_a = safe_list(output, "block_a_modified")
        block_b = safe_list(output, "block_b_new")
        return 2 * math.ceil(len(block_a) / 3) + 5 * math.ceil(len(block_b) / 3)

    if cell_name == "notifications":
        return len(safe_list(output, "notification_events"))

    if cell_name == "audits":
        return len(safe_list(output, "audited_entities"))

    if cell_name == "nfr_scoring":
        return (
            safe_int(output, "dimension_quality_attributes")
            + safe_int(output, "dimension_security_compliance")
            + safe_int(output, "dimension_user_experience_accessibility")
        )

    if cell_name == "functional_aggregator":
        return sum(safe_int(output, key) for key in DIM_KEYS)

    if cell_name in ("complexity_maturity", "invest_maturity"):
        return safe_int(output, "score")

    if cell_name in DIRECT_VALUE_CELLS:
        return safe_int(output, DIRECT_VALUE_CELLS[cell_name])

    return 0


def compute_aggregator_score(bindings):
    return sum(safe_int(bindings, key) for key in DIM_KEYS)


def build_nfr_dimensions(nfr_raw):
    details = safe_get(nfr_raw, "details", {})
    dimensions = []
    for score_field, dim_id, display_name, detail_key in NFR_DIMENSIONS:
        detail = safe_get(details, detail_key, {})
        dimensions.append({
            "id": dim_id,
            "name": display_name,
            "score": safe_int(nfr_raw, score_field),
            "summary": safe_str(detail, "assessment"),
            "detailed_explanation": safe_str(detail, "detailed_explanation"),
        })
    return dimensions


def build_maturity(cells, cell_name, breakdown_key, failed_cells):
    cell = safe_get(cells, cell_name, {})
    raw = safe_get(cell, "raw_output", {})
    if is_failed(raw):
        failed_cells.append(cell_name)
        return {"score": 0, "classification": "", "summary": "", "gaps": [], "breakdown": {}}
    return {
        "score": safe_int(raw, "score"),
        "classification": safe_str(raw, "classification"),
        "summary": safe_str(raw, "summary"),
        "gaps": safe_list(raw, "gaps"),
        "breakdown": safe_get(raw, breakdown_key, {}),
    }


def consolidate_story(data):
    story_key = safe_str(data, "story_key")
    story_name = safe_str(data, "story_name")
    cells = safe_get(data, "cells", {})

    failed_cells = []
    functional_dimensions = []
    functional_scores = {}

    for full_name, short_name, dim_id, display_name in FUNCTIONAL_DIMENSIONS:
        cell = safe_get(cells, full_name, {})
        raw_output = safe_get(cell, "raw_output", {})
        if is_failed(raw_output):
            failed_cells.append(full_name)
            score = 0
        else:
            score = compute_cell_score(short_name, raw_output)
        functional_scores[short_name] = score

        dim_result = {
            "id": dim_id,
            "name": display_name,
            "score": score,
            "summary": safe_str(raw_output, "summary"),
        }
        if short_name in CELLS_WITH_ITEMS:
            dim_result["items"] = safe_list(raw_output, "items")
        dim_result["reasoning"] = safe_str(raw_output, "reasoning")
        functional_dimensions.append(dim_result)

    aggregator_score = sum(functional_scores.values())

    agg_cell = safe_get(cells, "functional_aggregator", {})
    agg_raw = safe_get(agg_cell, "raw_output", {})
    if is_failed(agg_raw):
        failed_cells.append("functional_aggregator")

    nfr_cell = safe_get(cells, "nfr_scoring", {})
    nfr_raw = safe_get(nfr_cell, "raw_output", {})
    if is_failed(nfr_raw):
        failed_cells.append("nfr_scoring")
        nfr_score = 0
    else:
        nfr_score = compute_cell_score("nfr_scoring", nfr_raw)
    nfr_dimensions = build_nfr_dimensions(nfr_raw)

    cms = build_maturity(cells, "complexity_maturity", "complexity_breakdown", failed_cells)
    ims = build_maturity(cells, "invest_maturity", "invest_breakdown", failed_cells)

    bcp_total = aggregator_score + nfr_score

    return {
        "story_key": story_key,
        "story_name": story_name,
        "bcp_total": bcp_total,
        "cms": cms,
        "ims": ims,
        "functional_dimensions": functional_dimensions,
        "nfr_dimensions": nfr_dimensions,
        "has_failures": len(failed_cells) > 0,
        "failed_cells": failed_cells,
    }


def aggregate_stories(stories):
    if not isinstance(stories, list):
        stories = []

    summary = []
    total_bcp = 0

    for story in stories:
        cms = safe_get(story, "cms", {})
        ims = safe_get(story, "ims", {})
        entry = {
            "key": safe_str(story, "story_key"),
            "name": safe_str(story, "story_name"),
            "bcp": safe_int(story, "bcp_total"),
            "cms": safe_int(cms, "score"),
            "ims": safe_int(ims, "score"),
        }
        summary.append(entry)
        total_bcp += entry["bcp"]

    average_bcp = total_bcp / len(stories) if stories else 0

    highest = None
    lowest = None
    for entry in summary:
        if highest is None or entry["bcp"] > highest["bcp"]:
            highest = entry
        if lowest is None or entry["bcp"] < lowest["bcp"]:
            lowest = entry

    return {
        "summary": summary,
        "total_bcp": total_bcp,
        "average_bcp": average_bcp,
        "highest_complexity": {
            "key": highest["key"],
            "name": highest["name"],
            "bcp": highest["bcp"],
        } if highest else None,
        "lowest_complexity": {
            "key": lowest["key"],
            "name": lowest["name"],
            "bcp": lowest["bcp"],
        } if lowest else None,
        "stories": stories,
    }


def parse_json_arg(value):
    if os.path.isfile(value):
        with open(value, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(value)


def read_input(path):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_score(args):
    output = parse_json_arg(args.output)
    cell = args.cell
    if cell == "functional_aggregator":
        score = compute_cell_score("functional_aggregator", output)
    elif cell.startswith("functional_"):
        score = compute_cell_score(cell[len("functional_"):], output)
    else:
        score = compute_cell_score(cell, output)
    print(json.dumps({"score": score, "cell": args.cell}, ensure_ascii=False, indent=2))


def cmd_aggregate(args):
    bindings = parse_json_arg(args.bindings)
    score = compute_aggregator_score(bindings)
    print(json.dumps({"score": score, "total_bcp_functional": score}, ensure_ascii=False, indent=2))


def cmd_consolidate(args):
    data = read_input(args.input)
    result = consolidate_story(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_aggregate_stories(args):
    data = read_input(args.input)
    result = aggregate_stories(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="BCP 13-Dimensions Pipeline utility"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_score = sub.add_parser("score", help="Calculate score for a single cell from its JSON output")
    p_score.add_argument("--cell", required=True, help="Cell name (e.g., business_rules, interface_elements)")
    p_score.add_argument("--output", required=True, help="Cell JSON output (inline string or file path)")
    p_score.set_defaults(func=cmd_score)

    p_agg = sub.add_parser("aggregate", help="Calculate aggregator score from 10 dim bindings")
    p_agg.add_argument("--bindings", required=True, help="JSON bindings (inline string or file path)")
    p_agg.set_defaults(func=cmd_aggregate)

    p_con = sub.add_parser("consolidate", help="Consolidate a complete story result into structured JSON")
    p_con.add_argument("--input", required=True, help="Input JSON file path (or - for stdin)")
    p_con.set_defaults(func=cmd_consolidate)

    p_as = sub.add_parser("aggregate-stories", help="Aggregate multiple stories into a final report")
    p_as.add_argument("--input", required=True, help="Input JSON file path (or - for stdin)")
    p_as.set_defaults(func=cmd_aggregate_stories)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
