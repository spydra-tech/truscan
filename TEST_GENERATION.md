# Test Case Generation for AI Applications

The scanner can automatically generate security test cases by analyzing your AI application's code structure, extracting:
- **System prompts** from LLM API calls
- **Tool definitions** from MCP (`@mcp.tool()`, `@mcp.async_tool()`, `@mcp.resource()`, `@mcp.prompt()`), LangChain agents, etc.
- **Framework detection** (MCP, LangChain, OpenAI, Anthropic, etc.)

## How It Works

1. **Code Extraction**: Scans Python files to extract:
   - System prompts from `openai.ChatCompletion.create(messages=[{"role": "system", ...}])` or `Anthropic().messages.create(...)`
   - MCP tool handlers decorated with `@mcp.tool()`, `@mcp.async_tool()`, `@mcp.resource(...)`, `@mcp.prompt()`
   - LangChain agents and tools
   - Tool parameters and their types

2. **Sink Detection**: Analyzes tool implementations to detect dangerous sinks:
   - `eval()` / `exec()` → code injection tests
   - `subprocess.run()` / `os.system()` → command injection tests
   - `open()` / `Path()` → path traversal tests
   - `cursor.execute()` → SQL injection tests
   - `requests.get()` / `urllib.request.urlopen()` → SSRF tests

3. **Test Generation**: Creates test cases with:
   - **Prompt**: Concrete test input (e.g., "Call tool_name with param='../../../etc/passwd'")
   - **Expected behavior**: Should block, should succeed, should sanitize, etc.
   - **Ground truth**: Description of what correct behavior should be
   - **OWASP category**: LLM01, LLM02, LLM07, etc.
   - **Target tool**: Which tool/function this test targets

## Usage

### Basic Test Generation (Rule-Based)

```bash
# Generate test cases for scanned code
python -m llm_scan.runner . --generate-tests --format console

# Generate tests and save to JSON
python -m llm_scan.runner . --generate-tests --format json --out results.json

# Generate tests for MCP server code
python -m llm_scan.runner samples/mcp --generate-tests --format console
```

### AI-Enhanced Test Generation

For more sophisticated, context-aware test cases:

```bash
# With OpenAI
python -m llm_scan.runner . \
  --generate-tests \
  --enable-ai-filter \
  --ai-provider openai \
  --ai-model gpt-4 \
  --test-max-cases 30

# With Anthropic
python -m llm_scan.runner . \
  --generate-tests \
  --enable-ai-filter \
  --ai-provider anthropic \
  --ai-model claude-3-opus-20240229 \
  --test-max-cases 30
```

### Filter by Test Categories

```bash
# Generate only specific test categories
python -m llm_scan.runner . \
  --generate-tests \
  --test-categories prompt-injection \
  --test-categories tool-abuse \
  --test-max-cases 20
```

Available categories:
- `prompt-injection` - LLM01: Prompt injection attempts
- `jailbreak` - LLM01: Jailbreak attempts (developer mode, role-play)
- `tool-abuse` - LLM02/LLM07: Exploiting tool parameters (code/command injection, path traversal, SQL injection, SSRF)
- `data-exfiltration` - LLM06: Extracting system prompts, API keys, sensitive data
- `excessive-agency` - LLM08: Getting AI to take unauthorized actions
- `input-validation` - General input validation tests

## FastMCP evaluation test generation

For **FastMCP** (Python MCP SDK) servers, the scanner can generate **evaluation test cases**: natural-language prompts that should cause an agent to call each tool, plus ground truth. Only a **compact tool manifest** (name, description, parameters) is sent to the AI—never the full project.

1. **Extract** (no AI): Parse Python files with AST; find `@mcp.tool()`, `@mcp.async_tool()`, `@mcp.resource()`, `@mcp.prompt()`; extract tool name, docstring, parameters.
2. **Generate** (AI): Send the tool manifest to the LLM; receive 1–3 user prompts per tool that should trigger that tool, with ground truth.
3. **Output**: JSON with `tool_manifest` and `test_cases` for use in an evaluation harness.

### Usage

```bash
# Generate eval tests for FastMCP code (requires AI provider and API key)
python -m llm_scan.runner samples/mcp \
  --generate-eval-tests \
  --eval-test-out eval_tests.json \
  --ai-provider openai \
  --ai-model gpt-4

# Limit prompts per tool (default: 3)
python -m llm_scan.runner . --generate-eval-tests --eval-test-out eval.json --eval-test-max-prompts 5
```

Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (or use `--ai-api-key`). If no tools are found, the manifest and test_cases arrays are empty.

### LangChain evaluation test generation

For **LangChain** agents using the `@tool` decorator (from `langchain.tools` or `langchain_core.tools`), use `--eval-framework langchain`:

1. **Extract** (no AI): Parse Python files with AST; find `@tool` and `@tool("name")`; extract tool name (from decorator or function), docstring, parameters.
2. **Generate** (AI): Same as FastMCP—send the tool manifest to the LLM; receive user prompts and ground truth.
3. **Output**: Same JSON format as FastMCP.

```bash
# Generate eval tests for LangChain @tool code
python -m llm_scan.runner samples/langchain \
  --generate-eval-tests \
  --eval-framework langchain \
  --eval-test-out eval_tests_langchain.json \
  --ai-provider openai \
  --ai-model gpt-4
```

Supported: `@tool`, `@tool("custom_name")`, and async functions decorated with `@tool`. The default framework is `mcp`; use `--eval-framework langchain` for LangChain projects.

### LlamaIndex evaluation test generation

For **LlamaIndex** agents using `FunctionTool.from_defaults()` to wrap functions, use `--eval-framework llamaindex`:

1. **Extract** (no AI): Parse Python files with AST; find `FunctionTool.from_defaults(function_ref)` calls; extract the referenced function definitions (name, docstring, parameters).
2. **Generate** (AI): Same as FastMCP/LangChain—send the tool manifest to the LLM; receive user prompts and ground truth.
3. **Output**: Same JSON format as FastMCP/LangChain.

```bash
# Generate eval tests for LlamaIndex FunctionTool code
python -m llm_scan.runner samples/llama-index \
  --generate-eval-tests \
  --eval-framework llamaindex \
  --eval-test-out eval_tests_llamaindex.json \
  --ai-provider openai \
  --ai-model gpt-4
```

Supported: Functions wrapped with `FunctionTool.from_defaults(function)` or `FunctionTool.from_defaults(fn=function)`. The extractor finds the function reference and extracts its definition.


### LangGraph evaluation test generation

For **LangGraph** agents using `StateGraph` with `ToolNode` or `@tool` decorated functions, use `--eval-framework langgraph`:

1. **Extract** (no AI): Parse Python files with AST; find `@tool` decorated functions and tools referenced in `ToolNode([tool1, tool2, ...])` calls; extract function definitions (name, docstring, parameters).
2. **Generate** (AI): Same as FastMCP/LangChain/LlamaIndex—send the tool manifest to the LLM; receive user prompts and ground truth.
3. **Output**: Same JSON format as other frameworks.

```bash
# Generate eval tests for LangGraph StateGraph code
python -m llm_scan.runner samples/langgraph   --generate-eval-tests   --eval-framework langgraph   --eval-test-out eval_tests_langgraph.json   --ai-provider openai   --ai-model gpt-4
```

Supported: Functions decorated with `@tool` (from `langchain_core.tools`) and tools referenced in `ToolNode([tool1, tool2, ...])` calls. The extractor finds tools used in the graph structure and extracts their definitions.

### Output format

```json
{
  "tool_manifest": [
    { "name": "run_calculation", "description": "Evaluate a math expression.", "parameters": [{ "name": "expression", "type": "str" }], "decorator": "tool" }
  ],
  "test_cases": [
    { "prompt": "What is 2 + 3?", "expected_tool": "run_calculation", "ground_truth": "Agent should call run_calculation with expression='2 + 3'.", "eval_type": "tool_selection" }
  ],
  "meta": { "generation_duration_seconds": 1.2, "ai_model_used": "gpt-4" }
}
```

Each test case may include **`eval_type`**: one of `tool_selection` (default), `safety`, `prompt_injection`, `argument_correctness`, or `robustness`. The AI generator sets this so the eval runner (or custom pipelines) can treat cases differently (e.g. for `safety`, pass = agent refused).

### Running concrete evals (eval runner)

After generating an eval JSON, you can **run concrete evals** against a compiled graph (e.g. LangGraph) to measure:

- **Tool selection accuracy**: % of test cases where the agent called the `expected_tool`.
- **Tool invocation presence**: Same as above (the expected tool was invoked).
- **Valid path rate**: (LangGraph only, when `graph_structure` is in the JSON) % of runs where the sequence of nodes respected the graph edges (no illegal transitions).
- **Tool coverage**: Per-tool recall (for each tool, % of cases that expected that tool and where the agent called it).

**Requirements**: The graph’s runtime dependencies must be installed (e.g. `langgraph`, `langchain-core` for LangGraph). The graph must be loadable as a Python symbol.

**CLI** (from repo root):

```bash
# Run all test cases
python -m llm_scan.eval --eval-json eval_tests_langgraph.json \
  --graph samples.langgraph.langgraph_multi_agent_app:graph

# Limit to 5 cases (quick smoke test)
python -m llm_scan.eval --eval-json eval_tests_langgraph.json \
  --graph samples.langgraph.langgraph_multi_agent_app:graph --max-cases 5

# Verbose (per-case results)
python -m llm_scan.eval --eval-json eval_tests_langgraph.json \
  --graph samples.langgraph.langgraph_multi_agent_app:graph -v

# Skip path collection (faster; valid_path_rate will be omitted)
python -m llm_scan.eval --eval-json eval_tests_langgraph.json \
  --graph samples.langgraph.langgraph_multi_agent_app:graph --no-path
```

Alternatively: `llm-scan-eval` (if installed via pip), or `python -m llm_scan.eval.runner`.

**Graph spec**: `module.path:attribute` — the graph is loaded with `importlib.import_module(module.path)` then `getattr(mod, attribute)`. Example: `samples.langgraph.langgraph_multi_agent_app:graph`.

**Including graph structure in eval JSON**: When you generate eval tests with `--eval-framework langgraph`, the written JSON includes a `graph_structure` field (nodes, edges, entry_point). That is used for the valid-path check when you run the eval runner.

## Example Output

### Console Output

```
Test Case Generation:
  Frameworks detected: mcp
  Tools extracted: 3
  System prompts found: 0
  Test cases generated: 15

Generated Test Cases:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ extractor.py" startLine="127" endLine="594">
<function_calls>
<invoke name="read_file">
<parameter name="target_file">/Users/manish/code-scan2/llm_scan/engine/extraction_engine.py</parameter>
<parameter name="offset">170</parameter>
<parameter name="limit">50</parameter>
</invoke>
</function_calls>

<function_results>
<result>
<name>read_file</name>
<output>     172|    def _extract_tool_definition(
     173|        self, func_node: ast.AST, dec_type: str, file_path: str
     174|    ) -> ToolDefinition:
     175|        """Extract tool definition from decorated function."""
     176|        name = func_node.name
     177|        docstring = ast.get_docstring(func_node) or ""
     178|        parameters: Dict[str, str] = {}
     179|
     180|        # Extract parameters
     181|        for arg in func_node.args.args:
     182|            param_name = arg.arg
     183|            # Try to infer type from annotation
     184|            if arg.annotation:
     185|                if isinstance(arg.annotation, ast.Name):
     186|                    param_type = arg.annotation.id
     187|                elif isinstance(arg.annotation, ast.Constant):
     188|                    param_type = str(arg.annotation.value)
     189|                else:
     190|                    param_type = "str"  # Default
     191|            else:
     192|                param_type = "str"  # Default
     193|            parameters[param_name] = param_type
     194|
     193|            parameters[param_name] = param_type
     194|
     195|        # Detect dangerous sinks in function body
     196|        dangerous_sinks = self._detect_dangerous_sinks(func_node)
     197|
     196|        dangerous_sinks = self._detect_dangerous_sinks(func_node)
     197>
</thinking>

Let me create a comprehensive guide and also add a note to the README about test generation:
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
read_file