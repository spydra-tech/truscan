# VS Code Extension Overview

## Structure

```
vscode-extension/
├── src/
│   ├── extension.ts          # Main extension entry point
│   ├── scanner.ts            # Scanner integration with Python backend
│   ├── diagnosticProvider.ts # Converts findings to VS Code diagnostics
│   └── models.ts             # TypeScript interfaces matching scanner output
├── package.json              # Extension manifest and configuration
├── tsconfig.json             # TypeScript compilation settings
├── README.md                 # User documentation
├── QUICKSTART.md             # Quick start guide
├── CHANGELOG.md              # Version history
└── .vscode/
    ├── launch.json           # Debug configuration
    └── tasks.json            # Build tasks
```

## Architecture

### Extension Entry Point (`extension.ts`)
- Activates extension on Python/JavaScript/TypeScript files
- Registers commands and event handlers
- Manages extension lifecycle

### Scanner Integration (`scanner.ts`)
- Spawns Python process to run `llm_scan.runner`
- Handles JSON output parsing
- Implements caching for performance
- Manages workspace path resolution

### Diagnostic Provider (`diagnosticProvider.ts`)
- Converts scanner findings to VS Code diagnostics
- Maps severity levels (critical → Error, high/medium → Warning, etc.)
- Handles debouncing for file change events
- Shows progress indicators for workspace scans

### Models (`models.ts`)
- TypeScript interfaces matching scanner JSON output
- Ensures type safety when parsing scanner results

## Key Features

### 1. Automatic Scanning
- **On Save**: Scans file when saved (configurable)
- **On Open**: Scans file when opened (configurable)
- **Debounced**: Waits for file changes to settle before scanning

### 2. Manual Commands
- **Scan Workspace**: Scans entire workspace with progress indicator
- **Scan Current File**: Scans only the active editor
- **Clear Results**: Removes all diagnostics

### 3. Diagnostics Integration
- Findings appear in Problems panel
- Severity-based coloring (Error/Warning/Info)
- Clickable CWE links
- Remediation guidance in related information

### 4. Configuration
All settings are in VS Code settings:
- Enable/disable extension
- Python path
- Rules directory
- Severity filters
- Include/exclude patterns
- Scan behavior (on save/open)
- Scan delay

## Integration with Scanner

The extension calls the Python scanner via:

```bash
python3 -m llm_scan.runner <path> --format json --rules <rules_dir>
```

The scanner outputs JSON which is parsed and converted to VS Code diagnostics.

## Performance Considerations

1. **Caching**: Results are cached per file based on modification time
2. **Debouncing**: File changes are debounced to avoid excessive scanning
3. **Incremental**: Only scans changed files when possible
4. **Async**: All scanning is asynchronous to avoid blocking UI

## Future Enhancements

Potential improvements:
- Language server protocol (LSP) for better integration
- Code actions for quick fixes
- Hover information showing vulnerability details
- Status bar indicator showing scan status
- Support for more languages (JavaScript, TypeScript)
- Batch scanning with progress reporting
- Integration with VS Code's Code Actions API

## Testing

To test the extension:

1. Open extension in VS Code
2. Press F5 to launch Extension Development Host
3. In new window, open workspace with Python files
4. Open a vulnerable file (e.g., `samples/vulnerable_app.py`)
5. Save file and check Problems panel

## Building for Distribution

```bash
npm install -g vsce
vsce package
```

This creates a `.vsix` file that can be installed in VS Code.
