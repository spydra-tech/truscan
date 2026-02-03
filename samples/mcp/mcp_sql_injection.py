"""
Vulnerable MCP server sample: tool parameter used in raw SQL (SQL injection).
Used to test mcp-llm02-tool-param-to-sql.
"""
import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vulnerable Server", json_response=True)


@mcp.tool()
def get_user_by_name(username: str) -> str:
    """Look up user by name (VULNERABLE: tool param concatenated into SQL)."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # BAD: tool param in raw SQL string
    cursor.execute("SELECT * FROM users WHERE name = '" + username + "'")
    row = cursor.fetchone()
    conn.close()
    return str(row) if row else "Not found"
