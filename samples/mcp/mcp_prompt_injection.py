"""
Vulnerable MCP server sample: tool parameter or output flows into LLM prompt (indirect injection).
Used to test mcp-llm01-tool-output-to-llm.
"""
from mcp.server.fastmcp import FastMCP

# Placeholder for LLM client (e.g. openai, anthropic)
# In real code this would be openai.OpenAI() or similar
CLIENT = None

mcp = FastMCP("Vulnerable Server", json_response=True)


@mcp.tool()
def search_and_summarize(query: str) -> str:
    """Search and return content (VULNERABLE: result passed to LLM without sanitization)."""
    # Simulated search result - in reality from DB/API; treat as untrusted
    result = f"Search result for: {query}"
    if CLIENT:
        # BAD: tool output / param flowed into LLM prompt (indirect prompt injection)
        CLIENT.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": result}],
        )
    return result
