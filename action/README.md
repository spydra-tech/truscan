# LLM Security Scan GitHub Action

A GitHub Action that scans your codebase for LLM (Large Language Model) security vulnerabilities using Semgrep and optional AI-powered analysis.

## Features

- 🔍 **Comprehensive Scanning**: Detects LLM-specific vulnerabilities across multiple frameworks (OpenAI, Anthropic, Cohere, Langchain, LlamaIndex, Hugging Face, Azure, AWS Bedrock)
- 🤖 **AI-Powered Analysis**: Optional AI filtering to reduce false positives and enhance remediation guidance
- 📊 **Multiple Output Formats**: Supports console, JSON, and SARIF formats
- 🔗 **Backend Integration**: Optional upload of results to your backend API
- ⚡ **Fast & Reliable**: Built on Semgrep for efficient static analysis

## Usage

### Basic Usage

```yaml
name: LLM Security Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run LLM Security Scan
        uses: your-org/llm-security-scan-action@v1
```

### Advanced Usage with AI Analysis

```yaml
name: LLM Security Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run LLM Security Scan with AI
        uses: your-org/llm-security-scan-action@v1
        with:
          paths: 'src,lib'
          severity: 'high,critical'
          exclude: '**/test/**,**/node_modules/**'
          format: 'sarif'
          enable-ai-filter: 'true'
          ai-provider: 'openai'
          ai-model: 'gpt-4'
          ai-api-key: ${{ secrets.OPENAI_API_KEY }}
          ai-confidence-threshold: '0.8'
          ai-max-findings: '100'
```

### With Backend Upload

```yaml
name: LLM Security Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run LLM Security Scan and Upload
        uses: your-org/llm-security-scan-action@v1
        with:
          format: 'sarif'
          upload-endpoint: 'https://api.example.com/scans'
          application-id: ${{ secrets.APPLICATION_ID }}
          api-key: ${{ secrets.API_KEY }}
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `paths` | Comma-separated list of paths to scan | No | `.` |
| `severity` | Filter findings by severity (critical, high, medium, low, info) | No | `` |
| `exclude` | Comma-separated list of patterns to exclude | No | `` |
| `include` | Comma-separated list of patterns to include | No | `` |
| `python-version` | Python version to use | No | `3.9` |
| `format` | Output format (console, json, sarif) | No | `sarif` |
| `output` | Output file path | No | `` |
| `enable-ai-filter` | Enable AI-powered false positive filtering | No | `false` |
| `ai-provider` | AI provider (openai, anthropic) | No | `openai` |
| `ai-model` | AI model to use (e.g., gpt-4, claude-3-opus) | No | `gpt-4` |
| `ai-api-key` | API key for AI provider (use secrets) | No | `` |
| `ai-confidence-threshold` | Minimum confidence threshold for AI analysis (0.0-1.0) | No | `0.7` |
| `ai-max-findings` | Maximum number of findings to analyze with AI | No | `` |
| `upload-endpoint` | Backend API endpoint for uploading scan results | No | `` |
| `application-id` | Application ID for backend upload | No | `` |
| `api-key` | API key for backend upload (use secrets) | No | `` |

## Outputs

| Output | Description |
|--------|-------------|
| `scan-findings` | Number of findings detected |
| `sarif-path` | Path to SARIF output file |

## Examples

### Scan Specific Directories

```yaml
- uses: your-org/llm-security-scan-action@v1
  with:
    paths: 'src,lib,tests'
```

### Filter by Severity

```yaml
- uses: your-org/llm-security-scan-action@v1
  with:
    severity: 'critical,high'
```

### Exclude Patterns

```yaml
- uses: your-org/llm-security-scan-action@v1
  with:
    exclude: '**/test/**,**/node_modules/**,**/*.test.py'
```

### AI Analysis with Custom Threshold

```yaml
- uses: your-org/llm-security-scan-action@v1
  with:
    enable-ai-filter: 'true'
    ai-provider: 'anthropic'
    ai-model: 'claude-3-opus'
    ai-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
    ai-confidence-threshold: '0.85'
    ai-max-findings: '50'
```

### Upload to Backend

```yaml
- uses: your-org/llm-security-scan-action@v1
  with:
    format: 'json'
    upload-endpoint: 'https://api.example.com/api/scans'
    application-id: 'my-app-123'
    api-key: ${{ secrets.BACKEND_API_KEY }}
```

## Security Best Practices

1. **Never commit API keys**: Always use GitHub Secrets for sensitive values like `ai-api-key` and `api-key`
2. **Use least privilege**: Only grant necessary permissions to the action
3. **Review findings**: Regularly review scan results and update your code accordingly
4. **Keep updated**: Use the latest version of the action for security updates

## Supported Frameworks

- OpenAI
- Anthropic (Claude)
- Cohere
- Langchain
- LlamaIndex
- Hugging Face
- Azure OpenAI
- AWS Bedrock

## Requirements

- Python 3.9 or higher
- The scanner will be automatically installed from PyPI (`trusys-llm-scan`)

## Troubleshooting

### Scanner not found
Ensure Python is properly set up. The action uses `actions/setup-python@v5` by default.

### AI analysis not working
- Verify your API key is correctly set in GitHub Secrets
- Check that the AI provider and model are supported
- Review the action logs for detailed error messages

### Upload failing
- Verify all required inputs (`upload-endpoint`, `application-id`, `api-key`) are provided
- Check that your backend API is accessible from GitHub Actions runners
- Review network connectivity and authentication

## License

[Your License Here]

## Support

For issues and questions, please open an issue in the repository.
