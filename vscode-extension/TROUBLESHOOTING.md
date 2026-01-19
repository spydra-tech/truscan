# Troubleshooting Guide

## Error: "Extension 'llm-security.llm-security-scanner' not found"

This error typically occurs when VS Code cannot find or load the extension. Here are solutions:

### Solution 1: Run in Development Mode (Easiest)

1. **Open the extension folder in VS Code:**
   ```bash
   cd /Users/manish/code-scan2/vscode-extension
   code .
   ```

2. **Press F5** or go to Run → Start Debugging

3. **A new VS Code window will open** (Extension Development Host)

4. **In the new window**, open your workspace with Python files

5. The extension will activate automatically when you open a Python file

### Solution 2: Package and Install Extension

1. **Install vsce (VS Code Extension manager):**
   ```bash
   npm install -g vsce
   ```

2. **Package the extension:**
   ```bash
   cd /Users/manish/code-scan2/vscode-extension
   vsce package
   ```

3. **Install the VSIX file:**
   ```bash
   code --install-extension llm-security-scanner-1.0.0.vsix
   ```

4. **Reload VS Code:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Reload Window" and select it

### Solution 3: Check Extension Status

1. **List installed extensions:**
   ```bash
   code --list-extensions | grep llm
   ```

2. **If extension is installed, check if it's enabled:**
   - Open Extensions view (`Ctrl+Shift+X`)
   - Search for "LLM Security Scanner"
   - Make sure it's enabled (not disabled)

3. **Check extension output:**
   - View → Output
   - Select "LLM Security Scanner" from dropdown
   - Look for error messages

### Solution 4: Verify Extension Files

Make sure all required files exist:

```bash
cd /Users/manish/code-scan2/vscode-extension
ls -la out/extension.js    # Should exist
ls -la package.json        # Should exist
```

If `out/extension.js` doesn't exist, compile:
```bash
npm run compile
```

### Solution 5: Check Python Scanner Installation

The extension requires the Python scanner to be installed:

```bash
# Test if scanner works
python3 -m llm_scan.runner --help

# If not found, install it
cd /Users/manish/code-scan2
pip install -e .
```

### Solution 6: Manual Activation

If the extension doesn't activate automatically:

1. Open a Python file (`.py`)
2. The extension should activate on `onLanguage:python` event
3. Check Output panel for activation messages

### Common Issues

#### Issue: Extension compiles but doesn't run

**Fix:** Make sure you're running from the Extension Development Host window, not the main VS Code window.

#### Issue: "Cannot find module" errors

**Fix:** 
```bash
cd vscode-extension
npm install
npm run compile
```

#### Issue: Extension activates but no diagnostics

**Fix:**
1. Check that Python scanner is installed and working
2. Verify file matches include patterns (default: `*.py`)
3. Try manual scan: Command Palette → "LLM Security: Scan Current File"
4. Check severity filter settings

#### Issue: Extension ID mismatch

The extension ID format is: `{publisher}.{name}`

- Publisher: `llm-security`
- Name: `llm-security-scanner`
- Full ID: `llm-security.llm-security-scanner`

If you see a different ID in error messages, check `package.json`.

### Quick Test

1. Open Extension Development Host (F5)
2. Open `samples/vulnerable_app.py`
3. Save the file
4. Check Problems panel for diagnostics

If diagnostics appear, the extension is working!

### Getting Help

If issues persist:

1. Check VS Code Developer Tools: Help → Toggle Developer Tools
2. Check Output panel: View → Output → "LLM Security Scanner"
3. Check extension logs in Console tab of Developer Tools
4. Verify all prerequisites are installed
