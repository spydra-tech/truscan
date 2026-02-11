# Installation Guide

## Quick Install

### From PyPI (Recommended)

```bash
pip install trusys-llm-scan
```

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/your-org/code-scan2.git
cd code-scan2

# Install in editable mode
pip install -e .
# or
python3 -m pip install -e .
```

## Virtual Environment Setup

### Using venv

```bash
# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install package
pip install -e .
```

### Using conda

```bash
# Create conda environment
conda create -n llm-scan python=3.11
conda activate llm-scan

# Install package
pip install -e .
```

## VS Code Integration

If using VS Code and getting "llm_scan package not found" errors:

1. **Activate your virtual environment**:
   ```bash
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

2. **Install the package**:
   ```bash
   pip install -e /path/to/code-scan2
   ```

3. **Configure VS Code Python path** (if needed):
   - Open VS Code settings (`.vscode/settings.json`)
   - Add:
     ```json
     {
       "llmSecurityScanner.pythonPath": "venv/bin/python"
     }
     ```
   - Or set the Python interpreter: `Cmd+Shift+P` → "Python: Select Interpreter" → choose your venv

## Verify Installation

```bash
# Check version
trusys-llm-scan --version

# Or as Python module
python -m llm_scan.runner --version

# Run a test scan
python -m llm_scan.runner samples/mcp --format console
```

## Troubleshooting

### "llm_scan package not found"

- Ensure you're in the correct virtual environment
- Verify installation: `pip list | grep trusys-llm-scan`
- Reinstall: `pip install -e .` (from the repo root)

### "semgrep not found"

- Install Semgrep: `pip install semgrep`
- Or install all dependencies: `pip install -e .`

### Python Version Issues

- Requires Python 3.11 or higher
- Check version: `python3 --version`
- Use `python3` instead of `python` if needed
