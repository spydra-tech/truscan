# Trusys – LLM Security Scanner (VS Code Extension)

VS Code extension that runs the LLM Security Scanner inside the editor: it shows AI/LLM security findings in the **Problems** panel and supports optional AI analysis and database upload.

---

## What the extension does

- **Scans your code** for LLM-related vulnerabilities (prompt injection, code/command injection, insecure output handling, MCP tool misuse, etc.) using Semgrep rules.
- **Shows results in VS Code** as diagnostics (Problems panel, inline in the editor).
- **Can optionally** use AI to filter false positives and improve remediation text, and upload results to your backend.

**Requirements:** VS Code 1.74.0+, Python 3.11+. **No manual setup:** the extension installs the scanner and dependencies automatically when you open a folder or run a scan. You don’t need to run any commands or configure anything.

---

## Supported frameworks

The extension uses the same Semgrep rules as the CLI. Supported **languages** and **LLM/framework rule sets** include:

| Area | Supported |
|------|-----------|
| **Languages** | Python (primary), JavaScript, TypeScript (activation and include patterns; rules are largely Python-focused). |
| **LLM / API** | OpenAI, Anthropic, Cohere, Azure OpenAI, AWS Bedrock. |
| **Frameworks** | **LangChain**, **LlamaIndex**, **Hugging Face** (agents, tools, chains, document loaders, etc.). |
| **MCP** | **MCP (Model Context Protocol) / FastMCP** – Python SDK decorators `@mcp.tool()`, `@mcp.async_tool()`, `@mcp.resource()`, `@mcp.prompt()` (code/command/path injection, SSRF, SQL injection, prompt injection). |

**Generate Eval Tests** supports **FastMCP** (`@mcp.tool`), **LangChain** (`@tool`), **LlamaIndex** (`FunctionTool.from_defaults`), and **LangGraph** (`StateGraph` with `ToolNode`); set **Eval Framework** in settings to choose. For full rule coverage and framework details, see the main repository [README](https://github.com/spydra-tech/truscan) and [rules README](https://github.com/spydra-tech/truscan/blob/main/llm_scan/rules/python/README.md).

---

## Capabilities

| Capability | Description |
|------------|-------------|
| **Automatic scanning** | Scan on save and/or on open (configurable). |
| **Manual scanning** | **Scan Workspace** or **Scan Current File** from the Command Palette. |
| **Problems panel** | All findings appear as errors/warnings/info; click to jump to the line. |
| **Severity filter** | Choose which severities are shown (e.g. critical, high, medium). |
| **Rules and patterns** | Configure rules directory, include/exclude file patterns. |
| **AI analysis** (optional) | Use OpenAI/Anthropic to analyze findings (fewer false positives, better remediation). Requires API key and network. |
| **Database upload** (optional) | **Scan and Upload to Database** sends results to your backend. Requires endpoint, API key, and application ID. |
| **MCP / FastMCP** | Same rules as the CLI for `@mcp.tool()`, `@mcp.async_tool()`, `@mcp.resource()`, `@mcp.prompt()` (e.g. code/command/path injection, SSRF, SQL injection). |
| **Generate Eval Tests** | Create evaluation test cases for **FastMCP**, **LangChain**, **LlamaIndex**, or **LangGraph**: extracts tools from Python files, uses AI to generate a mix of prompts (including **eval_type**: tool_selection, safety, prompt_injection, argument_correctness, robustness), writes JSON. For LangGraph, output includes graph_structure for valid-path evals. Run concrete evals via CLI: `python -m llm_scan.eval`. Requires AI provider settings (and API key or env). |

---

## How to use

### 1. Install and run a scan

1. Install the extension (from VSIX or marketplace).
2. Open a folder (workspace) that contains your code.
3. The extension sets up the scanner automatically (you may see a short “Setting up…” or “Installing…” message the first time). No commands or settings are required.
4. **Scan:**
   - **Automatic:** Save or open a file (if **Scan on Save** / **Scan on Open** are on in settings).
   - **Manual:** `Ctrl+Shift+P` / `Cmd+Shift+P` → **LLM Security: Scan Workspace** or **LLM Security: Scan Current File**.
5. Open **Problems** (`Ctrl+Shift+M` / `Cmd+Shift+M`) to see findings; click a finding to go to the code.

### 2. Change what gets scanned and shown

- **Severity:** In settings, set `llmSecurityScanner.severityFilter` (e.g. `["critical", "high", "medium"]`).
- **Files:** Use `llmSecurityScanner.includePatterns` and `llmSecurityScanner.excludePatterns` (e.g. exclude `tests/`, `**/__pycache__/`).
- **Rules:** Set `llmSecurityScanner.rulesDirectory` (default uses the rules bundled with the scanner, e.g. `llm_scan/rules/python`).
- **Turn off auto-scan:** Set `llmSecurityScanner.scanOnSave` and/or `llmSecurityScanner.scanOnOpen` to `false`.

### 3. Use AI analysis (optional)

- **What it does:** Sends findings to OpenAI or Anthropic to reduce false positives and improve remediation text.
- **How to enable:**
  1. Settings → search “LLM Security”.
  2. Enable **AI Analysis** and set **AI Provider** (e.g. `openai`) and **AI Model** (e.g. `gpt-4`).
  3. Set **AI API Key** or use env var `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`.
- **When it runs:** During any scan (workspace or current file) when AI analysis is enabled.
- **Cost:** Uses the provider’s API; you can set **AI Max Findings** to cap how many findings are sent.

### 4. Upload results to your backend (optional)

- **What it does:** Sends scan results to your own API (e.g. for dashboards or history).
- **How to use:**
  1. Configure in settings: **Upload Endpoint**, **Application ID**, **API Key**.
  2. Run **LLM Security: Scan and Upload to Database** from the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`).
- **Note:** Normal **Scan Workspace** / **Scan Current File** do **not** upload; only the “Scan and Upload to Database” command does.

### 5. Generate Eval Tests (optional)

- **What it does:** Extracts tools from your Python code (FastMCP, LangChain, LlamaIndex, or LangGraph), calls the configured AI provider to generate test prompts with a **mix of eval types** (tool_selection, safety, prompt_injection, argument_correctness, robustness), and writes a JSON file (e.g. `eval_tests.json`). For LangGraph, the JSON includes **graph_structure** so you can run **valid-path** evals. Use the CLI to run concrete evals: `python -m llm_scan.eval --eval-json <path> --graph <module:attr>`.
- **How to use:**
  1. Set **AI Provider** and **AI Model** in settings (e.g. `openai`, `gpt-4`). Set **AI API Key** or use `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` in the environment.
  2. Set **Eval Framework** to `mcp` (FastMCP `@mcp.tool`), `langchain` (LangChain `@tool`), `llamaindex` (LlamaIndex `FunctionTool.from_defaults`), or `langgraph` (LangGraph `StateGraph` with `ToolNode`) in settings, or choose the framework when you run the command (quick pick).
  3. Run **LLM Security: Generate Eval Tests** from the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`). You can pick **FastMCP**, **LangChain**, **LlamaIndex**, or **LangGraph** for that run (or use the current setting).
  4. Choose where to save the JSON (default: `eval_tests.json` in the workspace root). When it finishes, you can open the file from the notification.
- **Note:** Requires a workspace folder and Python files with the chosen framework’s tools. To run evals (tool-selection accuracy, valid path rate, tool coverage), use the scanner CLI: see [TEST_GENERATION.md](https://github.com/spydra-tech/truscan/blob/main/TEST_GENERATION.md#running-concrete-evals-eval-runner).

### 6. Clear results

- **LLM Security: Clear Results** removes all current findings from the Problems panel.

### 7. Reinstall or fix scanner/dependencies

- **LLM Security: Install Dependencies** triggers the extension’s dependency install (scanner/Semgrep) again. Use if the scanner is missing or broken.

---

## Commands (Command Palette: `Ctrl+Shift+P` / `Cmd+Shift+P`)

| Command | What it does |
|---------|----------------|
| **LLM Security: Scan Workspace** | Scans the whole workspace; results only in Problems (no upload). |
| **LLM Security: Scan Current File** | Scans the active editor file; results only in Problems. |
| **LLM Security: Scan and Upload to Database** | Scans workspace and uploads results to your backend (needs upload settings). |
| **LLM Security: Clear Results** | Clears all extension diagnostics from the Problems panel. |
| **LLM Security: Install Dependencies** | Runs the extension’s installer for the scanner and Semgrep. |
| **LLM Security: Generate Eval Tests** | Generates eval test JSON for FastMCP, LangChain, LlamaIndex, or LangGraph (extracts tools, AI-generated prompts with eval_type mix; LangGraph includes graph_structure). Requires AI provider/model and API key. |

---

## Settings (search “LLM Security” in VS Code Settings)

**Scan behavior**

- `llmSecurityScanner.enabled` – Turn the extension on/off.
- `llmSecurityScanner.scanOnSave` – Scan when a file is saved.
- `llmSecurityScanner.scanOnOpen` – Scan when a file is opened.
- `llmSecurityScanner.scanDelay` – Delay (ms) before running a scan after a change.
- `llmSecurityScanner.severityFilter` – Which severities to show (e.g. `["critical","high","medium"]`).
- `llmSecurityScanner.includePatterns` – Glob patterns for files to include (e.g. `["*.py"]`).
- `llmSecurityScanner.excludePatterns` – Glob patterns to exclude (e.g. `["**/__pycache__/**"]`).

**Scanner**

- `llmSecurityScanner.pythonPath` – Python executable used to run the scanner (e.g. `python3` or `venv/bin/python`).
- `llmSecurityScanner.rulesDirectory` – Path to rules (relative to workspace or absolute).
- `llmSecurityScanner.autoInstallDependencies` – Whether to auto-install scanner/Semgrep on activation.

**AI analysis and Eval Tests (optional)**

- `llmSecurityScanner.enableAiAnalysis` – Enable/disable AI analysis for scans (when implemented).
- `llmSecurityScanner.aiProvider` – `openai` or `anthropic`. Used by **Generate Eval Tests** and AI analysis.
- `llmSecurityScanner.aiModel` – e.g. `gpt-4`, `gpt-3.5-turbo`, `claude-3-opus-20240229`. Used by **Generate Eval Tests** and AI analysis.
- `llmSecurityScanner.aiApiKey` – API key (or use `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`). Used by **Generate Eval Tests** and AI analysis.
- `llmSecurityScanner.evalTestMaxPromptsPerTool` – Max prompts per tool when generating eval tests (default: 3).
- `llmSecurityScanner.evalFramework` – Framework for eval extraction: `mcp` (FastMCP), `langchain` (LangChain), `llamaindex` (LlamaIndex), or `langgraph` (LangGraph) (default: mcp).
- `llmSecurityScanner.aiConfidenceThreshold` – Minimum confidence for AI verdict (0–1).
- `llmSecurityScanner.aiMaxFindings` – Max number of findings to send to AI (limits cost).

**Database upload (optional)**

- `llmSecurityScanner.uploadEndpoint` – Backend URL (e.g. `https://api.example.com/api/v1/scans`).
- `llmSecurityScanner.applicationId` – Application ID in your backend.
- `llmSecurityScanner.apiKey` – API key for the upload endpoint.

---

## Viewing results in VS Code

- **Problems panel:** View → Problems, or `Ctrl+Shift+M` / `Cmd+Shift+M`. Each finding shows rule, message, file, and line.
- **In editor:** Red/yellow/blue squiggles and gutter markers (by severity). Click to go to the line.
- **Remediation:** Shown in the problem message or in the hover where supported.

---

## Troubleshooting (extension-only)

**Extension doesn’t run or “scanner not found”**

- Ensure Python 3.11+ is installed and that `llmSecurityScanner.pythonPath` points to it.
- Run **LLM Security: Install Dependencies** or install manually: `pip install trusys-llm-scan` (and ensure Semgrep is available).
- Check **Output** → “LLM Security Scanner” for errors.

**"llm_scan package not found" or setup fails**

- The extension normally sets up the scanner automatically when you run a scan. If you see this error, ensure a **folder is open** (File → Open Folder) and run **Scan Workspace** or **Scan Current File** again; setup will run and the scan will retry.
- If it still fails, run **LLM Security: Install Dependencies** from the Command Palette. You can also set `llmSecurityScanner.pythonPath` to a Python that already has the scanner (e.g. a venv with `pip install trusys-llm-scan`).

**No findings**

- Confirm `severityFilter` includes the severities you expect.
- Check `includePatterns` / `excludePatterns` (e.g. file might be excluded).
- Run **Scan Workspace** or **Scan Current File** manually and watch Output for scanner output.

**AI analysis not running**

- Ensure `enableAiAnalysis` is `true` and `aiProvider` / `aiModel` are set.
- Set `aiApiKey` or `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`. Check Output for API errors.

**Generate Eval Tests fails**

- Set `aiProvider` and `aiModel` in settings; set `aiApiKey` or `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` in the environment.
- Ensure the workspace has Python files that define MCP tools (e.g. `@mcp.tool()`). Check **Output** → “LLM Security Scanner” for API or timeout errors.

**Database upload fails**

- Confirm `uploadEndpoint`, `applicationId`, and `apiKey` are set and that the backend is reachable.
- Use **Scan and Upload to Database** (upload is not done by the normal scan commands).

**Performance**

- Increase `scanDelay`, or disable `scanOnSave` / `scanOnOpen` and scan only via commands.
- Narrow `includePatterns` or add `excludePatterns`; set `aiMaxFindings` if using AI.

---

## Installing the extension

**From VSIX (e.g. local build)**

```bash
cd vscode-extension
npm install
npm run compile
vsce package
```

Then in VS Code: Extensions → … → Install from VSIX → choose the `.vsix` file.

**Development (F5)**

Open the `vscode-extension` folder in VS Code, press F5 to launch Extension Development Host. Use `llmSecurityScanner.pythonPath` in the host so it uses a Python with the scanner installed.

---

## More information

- Scanner and rules: see the main repository [README](https://github.com/spydra-tech/truscan) and [TEST_GENERATION.md](https://github.com/spydra-tech/truscan/blob/main/TEST_GENERATION.md) for CLI and eval tests.
- Backend/dashboard: see the main repo’s `backend/` documentation for server setup.
