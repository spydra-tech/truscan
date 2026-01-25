# Change Log

All notable changes to the LLM Security Scanner VS Code Extension will be documented in this file.

## [1.0.0] - 2024-01-23

### Added
- Initial release
- **Automatic semgrep installation** - No manual setup required! semgrep is automatically installed when you install the extension
- Automatic file scanning on save and open
- Workspace scanning support
- Real-time diagnostics in Problems panel
- OWASP LLM Top 10 vulnerability detection
- Configurable severity filtering
- Support for Python files
- Command palette integration
- Progress indicators for workspace scans
- Diagnostic caching for performance
- Virtual environment creation for externally-managed Python environments

### Features
- **Automatic Scanning**: Files are scanned automatically when saved or opened
- **Manual Scanning**: Commands to scan workspace or current file
- **Severity Levels**: Configurable severity filtering (critical, high, medium, low, info)
- **Problem Panel Integration**: Findings appear as diagnostics with proper severity
- **Remediation Guidance**: Shows remediation suggestions for each finding
- **CWE Links**: Clickable links to CWE documentation

### Configuration
- Enable/disable extension
- Configure Python path
- Set rules directory
- Configure include/exclude patterns
- Control scan behavior (on save, on open)
- Adjust scan delay for performance
