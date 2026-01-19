# Installation Guide

## Development Mode (Recommended for Testing)

### Step 1: Install Dependencies

```bash
cd vscode-extension
npm install
```

### Step 2: Compile Extension

```bash
npm run compile
```

This will compile TypeScript to JavaScript in the `out/` directory.

### Step 3: Run Extension in Development Mode

1. Open VS Code in the `vscode-extension` directory
2. Press `F5` or go to Run → Start Debugging
3. This will open a new "Extension Development Host" window
4. In the new window, open your workspace with Python files
5. The extension will automatically activate

### Step 4: Verify Extension is Active

- Check the Output panel: View → Output → Select "LLM Security Scanner"
- You should see: "LLM Security Scanner extension is now active!"
- Open a Python file and save it - diagnostics should appear

## Package and Install as VSIX

### Step 1: Install VS Code Extension Manager

```bash
npm install -g vsce
```

### Step 2: Package Extension

```bash
cd vscode-extension
vsce package
```

This creates `llm-security-scanner-1.0.0.vsix`

### Step 3: Install VSIX

**Option A: Command Line**
```bash
code --install-extension llm-security-scanner-1.0.0.vsix
```

**Option B: VS Code UI**
1. Open VS Code
2. Go to Extensions view (Ctrl+Shift+X / Cmd+Shift+X)
3. Click "..." menu → "Install from VSIX..."
4. Select the `.vsix` file

### Step 4: Reload VS Code

After installation, reload VS Code for the extension to activate.

## Troubleshooting "Extension Not Found" Error

### Issue: Extension ID Not Found

If you see `Extension 'llm-security.llm-security-scanner' not found`:

1. **Check if extension is installed:**
   ```bash
   code --list-extensions | grep llm-security
   ```

2. **Verify package.json:**
   - Publisher: `llm-security`
   - Name: `llm-security-scanner`
   - Extension ID: `llm-security.llm-security-scanner`

3. **Reinstall extension:**
   ```bash
   code --uninstall-extension llm-security.llm-security-scanner
   code --install-extension llm-security-scanner-1.0.0.vsix
   ```

4. **Check VS Code logs:**
   - Help → Toggle Developer Tools
   - Check Console for errors

### Issue: Extension Not Activating

1. **Check activation events:**
   - Extension activates on: `onLanguage:python`, `onLanguage:javascript`, `onLanguage:typescript`
   - Open a Python file to trigger activation

2. **Check Output panel:**
   - View → Output → Select "LLM Security Scanner"
   - Look for error messages

3. **Verify Python installation and package:**
   ```bash
   python3 --version
   python3 -m llm_scan.runner --help
   ```
   
   **⚠️ Important for Extension Development Host:**
   - The Extension Development Host uses the Python specified in `llmSecurityScanner.pythonPath` setting
   - Make sure `llm_scan` is installed in that Python environment
   - Test with: `[pythonPath] -m llm_scan.runner --help`
   - If it fails, install: `[pythonPath] -m pip install -e /path/to/code-scan2`

4. **Check extension settings:**
   - File → Preferences → Settings
   - Search for "LLM Security Scanner"
   - Verify `llmSecurityScanner.enabled` is `true`

### Issue: "llm_scan package not found" in Extension Development Host

This happens when the Extension Development Host uses a Python environment without `llm_scan` installed.

**Solution:**

1. **Check the Python path setting:**
   - In Extension Development Host: Settings → Search `llmSecurityScanner.pythonPath`
   - Note the Python path (e.g., `python3`, `venv/bin/python`)

2. **Test that Python environment:**
   ```bash
   # Use the exact path from settings
   python3 -m llm_scan.runner --help
   # Or if using venv:
   venv/bin/python -m llm_scan.runner --help
   ```

3. **If it fails, install in that environment:**
   ```bash
   # Install in the Python that VS Code uses
   python3 -m pip install -e /path/to/code-scan2
   # Or activate venv first:
   source venv/bin/activate
   pip install -e /path/to/code-scan2
   ```

4. **If using a virtual environment:**
   - Set `llmSecurityScanner.pythonPath` to: `venv/bin/python` (macOS/Linux) or `venv\Scripts\python.exe` (Windows)
   - Make sure the venv has both `semgrep` and `llm_scan` installed

### Issue: No Diagnostics Appearing

1. **Verify scanner is working with the correct Python:**
   ```bash
   # Use the Python from llmSecurityScanner.pythonPath setting
   python3 -m llm_scan.runner samples/vulnerable_app.py --format json
   ```

2. **Check file patterns:**
   - Default includes: `*.py`
   - Make sure your files match the pattern

3. **Check severity filter:**
   - Default shows: `critical`, `high`, `medium`
   - Lower severity findings won't appear

4. **Try manual scan:**
   - Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
   - "LLM Security: Scan Current File"

## Development Workflow

### Watch Mode (Auto-compile on changes)

```bash
npm run watch
```

Keep this running while developing. It will automatically recompile TypeScript on file changes.

### Debugging

1. Set breakpoints in TypeScript files
2. Press F5 to launch Extension Development Host
3. Debugger will attach automatically
4. Use VS Code debugger controls

### Testing Changes

1. Make changes to TypeScript files
2. Run `npm run compile` (or use watch mode)
3. In Extension Development Host: Help → Reload Window
4. Test your changes

## Extension ID Reference

- **Full ID**: `llm-security.llm-security-scanner`
- **Publisher**: `llm-security`
- **Name**: `llm-security-scanner`
- **Display Name**: `LLM Security Scanner`

## Common Commands

```bash
# Install dependencies
npm install

# Compile once
npm run compile

# Watch mode (auto-compile)
npm run watch

# Package extension
vsce package

# Install extension
code --install-extension llm-security-scanner-1.0.0.vsix

# Uninstall extension
code --uninstall-extension llm-security.llm-security-scanner

# List installed extensions
code --list-extensions
```
