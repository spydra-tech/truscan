# LLM Security Scan — GitHub Action

This **GitHub Action** runs the [trusys-llm-scan](https://pypi.org/project/trusys-llm-scan/) scanner in your repository to find LLM-related security issues (prompt injection, insecure output handling, data exfiltration, etc.) using Semgrep rules and optional AI-based filtering.

---

## What this action does

- **Scans** your code (Python) for LLM security patterns (OpenAI, Anthropic, Cohere, Langchain, LlamaIndex, Hugging Face, Azure, AWS Bedrock).
- **Installs** `trusys-llm-scan` and Semgrep from PyPI — no manual setup.
- **Outputs** results as **console**, **JSON**, or **SARIF** (for GitHub Code Scanning / Security tab).
- **Optional**: AI-based false positive filtering (OpenAI or Anthropic).
- **Optional**: Upload results to your own backend (e.g. dashboard).

---

## How to use the action (step by step)

### 1. Add a workflow file

In your repo, create or edit a workflow under `.github/workflows/`.

**Example:** `.github/workflows/llm-security-scan.yml`

### 2. Minimum workflow (scan on push/PR)

Copy this into that file. Replace `spydra-tech/trusys-llm-security-scan-action` with your action repo if you use a fork.

```yaml
name: LLM Security Scan

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  llm-scan:
    name: LLM Security Scan
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Run LLM Security Scan
        uses: spydra-tech/trusys-llm-security-scan-action@v1
```

- **Checkout** is required so the action can see your code.
- The action will **install** `trusys-llm-scan` and **run** the scan. Results appear in the job log.
- By default the action outputs **SARIF** and can upload it to GitHub Code Scanning (see below).

### 3. See results

- **In the run**: Open the workflow run → select the “Run LLM Security Scan” step and read the log.
- **In GitHub Security (SARIF)**: If you use the default `format: sarif` and the upload step runs, results show under the repo’s **Security** tab → **Code scanning**.

---

## Common configurations

### Scan only certain folders

Use the `paths` input (comma-separated):

```yaml
- name: Run LLM Security Scan
  uses: spydra-tech/trusys-llm-security-scan-action@v1
  with:
    paths: 'src,app,lib'
```

### Only high and critical findings

Use the `severity` input:

```yaml
- name: Run LLM Security Scan
  uses: spydra-tech/trusys-llm-security-scan-action@v1
  with:
    severity: 'critical,high'
```

### Ignore tests and dependencies

Use the `exclude` input (comma-separated patterns):

```yaml
- name: Run LLM Security Scan
  uses: spydra-tech/trusys-llm-security-scan-action@v1
  with:
    exclude: '**/test/**,**/tests/**,**/node_modules/**,**/venv/**'
```

### Use a specific Python version

```yaml
- name: Run LLM Security Scan
  uses: spydra-tech/trusys-llm-security-scan-action@v1
  with:
    python-version: '3.11'
```

### Get JSON or console output instead of SARIF

- **Console** (readable in the log):

```yaml
  with:
    format: 'console'
```

- **JSON** (e.g. for another step to process):

```yaml
  with:
    format: 'json'
    output: 'llm-scan-results.json'
```

---

## Optional: AI-based false positive filtering

The scanner can send findings to an AI provider (OpenAI or Anthropic) to reduce false positives and improve remediation text.

1. Add **secrets** in your repo (or org):  
   - For OpenAI: `OPENAI_API_KEY`  
   - For Anthropic: `ANTHROPIC_API_KEY`
2. In the workflow, pass the key and enable the filter:

```yaml
- name: Run LLM Security Scan
  uses: spydra-tech/trusys-llm-security-scan-action@v1
  with:
    format: 'sarif'
    enable-ai-filter: 'true'
    ai-provider: 'openai'
    ai-model: 'gpt-4'
    ai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

Optional tuning:

- `ai-confidence-threshold`: e.g. `'0.8'` (0.0–1.0).
- `ai-max-findings`: cap how many findings are sent to the AI (e.g. `'100'`).

**Important:** Do not put API keys in the workflow file; always use `secrets.*`.

---

## Optional: Upload results to your backend

If you have an API that accepts scan payloads (e.g. a dashboard), you can send results there.

Provide all three: `upload-endpoint`, `application-id`, and `api-key` (the action uses these to call your API):

```yaml
- name: Run LLM Security Scan
  uses: spydra-tech/trusys-llm-security-scan-action@v1
  with:
    format: 'json'
    upload-endpoint: 'https://your-api.example.com/scan/results'
    application-id: ${{ secrets.LLM_SCAN_APPLICATION_ID }}
    api-key: ${{ secrets.LLM_SCAN_API_KEY }}
```

Store the API key and application ID in repo or org **Secrets**; do not commit them.

---

## Full example (SARIF + AI filter + custom paths)

```yaml
name: LLM Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  llm-scan:
    name: LLM Security Scan
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Run LLM Security Scan
        id: scan
        uses: spydra-tech/trusys-llm-security-scan-action@v1
        with:
          paths: 'src,app'
          severity: 'critical,high,medium'
          exclude: '**/test/**,**/__pycache__/**'
          format: 'sarif'
          python-version: '3.11'
          enable-ai-filter: 'true'
          ai-provider: 'openai'
          ai-model: 'gpt-4'
          ai-api-key: ${{ secrets.OPENAI_API_KEY }}
          ai-confidence-threshold: '0.75'
          ai-max-findings: '200'

      - name: Summary
        run: |
          echo "Findings count: ${{ steps.scan.outputs.scan-findings }}"
          echo "SARIF file: ${{ steps.scan.outputs.sarif-path }}"
```

---

## Inputs reference

| Input | Description | Default |
|-------|-------------|---------|
| `paths` | Comma-separated paths to scan (e.g. `'.'` or `'src,app'`) | `'.'` |
| `severity` | Filter by severity: `critical`, `high`, `medium`, `low`, `info` (comma-separated) | *(all)* |
| `exclude` | Comma-separated glob patterns to exclude | *(none)* |
| `include` | Comma-separated glob patterns to include | *(defaults from scanner)* |
| `python-version` | Python version for the runner | `'3.9'` |
| `format` | Output format: `console`, `json`, or `sarif` | `'sarif'` |
| `output` | Output file path (optional; used for `json`/`sarif`) | *(auto for sarif)* |
| `enable-ai-filter` | Set to `'true'` to enable AI false-positive filtering | `'false'` |
| `ai-provider` | AI provider: `openai` or `anthropic` | `'openai'` |
| `ai-model` | Model name (e.g. `gpt-4`, `claude-3-opus`) | `'gpt-4'` |
| `ai-api-key` | API key for the AI provider (prefer `secrets.*`) | *(none)* |
| `ai-confidence-threshold` | Minimum confidence for AI (0.0–1.0) | `'0.7'` |
| `ai-max-findings` | Max findings to send to AI (optional) | *(no limit)* |
| `upload-endpoint` | Your backend URL to receive scan results | *(none)* |
| `application-id` | Application ID for your backend | *(none)* |
| `api-key` | API key for your backend (prefer `secrets.*`) | *(none)* |

---

## Outputs

| Output | Description |
|--------|-------------|
| `scan-findings` | Number of findings reported by the scan. |
| `sarif-path` | Path to the SARIF file (when `format: 'sarif'`). |

You can use these in later steps, e.g. `${{ steps.<step_id>.outputs.scan-findings }}`.

---

## What gets scanned?

- **Frameworks**: OpenAI, Anthropic, Cohere, Langchain, LlamaIndex, Hugging Face, Azure OpenAI, AWS Bedrock.
- **Issue types**: Prompt injection, insecure output handling, training-data poisoning, model DoS, supply chain, sensitive data exposure, excessive agency, overreliance, model theft, and related patterns.

The scanner is **trusys-llm-scan** from PyPI; the action installs it automatically. No need to add it to your repo or install it yourself.

---

## Pinning the action version

- **Branch:** `uses: spydra-tech/trusys-llm-security-scan-action@main` — follows latest on `main`.
- **Tag:** `uses: spydra-tech/trusys-llm-security-scan-action@v1.0.0` — recommended for stable CI.
- **Commit SHA:** `uses: spydra-tech/trusys-llm-security-scan-action@abc123...` — maximum stability.

---

## Troubleshooting

| Problem | What to do |
|--------|------------|
| “Scanner not found” or Python errors | Action sets up Python automatically; ensure you use a supported runner (e.g. `ubuntu-latest`). |
| No findings but expect some | Check `paths`, `exclude`, and `severity`. Try `format: 'console'` to see full log. |
| AI step fails or “invalid API key” | Verify the secret (e.g. `OPENAI_API_KEY`) is set in repo/org and that the key is valid. |
| Upload to backend fails | Confirm `upload-endpoint`, `application-id`, and `api-key` are all set and that the endpoint is reachable from GitHub’s network. |
| SARIF not in Security tab | Ensure the job has permission to write to the Security tab and that the “Upload SARIF” step in the action ran (it runs when `format` is `sarif`). |

For more help, open an issue in the [action repository](https://github.com/spydra-tech/trusys-llm-security-scan-action).
