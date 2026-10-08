# AGENTS.md — bcp-agent

## Project Identity

**bcp-agent** is a Python tool that calculates Business Complexity Points (BCP) for user stories using a 14-cell, 3-wave parallel pipeline with LLM providers. It supports CLI, HTTP API, MCP server, Python SDK, and two Claude Code skills.

**Language:** Python 3.10+
**Framework:** LangChain 1.4.x + FastAPI
**Package name:** `bcp-calculator` (v0.1.0)
**License:** MIT

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt   # for testing

# 2. Configure environment
cp .env.flow.example .env             # then edit .env with your API keys

# 3. Run the CLI
python run_cli.py tests/data/story1.md

# 4. Or start the API server
python run_api_server.py              # http://127.0.0.1:8000

# 5. Run tests
pytest
```

## Project Structure

```
bcp-agent/
├── run_cli.py                    # CLI entry point
├── run_api_server.py             # HTTP API server launcher
├── run_mcp.py                    # MCP server (stdio)
├── run_mcp_http_server.py        # MCP server (HTTP)
├── run_comparison.py             # Provider comparison tool
├── src/
│   ├── main.py                   # CLI implementation
│   ├── api/                      # FastAPI HTTP API
│   │   ├── server.py             # App + endpoints (/calculate, /status/{job_id})
│   │   └── models.py             # Pydantic models (StoryRequest, JobStatus)
│   ├── bcp/                      # Core BCP calculator
│   │   ├── bcp_calculator.py     # 14-cell, 3-wave pipeline orchestrator
│   │   ├── formula_evaluator.py  # Safe AST-based scoring formulas
│   │   ├── prompt_handler.py     # .md prompt template loading + Jinja2 binding
│   │   ├── llm_providers.py      # LangChain provider abstraction
│   │   ├── simple_llm_provider.py # Default httpx-based provider (OpenAI-compatible)
│   │   ├── bedrock_provider.py   # Native AWS Bedrock Converse API provider (httpx)
│   │   ├── logger.py             # Custom logging + StepLogger
│   │   └── prompts/thirteen/     # 14 prompt templates (.md files)
│   └── sdk/                      # Python SDK
│       └── client.py             # BCPClient class
├── skills/                       # Claude Code skills
│   ├── bcp-calculator-13d/       # BCP 13D skill (calls local API)
│   └── bcp-story-writing-coach/  # Story writing coach skill (reviews stories)
├── tests/
│   ├── data/                     # 15 sample stories (story1.md–story15.md)
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── test_bcp_calculator.py    # Calculator tests
│   ├── test_providers.py         # Provider tests
│   └── test_sdk.py               # SDK tests
├── docs/usage/                   # Usage guides (CLI, HTTP, MCP, SDK, Skill)
├── requirements.txt              # Pinned dependencies
├── requirements-dev.txt          # Dev dependencies (pytest, coverage)
├── pyproject.toml                # black, isort, mypy, pytest config
└── setup.py                      # Package setup
```

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.10+ |
| LLM Orchestration | LangChain | 1.4.2 |
| HTTP API | FastAPI + Uvicorn | 0.141.1 / 0.53.0 |
| Validation | Pydantic | 2.13.5 |
| Templates | Jinja2 | 3.1.6 |
| Testing | pytest + pytest-cov | 8.3.3 / 5.0.0 |
| Formatting | black | line-length 100 |
| Import sorting | isort | black profile, line-length 100 |
| Type checking | mypy | python 3.10, strict |
| HTTP Client | httpx | (via SimpleLLMProvider) |
| MCP | mcp[cli] | latest |

## LLM Providers

| Provider | Flag | When to use |
|----------|------|-------------|
| OpenAI (default) | `--provider openai` | OpenAI API or any OpenAI-compatible endpoint |
| Claude | `--provider claude` | Anthropic API directly |
| Flow OpenAI | `--provider flow-openai` | CI&T Flow LiteLLM proxy (JWT auth) |
| AWS Bedrock | `--provider bedrock` | Native AWS Bedrock Converse API (httpx, no boto3) |
| OpenRouter | `--provider openrouter` | OpenRouter aggregator (OpenAI-compatible, SimpleLLMProvider) |
| HuggingFace | `--provider huggingface` | HuggingFace inference router (OpenAI-compatible, SimpleLLMProvider) |

**Recommended model:** `gpt-6-luna` with `temperature=0` (lowest CV across repeated runs).

### Environment Variables

Copy one of the `.env.*.example` files to `.env` and fill in your API keys:

| File | Provider |
|------|----------|
| `.env.openai.example` | OpenAI direct |
| `.env.anthropic.example` | Anthropic Claude |
| `.env.flow.example` | Flow LiteLLM proxy |
| `.env.bedrock.example` | AWS Bedrock (native) |
| `.env.openrouter.example` | OpenRouter (OpenAI-compatible aggregator) |
| `.env.huggingface.example` | HuggingFace (OpenAI-compatible router) |
| `.env.llm-provider.example` | Local LLM gateway (no API key) |

Key variables per provider:

**OpenAI:** `OPENAI_API_KEY`, `OPENAI_BASE_URL` (optional), `OPENAI_MODEL_NAME` (default: `gpt-6-luna`)

**Claude:** `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL` (optional), `ANTHROPIC_MODEL_NAME` (default: `claude-sonnet-4-6`)

**Flow OpenAI:** `FLOW_LLM_LITE_HOST`, `FLOW_LITELLM_TOKEN_JWT`, `FLOW_TENANT` (optional), `FLOW_AGENT` (optional), `FLOW_LITELLM_MODEL_NAME` (optional, default: `gpt-6-luna`), `FLOW_LITELLM_MAX_TOKENS` (optional, default: `4096`), `FLOW_LITELLM_TEMPERATURE` (optional, default: `0`)

**AWS Bedrock (native):** `AWS_BEDROCK_REGION` (optional, default: `us-east-1`), `AWS_BEARER_TOKEN_BEDROCK` (optional — static token, otherwise uses `aws_bedrock_token_generator.provide_token()`), `FLOW_BEDROCK_MODEL_NAME` (optional, default: `openai.gpt-5.6-luna`), `FLOW_BEDROCK_MAX_TOKENS` (optional, default: `4096`), `FLOW_BEDROCK_TEMPERATURE` (optional, default: `0`)

**OpenRouter:** `OPENROUTER_API_KEY` (required), `OPENROUTER_MODEL_NAME` (optional, default: `openai/gpt-6-luna`), `OPENROUTER_SITE_URL` (optional — sent as `HTTP-Referer` header), `OPENROUTER_APP_TITLE` (optional — sent as `X-Title` header)

**HuggingFace:** `HF_TOKEN` (required), `HF_MODEL_NAME` (optional, default: `zai-org/GLM-5.2:novita`)

> **Never commit `.env`** — it is gitignored. Use `.env.*.example` files as templates.

## Common Commands

### Run the CLI

```bash
python run_cli.py path/to/story.md [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--provider` | `openai` | LLM provider (`openai`, `claude`, `flow-openai`, `bedrock`, `openrouter`, `huggingface`) |
| `--format` | `json` | Output format (`json` or `text`) |
| `--output-file` | stdout | Path to save results |
| `--log-level` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `--max-workers` | `5` | Parallel threads for Wave 1 |
| `--help` | — | Show all options |

### Run the API Server

```bash
python run_api_server.py [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `127.0.0.1` | Bind host |
| `--port` | `8000` | Bind port |
| `--reload` | off | Auto-reload on code changes |

API endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | API info |
| `POST` | `/calculate` | Submit BCP calculation job (async) |
| `GET` | `/status/{job_id}` | Poll job status |
| `GET` | `/docs` | Swagger UI |

### Run Tests

```bash
pytest                                    # all tests with coverage
pytest tests/unit/                        # unit tests only
pytest tests/integration/                 # integration tests only
pytest tests/unit/test_bcp_calculator.py  # specific test file
pytest -k "test_bcp_13d"                  # by name pattern
```

Coverage config is in `.coveragerc` (source: `src`, omits `llm_providers.py` and `tests/`).
Pytest config is in `pyproject.toml` (`testpaths`, `addopts = --cov=src --cov-report=term-missing`).

### Run Provider Comparisons

```bash
python run_comparison.py --stories-dir tests/data --output-dir tests/results --format excel
```

### Run the MCP Server

```bash
python run_mcp.py                         # stdio transport
python run_mcp_http_server.py --host 0.0.0.0 --port 51617  # HTTP transport
```

### Code Formatting and Linting

```bash
black .                                   # format (line-length 100)
isort .                                   # sort imports (black profile)
mypy src/                                 # type check (python 3.10, strict)
```

## Architecture

### BCP Pipeline (14 cells, 3 waves)

```
Wave 1 (parallel, ThreadPoolExecutor):
  ├── 10 functional dimension cells (D1–D10)
  └── 1 NFR cell (D11–D13 combined)

Wave 2 (depends on Wave 1 functional scores):
  └── Functional Aggregator (sums D1–D10)

Wave 3 (depends on Waves 1–2):
  ├── Complexity Maturity Score (CMS, 0–5)
  └── INVEST Maturity Score (IMS, 0–5)

Total BCP = functional_aggregator.score + nfr_scoring.score
```

Maturity scores (CMS, IMS) are complementary — not included in BCP total.

### 13 Dimensions

**Functional (D1–D10):**

| ID | Name | Cell name |
|----|------|-----------|
| D1 | Business Rules | `functional_business_rules` |
| D2 | Interface Elements | `functional_interface_elements` |
| D3 | Boundaries | `functional_boundaries` |
| D4 | Roles & Permissions | `functional_roles_permissions` |
| D5 | Solution Variabilities | `functional_solution_variabilities` |
| D6 | Domain Entities | `functional_domain_entities` |
| D7 | New Domain Entities | `functional_new_domain_entities` |
| D8 | Background Processes | `functional_background_processes` |
| D9 | Notifications | `functional_notifications` |
| D10 | Audits | `functional_audits` |

**NFR (D11–D13):**

| ID | Name | Cell name |
|----|------|-----------|
| D11 | Quality Attributes | `nfr_scoring` (combined) |
| D12 | Security & Compliance | `nfr_scoring` (combined) |
| D13 | UX & Accessibility | `nfr_scoring` (combined) |

### Scoring

Scores are computed by `FormulaEvaluator` — a safe AST-based expression evaluator that interprets per-dimension formulas (e.g., `sum(scores_extracted)`, `ceil(count(static_elements)/5)*static_weight`). This replaces hardcoded Python `match/case` logic. Formulas are defined in `FUNCTIONAL_DIMENSIONS` and `NFR_DIMENSIONS` lists in `bcp_calculator.py`.

### API Server (async job model)

The HTTP API uses an async job model — jobs are stored in an in-memory dict (lost on server restart):

1. `POST /calculate` with `{"content": "# Story Title\n\n...", "provider": "openai"}` → returns `{"job_id": "..."}`
2. `GET /status/{job_id}` → poll until `status` is `completed` or `failed`
3. Job states: `pending` → `processing` → `completed` (or `failed`)

### Result Structure

`BCPCalculator.calculate_bcp()` returns:

```python
{
    "story_name": str,           # first line of story content
    "total_bcp": int|float,      # functional_aggregator + nfr_scoring
    "breakdown": {               # 11 keys (10 functional + "nfr")
        "business_rules": int, "interface_elements": int, ...
        "nfr": int,
    },
    "maturity": {                # 2 keys
        "complexity": int,       # CMS score
        "invest": int,           # IMS score
    },
    "cells": {                   # 14 entries, keyed by cell name
        "functional_business_rules": {"score": int, "raw_output": {...}},
        ...
    },
}
```

## Claude Code Skills

### bcp-calculator-13d (Alpha)

Calls the **local API server** to calculate BCP 13 dimensions. Requires `run_api_server.py` running on `http://127.0.0.1:8000`. No auth token needed.

```
skills/bcp-calculator-13d/
├── SKILL.md                         # Agent instructions
└── scripts/bcp_calculate_13d.py     # API client (stdlib only)
```

The script submits stories via `POST /calculate`, polls `GET /status/{job_id}`, parses results, and retries failed cells up to 2 more times.

> **⚠️ Alpha Testing:** Scoring results may vary between runs.

### bcp-story-writing-coach

Rewrites existing stories using the 13 BCP dimension rules as a writing guide. Does **not** calculate BCP — improves writing quality via a gap-driven questionnaire. No API server needed.

```
skills/bcp-story-writing-coach/
├── SKILL.md                         # Agent instructions
└── rules/                           # 13 dimension rule files (D1–D13)
```

**Key principle:** No invention — every change must be traceable to explicit content, implicit deduction, or user responses.

## Code Conventions

### Style

- **Formatter:** black, line-length 100
- **Imports:** isort, black profile, line-length 100
- **Types:** mypy strict mode (python 3.10) — `warn_return_any`, `warn_unused_configs`, `disallow_untyped_defs`, `disallow_incomplete_defs`
- Follow PEP 8

### Patterns

- Prompt templates are `.md` files under `src/bcp/prompts/thirteen/` — loaded by `PromptHandler` with Jinja2 variable binding (`{{story.key}}`, `{{story.summary}}`, `{{story.description}}`)
- Scoring formulas are data-driven (defined in `FUNCTIONAL_DIMENSIONS` / `NFR_DIMENSIONS` lists), evaluated by `FormulaEvaluator` — not hardcoded
- LLM calls go through provider abstraction (`SimpleLLMProvider` is default — httpx-based, omits auth header for placeholder keys to avoid gateway hangs)
- Wave 1 parallelism via `ThreadPoolExecutor` — control with `--max-workers`
- API server uses in-memory job storage (not a database)
- Tests: `conftest.py` adds `src/` to `sys.path` so imports work without package install

### Commit Messages

Follow conventional commits:

```
feat: add new dimension scoring formula
fix: correct NFR scoring for edge case
refactor: extract provider selection logic
test: add unit tests for formula evaluator
docs: update skill usage guide
chore: bump dependencies
```

## Testing

### Test Structure

| Location | Purpose |
|----------|---------|
| `tests/unit/` | Unit tests (calculator, formula evaluator, providers, prompt handler, formatters) |
| `tests/integration/` | Integration tests (API server) |
| `tests/test_bcp_calculator.py` | Calculator tests |
| `tests/test_providers.py` | Provider tests |
| `tests/test_sdk.py` | SDK tests |
| `tests/data/` | 15 sample stories (`story1.md`–`story15.md`) |

### Running Tests

```bash
pytest                                     # all tests + coverage
pytest tests/unit/ --tb=short              # unit tests, short tracebacks
pytest -k "test_bcp_13d" -v                # by name, verbose
pytest --cov=src --cov-report=html         # HTML coverage report
```

Coverage is configured in `.coveragerc` and `pyproject.toml`. Coverage source is `src/`, omitting `llm_providers.py` and test files.

## Important Notes

- **Never commit `.env`** — it contains API keys. Use `.env.*.example` files as templates.
- **The API server stores jobs in memory** — restarting the server loses all pending/completed jobs.
- **Wave 1 runs 11 cells in parallel** — use `--max-workers` to control thread pool size (default: 5).
- **Maturity scores (CMS, IMS) are not part of BCP total** — they are complementary evaluations.
- **`SimpleLLMProvider` is the default provider** — it uses httpx directly instead of the openai SDK, which avoids compatibility issues with local gateways that hang when receiving `Authorization` headers with placeholder tokens.
- **The bcp-calculator-13d skill is in alpha** — scoring results may vary between runs.
- **Prompt templates can have model-specific overrides** — see `src/bcp/prompts/thirteen/overrides/gpt-6-luna/`.

## Integration Options

| Option | Entry point | Docs |
|--------|------------|------|
| CLI | `run_cli.py` | [cli_usage.md](docs/usage/cli_usage.md) |
| HTTP API | `run_api_server.py` | [http_api_usage.md](docs/usage/http_api_usage.md) |
| MCP (stdio) | `run_mcp.py` | [mcp_usage.md](docs/usage/mcp_usage.md) |
| MCP (HTTP) | `run_mcp_http_server.py` | [mcp_usage.md](docs/usage/mcp_usage.md) |
| Python SDK | `from src.sdk import BCPClient` | [sdk_usage.md](docs/usage/sdk_usage.md) |
| Skill (13D) | `skills/bcp-calculator-13d/` | [skill_usage.md](docs/usage/skill_usage.md) |
| Skill (Coach) | `skills/bcp-story-writing-coach/` | [SKILL.md](skills/bcp-story-writing-coach/SKILL.md) |

## Pitfalls to Avoid

1. **Don't edit `.env` files** — they are gitignored and contain secrets. Edit `.env.*.example` templates instead.
2. **Don't use `ddl-auto` or database migrations** — this project has no database. The API server uses in-memory storage.
3. **Don't hardcode scoring logic** — use `FormulaEvaluator` with formulas defined in `FUNCTIONAL_DIMENSIONS` / `NFR_DIMENSIONS`.
4. **Don't call `flow.ciandt.com` from the skill** — the bcp-calculator-13d skill calls the **local API server** (`http://127.0.0.1:8000`), not the remote Flow API.
5. **Don't forget to start the API server** before using the bcp-calculator-13d skill: `python run_api_server.py`.
6. **Don't add pip packages to the skill scripts** — `bcp_calculate_13d.py` uses Python stdlib only.
7. **Don't change prompt template variable syntax** — templates use Jinja2 `{{variable}}` format, loaded by `PromptHandler`.
8. **Don't skip `conftest.py`** — it adds `src/` to `sys.path` so test imports work without `pip install -e .`.
