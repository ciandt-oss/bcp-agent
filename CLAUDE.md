# BCP Calculator - Claude Code Assistant Guide

## Project Overview

The BCP Calculator is a command-line tool that analyzes user stories and calculates Business Complexity Points (BCP) using LangChain with support for multiple LLM providers. The recommended model is `mistral-small-2503` with `temperature=0`, tested with the 13-dimensions pipeline to produce the lowest Coefficient of Variation (CV) across repeated executions. This application orchestrates a 14-cell pipeline across 3 parallel execution waves to evaluate story complexity across 13 dimensions: 10 functional dimensions, 3 NFR (Non-Functional Requirements) dimensions, and 2 complementary maturity evaluations.

The tool also provides functionality to compare results between different LLM providers, generating detailed comparison reports and visualizations to help evaluate differences in BCP calculations.

## Architecture

### Core Components
- **main.py**: Entry point wrapper for the CLI application
- **run_comparison.py**: Wrapper script for running provider comparisons
- **src/main.py**: Main CLI implementation with argument parsing (including `--max-workers` flag)
- **src/bcp/bcp_calculator.py**: Core orchestration logic for the 14-cell, 3-wave parallel pipeline
- **src/bcp/formula_evaluator.py**: Safe AST-based formula evaluator for dimension scoring (replaces hardcoded Python scoring)
- **src/bcp/prompt_handler.py**: Manages loading and processing `.md` prompt templates from subdirectories, story dict bindings (`{{story.key}}`, `{{story.summary}}`, `{{story.description}}`), and improved JSON parsing
- **src/bcp/llm_providers.py**: Provider abstraction for different LLM services
- **`simple_llm_provider.py`**: Primary LLM provider using httpx directly. Default for all OpenAI-compatible endpoints (Flow gateway, Ollama, OpenAI, etc.). Inherits from `LLMProvider`. Sends auth header only with real API keys; omits it for placeholders to avoid gateway hangs.
- **src/bcp/logger.py**: Custom logging functionality
- **src/bcp/prompts/thirteen/**: Directory containing 13-dimensions prompt templates (`.md` files)
  - `functional/`: 10 functional dimension prompts + aggregator prompt
  - `functional-scoring.md`: V1 monolithic scoring prompt (kept for comparison)
  - `nfr-scoring.md`: NFR scoring prompt
  - `complexity-maturity.md`: Complexity maturity evaluation prompt
  - `invest-maturity.md`: INVEST maturity evaluation prompt
- **tests/compare_providers.py**: Tool for comparing BCP results between different providers
- **tests/data/**: Directory containing sample user stories for testing
- **`skill/bcp-calculator-13d/`**: Self-contained Claude Code skill for BCP 13D calculation. No external API, no SDK, no provider configuration — the agent processes prompts directly. Contains `SKILL.md` (agent instructions), `scripts/bcp_pipeline.py` (score calculation utility, stdlib only), and `prompts/thirteen/` (14 prompt templates, self-contained copy).

### Flow Structure

The pipeline executes 14 cells across 3 waves:

**Wave 1 (parallel via ThreadPoolExecutor):**
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
11. NFR Scoring (Quality Attributes + Security & Compliance + User Experience & Accessibility)

**Wave 2 (depends on Wave 1 functional scores):**
12. Functional Aggregator — sums the 10 functional dimension scores

**Wave 3 (depends on Waves 1–2):**
13. Complexity Maturity (complementary, 0–5 score)
14. INVEST Maturity (complementary, 0–5 score)

**Total BCP** = `functional_aggregator.score + nfr_scoring.score`

Scoring is performed by `FormulaEvaluator`, a safe AST-based expression evaluator that interprets per-dimension formulas (e.g., `sum(scores_extracted)`, `ceil(count(static_elements)/5)*static_weight + ceil(count(dynamic_elements)/5)*dynamic_weight`, `count(notification_events)`). This replaces the previous hardcoded Python `match/case` scoring logic.

## Technology Stack
- **Python**: Primary programming language
- **LangChain 1.4.2**: LLM orchestration framework
- **LangChain Core 1.6.3**: Core LangChain primitives
- **LangChain OpenAI 1.6.2**: OpenAI provider integration
- **LangChain Anthropic 1.7.2**: Anthropic provider integration
- **Mistral Small 2503 (mistral-small-2503)**: Recommended model, tested with lowest CV
- **OpenAI SDK 3.16.2**: OpenAI API client
- **Anthropic SDK 1.7.0**: Anthropic API client
- **Jinja2 3.1.6**: Template engine for prompt rendering
- **Pydantic 2.13.5**: Data validation for API models
- **FastAPI 0.141.1**: HTTP API server
- **Pandas**: Data manipulation for provider comparisons
- **Matplotlib**: Visualization for comparison reports
- **httpx**: HTTP client for SimpleLLMProvider (direct OpenAI-compatible API calls)
- **Environment Variables**: Configuration management

> **Recommended model:** `mistral-small-2503` with `temperature=0`. This combination was tested with the 13-dimensions pipeline and produces the lowest Coefficient of Variation (CV). All providers default to this model unless overridden via environment variables.

## Common Tasks

### Running the Application
```bash
python run_cli.py path/to/user_story.md --log-level DEBUG --output-file results.txt --max-workers 10
```

The `--max-workers` flag controls the ThreadPoolExecutor parallelism for Wave 1 cells (default: 5).

### Running Provider Comparisons
Compare BCP calculations between OpenAI and Claude using the provider comparison tool:
```bash
python run_comparison.py --stories-dir tests/data --output-dir tests/results --format excel
```

Available options:
- `--stories-dir`: Directory containing user story files (default: tests/data)
- `--output-dir`: Directory to save results (default: tests/results)
- `--log-level`: Set the logging level (default: INFO)
- `--format`: Output format for comparison (json, csv, or excel) (default: excel)

### Testing
The application includes test data in the `tests/data/` directory with sample user stories.

### Environment Setup
1. Copy `.env.example` to `.env`
2. Add your API keys (OpenAI and/or Anthropic) to the `.env` file
3. Install dependencies: `pip install -r requirements.txt`

## Development Notes

### Key Design Patterns
- Decomposed parallel pipeline: 14 cells across 3 execution waves (Wave 1 parallel via ThreadPoolExecutor)
- Safe AST-based formula evaluation for dimension scoring (FormulaEvaluator)
- `.md` prompt templates loaded from subdirectories under `prompts/thirteen/`
- Prompts use `{{story.key}}`, `{{story.summary}}`, `{{story.description}}` template variables bound from the story dict
- Structured output parsing from LLM responses
- Comprehensive logging for debugging and monitoring
- File-based input/output for user stories and results

### Error Handling
The application should handle:
- Invalid user story formats
- API rate limits and failures
- Missing or malformed prompt templates
- File I/O errors

### Performance Considerations
- Wave 1 executes 11 cells (10 functional + 1 NFR) in parallel — use `--max-workers` to control thread pool size
- Wave 2 (aggregator) depends on all 10 functional scores from Wave 1
- Wave 3 (maturity evaluations) depends on the aggregator + NFR results; maturity scores are complementary and not part of the BCP total
- Total BCP = `functional_aggregator.score + nfr_scoring.score`

## Troubleshooting

### Common Issues
- **API Key Issues**: Ensure the appropriate API keys are properly set in `.env`
- **Missing Dependencies**: Run `pip install -r requirements.txt`
- **File Path Errors**: Use absolute paths for user story files
- **Logging**: Use `--log-level DEBUG` for detailed execution info

### MCP Server
The MCP server (`run_mcp.py` and `run_mcp_http_server.py`) uses `MCPServer` from `mcp.server.mcpserver` (mcp 2.x). Host, port, and `streamable_http_path` are passed to `run()` as kwargs.

### Output Validation
The final output should include:
- Results from each of the 14 cells
- Breakdown of scores by dimension (10 functional + NFR)
- Total BCP (sum of functional aggregator + NFR scores)
- Maturity evaluation scores (Complexity and INVEST, complementary — not part of BCP total)

#### Provider Comparison Reports
When using the provider comparison functionality, reports include:
- Raw comparison data for each story processed with each provider
- Pivot tables comparing results between providers
- Difference analysis showing absolute and percentage differences
- Visualizations (when using excel format):
  - Total BCP comparison charts
  - Processing time comparison
  - Component breakdown averages

## Standalone Skill (`skill/bcp-calculator-13d/`)

A self-contained Claude Code skill that calculates BCP 13 dimensions without any external API, SDK, or provider. The agent processes the prompts directly — Claude IS the LLM.

### Structure

```
skill/bcp-calculator-13d/
├── SKILL.md                    # Agent instructions (trigger, pipeline steps, output format)
├── scripts/bcp_pipeline.py     # Score calculation & consolidation (stdlib only, no pip)
└── prompts/thirteen/           # 14 self-contained prompt templates (own copy, not from src/bcp/)
    ├── functional/             # 10 functional dimension prompts + aggregator
    ├── nfr-scoring.md          # NFR scoring (3 dimensions)
    ├── complexity-maturity.md  # Complexity Maturity Score (CMS)
    └── invest-maturity.md      # INVEST Maturity Score (IMS)
```

### How It Differs from `src/bcp/`

| Aspect | `src/bcp/` (bcp-agent) | `skill/bcp-calculator-13d/` (skill) |
|--------|------------------------|--------------------------------------|
| LLM calls | Uses LangChain + LLM providers (OpenAI, Claude, Flow) | Agent processes prompts directly (no SDK) |
| Dependencies | langchain, jinja2, openai, anthropic (pip packages) | Python stdlib only (for `bcp_pipeline.py`) |
| Prompts | `src/bcp/prompts/thirteen/` (shared) | `skill/.../prompts/thirteen/` (own copy) |
| Formula eval | `formula_evaluator.py` (AST-based) | `bcp_pipeline.py` (inline in script) |
| Configuration | `.env` with API keys, model names, base URLs | None — fully agnostic |
| Use case | CLI tool, API server, MCP server, SDK | Claude Code skill invocation |

### `bcp_pipeline.py` Commands

| Command | Purpose |
|---------|---------|
| `score --cell <name> --output <json>` | Calculate a single cell's score |
| `aggregate --bindings <json>` | Calculate aggregator score from 10 dim bindings |
| `consolidate --input <file>` | Consolidate all 14 cell outputs into structured JSON |
| `aggregate-stories --input <file>` | Aggregate multiple stories into summary report |

### Determinism Enforcement

The `SKILL.md` enforces absolute determinism: each prompt must return exactly the JSON it specifies — no variations, no abstractions, no extra fields, no missing fields. Variance testing (10 runs per story) showed CV average of 2.40%, with 1 of 4 stories achieving perfect determinism (CV = 0%).

## Code Conventions
- Follow Python PEP 8 style guidelines
- Use descriptive variable names for cell results
- Implement proper error handling for each cell
- Maintain comprehensive logging throughout the pipeline
- Prompt templates are `.md` files under `src/bcp/prompts/thirteen/` (organized in `functional/` subdir and top level)
- Scoring formulas are defined in `FUNCTIONAL_DIMENSIONS` and `NFR_DIMENSIONS` lists in `bcp_calculator.py` and evaluated by `FormulaEvaluator`