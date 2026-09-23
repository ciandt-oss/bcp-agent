# BCP Calculator

A tool for calculating Business Complexity Points (BCP) of user stories using LangChain with support for multiple LLM providers. The recommended model is `mistral-small-2503` with `temperature=0`, tested with the 13-dimensions pipeline to produce the lowest Coefficient of Variation (CV) across repeated executions.

> **Note:** The next version will feature broader model family coverage, expanding support and testing across additional LLM families beyond the current OpenAI-compatible providers.

## Overview

The BCP Calculator analyzes user stories and calculates their Business Complexity Points based on 13 dimensions:

**10 Functional dimensions:**
1. Business Rules
2. Interface Elements
3. Solution Variabilities
4. Domain Entities
5. New Domain Entities
6. Roles & Permissions
7. Boundaries
8. Background Processes
9. Notifications
10. Audits

**3 NFR (Non-Functional Requirements) dimensions:**

11. Quality Attributes
12. Security & Compliance
13. User Experience & Accessibility

**2 Maturity evaluations (complementary, not part of BCP total):**
- Complexity Maturity (0–5 score)
- INVEST Maturity (0–5 score)

The application orchestrates 14 cells across 3 parallel execution waves:
- **Wave 1**: 10 functional dimension cells + 1 NFR cell (executed in parallel via ThreadPoolExecutor)
- **Wave 2**: 1 aggregator cell (depends on the 10 functional scores from Wave 1)
- **Wave 3**: 2 maturity evaluation cells (depend on the aggregator + NFR results from Waves 1–2)

**Total BCP** = `functional_aggregator.score + nfr_scoring.score`

## Recommended Model

The recommended model is `mistral-small-2503` with `temperature=0`. This combination was tested with the 13-dimensions pipeline and produces the lowest Coefficient of Variation (CV) across repeated executions. All providers default to this model unless overridden via environment variables.

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd bcp-agent
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

**Key dependencies (pinned in `requirements.txt`):**

| Package | Version |
|---------|---------|
| langchain | 1.4.2 |
| langchain-core | 1.6.3 |
| langchain-openai | 1.6.2 |
| langchain-anthropic | 1.7.2 |
| openai | 3.16.2 |
| anthropic | 1.7.0 |
| jinja2 | 3.1.6 |
| pydantic | 2.13.5 |
| fastapi | 0.141.1 |

3. Set up your environment variables:
   ```
   cp .env.example .env
   ```
   
   Then edit the `.env` file to add your API keys for the providers you want to use (OpenAI and/or Anthropic).

## LLM Providers

The BCP Calculator supports four LLM providers, selected via the `--provider` flag. Each requires its own set of environment variables in your `.env` file.

---

### SimpleLLMProvider (Default — Recommended)

`SimpleLLMProvider` is the default provider for all OpenAI-compatible endpoints. It uses `httpx` directly instead of the `openai` SDK, which avoids compatibility issues with local gateways (Flow, Ollama, vLLM, etc.) that hang when receiving `Authorization` headers with placeholder tokens.

**When to use:**
- Flow gateway (local) — no API key needed
- Ollama, vLLM, LM Studio (local) — no API key needed
- OpenAI direct (api.openai.com) — with real API key
- Any OpenAI-compatible endpoint

**Auth behavior:** Sends `Authorization: Bearer <key>` when a real API key is provided. Omits the header when the key is a placeholder (`test-key`, `dummy`, `none`, empty string).

The langchain-based providers (`OpenAIProvider`, `ClaudeProvider`, `FlowLiteLLMProvider`) remain available but are not the default. Use them when you need langchain-specific features.

---

### OpenAI (`--provider openai`)

Connects directly to the OpenAI API using `langchain-openai`.

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | Your OpenAI API key |
| `OPENAI_MODEL_NAME` | No | `mistral-small-2503` | Model to use |

**.env example:**
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL_NAME=mistral-small-2503
```

**Usage:**
```bash
python run_cli.py story.md --provider openai
```

---

### Anthropic Claude (`--provider claude`)

Connects directly to the Anthropic API using `langchain-anthropic`.

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | — | Your Anthropic API key |
| `ANTHROPIC_MODEL_NAME` | No | `mistral-small-2503` | Model to use |

**.env example:**
```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL_NAME=mistral-small-2503
```

**Usage:**
```bash
python run_cli.py story.md --provider claude
```

---

### Flow OpenAI (`--provider flow-openai`)

> **Note:** This is the langchain-based provider (`FlowLiteLLMProvider`). For Flow gateway usage, `SimpleLLMProvider` (the default `openai` provider) is recommended instead.

Routes requests through [CI&T Flow](https://flow.ciandt.com)'s LiteLLM proxy. Authenticates via Azure AD B2C OAuth2 client_credentials grant (the token is sent as a `FlowToken` header).

| Variable | Required | Default | Description |
|---|---|---|---|
| `FLOW_LLM_LITE_HOST` | Yes | — | Flow LiteLLM proxy URL (e.g. `https://flow.ciandt.com/flow-litellm`) |
| `B2C_TENANT` | No | `citflowdevb2c.onmicrosoft.com` | Azure B2C tenant |
| `FLOW_LITELLM_CLIENT_ID` | Yes* | — | Azure B2C app registration client ID (*falls back to `CLIENT_ID`) |
| `FLOW_LITELLM_CLIENT_SECRET` | Yes* | — | Azure B2C app registration client secret (*falls back to `CLIENT_SECRET`) |
| `FLOW_LITELLM_SCOPE` | Yes** | — | Azure B2C scope URI for flow-litellm app registration (**or via `ACCESS_SCOPES` JSON with `flow-litellm` key) |
| `FLOW_TENANT` | No | `flowteam` | Tenant identifier sent in the `FlowTenant` header |
| `FLOW_AGENT` | No | `bcp-opensource` | Agent identifier sent in the `FlowAgent` header |
| `FLOW_LITELLM_MODEL_NAME` | No | `mistral-small-2503` | Model to use |
| `FLOW_LITELLM_MAX_TOKENS` | No | `4096` | Maximum tokens to generate |
| `FLOW_LITELLM_TEMPERATURE` | No | `0` | Sampling temperature |

**.env example:**
```env
FLOW_LLM_LITE_HOST=https://flow.ciandt.com/flow-litellm
B2C_TENANT=citflowdevb2c.onmicrosoft.com
FLOW_LITELLM_CLIENT_ID=my-client-id
FLOW_LITELLM_CLIENT_SECRET=my-client-secret
FLOW_LITELLM_SCOPE=https://citflowdevb2c.onmicrosoft.com/citflowdev_app_flow-litellm_sys_sa/.default
FLOW_TENANT=myteam
FLOW_AGENT=bcp-opensource
FLOW_LITELLM_MODEL_NAME=mistral-small-2503
```

**Usage:**
```bash
python run_cli.py story.md --provider flow-openai
```

---

## Integration Options

The BCP Calculator can be used in five different ways:

1. **[Command Line Interface (CLI)](docs/usage/cli_usage.md)** - Use as a traditional command-line tool
2. **[HTTP API](docs/usage/http_api_usage.md)** - Run as a RESTful API service
3. **[Model Context Protocol (MCP)](docs/usage/mcp_usage.md)** - Use with any MCP client (stdio or streamable HTTP)
4. **[Python SDK](docs/usage/sdk_usage.md)** - Import and use as a Python library
5. **[MCP Server](docs/usage/mcp_usage.md)** - Run the MCP as a standalone server (stdio or HTTP transport)

Choose the integration option that best fits your workflow. Click the links above for detailed usage instructions for each option.

## Basic CLI Usage

Run the BCP Calculator with a user story file:

```
python run_cli.py path/to/user_story.md
```

### Options

- `--log-level`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is INFO.
- `--output-file`: Path to save the output results. If not provided, results are printed to stdout.
- `--provider`: LLM provider to use (openai, claude, flow-openai, flow-bedrock). Default is openai.
- `--format`: Output format (text or json). Default is json.
- `--max-workers`: Maximum number of parallel threads per wave (default: 5). Controls the ThreadPoolExecutor parallelism for Wave 1 cells.

For more detailed CLI usage information, see the [CLI Usage Guide](docs/usage/cli_usage.md).

## Output

The output includes:
- Results from each of the 14 cells in the pipeline
- Final Business Complexity Points (BCP), calculated as `functional_aggregator.score + nfr_scoring.score`
- Breakdown of points by dimension (10 functional dimensions + NFR)
- Maturity evaluation scores (Complexity and INVEST, complementary — not included in BCP total)

### Sample JSON Output

```json
{
  "story_name": "User Story: Add Payment Method",
  "cells": {
    "functional_business_rules": {"score": 6, "raw_output": {}},
    "functional_interface_elements": {"score": 11, "raw_output": {}},
    "functional_solution_variabilities": {"score": 1, "raw_output": {}},
    "functional_domain_entities": {"score": 2, "raw_output": {}},
    "functional_new_domain_entities": {"score": 0, "raw_output": {}},
    "functional_roles_permissions": {"score": 3, "raw_output": {}},
    "functional_boundaries": {"score": 5, "raw_output": {}},
    "functional_background_processes": {"score": 3, "raw_output": {}},
    "functional_notifications": {"score": 1, "raw_output": {}},
    "functional_audits": {"score": 1, "raw_output": {}},
    "nfr_scoring": {"score": 4, "raw_output": {}},
    "functional_aggregator": {"score": 33, "raw_output": {}},
    "complexity_maturity": {"score": 3, "raw_output": {}},
    "invest_maturity": {"score": 4, "raw_output": {}}
  },
  "breakdown": {
    "business_rules": 6,
    "interface_elements": 11,
    "solution_variabilities": 1,
    "domain_entities": 2,
    "new_domain_entities": 0,
    "roles_permissions": 3,
    "boundaries": 5,
    "background_processes": 3,
    "notifications": 1,
    "audits": 1,
    "nfr": 4
  },
  "total_bcp": 37,
  "maturity": {
    "complexity": 3,
    "invest": 4
  }
}
```

## Project Structure

### Core Application Files
- `run_cli.py`: Entry point wrapper for the CLI application
- `run_api_server.py`: HTTP API server launcher
- `run_mcp_server.py`: MCP server launcher (stdio)
- `run_mcp_http_server.py`: MCP server launcher (HTTP)
- `run_comparison.py`: Tool for comparing BCP results between different providers
- `src/main.py`: Main CLI implementation
- `src/api/`: HTTP API implementation
- `src/mcp/`: MCP implementation
- `src/sdk/`: SDK implementation
- `src/bcp/`: Core package containing BCP calculator functionality
  - `__init__.py`: Package exports (BCPCalculator, PromptHandler, FormulaEvaluator, LLMProvider, etc.)
  - `bcp_calculator.py`: Core logic for orchestrating the 14-cell, 3-wave parallel pipeline
  - `formula_evaluator.py`: Safe AST-based formula evaluator for dimension scoring
  - `prompt_handler.py`: Handles loading and processing `.md` prompt templates from subdirectories, story dict bindings, and JSON parsing
  - `llm_providers.py`: Provider abstraction for different LLM services
  - `simple_llm_provider.py`: Default LLM provider using httpx directly for OpenAI-compatible endpoints
  - `logger.py`: Custom logging functionality
  - `prompts/thirteen/`: Directory containing the 13-dimensions prompt templates (`.md` files)
    - `functional/`: 10 functional dimension prompts + aggregator prompt
    - `functional-scoring.md`: V1 monolithic scoring prompt (kept for comparison)
    - `nfr-scoring.md`: NFR scoring prompt (3 NFR dimensions)
    - `complexity-maturity.md`: Complexity maturity evaluation prompt
    - `invest-maturity.md`: INVEST maturity evaluation prompt

### Testing and Utilities
- `tests/test_bcp_calculator.py`: Unit tests for the calculator
- `tests/test_providers.py`: Test script for LLM providers
- `tests/compare_providers.py`: Script to compare results between providers

### Documentation
- `docs/usage/`: Directory containing usage guides for each integration option
  - `cli_usage.md`: CLI usage guide
  - `http_api_usage.md`: HTTP API usage guide
  - `mcp_usage.md`: MCP usage guide
  - `sdk_usage.md`: SDK usage guide
- `README.md`: Project documentation
- `LICENSE`: License information

### Standalone Skill
- `skill/`: Standalone Claude Code skill (no API, no SDK)
  - `bcp-calculator-13d/`: BCP 13D skill with prompts + pipeline script

## Standalone Skill

The `skill/bcp-calculator-13d/` directory contains a **self-contained Claude Code skill** that calculates BCP 13 dimensions without any external API, SDK, or provider configuration. The agent (Claude) processes the prompts directly — Claude IS the LLM.

### Structure

```
skill/bcp-calculator-13d/
├── SKILL.md                              # Skill instructions for the agent
├── scripts/
│   └── bcp_pipeline.py                   # Score calculation & consolidation (stdlib only)
└── prompts/
    └── thirteen/
        ├── functional/
        │   ├── business-rules.md
        │   ├── interface-elements.md
        │   ├── solution-variabilities.md
        │   ├── domain-entities.md
        │   ├── new-domain-entities.md
        │   ├── roles-permissions.md
        │   ├── boundaries.md
        │   ├── background-processes.md
        │   ├── notifications.md
        │   ├── audits.md
        │   └── aggregator.md
        ├── nfr-scoring.md
        ├── complexity-maturity.md
        └── invest-maturity.md
```

### How It Works

When the skill is triggered, the agent:

1. **Identifies stories** — from inline text, a `.md` file, or a folder of `story-*.md` files
2. **Groups stories into waves** — 3-5 stories per wave for batch processing
3. **Executes the 3-wave pipeline** for each story:
   - **Wave 1:** Processes 11 prompts (10 functional + NFR) — the agent reads each `.md` prompt, fills in `{{story.key}}`, `{{story.summary}}`, `{{story.description}}`, and processes it as the LLM
   - **Wave 2:** Processes the aggregator prompt with `{{dim_*}}` bindings (numeric scores from Wave 1)
   - **Wave 3:** Processes 2 maturity prompts with `{{functional_scoring}}` and `{{nfr_scoring}}` bindings (full JSON from Waves 1-2)
4. **Calculates scores** — uses `bcp_pipeline.py` to apply the 14 score formulas
5. **Consolidates and presents** — produces BCP Total, CMS, IMS, and all 13 dimension scores

### `bcp_pipeline.py` — Score Calculation Utility

A standalone Python script (stdlib only — no pip packages required) with 4 commands:

| Command | Purpose |
|---------|---------|
| `score` | Calculates a single cell's score from its JSON output |
| `aggregate` | Calculates the aggregator score from 10 dimension bindings |
| `consolidate` | Consolidates all 14 cell outputs of a story into structured JSON |
| `aggregate-stories` | Aggregates multiple stories into a summary report |

```bash
# Calculate a cell's score
python scripts/bcp_pipeline.py score --cell business_rules --output '{"scores_extracted": [3, 5]}'

# Calculate aggregator score
python scripts/bcp_pipeline.py aggregate --bindings '{"dim_business_rules": 8, ...}'

# Consolidate a complete story
python scripts/bcp_pipeline.py consolidate --input story_results.json

# Aggregate multiple stories
python scripts/bcp_pipeline.py aggregate-stories --input all_stories.json
```

### Key Features

- **Fully agnostic** — no provider, model, API key, or endpoint configuration needed
- **Zero dependencies** — only Python stdlib (no pip packages for the script; prompts are processed by the agent)
- **Self-contained** — owns its copy of the 14 prompts; does not import from `src/bcp/`
- **Deterministic** — the SKILL.md enforces absolute determinism: return exactly the JSON each prompt specifies, no variations or abstractions
- **Wave-based** — 3 waves per story (11 + 1 + 2 cells); multiple stories grouped in waves of 3-5

## License

[MIT License](LICENSE)
