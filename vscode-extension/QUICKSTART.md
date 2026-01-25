# Quick Start Guide

## Prerequisites

1. **Python 3.11+** installed and accessible
2. **LLM Security Scanner** package installed in the Python environment that VS Code will use:
   ```bash
   # Install in your Python environment
   pip install -e /path/to/code-scan2
   ```
   
   **⚠️ Critical**: The package must be installed in the same Python environment that VS Code uses. When you press F5 to test the extension, it will use the Python interpreter specified in `llmSecurityScanner.pythonPath` setting.
   
   **If using a virtual environment:**
   ```bash
   # Activate your venv first
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e /path/to/code-scan2
   
   # Then configure VS Code setting:
   # llmSecurityScanner.pythonPath = "venv/bin/python"
   ```

## Installation Steps

### 1. Install Extension Dependencies

```bash
cd vscode-extension
npm install
```

### 2. Compile Extension

```bash
npm run compile
```

### 3. Test Extension

1. Open VS Code in the `vscode-extension` directory
2. Press `F5` to launch a new Extension Development Host window
3. In the new window, open a workspace with Python files
4. The extension should automatically activate

### 4. Verify Installation

1. Open a Python file that uses LLM APIs (e.g., `samples/vulnerable_app.py`)
2. Save the file - you should see diagnostics appear in the Problems panel
3. Or run the command: "LLM Security: Scan Workspace"

## Configuration

Open VS Code settings and configure:

```json
{
  "llmSecurityScanner.enabled": true,
  "llmSecurityScanner.pythonPath": "python3",
  "llmSecurityScanner.rulesDirectory": "llm_scan/rules/python"
}
```

## Testing with Sample Files

1. Open the workspace containing the `samples/` directory
2. Open `samples/vulnerable_app.py`
3. Save the file or run "LLM Security: Scan Current File"
4. Check the Problems panel for findings

## Troubleshooting

### Extension Not Activating

- Check Output panel: View → Output → Select "LLM Security Scanner"
- Verify Python is accessible: `python3 --version`
- **Verify scanner is installed in the correct Python environment:**
  - Check which Python VS Code is using: Look at `llmSecurityScanner.pythonPath` setting
  - Test with that Python: `[pythonPath] -m llm_scan.runner --help`
  - If it fails, install the package in that environment:
    ```bash
    [pythonPath] -m pip install -e /path/to/code-scan2
    ```

### No Diagnostics Showing

- Check that file matches include patterns (default: `**/*.py`)
- Verify severity filter includes your findings
- Try manual scan: Command Palette → "LLM Security: Scan Workspace"

### Path Issues

If you see path-related errors:
- Use absolute paths in `rulesDirectory` setting
- Ensure workspace root contains `llm_scan` directory
- Check file paths in error messages

## Next Steps

- Customize severity filters
- Configure include/exclude patterns
- Set up workspace-specific settings
- Review detected vulnerabilities in Problems panel
