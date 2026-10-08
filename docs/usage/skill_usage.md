# Skill Usage Guide for BCP Calculator 13D

This guide explains how to use the BCP Calculator 13D as a Claude Code skill that calls the local API server.

## Prerequisites

Before using the skill, make sure you have:

1. Installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables:
   ```bash
   cp .env.flow.example .env
   ```
   Then edit the `.env` file to add your API keys for the providers you want to use. Supported providers:
   - OpenAI: set OPENAI_API_KEY and optional OPENAI_MODEL_NAME
   - Anthropic (Claude): set ANTHROPIC_API_KEY and optional ANTHROPIC_MODEL_NAME
   - Flow OpenAI (flow-openai): set FLOW_LLM_LITE_HOST, FLOW_LITELLM_CLIENT_ID, FLOW_LITELLM_CLIENT_SECRET, FLOW_LITELLM_SCOPE, optional FLOW_TENANT, FLOW_AGENT, FLOW_LITELLM_MODEL_NAME

3. Started the local API server:
   ```bash
   python run_api_server.py
   ```
   The server runs on `http://127.0.0.1:8000` by default. Verify it is online:
   ```bash
   curl -s http://127.0.0.1:8000/
   ```

## How It Works

The skill is a Claude Code agent skill defined in `skills/bcp-calculator-13d/SKILL.md`. When triggered, the agent:

1. **Checks the local server** — verifies that `run_api_server.py` is running on `http://127.0.0.1:8000`
2. **Identifies the stories** — from chat text, a single `.md` file, or a directory of `story-*.md` files
3. **Calls the bundled script** — `scripts/bcp_calculate_13d.py` submits the story to the local API and polls for results
4. **Presents the results** — formats the JSON output into Markdown tables with BCP Total, CMS, IMS, and all 13 dimension scores

No authentication token is required — the local API server accepts requests directly without a Bearer token.

## Triggering the Skill

The skill can be triggered by natural language or by name. The skill was designed for pt-BR users (Flow/CI&T), so triggers are in Portuguese — English equivalents work too as long as the keywords "BCP", "13d", or "13 dimensions" are present:

- "Calculate the BCP 13 dimensions for this story: Title: Export CSV report..."
- "Calculate the BCP 13d for the file `docs/stories/story-001.md`"
- "Calculate the BCP 13d for all stories in the `docs/PRD/sprint-42/` folder"
- "How much is this story worth in BCP 13 dimensions?"
- "bcp-calculator-13d" (direct invocation by name)
- "Evaluate 13d complexity for the file `planning/story-login.md`"

## The Bundled Script

The skill uses `scripts/bcp_calculate_13d.py` to interact with the local API. You can also run it directly from the command line.

### Basic Usage

Calculate BCP from a story `.md` file:

```bash
python skills/bcp-calculator-13d/scripts/bcp_calculate_13d.py \
  --file tests/data/story1.md
```

Calculate BCP from inline text:

```bash
python skills/bcp-calculator-13d/scripts/bcp_calculate_13d.py \
  --title "User Story: Add Payment Method" \
  --description "## Business Narrative\n\nAs a user, I want to add a payment method..."
```

### Options

The script supports the following options:

| Option | Description | Default |
|--------|-------------|---------|
| `--file` | Path to story `.md` file (extracts title + relevant sections automatically) | — |
| `--title` | Story title (requires `--description`, mutually exclusive with `--file`) | — |
| `--description` | Story description (required when `--title` is used) | — |
| `--id` | Numeric story ID for batch identification | 0 |
| `--key` | Traceability key (auto-generated if omitted) | auto |
| `--base-url` | API base URL | `http://127.0.0.1:8000` |
| `--provider` | LLM provider to use (`openai`, `claude`, `flow-openai`) | `openai` |

### Input Format

The script accepts two mutually exclusive input modes:

**File mode (`--file`):** The script reads a Markdown file and automatically extracts:
- **Title** — from frontmatter `title:` or the first `# ` heading
- **Description** — concatenates the following `## ` sections. The script matches these literal Portuguese section names in the `.md` file:
  - `Narrativa de Negócio` (Business Narrative) — includes `Regras de Negócio` (Business Rules) and `Edge Cases` subsections
  - `Narrativa Técnica` (Technical Narrative)
  - `Critérios de Aceite` (Acceptance Criteria)

> **Note:** These section names are hardcoded in the script. The story `.md` files must use these exact Portuguese headings for the script to extract content. English-only headings will not be recognized.

**Inline mode (`--title` + `--description`):** The title and description are passed directly as strings. The description should include the same content that would appear in the sections listed above.

### Using Different Providers

Process with OpenAI (default):

```bash
python skills/bcp-calculator-13d/scripts/bcp_calculate_13d.py \
  --file tests/data/story1.md --provider openai
```

Process with Claude:

```bash
python skills/bcp-calculator-13d/scripts/bcp_calculate_13d.py \
  --file tests/data/story1.md --provider claude
```

### Custom API Server URL

If the API server is running on a different host or port:

```bash
python skills/bcp-calculator-13d/scripts/bcp_calculate_13d.py \
  --file tests/data/story1.md --base-url http://localhost:9000
```

## Understanding the Output

The script outputs a JSON object with the following structure:

```json
{
  "bcp_total": 28,
  "story_name": "User Story: Add Payment Method",
  "cms": {
    "score": 3,
    "classification": "Meets Basic Standards",
    "summary": "The story meets basic standards...",
    "gaps": ["Payment validation rules not fully specified"],
    "breakdown": {
      "clarity": 3,
      "completeness": 3,
      "explicit_definitions": 2,
      "testability": 4,
      "business_value": 4
    }
  },
  "ims": {
    "score": 4,
    "classification": "Demonstrates Good Maturity",
    "summary": "The story demonstrates good maturity...",
    "gaps": ["Payment gateway integration details not specified"],
    "breakdown": {
      "independent": 4,
      "negotiable": 4,
      "valuable": 5,
      "estimable": 3,
      "small": 4,
      "testable": 4
    }
  },
  "functional_dimensions": [
    {
      "id": "D1",
      "name": "Business Rules",
      "score": 7,
      "summary": "3 rules identified",
      "items": ["Rule 1 — Score: 3", "Rule 2 — Score: 2", "Rule 3 — Score: 2"],
      "reasoning": ""
    }
  ],
  "nfr_dimensions": [
    {
      "id": "D11",
      "name": "Quality Attributes",
      "score": 3,
      "summary": "Moderate quality attribute complexity",
      "detailed_explanation": ""
    }
  ],
  "has_failures": false,
  "failed_cells": []
}
```

### Output Fields

| Field | Description |
|-------|-------------|
| `bcp_total` | Total Business Complexity Points (functional aggregator + NFR) |
| `story_name` | Name of the user story (first line of content) |
| `cms` | Complexity Maturity Score — score (0-5), classification, summary, gaps, and breakdown |
| `ims` | INVEST Maturity Score — score (0-5), classification, summary, gaps, and breakdown |
| `functional_dimensions` | Array of 10 functional dimensions (D1-D10), each with id, name, score, summary, items, and reasoning |
| `nfr_dimensions` | Array of 3 NFR dimensions (D11-D13), each with id, name, score, summary, and detailed_explanation |
| `has_failures` | Boolean indicating whether any cells failed |
| `failed_cells` | List of cell names that failed (present when `has_failures` is true) |
| `failed_details` | List of `{name, error}` for each failed cell (present when `has_failures` is true) |

## Batch Processing

To calculate BCP for multiple stories, run the script once per file:

```bash
for file in docs/stories/story-*.md; do
  echo "Processing $file..."
  python skills/bcp-calculator-13d/scripts/bcp_calculate_13d.py \
    --file "$file" >> batch_results.json
done
```

The skill agent handles batches automatically — it processes each story sequentially and presents a summary table followed by individual details.

## How the Script Talks to the API

The script uses an async job model to communicate with the local API server:

1. **Submit** — `POST /calculate` with `{"content": "# Title\n\nDescription...", "provider": "openai"}`
2. **Poll** — `GET /status/{job_id}` every 3 seconds until status is `completed` or `failed`
3. **Parse** — extracts BCP total, CMS, IMS, and dimension scores from the result

If any cells fail, the script automatically retries up to 2 more times (3 total attempts).

---

> ## ⚠️ Important: Why the Skill Delegates to the API Server (Instead of Running Prompts Locally)
>
> The BCP 13-dimensions calculation is not a mathematical formula — it consists of **14 independent LLM calls** with specialized prompts that return structured JSON, followed by consolidation and scoring. Running these prompts directly in the skill (i.e., having the agent process them locally) would introduce three significant problems:
>
> ### 1. Local Environment Interference
>
> The agent running on the user's machine may have other tools configured (MCP servers, hooks, custom skills, plugins). During the processing of the 14 prompts, the agent could inadvertently call these tools or interpret the output differently on each execution, introducing variability in the results — the exact opposite of what is needed in a complexity metric.
>
> ### 2. No Control Over Model and Parameters
>
> The API server runs with a configured LLM provider (model, temperature=0, max_tokens) in a dedicated, isolated environment. This ensures determinism and consistency across executions. In the user's local environment, there is no control over which model the agent is using, what temperature is set, or whether system prompts are injecting extra behavior.
>
> ### 3. Scoring Reliability
>
> The `FormulaEvaluator` (AST-based expression evaluator) and the failed-cell retry logic run on the server. Porting all of this to the skill would mean reimplementing this logic in scripts that run in the agent's non-isolated context, subject to the same interference.
>
> ### Current Architecture
>
> The skill does only what it is good at: **identify stories, format input, call the API, and present results**. The heavy computation happens on the server (`run_api_server.py`), which provides:
> - Isolated, dedicated environment
> - Configurable and consistent LLM provider
> - 14-cell pipeline with 3 parallel waves
> - Automatic retry of failed cells
> - Deterministic scoring via `FormulaEvaluator`
>
> ### Recommendation: Host the API on an Internal Cloud
>
> If the goal is to eliminate the step of starting the server locally for each user, the recommendation is to **host the API server on an internal cloud** (e.g., a container on ECS, Cloud Run, or an EC2 instance). In this scenario:
>
> - The skill would point to `--base-url https://bcp-api.internal.example.com` (or equivalent)
> - Users do not need to start anything locally — the skill checks the endpoint and proceeds
> - The team retains full control over model, prompt versions, temperature, and configurations
> - Centralized logging, usage monitoring, and SLA guarantees
> - Updates to prompts or the pipeline are applied in one place, without requiring users to update the skill
>
> This would be a configuration change only (environment variable or `--base-url` parameter) — no code changes needed. The skill already supports this natively.

---

## Troubleshooting

### Common Issues

1. **Server Not Running**:
   - Check that the API server is online: `curl -s http://127.0.0.1:8000/`
   - If offline, start it: `python run_api_server.py`
   - Check that the port is not already in use by another application

2. **Job Not Found (404)**:
   - Jobs are stored in memory — if the server restarts, all jobs are lost
   - Re-run the calculation

3. **Provider Errors**:
   - Ensure the appropriate API keys are properly set in `.env`
   - Check that you have access to the LLM provider you're trying to use

4. **No Relevant Sections Found**:
   - The story `.md` file must contain sections with these exact Portuguese headings: `## Narrativa de Negócio` (Business Narrative), `## Narrativa Técnica` (Technical Narrative), and `## Critérios de Aceite` (Acceptance Criteria)
   - These section names are hardcoded in the script and must match exactly, including accents
   - English-only headings will not be recognized by the script

5. **Calculation Timeout**:
   - The script waits up to 300 seconds for a job to complete
   - Long stories or high server load may cause longer processing times
   - Check the server logs for any error messages

6. **Failed Cells After Retries**:
   - If `has_failures` is still true after 3 attempts, some LLM cells failed
   - Check the `failed_cells` and `failed_details` fields for which cells failed
   - Retry later or verify that the LLM provider is stable
