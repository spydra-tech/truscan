# LLM Security Scanner - GitHub Actions Workflows

This directory contains reusable GitHub Actions workflows for scanning code with the LLM Security Scanner.

## Available Workflows

### `llm-scan-reusable.yml`

A reusable workflow that can be called from any repository to scan code for LLM-specific vulnerabilities.

## Usage in Other Repositories

To use the LLM Security Scanner in your repository, create a workflow file (e.g., `.github/workflows/llm-scan.yml`) that calls the reusable workflow:

### Basic Example

```yaml
name: LLM Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  scan:
    uses: YOUR_ORG/code-scan2/.github/workflows/llm-scan-reusable.yml@main
    with:
      scanner_repo: 'YOUR_ORG/code-scan2'
      scanner_ref: 'main'
      paths: '.'
```

### Advanced Example with Custom Options

```yaml
name: LLM Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:

jobs:
  scan:
    uses: YOUR_ORG/code-scan2/.github/workflows/llm-scan-reusable.yml@main
    with:
      scanner_repo: 'YOUR_ORG/code-scan2'
      scanner_ref: 'main'
      paths: 'src/,app/'
      severity: 'critical,high,medium'
      exclude_patterns: 'tests/**,node_modules/**,**/__pycache__/**,dist/**,build/**'
      include_patterns: '*.py'
      python_version: '3.11'
      artifact_name: 'llm-security-scan-results'
      artifact_retention_days: 60
```

## Input Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `scanner_repo` | Repository containing the scanner (format: owner/repo) | No | (uses current repo if empty) |
| `scanner_ref` | Branch, tag, or SHA for the scanner repo | No | `main` |
| `paths` | Paths to scan (comma-separated) | No | `.` |
| `severity` | Filter by severity (comma-separated: critical,high,medium,low,info) | No | (all severities) |
| `exclude_patterns` | Exclude patterns (comma-separated) | No | `tests/**,.github/**,**/__pycache__/**` |
| `include_patterns` | Include patterns (comma-separated, e.g., `*.py`) | No | (all files) |
| `python_version` | Python version to use | No | `3.11` |
| `artifact_name` | Name for the SARIF artifact | No | `llm-scan-results` |
| `artifact_retention_days` | Number of days to retain the artifact | No | `30` |

## Examples

### Scan Only Python Files

```yaml
jobs:
  scan:
    uses: YOUR_ORG/code-scan2/.github/workflows/llm-scan-reusable.yml@main
    with:
      scanner_repo: 'YOUR_ORG/code-scan2'
      paths: '.'
      include_patterns: '*.py'
```

### Scan Only Critical and High Severity Issues

```yaml
jobs:
  scan:
    uses: YOUR_ORG/code-scan2/.github/workflows/llm-scan-reusable.yml@main
    with:
      scanner_repo: 'YOUR_ORG/code-scan2'
      paths: '.'
      severity: 'critical,high'
```

### Scan Multiple Directories with Custom Exclusions

```yaml
jobs:
  scan:
    uses: YOUR_ORG/code-scan2/.github/workflows/llm-scan-reusable.yml@main
    with:
      scanner_repo: 'YOUR_ORG/code-scan2'
      paths: 'src/,lib/,app/'
      exclude_patterns: 'tests/**,migrations/**,**/__pycache__/**,venv/**,.venv/**'
```

## Important Notes

1. **Repository Reference**: Replace `YOUR_ORG/code-scan2` with your actual repository path (e.g., `myorg/code-scan2`).

2. **Branch/Tag Reference**: Use `@main`, `@v1.0.0`, or any other branch/tag reference to pin to a specific version of the workflow.

3. **Permissions**: The workflow only requires `contents: read` permission, which is the default.

4. **Artifacts**: SARIF results are uploaded as artifacts that can be downloaded from the Actions run page.

5. **Private Repositories**: If your repository is private, make sure the `GITHUB_TOKEN` has access to checkout the `code-scan2` repository (or use a Personal Access Token with appropriate permissions).

## Troubleshooting

### Workflow Not Found

If you see an error like "Workflow not found", check:
- The repository path is correct
- The branch/tag reference exists
- You have access to the repository

### Permission Denied

If you see permission errors:
- Ensure `GITHUB_TOKEN` has the necessary permissions
- For private repos, you may need to use a Personal Access Token

### No Findings

If the scan completes but shows no findings:
- Check that your code actually contains LLM API calls
- Verify the paths you're scanning are correct
- Check the exclude patterns aren't too broad

## Support

For issues or questions, please open an issue in the [code-scan2 repository](https://github.com/YOUR_ORG/code-scan2).
