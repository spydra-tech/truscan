"""
Vulnerable MCP server sample: tool parameter passed to subprocess (command injection).
Used to test mcp-llm02-tool-param-to-subprocess.
"""
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vulnerable Server", json_response=True)


@mcp.tool()
def run_command(command: str) -> str:
    """Run a shell command (VULNERABLE: tool param to subprocess)."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)  # BAD
    return result.stdout or result.stderr
