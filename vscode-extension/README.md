# LLM Security Scanner - VS Code Extension

A VS Code extension that integrates the LLM Security Scanner to detect AI/LLM-specific security vulnerabilities in your code.

## Features

- 🔍 **Automatic Scanning**: Scans files automatically on save and open
- ⚠️ **Real-time Diagnostics**: Shows vulnerabilities in the Problems panel
- 🎯 **OWASP Top 10 Coverage**: Detects all OWASP LLM Top 10 vulnerabilities
- 📊 **Severity Filtering**: Configure which severity levels to display
- 🚀 **Workspace Scanning**: Scan entire workspace with a single command
- 💡 **Remediation Guidance**: Shows remediation suggestions for each finding

## Installation

### From Source

1. Clone the repository
2. Navigate to the `vscode-extension` directory
3. Install dependencies:
   ```bash
   npm install
   ```
4. Compile the extension:
   ```bash
   npm run compile
   ```
5. Press `F5` in VS Code to open a new window with the extension loaded

### Package Extension

To create a `.vsix` package for distribution:

```bash
npm install -g vsce
vsce package
```

Then install the `.vsix` file in VS Code:
- Open VS Code
- Go to Extensions view
- Click "..." menu → "Install from VSIX..."
- Select the generated `.vsix` file

## Requirements

- VS Code 1.74.0 or higher
- Python 3.11+ 
- **Automatic Installation**: The extension automatically installs required Python dependencies (`semgrep` and `llm-scan`) on first activation
- **Manual Installation** (optional): If automatic installation fails, see instructions below

### Automatic Dependency Installation

The extension automatically checks and installs required Python dependencies when activated:
- **semgrep**: Static analysis engine
- **llm-scan**: The scanner package (installed from local source if available, or from PyPI)

This happens automatically in the background with a progress notification. You can disable this by setting `llmSecurityScanner.autoInstallDependencies` to `false` in settings.

### Manual Installation (If Needed)

If automatic installation fails or you prefer to install manually:

**Option 1: Install from source (Development)**
```bash
cd /path/to/code-scan2
pip install -e .
```

**Option 2: Install as package (if published)**
```bash
pip install llm-scan
```

**Option 3: Using a Virtual Environment (Recommended)**

If you're using a virtual environment, make sure to:
1. Install the package in your venv:
   ```bash
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -e /path/to/code-scan2
   ```

2. Configure VS Code to use the venv Python:
   - Open VS Code Settings (Ctrl+, / Cmd+,)
   - Search for `llmSecurityScanner.pythonPath`
   - Set it to your venv Python path (e.g., `venv/bin/python` or `venv\Scripts\python.exe`)

**Verify installation:**
```bash
# Test with the Python interpreter VS Code will use
python3 -m llm_scan.runner --help
# Or if using venv:
venv/bin/python -m llm_scan.runner --help
```

If this command works, the extension will be able to use the scanner.

**⚠️ Important for Extension Development Host:**
When you press F5 to test the extension, the Extension Development Host uses the Python interpreter specified in `llmSecurityScanner.pythonPath`. Make sure that Python environment has `llm_scan` installed!

## Configuration

The extension can be configured via VS Code settings:

```json
{
  "llmSecurityScanner.enabled": true,
  "llmSecurityScanner.rulesDirectory": "llm_scan/rules/python",
  "llmSecurityScanner.pythonPath": "python3",
  "llmSecurityScanner.severityFilter": ["critical", "high", "medium"],
  "llmSecurityScanner.includePatterns": ["*.py"],
  "llmSecurityScanner.excludePatterns": ["**/__pycache__/**", "**/node_modules/**"],
  "llmSecurityScanner.scanOnSave": true,
  "llmSecurityScanner.scanOnOpen": true,
  "llmSecurityScanner.scanDelay": 500,
  "llmSecurityScanner.autoInstallDependencies": true
}
```

### Settings

- **`llmSecurityScanner.enabled`**: Enable/disable the extension
- **`llmSecurityScanner.rulesDirectory`**: Path to rules directory (relative to workspace root)
- **`llmSecurityScanner.pythonPath`**: Path to Python interpreter
- **`llmSecurityScanner.severityFilter`**: Array of severity levels to show
- **`llmSecurityScanner.includePatterns`**: File patterns to include
- **`llmSecurityScanner.excludePatterns`**: File patterns to exclude
- **`llmSecurityScanner.scanOnSave`**: Automatically scan files on save
- **`llmSecurityScanner.scanOnOpen`**: Automatically scan files when opened
- **`llmSecurityScanner.scanDelay`**: Delay in milliseconds before scanning after changes
- **`llmSecurityScanner.autoInstallDependencies`**: Automatically install Python dependencies on extension activation (default: true)

## Commands

The extension provides the following commands (accessible via Command Palette `Ctrl+Shift+P` / `Cmd+Shift+P`):

- **LLM Security: Scan Workspace** - Scan entire workspace for vulnerabilities
- **LLM Security: Scan Current File** - Scan only the currently active file
- **LLM Security: Clear Results** - Clear all diagnostic results
- **LLM Security: Install Dependencies** - Manually trigger dependency installation

## Usage

### Automatic Scanning

By default, the extension automatically scans files when:
- A file is saved
- A file is opened

You can disable this behavior in settings.

### Manual Scanning

1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type "LLM Security"
3. Select "Scan Workspace" or "Scan Current File"

### Viewing Results

Scan results appear in the **Problems** panel:
- Critical/Error findings show as red errors
- High/Medium findings show as yellow warnings
- Low/Info findings show as blue information

Click on a finding to jump to the code location.

## Detected Vulnerabilities

The extension detects vulnerabilities from the OWASP LLM Top 10:

1. **LLM01: Prompt Injection** - Unsanitized user input in prompts
2. **LLM02: Insecure Output Handling** - LLM output used unsafely
3. **LLM03: Training Data Poisoning** - Training data from untrusted sources
4. **LLM04: Model Denial of Service** - Resource exhaustion attacks
5. **LLM05: Supply Chain Vulnerabilities** - Untrusted models/plugins
6. **LLM06: Sensitive Information Disclosure** - Secrets/PII in prompts
7. **LLM07: Insecure Plugin Design** - Plugin execution without authorization
8. **LLM08: Excessive Agency** - Overprivileged LLM actions
9. **LLM09: Overreliance** - Blind trust in LLM output
10. **LLM10: Model Theft** - Unauthorized model access

Plus additional code injection and command injection patterns.

## Troubleshooting

### Extension Not Working

1. Check that Python is installed and accessible
2. Verify that `llm_scan` package is installed:
   ```bash
   python3 -m llm_scan.runner --help
   ```
3. Check the Output panel for error messages (View → Output → "LLM Security Scanner")

### No Results Showing

1. Verify that files match the `includePatterns` setting
2. Check that files are not excluded by `excludePatterns`
3. Ensure severity filter includes the severity of findings
4. Try running "Scan Workspace" command manually

### Performance Issues

- Increase `scanDelay` to reduce scanning frequency
- Disable `scanOnSave` or `scanOnOpen` if scanning is too frequent
- Use `excludePatterns` to skip large directories

## Development

### Building

```bash
npm install
npm run compile
```

### Watching for Changes

```bash
npm run watch
```

### Testing

```bash
npm test
```

## License

Same as the main LLM Security Scanner project.

## Contributing

Contributions welcome! Please see the main project README for contribution guidelines.
