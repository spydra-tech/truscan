"""
Vulnerable MCP server sample: @mcp.prompt() handler param passed to dangerous sink.
Used to test rules that include prompt() as a pattern-source.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vulnerable Server", json_response=True)


@mcp.prompt()
def custom_prompt(topic: str, style: str = "formal") -> str:
    """Generate a prompt template (VULNERABLE: prompt param to eval for 'dynamic' style)."""
    # BAD: style (or topic) from prompt handler passed to eval
    allowed = ["formal", "casual"]
    if style not in allowed:
        style = eval(style)  # Intended to be safe; actually allows code execution
    return f"Write a {style} paragraph about {topic}."
