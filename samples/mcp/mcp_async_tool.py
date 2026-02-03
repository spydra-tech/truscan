"""
Vulnerable MCP server sample: @mcp.async_tool() handler with dangerous sinks.
Used to test rules that include async_tool() as a pattern-source.
"""
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vulnerable Server", json_response=True)


@mcp.async_tool()
async def run_async_command(cmd: str) -> str:
    """Run a command (VULNERABLE: async_tool param to subprocess)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # BAD
    return result.stdout or result.stderr


@mcp.async_tool()
async def eval_expression(expression: str) -> str:
    """Evaluate expression (VULNERABLE: async_tool param to eval)."""
    return str(eval(expression))  # BAD
