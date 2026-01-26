# Quick Start: Installing llm-scan from PyPI

## Installation

```bash
pip install llm-scan
```

## Basic Usage

```bash
# Scan current directory
llm-scan . --format console

# Scan specific directory
llm-scan src/ --format console

# Output to SARIF file
llm-scan . --format sarif --out results.sarif

# Output to JSON file
llm-scan . --format json --out results.json

# Filter by severity
llm-scan . --severity critical high --format console

# Upload results to server (requires API key and application ID)
llm-scan . \
  --upload https://api.example.com/v1/scans \
  --api-key YOUR_API_KEY \
  --application-id YOUR_APP_ID
```

## Help

```bash
llm-scan --help
```

## Requirements

- Python 3.11 or higher
- `semgrep` (automatically installed as a dependency)
- `requests` (automatically installed as a dependency)

## Optional: AI Filtering

To use AI-based false positive filtering, install additional dependencies:

```bash
# For OpenAI
pip install openai

# For Anthropic
pip install anthropic
```

Then use:

```bash
llm-scan . --enable-ai-filter --ai-provider openai --ai-model gpt-4
```

## More Information

See the [README.md](README.md) for full documentation.
