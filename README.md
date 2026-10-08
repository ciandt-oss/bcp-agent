# BCP Calculator

A tool for calculating Business Complexity Points (BCP) of user stories using LangChain with support for multiple LLM providers. The recommended model is `gpt-6-luna` with `temperature=0`, tested with the 13-dimensions pipeline to produce the lowest Coefficient of Variation (CV) across repeated executions.

> **Note:** The next version will feature broader model family coverage, expanding support and testing across additional LLM families beyond the current OpenAI-compatible providers.

> **Note:** The BCP 13D skill (`bcp-calculator-13d`) is currently in **alpha testing**. Scoring results may vary between runs. Feedback and bug reports are welcome.

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

The recommended model is `gpt-6-luna` with `temperature=0`. This combination was tested with the 13-dimensions pipeline and produces the lowest Coefficient of Variation (CV) across repeated executions. All providers default to this model unless overridden via environment variables.

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
   cp .env.flow.example .env
   ```
   
   Then edit the `.env` file to add your API keys for the providers you want to use.

   Provider-specific example files are also available:
   - `.env.llm-provider.example` — LLM local gateway (no API key needed)
   - `.env.openai.example` — OpenAI direct (api.openai.com)
   - `.env.anthropic.example` — Anthropic Claude
   - `.env.flow.example` — Flow OpenAI (LiteLLM proxy, JWT token)
   - `.env.bedrock.example` — AWS Bedrock (native Converse API)
   - `.env.openrouter.example` — OpenRouter (OpenAI-compatible aggregator)
   - `.env.huggingface.example` — HuggingFace (OpenAI-compatible router)

   Copy the one that matches your setup, e.g.:
   ```
   cp .env.flow.example .env
   ```

## LLM Providers

The BCP Calculator supports six LLM providers, selected via the `--provider` flag. Each requires its own set of environment variables in your `.env` file.

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

Uses `SimpleLLMProvider` (httpx-based) to connect to any OpenAI-compatible endpoint. This is the default provider.

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | Your OpenAI API key (or placeholder for local gateways) |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | Base URL for the endpoint (use for local gateways, Ollama, etc.) |
| `OPENAI_MODEL_NAME` | No | `gpt-6-luna` | Model to use |

**.env example:**
```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-6-luna
```

**Usage:**
```bash
python run_cli.py story.md --provider openai
```

---

### Anthropic Claude (`--provider claude`)

Connects directly to the Anthropic API using `langchain-anthropic`.

Configured for maximum determinism in BCP scoring:
- `temperature=0` — no sampling randomness
- `thinking={"type": "disabled"}` — disables adaptive thinking (always-on by default in Claude models)
- `reasoning_effort="low"` — minimizes reasoning variation

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | — | Your Anthropic API key |
| `ANTHROPIC_BASE_URL` | No | `https://api.anthropic.com` | Base URL (use for proxies or Anthropic-compatible endpoints) |
| `ANTHROPIC_MODEL_NAME` | No | `claude-sonnet-4-6` | Model to use |
| `ANTHROPIC_THINKING` | No | `{"type": "disabled"}` | Thinking config JSON — disables adaptive thinking for determinism |
| `ANTHROPIC_REASONING_EFFORT` | No | `low` | Reasoning effort (`low`, `medium`, `high`, `xhigh`, `max`) |

**.env example:**
```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL_NAME=claude-sonnet-4-6
ANTHROPIC_THINKING={"type": "disabled"}
ANTHROPIC_REASONING_EFFORT=low
```

**Usage:**
```bash
python run_cli.py story.md --provider claude
```

---

### Flow OpenAI (`--provider flow-openai`)

Routes requests through [CI&T Flow](https://flow.ciandt.com)'s LiteLLM proxy. Authenticates using a JWT token sent as `Authorization: Bearer` header.

| Variable | Required | Default | Description |
|---|---|---|---|
| `FLOW_LLM_LITE_HOST` | Yes | — | Flow LiteLLM proxy URL (e.g. `https://flow.ciandt.com/flow-litellm`) |
| `FLOW_LITELLM_TOKEN_JWT` | Yes | — | JWT token for the LiteLLM proxy (sent as `Authorization: Bearer`) |
| `FLOW_TENANT` | No | `flowteam` | Tenant identifier sent in the `FlowTenant` header |
| `FLOW_AGENT` | No | `bcp-opensource` | Agent identifier sent in the `FlowAgent` header |
| `FLOW_LITELLM_MODEL_NAME` | No | `gpt-6-luna` | Model to use (legacy alias: `FLOW_MODEL_NAME`) |
| `FLOW_LITELLM_MAX_TOKENS` | No | `4096` | Maximum tokens to generate (legacy alias: `FLOW_MAX_TOKENS`) |
| `FLOW_LITELLM_TEMPERATURE` | No | `0` | Sampling temperature |

**.env example:**
```env
FLOW_LLM_LITE_HOST=https://flow.ciandt.com/flow-litellm
FLOW_LITELLM_TOKEN_JWT=your_jwt_token_here
FLOW_TENANT=flowteam
FLOW_AGENT=bcp-opensource
FLOW_LITELLM_MODEL_NAME=gpt-6-luna
```

**Usage:**
```bash
python run_cli.py story.md --provider flow-openai
```

---

### AWS Bedrock (`--provider bedrock`)

Calls the [AWS Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) directly using `httpx` (no boto3, no langchain). The provider name remains `bedrock` for backward compatibility.

**Endpoint:** `POST https://bedrock-runtime.{region}.amazonaws.com/model/{modelId}/converse`

**Auth:** Uses `aws_bedrock_token_generator.provide_token()` (auto-refreshed bearer token) by default. Alternatively, set `AWS_BEARER_TOKEN_BEDROCK` to supply a static token.

| Variable | Required | Default | Description |
|---|---|---|---|
| `AWS_BEDROCK_REGION` | No | `us-east-1` | AWS region for the Bedrock runtime endpoint |
| `AWS_BEARER_TOKEN_BEDROCK` | No | — | Static bearer token (overrides token generator) |
| `FLOW_BEDROCK_MODEL_NAME` | No | `openai.gpt-5.6-luna` | Bedrock model ID |
| `FLOW_BEDROCK_MAX_TOKENS` | No | `4096` | Maximum tokens to generate |
| `FLOW_BEDROCK_TEMPERATURE` | No | `0` | Sampling temperature |

**.env example:**
```env
AWS_BEDROCK_REGION=us-east-1
FLOW_BEDROCK_MODEL_NAME=openai.gpt-5.6-luna
FLOW_BEDROCK_MAX_TOKENS=4096
FLOW_BEDROCK_TEMPERATURE=0
```

**Usage:**
```bash
python run_cli.py story.md --provider bedrock
```

---

### OpenRouter (`--provider openrouter`)

Uses `SimpleLLMProvider` (httpx-based) to connect to the [OpenRouter](https://openrouter.ai) API, which aggregates multiple LLM providers behind an OpenAI-compatible Chat Completions endpoint.

**Endpoint:** `POST https://openrouter.ai/api/v1/chat/completions`

**Auth:** `Authorization: Bearer {OPENROUTER_API_KEY}`

Optional attribution headers (`HTTP-Referer`, `X-Title`) are sent when `OPENROUTER_SITE_URL` and `OPENROUTER_APP_TITLE` are set.

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENROUTER_API_KEY` | Yes | — | Your OpenRouter API key |
| `OPENROUTER_MODEL_NAME` | No | `openai/gpt-6-luna` | Model to use (OpenRouter model identifier) |
| `OPENROUTER_SITE_URL` | No | — | Site URL sent as `HTTP-Referer` header (for app attribution) |
| `OPENROUTER_APP_TITLE` | No | — | App title sent as `X-Title` header (for app attribution) |

**.env example:**
```env
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL_NAME=openai/gpt-6-luna
OPENROUTER_SITE_URL=https://example.com
OPENROUTER_APP_TITLE=BCP Calculator
```

**Usage:**
```bash
python run_cli.py story.md --provider openrouter
```

---

### HuggingFace (`--provider huggingface`)

Uses `SimpleLLMProvider` (httpx-based) to connect to the [HuggingFace](https://huggingface.co) inference router, which exposes an OpenAI-compatible Chat Completions endpoint.

**Endpoint:** `POST https://router.huggingface.co/v1/chat/completions`

**Auth:** `Authorization: Bearer {HF_TOKEN}`

| Variable | Required | Default | Description |
|---|---|---|---|
| `HF_TOKEN` | Yes | — | Your HuggingFace access token |
| `HF_MODEL_NAME` | No | `zai-org/GLM-5.2:novita` | Model to use (HuggingFace model identifier) |

**.env example:**
```env
HF_TOKEN=hf_...
HF_MODEL_NAME=zai-org/GLM-5.2:novita
```

**Usage:**
```bash
python run_cli.py story.md --provider huggingface
```

---

## Integration Options

The BCP Calculator can be used in six different ways:

1. **[Command Line Interface (CLI)](docs/usage/cli_usage.md)** - Use as a traditional command-line tool
2. **[HTTP API](docs/usage/http_api_usage.md)** - Run as a RESTful API service
3. **[Model Context Protocol (MCP)](docs/usage/mcp_usage.md)** - Use with any MCP client (stdio or streamable HTTP)
4. **[Python SDK](docs/usage/sdk_usage.md)** - Import and use as a Python library
5. **[Claude Code Skill (13D)](docs/usage/skill_usage.md)** - Claude Code skill that calls the local API server for 13-dimensions BCP calculation
6. **[Claude Code Skill (Story Writing Coach)](#skills)** - Claude Code skill that reviews and coaches story writing against the 13 BCP dimensions

Choose the integration option that best fits your workflow. Click the links above for detailed usage instructions for each option.

## Basic CLI Usage

Run the BCP Calculator with a user story file:

```
python run_cli.py path/to/user_story.md
```

### Options

- `--log-level`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is INFO.
- `--output-file`: Path to save the output results. If not provided, results are printed to stdout.
- `--provider`: LLM provider to use (openai, claude, flow-openai, bedrock, openrouter, huggingface). Default is openai.
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
- `run_mcp.py`: MCP server launcher (stdio)
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
  - `bedrock_provider.py`: Native AWS Bedrock Converse API provider using httpx
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
  - `skill_usage.md`: Claude Code skill usage guide (13D)
  - `README.md`: Index of usage guides
- `README.md`: Project documentation
- `LICENSE`: License information

### Skills
- `skills/`: Claude Code skills
  - `bcp-calculator-13d/`: BCP 13D skill — calls the local API server to calculate BCP
    - `SKILL.md`: Skill instructions for the agent
    - `scripts/bcp_calculate_13d.py`: Script that submits stories to the local API and parses results
  - `bcp-story-writing-coach/`: Story writing coach skill — reviews stories against the 13 BCP dimensions
    - `SKILL.md`: Skill instructions for the agent
    - `rules/`: 13 dimension rule files (D1–D13)

## Skills

The `skills/` directory contains **Claude Code skills** that provide agent-driven interfaces to the BCP Calculator.

### BCP Calculator 13D Skill

> **⚠️ Alpha Testing:** This skill is currently in alpha. Scoring results may vary between run.

The `skills/bcp-calculator-13d/` skill calculates BCP 13 dimensions by calling the **local API server** (`run_api_server.py`). It is not standalone — it requires the API server to be running.

#### Structure

```
skills/bcp-calculator-13d/
├── SKILL.md                              # Skill instructions for the agent
└── scripts/
    └── bcp_calculate_13d.py              # API client script (stdlib only)
```

#### How It Works

When the skill is triggered, the agent:

1. **Checks the local server** — verifies that `run_api_server.py` is running on `http://127.0.0.1:8000`
2. **Identifies stories** — from inline text, a `.md` file, or a folder of `story-*.md` files
3. **Calls the bundled script** — `bcp_calculate_13d.py` submits each story to the local API (`POST /calculate`) and polls for results (`GET /status/{job_id}`)
4. **Presents the results** — formats the JSON output into Markdown tables with BCP Total, CMS, IMS, and all 13 dimension scores

No authentication token is required — the local API server accepts requests directly.

#### `bcp_calculate_13d.py` — API Client Script

A standalone Python script (stdlib only — no pip packages required) that:

| Action | Purpose |
|--------|---------|
| Submit job | `POST /calculate` with story content and provider |
| Poll status | `GET /status/{job_id}` every 3 seconds until completed or failed |
| Parse result | Extracts BCP total, CMS, IMS, and 13 dimension scores from the response |
| Retry | Automatically retries up to 2 more times if any cells fail |

```bash
# Calculate from a story file
python skills/bcp-calculator-13d/scripts/bcp_calculate_13d.py \
  --file tests/data/story1.md --provider openai

# Calculate from inline text
python skills/bcp-calculator-13d/scripts/bcp_calculate_13d.py \
  --title "User Story: Add Payment Method" \
  --description "## Narrativa de Negócio (Business Narrative)\n\nAs a user, I want to..."
```

#### Key Features

- **Requires local API server** — start with `python run_api_server.py` before using the skill
- **No authentication** — the local API server does not require a Bearer token
- **Stdlib only** — the script uses only Python standard library (no pip packages)
- **Provider selection** — choose between `openai`, `claude`, `flow-openai`, `bedrock`, `openrouter`, and `huggingface` via `--provider`
- **Automatic retry** — retries failed cells up to 2 more times (3 total attempts)

For detailed usage instructions, see the [Skill Usage Guide](docs/usage/skill_usage.md).

### BCP Story Writing Coach Skill

The `skills/bcp-story-writing-coach/` skill rewrites existing user stories using the **13 BCP dimension scoring rules** as a writing guide. It does **not** calculate BCP, does **not** score, and does **not** invent requirements — it only makes explicit what is already implicit or missing, via a gap-driven questionnaire.

Statistical analysis of BCP batches showed that a significant portion of scoring instability comes from **story writing quality**, not from the model or prompt. No prompt adjustment can fix a poorly written story — the cause must be addressed at the source.

#### Structure

```
skills/bcp-story-writing-coach/
├── SKILL.md                              # Skill instructions for the agent
└── rules/
    ├── README.md                         # Rules index + how to read
    ├── d01-business-rules.md             # D1  · Business Rules
    ├── d02-interface-elements.md         # D2  · Interface Elements
    ├── d03-boundaries.md                 # D3  · Boundaries
    ├── d04-roles-permissions.md          # D4  · Roles & Permissions
    ├── d05-solution-variabilities.md     # D5  · Solution Variabilities
    ├── d06-domain-entities.md            # D6  · Domain Entities
    ├── d07-new-domain-entities.md        # D7  · New Domain Entities
    ├── d08-background-processes.md       # D8  · Background Processes
    ├── d09-notifications.md              # D9  · Notifications
    ├── d10-audits.md                     # D10 · Audits
    ├── d11-quality-attributes.md         # D11 · Quality Attributes (NFR)
    ├── d12-security-compliance.md        # D12 · Security & Compliance (NFR)
    └── d13-ux-accessibility.md           # D13 · UX & Accessibility (NFR)
```

Each rule file describes, in pedagogical format (without exposing scoring tiers or numeric values), what the BCP evaluator looks for in that dimension — and therefore what the story needs to make explicit to be well assessed.

#### How It Works

When the skill is triggered, the agent:

1. **Receives the story** — from inline text, a `.md` file, or a folder of stories
2. **Static analysis** — determines for each of the 13 dimensions whether it is relevant and covered, relevant with gaps, or not relevant. Uses the `rules/` files as a reading guide (progressive disclosure — only loads files for candidate dimensions)
3. **Gap-driven questionnaire** — presents gaps to the user in rounds of ~5 questions, prioritized by impact on the assessment. Includes a fallback relevance checklist for stories too vague to detect dimensions with confidence
4. **Rewrites the story** — incorporates explicit content, implicit content made explicit, and questionnaire answers. Does not add requirements that don't come from these three sources
5. **Presents the output** — 4 blocks: annotated diff, clean version, rationale per dimension, and unaddressed gaps table

#### Key Principle — No Invention

Every change in the rewritten story must be traceable to one of:
1. **Explicit content** — already written in the original story
2. **Implicit content** — direct and obvious deduction from the text
3. **User response** — obtained via the gap-driven questionnaire

Gaps that the user did not answer are explicitly marked as "unaddressed" in the output, with the impact explained. The skill never fills a gap on its own.

#### Triggers

The skill is designed for pt-BR users (Flow/CI&T). Triggers are in Portuguese by design:

- "Reescreve essa story pra melhorar a qualidade antes de calcular o BCP"
- "Revisa a story `docs/stories/story-042.md` com o story writing coach"
- "Essa story tá instável no BCP 13d, melhora a escrita dela"
- "bcp-story-writing-coach" (direct invocation by name)

#### Key Features

- **No BCP calculation** — this skill improves writing quality, it does not score or calculate BCP. Use `bcp-calculator-13d` for that
- **No invention** — every change is traceable to explicit content, implicit deduction, or user answers
- **Gap-driven** — the questionnaire targets only the gaps that matter for the relevant dimensions
- **Scope gate** — detects epics disguised as stories and recommends splitting before rewriting
- **Contradiction handling** — treats internal contradictions as blockers, not as ordinary gaps
- **Language-preserving** — the output follows the language of the original story

For more details, see the skill's `SKILL.md`.

## License

[MIT License](LICENSE)
