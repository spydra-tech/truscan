# MCP (Model Context Protocol) sample servers

Vulnerable sample servers for testing Python MCP rules. Each file demonstrates one or more patterns that the scanner should flag.

| Sample | Decorator(s) | Vulnerability | Rule ID(s) |
|--------|--------------|---------------|------------|
| `mcp_code_injection.py` | `@mcp.tool()` | Tool param → `eval` / `exec` | `mcp-llm02-tool-param-to-eval`, `mcp-llm02-tool-param-to-exec-globals` |
| `mcp_command_injection.py` | `@mcp.tool()` | Tool param → `subprocess.run(..., shell=True)` | `mcp-llm02-tool-param-to-subprocess` |
| `mcp_path_traversal.py` | `@mcp.tool()` | Tool param → `Path(...).read_text()` | `mcp-llm02-tool-param-to-file-ops` |
| `mcp_prompt_injection.py` | `@mcp.tool()` | Tool param/output → LLM `messages` | `mcp-llm01-tool-output-to-llm` |
| `mcp_ssrf.py` | `@mcp.tool()` | Tool param (URL) → `requests.get()` | `mcp-llm02-tool-param-to-request` |
| `mcp_sql_injection.py` | `@mcp.tool()` | Tool param → raw SQL `cursor.execute()` | `mcp-llm02-tool-param-to-sql` |
| `mcp_async_tool.py` | `@mcp.async_tool()` | Async tool param → `subprocess.run` / `eval` | Same rule IDs as above |
| `mcp_resource.py` | `@mcp.resource(...)` | Resource URI param → `Path(...).read_text()` | `mcp-llm02-tool-param-to-file-ops` |
| `mcp_prompt_handler.py` | `@mcp.prompt()` | Prompt handler param → `eval()` | `mcp-llm02-tool-param-to-eval` |

Run the scanner on this directory:

```bash
python -m llm_scan.runner samples/mcp --rules llm_scan/rules/python/mcp --format console
```
