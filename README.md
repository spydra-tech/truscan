# LLM Security Scanner

A Python-based code scanning tool that uses the Semgrep Python SDK to detect AI/LLM-specific vulnerabilities. This tool is designed to run in both GitHub Actions (headless CI) and as the scanning engine behind a VS Code extension.

## Components

- **Scanner** (`llm_scan/`): Python package for scanning code
- **VS Code Extension** (`vscode-extension/`): IDE integration
- **Visual Studio Extension** (`visual-studio-extension/`): Full IDE integration
- **Backend API** (`backend/`): Node.js server with MySQL for storing scan results (similar to Semgrep dashboard)

## Features

- **Semgrep Python SDK Integration**: Uses Semgrep's Python APIs directly (no CLI subprocess calls)
- **Multi-language Support**: Architecture supports Python, JavaScript, and TypeScript (initial rules are Python-focused)
- **Offline-first**: All scanning runs without network access
- **Multiple Output Formats**: SARIF (for GitHub Code Scanning), JSON (for VS Code), and human-readable console output
- **Extensible Rule System**: Easy to add new rule packs and vulnerability patterns
- **Performance Optimized**: Incremental scanning, respects .gitignore, configurable include/exclude patterns

## Installation

### From PyPI (Recommended)

```bash
pip install llm-scan
```

This will install the `llm-scan` command-line tool and all dependencies.

### From Source

For development or if you need the latest version:

```bash
# Clone the repository
git clone https://github.com/your-org/code-scan2.git
cd code-scan2

# Install dependencies
pip install semgrep requests

# Install in development mode
pip install -e .
```

## Quick Start

### Command Line Usage

After installation, you can use the `llm-scan` command:

```bash
# Scan current directory
llm-scan . --format console

# Or use as a Python module
python -m llm_scan.runner . --format console

# Scan specific paths with SARIF output
python -m llm_scan.runner \
  src/ tests/ \
  --rules llm_scan/rules/python \
  --format sarif \
  --out results.sarif \
  --exclude 'tests/**' \
  --exclude '**/__pycache__/**'

# Filter by severity
python -m llm_scan.runner \
  . \
  --severity critical high \
  --format json \
  --out results.json

# Enable AI-based false positive filtering
python -m llm_scan.runner \
  . \
  --enable-ai-filter \
  --ai-provider openai \
  --ai-model gpt-4 \
  --format console

# AI filtering with specific rules only
python -m llm_scan.runner \
  . \
  --enable-ai-filter \
  --ai-analyze-rules openai-prompt-injection-direct \
  --ai-analyze-rules openai-excessive-agency-file-deletion \
  --format console
```

### Python Library Usage

```python
from llm_scan.config import ScanConfig
from llm_scan.runner import run_scan
from llm_scan.models import Severity

config = ScanConfig(
    paths=["src/"],
    rules_dir="llm_scan/rules/python",
    include_patterns=["*.py"],
    exclude_patterns=["tests/**"],
    severity_filter=[Severity.CRITICAL, Severity.HIGH],
    output_format="json",
)

result = run_scan(config)
for finding in result.findings:
    print(f"{finding.severity}: {finding.message}")
```

### VS Code Extension Integration

```python
from llm_scan.runner import run_scan_for_vscode
from llm_scan.models import ScanRequest, Severity

request = ScanRequest(
    paths=["/workspace/src"],
    rules_dir="/workspace/llm_scan/rules/python",
    include_patterns=["*.py"],
    severity_filter=[Severity.CRITICAL, Severity.HIGH],
    output_format="json"
)

response = run_scan_for_vscode(request)
if response.success:
    # Process response.result.findings
    pass
```

See [vscode-integration.md](vscode-integration.md) for the complete integration contract.

## AI-Powered False Positive Filtering

The scanner includes an optional AI-based false positive filter that uses LLM APIs to analyze Semgrep findings and filter out false positives. This feature helps reduce noise and improve the accuracy of security findings.

### How It Works

1. **Semgrep Scan**: First, Semgrep runs and finds potential vulnerabilities
2. **AI Analysis**: Selected findings are analyzed by an AI model (OpenAI GPT-4 or Anthropic Claude)
3. **Context-Aware Filtering**: AI considers code context, sanitization, framework protections, and exploitability
4. **Confidence-Based Filtering**: Only high-confidence false positives are filtered (configurable threshold)

### Usage

```bash
# Enable AI filtering with OpenAI
python -m llm_scan.runner . \
  --enable-ai-filter \
  --ai-provider openai \
  --ai-model gpt-4 \
  --ai-confidence-threshold 0.7

# Use Anthropic Claude
python -m llm_scan.runner . \
  --enable-ai-filter \
  --ai-provider anthropic \
  --ai-model claude-3-opus-20240229

# Analyze only specific rules (cost optimization)
python -m llm_scan.runner . \
  --enable-ai-filter \
  --ai-analyze-rules openai-prompt-injection-direct \
  --ai-analyze-rules openai-excessive-agency-file-deletion
```

### Configuration Options

- `--enable-ai-filter`: Enable AI filtering
- `--ai-provider`: Choose provider (`openai` or `anthropic`)
- `--ai-model`: Model name (e.g., `gpt-4`, `gpt-3.5-turbo`, `claude-3-opus-20240229`)
- `--ai-api-key`: API key (or use environment variables)
- `--ai-confidence-threshold`: Confidence threshold (0.0-1.0, default: 0.7)
- `--ai-analyze-rules`: Specific rule IDs to analyze (can be used multiple times)

### Cost Considerations

- AI filtering is **optional** and **disabled by default**
- Only analyzes findings with `confidence: "medium"` or `"low"` by default
- Uses caching to avoid re-analyzing identical code patterns
- Processes findings in batches for efficiency
- Estimated cost: ~$0.01-0.10 per analyzed finding

### When to Use AI Filtering

- **Recommended for**: Medium/low confidence rules, complex patterns, reducing false positives
- **Not needed for**: High confidence rules, simple patterns, cost-sensitive environments
- **Best practice**: Start with specific rules (`--ai-analyze-rules`) to test effectiveness

## Detected Vulnerabilities

The scanner detects vulnerabilities based on the **OWASP Top 10 for LLM Applications**:

### OWASP LLM Top 10 Coverage

1. **LLM01: Prompt Injection** - Unsanitized user input in prompts
2. **LLM02: Insecure Output Handling** - LLM output used unsafely (code/command injection, XSS)
3. **LLM03: Training Data Poisoning** - Training data from untrusted sources
4. **LLM04: Model Denial of Service** - Resource exhaustion through excessive tokens/requests
5. **LLM05: Supply Chain Vulnerabilities** - Untrusted models, libraries, or plugins
6. **LLM06: Sensitive Information Disclosure** - Secrets/PII in prompts or responses
7. **LLM07: Insecure Plugin Design** - Plugin execution without authorization/validation
8. **LLM08: Excessive Agency** - LLM granted excessive permissions
9. **LLM09: Overreliance** - Blind trust in LLM output without validation
10. **LLM10: Model Theft** - Unauthorized model access or extraction

### Core Vulnerability Patterns

- **Code Injection (CWE-94)**: LLM output passed to `eval()`, `exec()`, or `compile()`
- **Command Injection (CWE-78)**: LLM output passed to `subprocess.run()`, `subprocess.call()`, `subprocess.Popen()`, or `os.system()`
- **XSS (CWE-79)**: LLM output rendered in HTML without escaping

### Supported LLM APIs

- **OpenAI**:
  - Legacy API (`openai.ChatCompletion.create`, `openai.Completion.create`)
  - v1 client (`OpenAI().chat.completions.create`)
- **Anthropic**: `Anthropic().messages.create`
- **Generic LLM wrappers**: `call_llm()`, `.llm()`, `.generate()`, `.chat()`

Rules are organized by provider in `python/{provider}/generic/` directories.

## Project Structure

```
llm_scan/
├── __init__.py
├── models.py              # Data models (Finding, ScanResult, etc.)
├── config.py              # Configuration management
├── runner.py              # Main entry point and CLI
├── engine/
│   ├── semgrep_engine.py  # Semgrep Python SDK integration
│   ├── ai_engine.py       # AI-based false positive filtering
│   └── ai_providers.py    # AI provider implementations (OpenAI, Anthropic)
├── utils/
│   └── code_context.py    # Code context extraction for AI analysis
├── output/
│   ├── sarif.py           # SARIF formatter
│   ├── json.py            # JSON formatter
│   └── console.py         # Console formatter
├── enrich/
│   └── uploader.py        # Optional upload interface
└── rules/
    └── python/            # Semgrep rule packs
        ├── openai/        # OpenAI-specific rules
        │   ├── generic/   # Framework-agnostic OpenAI rules
        │   │   ├── prompt-injection.yaml
        │   │   ├── code-injection.yaml
        │   │   ├── command-injection.yaml
        │   │   ├── sql-injection.yaml
        │   │   ├── sensitive-info-disclosure.yaml
        │   │   ├── model-dos.yaml
        │   │   ├── overreliance.yaml
        │   │   ├── supply-chain.yaml
        │   │   ├── jailbreak.yaml
        │   │   ├── data-exfiltration.yaml
        │   │   ├── inventory.yaml
        │   │   └── taint-sources.yaml
        │   ├── flask/     # Flask-specific patterns (future)
        │   └── django/    # Django-specific patterns (future)
        ├── anthropic/     # Anthropic-specific rules
        │   └── generic/
        │       ├── prompt-injection.yaml
        │       ├── code-injection.yaml
        │       ├── inventory.yaml
        │       └── taint-sources.yaml
        └── [other providers]/  # Additional LLM providers
```

## Adding New Rules

### How to Add a New Rule Pack

1. Create a new YAML file in the appropriate location following the structure:
   - `llm_scan/rules/python/{llm_framework}/generic/` for framework-agnostic rules
   - `llm_scan/rules/python/{llm_framework}/{web_framework}/` for web framework-specific rules
   - Example: `llm_scan/rules/python/openai/generic/my-new-rule.yaml`

```yaml
rules:
  - id: my-new-rule
    pattern: |
      $LLM_OUTPUT = ...
      dangerous_function($LLM_OUTPUT)
    message: "LLM output passed to dangerous function"
    severity: ERROR
    languages: [python]
    metadata:
      category: security
      cwe: "CWE-XXX"
      remediation: "Fix guidance here"
    paths:
      include:
        - "**/*.py"
```

2. The rule will be automatically loaded when scanning with the rules directory.

### How to Add a Sink Family

Sinks are dangerous functions that should not receive untrusted LLM output. To add a new sink family:

1. Add patterns to existing rule files in the appropriate framework directory:
   - For OpenAI: `llm_scan/rules/python/openai/generic/{vulnerability-type}.yaml`
   - For Anthropic: `llm_scan/rules/python/anthropic/generic/{vulnerability-type}.yaml`

```yaml
rules:
  - id: llm-to-new-sink
    patterns:
      - pattern-either:
          - pattern: dangerous_sink1($LLM_OUTPUT)
          - pattern: dangerous_sink2($LLM_OUTPUT)
      - pattern-inside: |
          $LLM_RESPONSE = $LLM_CALL(...)
          ...
    message: "LLM output flows to dangerous sink"
    severity: ERROR
    languages: [python]
```

2. Update the category mapping in `llm_scan/engine/semgrep_engine.py` if needed:

```python
CATEGORY_MAP = {
    "code-injection": Category.CODE_INJECTION,
    "command-injection": Category.COMMAND_INJECTION,
    "llm-to-new-sink": Category.OTHER,  # Add your category
}
```

### How to Add a Provider/Source

LLM providers are sources of taint. To add support for a new LLM provider:

1. Create the provider directory structure:
   ```bash
   mkdir -p llm_scan/rules/python/{new_provider}/generic
   ```

2. Add taint source patterns to `llm_scan/rules/python/{new_provider}/generic/taint-sources.yaml`:

```yaml
rules:
  - id: llm-taint-new-provider
    patterns:
      - pattern: $CLIENT.new_provider_api(...)
      - pattern-inside: |
          $RESPONSE = ...
          $CONTENT = $RESPONSE.output
          ...
          $SINK($CONTENT)
    message: "New provider API response content flows to dangerous sink"
    severity: WARNING
    languages: [python]
```

3. Add complete taint flow rules in `llm_scan/rules/python/{new_provider}/generic/code-injection.yaml` or similar:

```yaml
rules:
  - id: llm-to-sink-new-provider
    patterns:
      - pattern: |
          $RESPONSE = $CLIENT.new_provider_api(...)
      - pattern: |
          $CONTENT = $RESPONSE.output
      - pattern: |
          dangerous_sink($CONTENT)
    message: "New provider LLM output flows to dangerous sink"
    severity: ERROR
```

## Running Locally

### Basic Scan

```bash
python -m llm_scan.runner --paths . --format console
```

### With Custom Rules

```bash
python -m llm_scan.runner \
  --paths src/ \
  --rules /path/to/custom/rules \
  --format json \
  --out results.json
```

### Exclude Patterns

```bash
python -m llm_scan.runner \
  --paths . \
  --exclude 'tests/**' \
  --exclude '**/__pycache__/**' \
  --exclude '.venv/**'
```

## Running in CI

### GitHub Actions

See [.github/workflows/llm-scan.yml](.github/workflows/llm-scan.yml) for a complete example.

The workflow:
1. Checks out code
2. Sets up Python
3. Installs dependencies (semgrep, pytest)
4. Runs the scanner
5. Uploads SARIF results to GitHub Code Scanning

### Other CI Systems

The scanner can be integrated into any CI system that supports Python:

```bash
pip install semgrep
pip install -e .
python -m llm_scan.runner \
  --paths . \
  --format sarif \
  --out results.sarif
```

## Testing

Run tests with pytest:

```bash
pip install pytest
pytest tests/
```

### Test Fixtures

The `tests/fixtures/` directory contains:
- **Positive tests** (`positive/`): Files that should trigger findings
- **Negative tests** (`negative/`): Files that should not trigger findings

### Running Specific Tests

```bash
# Test engine only
pytest tests/test_engine.py

# Test output formatters
pytest tests/test_output.py

# Test with verbose output
pytest -v tests/
```

## Output Formats

### SARIF (Static Analysis Results Interchange Format)

For GitHub Code Scanning integration:

```bash
python -m llm_scan.runner --paths . --format sarif --out results.sarif
```

### JSON

For programmatic consumption:

```bash
python -m llm_scan.runner --paths . --format json --out results.json
```

### Console

Human-readable output (default):

```bash
python -m llm_scan.runner --paths . --format console
```

## Configuration

### ScanConfig Options

- `paths`: List of paths to scan (files or directories)
- `rules_dir`: Path to rules directory
- `include_patterns`: Glob patterns for files to include
- `exclude_patterns`: Glob patterns for files to exclude
- `enabled_rules`: List of rule IDs to enable (None = all)
- `disabled_rules`: List of rule IDs to disable
- `severity_filter`: List of severity levels to include
- `output_format`: "sarif", "json", or "console"
- `output_file`: Output file path (optional for console)
- `respect_gitignore`: Whether to respect .gitignore (default: True)
- `max_target_bytes`: Maximum file size to scan (default: 1MB)

## Extensibility

### Rule Pack Abstraction

Rule packs are defined by:
- Name
- Languages supported
- Path to rule files
- Version
- Default enabled status

### Plugin Registry

Future versions will support:
- Entrypoint-based rule pack discovery
- Local folder configuration
- Remote rule pack fetching (with offline fallback)

## Performance Considerations

- **Incremental Scanning**: Only scan changed files when possible
- **File Size Limits**: Large files (>1MB) are skipped by default
- **Gitignore Support**: Automatically excludes files in .gitignore
- **Parallel Execution**: Semgrep handles parallel rule execution internally

## Limitations

- Initial rule set focuses on Python vulnerabilities
- JavaScript/TypeScript rules are planned but not yet implemented
- Dataflow analysis is limited to Semgrep's taint tracking capabilities
- Some complex taint flows may require multiple rule passes

## Contributing

1. Add test fixtures for new vulnerability patterns
2. Create Semgrep YAML rules following existing patterns
3. Update documentation
4. Add tests for new functionality

## License

[Specify your license here]

## Acknowledgments

- Built on [Semgrep](https://semgrep.dev/)
- Inspired by security scanning tools like CodeQL and Bandit
