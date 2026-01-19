# Quick Fix: "Extension Not Found" Error

## The Problem

VS Code is looking for extension `llm-security.llm-security-scanner` but can't find it because it's not installed yet.

## Quick Solution (2 minutes)

### Option 1: Run in Development Mode (No Installation Needed)

1. **Open extension folder in VS Code:**
   ```bash
   cd /Users/manish/code-scan2/vscode-extension
   code .
   ```

2. **Press F5** (or Run → Start Debugging)

3. **A new window opens** - this is your Extension Development Host

4. **In the new window**, open your workspace:
   - File → Open Folder
   - Select your project folder

5. **Open a Python file** - extension activates automatically!

✅ **Done!** The extension is now running in development mode.

### Option 2: Install as Extension

1. **Install vsce:**
   ```bash
   npm install -g vsce
   ```

2. **Package extension:**
   ```bash
   cd /Users/manish/code-scan2/vscode-extension
   vsce package
   ```

3. **Install:**
   ```bash
   code --install-extension llm-security-scanner-1.0.0.vsix
   ```

4. **Reload VS Code:**
   - `Ctrl+Shift+P` → "Reload Window"

✅ **Done!** Extension is now installed.

## Verify It's Working

1. Open a Python file with LLM code (e.g., `samples/vulnerable_app.py`)
2. Save the file
3. Check Problems panel (View → Problems)
4. You should see diagnostics if vulnerabilities are found

## Still Not Working?

### Error: "llm_scan package not found" in Extension Development Host

This error occurs when the Extension Development Host (the window that opens when you press F5) uses a Python environment that doesn't have `llm_scan` installed.

**Solution:**

1. **Check which Python the extension is using:**
   - In the Extension Development Host window, open Settings (Ctrl+, / Cmd+,)
   - Search for `llmSecurityScanner.pythonPath`
   - Note the Python path (default is `python3`)

2. **Verify the package is installed in that Python:**
   ```bash
   # Test with the exact Python path from settings
   python3 -m llm_scan.runner --help
   # Or if using venv:
   venv/bin/python -m llm_scan.runner --help
   ```

3. **If it fails, install in that environment:**
   ```bash
   # Install in the Python environment VS Code uses
   python3 -m pip install -e /path/to/code-scan2
   # Or if using venv:
   source venv/bin/activate
   pip install -e /path/to/code-scan2
   ```

4. **If using a virtual environment:**
   - Make sure to set `llmSecurityScanner.pythonPath` to your venv Python:
     - `venv/bin/python` (macOS/Linux)
     - `venv\Scripts\python.exe` (Windows)

### Check Scanner Installation

The extension requires the `llm_scan` Python package. Verify it's installed:

```bash
python3 -m llm_scan.runner --help
```

If this fails, install it:
```bash
cd /Users/manish/code-scan2
pip install -e .
```

**⚠️ Important**: The package must be installed in the Python environment that VS Code uses, not just any Python on your system!

### Run Setup Script

```bash
cd /Users/manish/code-scan2/vscode-extension
./setup.sh
```

Then follow Option 1 above.

## Extension ID Reference

- **Full ID**: `llm-security.llm-security-scanner`
- **Publisher**: `llm-security`  
- **Name**: `llm-security-scanner`

This ID is correct in `package.json`. The error just means the extension needs to be loaded/installed.
