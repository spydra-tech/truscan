# Scanner Installation Guide

## The Issue

If you see: `Scanner script not found at /path/to/llm_scan/runner.py`

This means the `llm_scan` Python package is not installed or not accessible.

## Solution: Install the Scanner Package

The VS Code extension uses the installed `llm_scan` package via:
```bash
python3 -m llm_scan.runner
```

### Step 1: Install from Source

```bash
# Navigate to the scanner project
cd /Users/manish/code-scan2

# Install in development mode
pip install -e .
```

### Step 2: Verify Installation

```bash
python3 -m llm_scan.runner --help
```

You should see help output. If you see "No module named llm_scan", the installation failed.

### Step 3: Check Python Path

The extension uses `python3` by default. If your Python is named differently:

1. Open VS Code Settings
2. Search for "LLM Security Scanner"
3. Set `llmSecurityScanner.pythonPath` to your Python executable:
   - `python`
   - `/usr/bin/python3`
   - `/path/to/venv/bin/python`
   - etc.

### Step 4: Test the Extension

1. Reload VS Code window
2. Open a Python file
3. Save the file
4. Check Problems panel for diagnostics

## Alternative: Use Virtual Environment

If you're using a virtual environment:

```bash
# Activate your venv
source venv/bin/activate  # or: . venv/bin/activate

# Install scanner
pip install -e /path/to/code-scan2

# Set Python path in VS Code settings
# llmSecurityScanner.pythonPath: "venv/bin/python"
```

## Troubleshooting

### Error: "No module named llm_scan"

**Fix:** Install the package:
```bash
pip install -e /Users/manish/code-scan2
```

### Error: "python3: command not found"

**Fix:** Set the correct Python path in VS Code settings:
- `llmSecurityScanner.pythonPath`: Set to your Python executable

### Error: "Permission denied"

**Fix:** Use a virtual environment or install with `--user`:
```bash
pip install --user -e /Users/manish/code-scan2
```

### Error: "Scanner process timed out"

**Fix:** 
- Check if scanner is working: `python3 -m llm_scan.runner samples/ --format json`
- Increase timeout in code if needed (currently 30 seconds)

## Verification Checklist

- [ ] `python3 -m llm_scan.runner --help` works
- [ ] VS Code setting `llmSecurityScanner.pythonPath` is correct
- [ ] Extension is loaded (check Output panel)
- [ ] Python file opens without errors
- [ ] Manual scan works (Command Palette → "LLM Security: Scan Current File")

## Quick Test

```bash
# Test scanner directly
python3 -m llm_scan.runner samples/vulnerable_app.py --format json

# Should output JSON with findings
```

If this works, the extension should work too!
