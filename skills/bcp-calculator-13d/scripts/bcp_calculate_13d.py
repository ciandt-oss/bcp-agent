#!/usr/bin/env python3
"""
BCP Calculator 13D — Local API Server

Calls the local BCP Calculator API server (run_api_server.py) which runs the
13-dimensions BCP engine and returns a structured JSON with BCP total,
CMS, IMS, and all 13 dimension scores.

The local API uses an async job model: POST /calculate to submit a job, then
poll GET /status/{job_id} until the result is ready.

Usage (inline):
  python bcp_calculate_13d.py --title "Story Title" --description "Story description"

Usage (from .md file — extracts title + relevant sections automatically):
  python bcp_calculate_13d.py --file path/to/story.md
  python bcp_calculate_13d.py --file path/to/story.md --id 3

Usage (choose LLM provider):
  python bcp_calculate_13d.py --file path/to/story.md --provider openai
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
CALCULATE_PATH = "/calculate"
STATUS_PATH = "/status/"
POLL_INTERVAL = 3  # seconds between status polls
POLL_TIMEOUT = 300  # max seconds to wait for job completion

ALLOWED_PROVIDERS = ["openai", "claude", "flow-openai"]
MAX_RETRIES = 2  # Up to 2 retries (3 total attempts) for failed cells

SECTIONS_TO_EXTRACT = [
    "Narrativa de Negócio",
    "Narrativa Tecnica",
    "Narrativa Técnica",
    "Critérios de Aceite",
    "Criterios de Aceite",
]

# Cell name → (dimension_id, display_name, score_field_in_result)
FUNCTIONAL_DIMENSIONS = [
    ("functional_business_rules", "D1", "Business Rules", "dimension_business_rules"),
    ("functional_interface_elements", "D2", "Interface Elements", "dimension_interface_elements"),
    ("functional_boundaries", "D3", "Boundaries", "dimension_boundaries"),
    ("functional_roles_permissions", "D4", "Roles & Permissions", "dimension_roles_permissions"),
    ("functional_solution_variabilities", "D5", "Solution Variabilities", "dimension_solution_variabilities"),
    ("functional_domain_entities", "D6", "Domain Entities", "dimension_domain_entities"),
    ("functional_new_domain_entities", "D7", "New Domain Entities", "dimension_new_domain_entities"),
    ("functional_background_processes", "D8", "Background Processes", "dimension_background_processes"),
    ("functional_notifications", "D9", "Notifications", "dimension_notifications"),
    ("functional_audits", "D10", "Audits", "dimension_audits"),
]

# Sub-fields inside nfr_scoring.result → (field_name, dimension_id, display_name)
NFR_DIMENSIONS = [
    ("dimension_quality_attributes", "D11", "Quality Attributes"),
    ("dimension_security_compliance", "D12", "Security & Compliance"),
    ("dimension_user_experience_accessibility", "D13", "UX & Accessibility"),
]

# ---------------------------------------------------------------------------
# Markdown extraction (reused from bcp-calculator skill)
# ---------------------------------------------------------------------------


def extract_from_markdown(path: str) -> tuple:
    """
    Reads a story .md file and returns (title, description, key).

    Title: frontmatter `title:` or first `# `.
    Description: concatenated relevant sections.
    Key: frontmatter `jira_issue:` or filename without extension.
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()

    title = _extract_title(content)
    description = _extract_sections(content)
    key = _extract_key(content, path)
    return title, description, key


def _extract_title(content: str) -> str:
    fm_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if fm_match:
        return fm_match.group(1).strip()

    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()

    return "Story sem título"


def _extract_sections(content: str) -> str:
    """
    Extracts h2-level sections by name. Each extracted section includes all
    content until the next h2 (subsections h3/h4 are included).
    """
    blocks = re.split(r'^## ', content, flags=re.MULTILINE)

    collected = []
    for block in blocks:
        if not block.strip():
            continue
        first_line_end = block.index('\n') if '\n' in block else len(block)
        heading = block[:first_line_end].strip()
        body = block[first_line_end:].strip()

        normalized = _normalize(heading)
        if any(_normalize(s) in normalized or normalized in _normalize(s)
               for s in SECTIONS_TO_EXTRACT):
            collected.append(f"## {heading}\n\n{body}")

    return "\n\n---\n\n".join(collected)


def _extract_key(content: str, path: str) -> str:
    """Extract key from frontmatter jira_issue or filename."""
    jira_match = re.search(r'^jira_issue:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if jira_match:
        return jira_match.group(1).strip()

    basename = os.path.splitext(os.path.basename(path))[0]
    if basename:
        return basename

    return ""


def _normalize(text: str) -> str:
    """Lowercase + remove accents for fuzzy matching."""
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'õ': 'o', 'ô': 'o',
        'ú': 'u', 'ü': 'u',
        'ç': 'c',
    }
    result = text.lower()
    for accented, plain in replacements.items():
        result = result.replace(accented, plain)
    return result


# ---------------------------------------------------------------------------
# API call — async job submission + polling
# ---------------------------------------------------------------------------


def _submit_job(base_url: str, content: str, provider: str) -> dict:
    """POST /calculate to submit a BCP calculation job. Returns {"job_id": ...} or error."""
    url = base_url.rstrip("/") + CALCULATE_PATH

    body = {
        "content": content,
        "provider": provider,
    }
    payload = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        return {"error": True, "status_code": e.code, "message": resp_body}
    except urllib.error.URLError as e:
        return {"error": True, "status_code": None, "message": str(e.reason)}


def _poll_status(base_url: str, job_id: str) -> dict:
    """GET /status/{job_id} — poll job status until completed/failed or timeout."""
    url = base_url.rstrip("/") + STATUS_PATH + job_id

    req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        return {"error": True, "status_code": e.code, "message": resp_body}
    except urllib.error.URLError as e:
        return {"error": True, "status_code": None, "message": str(e.reason)}


def _wait_for_result(base_url: str, job_id: str) -> dict:
    """Poll /status/{job_id} until the job is completed or failed."""
    elapsed = 0
    while elapsed < POLL_TIMEOUT:
        status_resp = _poll_status(base_url, job_id)

        if status_resp.get("error"):
            return status_resp

        status = status_resp.get("status", "")
        if status == "completed":
            return status_resp.get("result", {})
        if status == "failed":
            return {"error": True, "status_code": None,
                    "message": status_resp.get("error", "Job failed")}

        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    return {"error": True, "status_code": None,
            "message": f"Job timed out after {POLL_TIMEOUT}s (job_id={job_id})"}


# ---------------------------------------------------------------------------
# Response parsing — local API format (cells is a dict keyed by cell name)
# ---------------------------------------------------------------------------


def _get_cell(cells: dict, name: str) -> dict | None:
    """Get a cell by name from the cells dict."""
    return cells.get(name)


def _get_cell_raw_output(cells: dict, name: str) -> dict | None:
    """Get the raw_output dict from a cell, or None."""
    cell = _get_cell(cells, name)
    if cell and isinstance(cell, dict):
        return cell.get("raw_output")
    return None


def _parse_functional_dimensions(cells: dict) -> list:
    """Extract the 10 functional dimension scores from individual cells.

    Reads score and raw_output (summary, items, reasoning) from each cell.
    """
    dimensions = []
    for cell_name, dim_id, display_name, score_field in FUNCTIONAL_DIMENSIONS:
        raw = _get_cell_raw_output(cells, cell_name)
        cell = _get_cell(cells, cell_name)
        if raw:
            dimensions.append({
                "id": dim_id,
                "name": display_name,
                "score": cell.get("score", 0),
                "summary": raw.get("summary", ""),
                "items": raw.get("items", []),
                "reasoning": raw.get("reasoning", ""),
            })
        else:
            dimensions.append({
                "id": dim_id,
                "name": display_name,
                "score": None,
                "summary": "⚠️ FAILED" if cell and cell.get("raw_output", {}).get("error") else "N/A",
                "items": [],
                "reasoning": "",
            })
    return dimensions


def _parse_nfr_dimensions(cells: dict) -> list:
    """Extract the 3 NFR dimension scores from the nfr_scoring cell.

    Reads scores from raw_output and detailed_explanation alongside assessment
    to match the level of detail available in the portal CSV export.
    """
    raw = _get_cell_raw_output(cells, "nfr_scoring")
    if not raw:
        return [
            {
                "id": dim_id, "name": display_name, "score": None,
                "summary": "⚠️ FAILED", "detailed_explanation": "",
            }
            for _, dim_id, display_name in NFR_DIMENSIONS
        ]

    details = raw.get("details", {})
    dimensions = []

    # Map detail keys for summaries
    detail_keys = {
        "dimension_quality_attributes": "quality_attributes",
        "dimension_security_compliance": "security_compliance",
        "dimension_user_experience_accessibility": "user_experience_accessibility",
    }

    for field_name, dim_id, display_name in NFR_DIMENSIONS:
        score = raw.get(field_name, 0)
        detail_key = detail_keys.get(field_name, "")
        detail = details.get(detail_key, {})
        summary = detail.get("assessment", raw.get("summary", ""))
        detailed_explanation = detail.get("detailed_explanation", "")
        dimensions.append({
            "id": dim_id,
            "name": display_name,
            "score": score,
            "summary": summary,
            "detailed_explanation": detailed_explanation,
        })

    return dimensions


def _parse_maturity(cells: dict, cell_name: str, breakdown_key: str) -> dict:
    """Extract maturity cell (CMS or IMS) data from raw_output."""
    raw = _get_cell_raw_output(cells, cell_name)
    if not raw:
        cell = _get_cell(cells, cell_name)
        return {
            "score": None,
            "classification": None,
            "summary": "⚠️ FAILED" if cell and cell.get("raw_output", {}).get("error") else "N/A",
            "gaps": [],
            "breakdown": {},
        }

    return {
        "score": raw.get("score"),
        "classification": raw.get("classification"),
        "summary": raw.get("summary", ""),
        "gaps": raw.get("gaps", []),
        "breakdown": raw.get(breakdown_key, {}),
    }


def _has_failed_cells(cells: dict) -> list:
    """Return list of cell names where raw_output has an error."""
    failed = []
    for name, cell in cells.items():
        if isinstance(cell, dict):
            raw = cell.get("raw_output", {})
            if isinstance(raw, dict) and raw.get("error"):
                failed.append(name)
    return failed


def _get_failed_details(cells: dict) -> list:
    """Return list of {name, error} for each failed cell."""
    details = []
    for name, cell in cells.items():
        if isinstance(cell, dict):
            raw = cell.get("raw_output", {})
            if isinstance(raw, dict) and raw.get("error"):
                details.append({"name": name, "error": raw.get("error", "unknown")})
    return details


def _parse_response(api_result: dict) -> dict:
    """Parse the local API result into the structured output format."""
    cells = api_result.get("cells", {})
    if not isinstance(cells, dict):
        cells = {}
    failed = _has_failed_cells(cells)

    result = {
        "bcp_total": api_result.get("total_bcp", 0),
        "story_name": api_result.get("story_name", ""),
        "cms": _parse_maturity(cells, "complexity_maturity", "complexity_breakdown"),
        "ims": _parse_maturity(cells, "invest_maturity", "invest_breakdown"),
        "functional_dimensions": _parse_functional_dimensions(cells),
        "nfr_dimensions": _parse_nfr_dimensions(cells),
        "has_failures": len(failed) > 0,
        "failed_cells": failed,
    }

    if failed:
        result["failed_details"] = _get_failed_details(cells)

    return result


# ---------------------------------------------------------------------------
# Calculate with retry
# ---------------------------------------------------------------------------


def calculate_bcp_13d(content: str, provider: str = "openai",
                      base_url: str = DEFAULT_BASE_URL) -> dict:
    """
    Submit a BCP calculation job to the local API server, poll for the result,
    and parse the response. Retries up to MAX_RETRIES times if any cells fail.
    """
    api_result = _submit_and_wait(content, provider, base_url)

    # HTTP-level error — no retry
    if api_result.get("error"):
        return api_result

    result = _parse_response(api_result)

    # Retry logic for failed cells
    if result["has_failures"]:
        for attempt in range(1, MAX_RETRIES + 1):
            time.sleep(2)  # Brief pause before retry
            api_result = _submit_and_wait(content, provider, base_url)

            if api_result.get("error"):
                return api_result

            result = _parse_response(api_result)

            if not result["has_failures"]:
                break

        # After all retries, add error message if still failing
        if result["has_failures"]:
            count = len(result["failed_cells"])
            cells_str = ", ".join(result["failed_cells"])
            result["error_message"] = (
                f"Calculation failed after {MAX_RETRIES + 1} attempts. "
                f"{count} cell(s) failed: {cells_str}."
            )

    return result


def _submit_and_wait(content: str, provider: str, base_url: str) -> dict:
    """Submit a job and wait for the result."""
    submit_resp = _submit_job(base_url, content, provider)

    if submit_resp.get("error"):
        return submit_resp

    job_id = submit_resp.get("job_id")
    if not job_id:
        return {"error": True, "status_code": None,
                "message": "No job_id returned from /calculate"}

    return _wait_for_result(base_url, job_id)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Calculate BCP (13 dimensions) for a user story via local API server"
    )
    parser.add_argument(
        "--id", type=int, default=0,
        help="Numeric story ID (default: 0)",
    )
    parser.add_argument(
        "--key", default="",
        help="Story key for traceability (auto-generated if omitted)",
    )
    parser.add_argument(
        "--base-url", default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--provider", choices=ALLOWED_PROVIDERS, default="openai",
        help="LLM provider (default: openai)",
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--file",
        help="Path to story .md file (extracts title + relevant sections automatically)",
    )
    source.add_argument(
        "--title",
        help="Story title (requires --description)",
    )

    parser.add_argument(
        "--description",
        help="Story description (required when --title is used)",
    )

    args = parser.parse_args()

    # Resolve input
    if args.file:
        try:
            title, description, auto_key = extract_from_markdown(args.file)
        except FileNotFoundError:
            print(json.dumps({
                "error": True, "status_code": None,
                "message": f"File not found: {args.file}",
            }))
            sys.exit(1)
    else:
        if not args.description:
            parser.error("--description is required when --title is used")
        title = args.title
        description = args.description
        auto_key = ""

    # Validate description
    if not description.strip():
        print(json.dumps({
            "error": True,
            "status_code": None,
            "message": "No relevant sections found in the file. Ensure the story contains "
                       "'## Narrativa de Negócio', '## Narrativa Técnica' and '## Critérios de Aceite'.",
        }))
        sys.exit(1)

    # Build the content string that the local API expects
    content = f"# {title}\n\n{description}"

    result = calculate_bcp_13d(content=content, provider=args.provider, base_url=args.base_url)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result.get("error") or result.get("has_failures"):
        sys.exit(1)


if __name__ == "__main__":
    main()
