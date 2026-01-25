# Visual Studio Extension Quick Start

## What This Extension Does

The LLM Security Scanner Visual Studio extension integrates the Python-based LLM Security Scanner into Visual Studio, allowing you to:

- 🔍 **Automatically scan** Python files for LLM security vulnerabilities
- ⚠️ **View findings** in Visual Studio's Error List
- 🎯 **Get remediation guidance** for each vulnerability
- 🚀 **Scan entire workspaces** with a single command

## Installation (5 minutes)

### Step 1: Install Prerequisites

1. **Visual Studio 2022** (17.0+) with:
   - Visual Studio extension development workload
   - .NET desktop development workload

2. **Python 3.11+** with scanner installed:
   ```bash
   # From project root
   pip install -e .
   pip install semgrep
   ```

### Step 2: Build Extension

1. Open `visual-studio-extension/LLMSecurityScanner.sln` in Visual Studio
2. Restore NuGet packages (right-click solution)
3. Build → Build Solution (Ctrl+Shift+B)
4. VSIX file created in `bin\Release\`

### Step 3: Install Extension

1. Double-click `bin\Release\LLMSecurityScanner.vsix`
2. Click **Install**
3. Restart Visual Studio

## First Use

1. **Open a Python project** in Visual Studio
2. **Open a Python file** with LLM code (e.g., `samples/langchain/langchain_code_injection.py`)
3. **Save the file** - extension automatically scans
4. **View results** in **View → Error List** (Ctrl+\\, E)

## Manual Scanning

1. **Right-click** a file or folder in Solution Explorer
2. Select **"Scan with LLM Security Scanner"**
3. Results appear in Error List

## Understanding Results

Findings appear in Error List with:
- **🔴 Red (Error)**: Critical/High severity vulnerabilities
- **🟡 Yellow (Warning)**: Medium severity issues
- **🔵 Blue (Message)**: Low/Info severity findings

Click a finding to:
- Navigate to the code location
- View remediation guidance in the description panel
- See CWE and OWASP classification

## Configuration

**Tools → Options → LLM Security Scanner**

- **Python Path**: Path to Python interpreter (default: `python3`)
- **Rules Directory**: Custom rules path (optional)
- **Auto-scan on Save**: Enable/disable automatic scanning

## Troubleshooting

**Extension not loading?**
- Check Visual Studio version (needs 17.0+)
- Check Output window for errors

**Scanner not found?**
- Verify: `python3 -m llm_scan.runner --help`
- Check Python path in settings

**No findings?**
- Verify file has LLM code
- Check Error List filters
- Try manual scan

## Next Steps

- Read [README.md](README.md) for detailed documentation
- See [BUILD.md](BUILD.md) for build instructions
- Check [INSTALLATION.md](INSTALLATION.md) for installation details
