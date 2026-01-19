# Prerequisites for VS Code Extension

## Required Python Packages

The extension requires the following Python packages to be installed:

### 1. Semgrep

```bash
pip install semgrep
```

### 2. LLM Scan Package

**Option A: Install from source (Recommended)**
```bash
cd /Users/manish/code-scan2
pip install -e .
```

This installs the package in "editable" mode, so changes to the code are immediately available.

**Option B: Install dependencies only**
```bash
cd /Users/manish/code-scan2
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Check semgrep
semgrep --version

# Check llm_scan
python3 -m llm_scan.runner --help
```

Both commands should work without errors.

## Installation Steps

### Complete Setup

```bash
# 1. Install semgrep
pip install semgrep

# 2. Install llm_scan package
cd /Users/manish/code-scan2
pip install -e .

# 3. Verify
python3 -m llm_scan.runner samples/vulnerable_app.py --format json
```

### Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install semgrep
pip install -e /Users/manish/code-scan2

# Verify installation
venv/bin/python -m llm_scan.runner --help  # Should work

# Configure VS Code to use venv Python
# In VS Code Settings, set:
# llmSecurityScanner.pythonPath = "venv/bin/python"
# (or "venv\\Scripts\\python.exe" on Windows)
```

**⚠️ Important**: When testing the extension with F5 (Extension Development Host), make sure the `pythonPath` setting points to the venv Python that has the packages installed!

## Common Errors and Fixes

### Error: "No module named 'semgrep'"

**Fix:**
```bash
pip install semgrep
```

### Error: "No module named 'llm_scan'"

**Fix:**
```bash
cd /Users/manish/code-scan2
pip install -e .
```

### Error: "Scanner script not found"

**Fix:** This error means the package isn't installed. The extension uses `python3 -m llm_scan.runner`, so the package must be installed via pip.

### Error: "python3: command not found"

**Fix:** Set the correct Python path in VS Code settings:
- Open Settings (Ctrl+, / Cmd+,)
- Search for "llmSecurityScanner.pythonPath"
- Set to your Python executable (e.g., `python`, `/usr/bin/python3`, `venv/bin/python`)

## Testing Installation

Run this test to verify everything works:

```bash
# Test 1: Semgrep
semgrep --version
# Should show version number

# Test 2: LLM Scanner
python3 -m llm_scan.runner samples/vulnerable_app.py --format json
# Should output JSON with findings

# Test 3: Extension
# Open VS Code, load extension, scan a file
# Should see diagnostics in Problems panel
```

## System Requirements

- **Python**: 3.11 or higher
- **pip**: Latest version
- **VS Code**: 1.74.0 or higher
- **Node.js**: For extension development (if modifying extension)

## Installation Verification

After installation, you should be able to run:

```bash
python3 -m llm_scan.runner --help
```

And see the scanner help output. If this works, the VS Code extension will work too.
