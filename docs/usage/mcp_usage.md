# MCP Server for BCP Calculator

This guide explains how to use the BCP Calculator as a Model Completion Provider (MCP) server.

## Prerequisites

Before using the MCP server, make sure you have:

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
   - AWS Bedrock (bedrock): set AWS_BEDROCK_REGION (optional, default: us-east-1), optional FLOW_BEDROCK_MODEL_NAME, FLOW_BEDROCK_TEMPERATURE. Auth via aws_bedrock_token_generator (auto-refreshed) or AWS_BEARER_TOKEN_BEDROCK env var
   - OpenRouter (openrouter): set OPENROUTER_API_KEY (required), optional OPENROUTER_MODEL_NAME (default: openai/gpt-6-luna), OPENROUTER_SITE_URL (optional), OPENROUTER_APP_TITLE (optional)
   - HuggingFace (huggingface): set HF_TOKEN (required), optional HF_MODEL_NAME (default: zai-org/GLM-5.2:novita)

## Starting the MCP Server (stdio)

You can start the MCP server locally using stdio transport:

```bash
python run_mcp.py
```

This mode is useful for desktop clients that spawn the server process.

## Starting the MCP Server (Streamable HTTP)

To run the MCP server as a standalone HTTP service (remote-friendly):

```bash
python run_mcp_http_server.py --host 0.0.0.0 --port 51617
```

Notes:
- Allowed origins default to "*". You can override with `--allowed-origins` or `MCP_ALLOWED_ORIGINS`.
- Provider configuration is read from `.env` by default. Set BCP_PROVIDER to one of: openai | claude | flow-openai | bedrock | openrouter | huggingface. MCP requests can optionally override provider and credentials per-call using the tool arguments.

## MCP Client Examples

### Stdio Client Configuration

Configure MCP clients (e.g., continue.dev) to call the BCP tool via stdio:

```json
    "bcp": {
        "command": "~/cit/flow/github/flow-ciandt/bcp-agent/venv/bin/python",
        "args": [
            "~/cit/flow/github/flow-ciandt/bcp-agent/run_mcp.py"
        ],
        "env": {
            "OPENAI_API_KEY": "${OPENAI_API_KEY}"
        },
        "type": "stdio"
    }
```

### HTTP Client Usage

For HTTP clients, point them to the MCP HTTP server URL. Specific configuration varies by client; consult your MCP client documentation. A common approach is using the MCP Inspector to connect to `http://localhost:51617`.
