"""
Vulnerable MCP server sample: tool parameter (URL) passed to HTTP client (SSRF).
Used to test mcp-llm02-tool-param-to-request.
"""
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vulnerable Server", json_response=True)


@mcp.tool()
def fetch_url(url: str) -> str:
    """Fetch content from a URL (VULNERABLE: tool param to requests.get, SSRF risk)."""
    resp = requests.get(url, timeout=5)  # BAD: URL from tool param, no allowlist
    return resp.text[:4096]
