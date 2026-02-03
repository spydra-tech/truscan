"""
Vulnerable MCP server sample: tool parameter passed to eval/exec (code injection).
Used to test mcp-llm02-tool-param-to-eval and mcp-llm02-tool-param-to-exec-globals.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vulnerable Server", json_response=True)


@mcp.tool()
def run_calculation(expression: str) -> str:
    """Evaluate a math expression (VULNERABLE: uses eval on tool input)."""
    return str(eval(expression))  # BAD: tool param to eval


@mcp.tool()
def run_code(code: str) -> str:
    """Run Python code (VULNERABLE: uses exec on tool input)."""
    local_vars = {}
    exec(code, {"__builtins__": __builtins__}, local_vars)  # BAD: tool param to exec
    return str(local_vars.get("result", ""))
