# BCP Calculator

A tool for calculating Business Complexity Points (BCP) of user stories using LangChain with support for multiple LLM providers (OpenAI GPT-4o-2024-05-13 and Anthropic Claude).

## Overview

The BCP Calculator analyzes user stories and calculates their Business Complexity Points based on:
- Business Rules Complexity
- Interface Elements Complexity
- Boundaries Complexity

The application orchestrates a flow through 6 predefined prompt steps:
1. Story Maturity Complexity (complementary analysis)
2. Story INVEST Maturity (complementary analysis)
3. Break Elements (separates the story into Business Rules, Interface Elements, and Boundaries)
4. Boundaries Complexity (calculates complexity points for Boundaries)
5. Interface Elements Complexity (calculates complexity points for Interface Elements)
6. Business Rules Complexity (calculates complexity points for Business Rules)

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

3. Set up your environment variables:
   ```
   cp .env.example .env
   ```
   
   Then edit the `.env` file to add your API keys for the providers you want to use (OpenAI and/or Anthropic).

## LLM Providers

The BCP Calculator supports four LLM providers, selected via the `--provider` flag. Each requires its own set of environment variables in your `.env` file.

---

### OpenAI (`--provider openai`)

Connects directly to the OpenAI API using `langchain-openai`.

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | Your OpenAI API key |
| `OPENAI_MODEL_NAME` | No | `gpt-4o-2024-05-13` | Model to use |

**.env example:**
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL_NAME=gpt-4o-2024-05-13
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
| `ANTHROPIC_MODEL_NAME` | No | `claude-3-sonnet-20240229-v1:0` | Model to use |

**.env example:**
```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL_NAME=claude-3-sonnet-20240229-v1:0
```

**Usage:**
```bash
python run_cli.py story.md --provider claude
```

---

### Flow OpenAI (`--provider flow-openai`)

Routes requests through [CI&T Flow](https://flow.ciandt.com)'s OpenAI-compatible orchestration layer. Authenticates via client credentials (exchanged for a Bearer token automatically).

| Variable | Required | Default | Description |
|---|---|---|---|
| `FLOW_BASE_URL` | Yes | — | Flow base URL (e.g. `https://flow.ciandt.com`) |
| `FLOW_CLIENT_ID` | Yes | — | Flow API client ID |
| `FLOW_CLIENT_SECRET` | Yes | — | Flow API client secret |
| `FLOW_TENANT` | No | `flowteam` | Tenant identifier sent in the `FlowTenant` header |
| `FLOW_AGENT` | No | `bcp-opensource` | Agent identifier sent in the `FlowAgent` header |
| `FLOW_MODEL_NAME` | No | `gpt-4o-mini` | Model to use (OpenAI-compatible names) |
| `FLOW_MAX_TOKENS` | No | `4096` | Maximum tokens to generate |

**.env example:**
```env
FLOW_BASE_URL=https://flow.ciandt.com
FLOW_CLIENT_ID=my-client-id
FLOW_CLIENT_SECRET=my-client-secret
FLOW_TENANT=myteam
FLOW_AGENT=bcp-opensource
FLOW_MODEL_NAME=gpt-4o-mini
```

**Usage:**
```bash
python run_cli.py story.md --provider flow-openai
```

---

### Flow Bedrock (`--provider flow-bedrock`)

Routes requests through CI&T Flow's Bedrock endpoint, which provides access to AWS Bedrock models (including Claude via Bedrock). Uses the same client credentials authentication as `flow-openai`.

| Variable | Required | Default | Description |
|---|---|---|---|
| `FLOW_BASE_URL` | Yes | — | Flow base URL (e.g. `https://flow.ciandt.com`) |
| `FLOW_CLIENT_ID` | Yes | — | Flow API client ID |
| `FLOW_CLIENT_SECRET` | Yes | — | Flow API client secret |
| `FLOW_TENANT` | No | `flowteam` | Tenant identifier sent in the `FlowTenant` header |
| `FLOW_AGENT` | No | `bcp-opensource` | Agent identifier sent in the `FlowAgent` header |
| `FLOW_BEDROCK_MODEL_NAME` | No | `anthropic.claude-3-5-haiku` | Bedrock model ID |
| `FLOW_BEDROCK_MAX_TOKENS` | No | `1000` | Maximum tokens to generate |
| `FLOW_BEDROCK_TEMPERATURE` | No | `1.0` | Sampling temperature |
| `FLOW_BEDROCK_TOP_P` | No | `0.999` | Top-p sampling |
| `FLOW_BEDROCK_TOP_K` | No | `250` | Top-k sampling |
| `FLOW_BEDROCK_ANTHROPIC_VERSION` | No | `bedrock-2023-05-31` | Anthropic API version for Bedrock |

**.env example:**
```env
FLOW_BASE_URL=https://flow.ciandt.com
FLOW_CLIENT_ID=my-client-id
FLOW_CLIENT_SECRET=my-client-secret
FLOW_TENANT=myteam
FLOW_BEDROCK_MODEL_NAME=anthropic.claude-3-5-haiku
FLOW_BEDROCK_MAX_TOKENS=1000
```

**Usage:**
```bash
python run_cli.py story.md --provider flow-bedrock
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
- `--provider`: LLM provider to use (openai, claude, flow-openai or flow-bedrock). Default is openai.
- `--format`: Output format (text or json). Default is json.

For more detailed CLI usage information, see the [CLI Usage Guide](docs/usage/cli_usage.md).

## Output

The output includes:
- Results from each step in the process
- Final Business Complexity Points (BCP)
- Breakdown of points by component (Business Rules, Interface Elements, Boundaries)

### Sample JSON Output

```json
{
  "story_name": "User Story: Add Payment Method",
  "total_bcp": 13,
  "components": {
    "Business Rules": 5,
    "UI Elements": 3,
    "External Integrations": 5
  },
  "steps": {
    "Story Maturity Complexity": {
      "assessment": "The story is well-defined with clear acceptance criteria",
      "score": 4,
      "classification": "Mature"
    },
    "Story INVEST Maturity": {
      "assessment": "Independent, testable, but somewhat large in scope",
      "score": 3,
      "classification": "Partially Mature"
    },
    "Business Rules Complexity": {
      "total": 5
    },
    "UI Elements Complexity": {
      "total": 3
    },
    "External Integrations Complexity": {
      "total": 5
    }
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
  - `__init__.py`: Package exports
  - `bcp_calculator.py`: Core logic for orchestrating the flow
  - `prompt_handler.py`: Handle loading and processing prompts
  - `llm_providers.py`: Provider abstraction for different LLM services
  - `logger.py`: Custom logging functionality
  - `prompts/`: Directory containing the prompt templates

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

## License

[MIT License](LICENSE)