from typing import Any
from mcp.server.mcpserver import MCPServer
import logging

from src.bcp.bcp_calculator import BCPCalculator
from src.bcp.logger import setup_logger

mcp = MCPServer("bcp-calculator-mcp")

logger = setup_logger(logging.INFO)

@mcp.tool()
async def calculate_bcp(story_content: str, provider: str = "openai") -> dict:
    """Calculate BCP.

    Args:
        story: User story content
        provider: LLM provider to use (openai, claude, flow-openai, flow-bedrock)
    """
    calculator = BCPCalculator(logger, provider_name=provider)
    result = calculator.calculate_bcp(story_content)

    return {"result": result}

if __name__ == "__main__":
    logger.info(f"MCP Server starting...")
    mcp.run(transport='stdio')
