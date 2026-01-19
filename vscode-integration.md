# VS Code Extension Integration Contract

This document defines the integration contract between the LLM Security Scanner and VS Code extensions.

## Overview

The scanner provides a library interface (`run_scan_for_vscode`) that accepts a `ScanRequest` and returns a `ScanResponse`. This allows VS Code extensions to call the scanner programmatically.

## Request Schema

### ScanRequest

```json
{
  "paths": ["string"],
  "rules_dir": "string (optional)",
  "include_patterns": ["string (optional)"],
  "exclude_patterns": ["string (optional)"],
  "enabled_rules": ["string (optional)"],
  "severity_filter": ["critical" | "high" | "medium" | "low" | "info" (optional)"],
  "output_format": "json"
}
```

**Fields:**
- `paths` (required): Array of file or directory paths to scan
- `rules_dir` (optional): Path to rules directory. Defaults to `llm_scan/rules`
- `include_patterns` (optional): Glob patterns for files to include (e.g., `["*.py"]`)
- `exclude_patterns` (optional): Glob patterns for files to exclude (e.g., `["tests/**"]`)
- `enabled_rules` (optional): List of rule IDs to enable (if not provided, all rules are enabled)
- `severity_filter` (optional): Array of severity levels to include in results
- `output_format` (optional): Output format, must be `"json"` for VS Code integration

## Response Schema

### ScanResponse

```json
{
  "success": true,
  "result": {
    "findings": [
      {
        "rule_id": "string",
        "message": "string",
        "severity": "critical" | "high" | "medium" | "low" | "info",
        "category": "code-injection" | "command-injection" | "prompt-injection" | "data-exposure" | "other",
        "location": {
          "file_path": "string",
          "start_line": number,
          "start_column": number,
          "end_line": number,
          "end_column": number,
          "snippet": "string (optional)"
        },
        "cwe": "string (optional)",
        "remediation": "string (optional)",
        "dataflow_path": [
          {
            "file_path": "string",
            "start_line": number,
            "start_column": number,
            "end_line": number,
            "end_column": number,
            "message": "string"
          }
        ],
        "metadata": {}
      }
    ],
    "scanned_files": ["string"],
    "rules_loaded": ["string"],
    "scan_duration_seconds": number,
    "metadata": {}
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "string"
}
```

## Example Request

```json
{
  "paths": ["/workspace/src"],
  "rules_dir": "/workspace/llm_scan/rules/python",
  "include_patterns": ["*.py"],
  "exclude_patterns": ["tests/**", "**/__pycache__/**"],
  "severity_filter": ["critical", "high", "medium"],
  "output_format": "json"
}
```

## Example Response

```json
{
  "success": true,
  "result": {
    "findings": [
      {
        "rule_id": "llm-to-eval-complete",
        "message": "LLM output flows directly to eval/exec/compile - CRITICAL CODE INJECTION RISK",
        "severity": "critical",
        "category": "code-injection",
        "location": {
          "file_path": "/workspace/src/app.py",
          "start_line": 42,
          "start_column": 5,
          "end_line": 42,
          "end_column": 20,
          "snippet": "eval(llm_output)"
        },
        "cwe": "CWE-94",
        "remediation": "NEVER execute LLM output as code. Use safe parsing, validation, and whitelisting.",
        "dataflow_path": [],
        "metadata": {
          "semgrep_rule_id": "llm-to-eval-complete",
          "semgrep_severity": "ERROR"
        }
      }
    ],
    "scanned_files": [
      "/workspace/src/app.py",
      "/workspace/src/utils.py"
    ],
    "rules_loaded": [
      "/workspace/llm_scan/rules/python/llm-code-injection.yaml",
      "/workspace/llm_scan/rules/python/llm-command-injection.yaml"
    ],
    "scan_duration_seconds": 2.34,
    "metadata": {}
  }
}
```

## Python Usage

```python
from llm_scan.runner import run_scan_for_vscode
from llm_scan.models import ScanRequest, Severity

request = ScanRequest(
    paths=["/workspace/src"],
    rules_dir="/workspace/llm_scan/rules/python",
    include_patterns=["*.py"],
    exclude_patterns=["tests/**"],
    severity_filter=[Severity.CRITICAL, Severity.HIGH],
    output_format="json"
)

response = run_scan_for_vscode(request)

if response.success:
    for finding in response.result.findings:
        print(f"{finding.severity}: {finding.message} at {finding.location.file_path}:{finding.location.start_line}")
else:
    print(f"Scan failed: {response.error}")
```

## VS Code Extension Implementation Notes

1. **Async Execution**: The scanner can be slow for large codebases. Consider running scans in a background thread or process.

2. **Incremental Scanning**: Only scan changed files when possible. The `paths` field accepts individual files.

3. **Error Handling**: Always check `response.success` before accessing `response.result`.

4. **Progress Reporting**: The scanner doesn't provide progress callbacks. For long-running scans, consider showing a progress indicator.

5. **Caching**: Consider caching results per file hash to avoid re-scanning unchanged files.

6. **Configuration**: Allow users to configure:
   - Rules directory path
   - Severity filters
   - Include/exclude patterns
   - Enabled/disabled rules
