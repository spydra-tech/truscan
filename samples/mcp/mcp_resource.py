"""
Vulnerable MCP server sample: @mcp.resource() handler params used in file ops (path traversal).
Used to test rules that include resource() as a pattern-source.
"""
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vulnerable Server", json_response=True)


@mcp.resource("file:///docs/{filename}")
def get_doc(filename: str) -> str:
    """Serve file content by filename (VULNERABLE: resource param as path)."""
    # BAD: filename from resource URI template used as path (e.g. ../../../etc/passwd)
    return Path(filename).read_text()
