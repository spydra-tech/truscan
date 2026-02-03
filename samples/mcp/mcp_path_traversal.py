"""
Vulnerable MCP server sample: tool parameter used as file path (path traversal).
Used to test mcp-llm02-tool-param-to-file-ops.
"""
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vulnerable Server", json_response=True)


@mcp.tool()
def read_file(filepath: str) -> str:
    """Read a file (VULNERABLE: tool param used as path without validation)."""
    return Path(filepath).read_text()  # BAD: path from tool param
