# Visual Studio Extension Installation Guide

## Quick Start

### Prerequisites

1. **Visual Studio 2022** (17.0 or later)
2. **Python 3.11+** with LLM Security Scanner installed:
   ```bash
   # From project root
   pip install -e .
   pip install semgrep
   ```

### Installation Steps

1. **Build the extension** (see [BUILD.md](BUILD.md))

2. **Install the VSIX:**
   - Locate `bin\Release\LLMSecurityScanner.vsix`
   - Double-click to install
   - Or: **Tools → Extensions and Updates → Install from VSIX**

3. **Restart Visual Studio**

4. **Verify installation:**
   - **Tools → Extensions and Updates**
   - Search for "LLM Security Scanner"
   - Should show as installed and enabled

## Configuration

### Python Path

1. **Tools → Options → LLM Security Scanner**
2. Set **Python Path** (default: `python3`)
3. Set **Rules Directory** (optional, defaults to package rules)

### Auto-Scan Settings

- **Scan on Save**: Automatically scan files when saved (default: enabled)
- **Scan on Open**: Scan files when opened (default: enabled)

## Usage

### Automatic Scanning

The extension automatically scans Python files when:
- A file is saved (if enabled)
- A workspace is opened
- A file is opened (if enabled)

### Manual Scanning

1. **Right-click** on a file or folder in Solution Explorer
2. Select **"Scan with LLM Security Scanner"**
3. Results appear in the **Error List**

### Viewing Results

1. Open **View → Error List** (Ctrl+\\, E)
2. Findings appear with severity indicators:
   - 🔴 **Errors** (Critical/High severity)
   - 🟡 **Warnings** (Medium severity)
   - 🔵 **Messages** (Low/Info severity)
3. **Click** on a finding to navigate to the code
4. **View details** in Error List description panel

## Troubleshooting

### Extension Not Loading

1. Check Visual Studio version (requires 17.0+)
2. Check **Output** window for errors
3. Verify extension is enabled: **Tools → Extensions and Updates**

### Scanner Not Found

1. Verify Python: `python3 --version`
2. Verify scanner: `python3 -m llm_scan.runner --help`
3. Check Python path in extension settings
4. Ensure scanner is installed in the correct Python environment

### No Findings Appearing

1. Verify file contains LLM-related code
2. Check Error List filters (may be filtered out)
3. Check **Output** window for scanner errors
4. Try manual scan: Right-click file → "Scan with LLM Security Scanner"

### Build Errors

See [BUILD.md](BUILD.md) for build troubleshooting.

## Uninstallation

1. **Tools → Extensions and Updates**
2. Find "LLM Security Scanner"
3. Click **Uninstall**
4. Restart Visual Studio

## Support

For issues or questions:
- Check the main project README
- Review [BUILD.md](BUILD.md) for build issues
- Check Visual Studio Output window for error messages
