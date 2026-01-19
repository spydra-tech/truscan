# Project Structure

```
code-scan2/
├── .github/
│   └── workflows/
│       └── llm-scan.yml              # GitHub Actions workflow example
├── llm_scan/                          # Main package
│   ├── __init__.py
│   ├── models.py                      # Data models (Finding, ScanResult, etc.)
│   ├── config.py                      # Configuration management
│   ├── runner.py                      # Main entry point and CLI
│   ├── engine/
│   │   ├── __init__.py
│   │   └── semgrep_engine.py          # Semgrep Python SDK integration
│   ├── output/
│   │   ├── __init__.py
│   │   ├── sarif.py                   # SARIF formatter
│   │   ├── json.py                    # JSON formatter
│   │   └── console.py                 # Console formatter
│   ├── enrich/
│   │   ├── __init__.py
│   │   └── uploader.py                # Optional upload interface
│   └── rules/
│       └── python/                     # Semgrep rule packs
│           ├── llm-code-injection.yaml
│           ├── llm-command-injection.yaml
│           ├── llm-taint-sources.yaml
│           └── llm-complete-rules.yaml
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── test_engine.py                  # Engine tests
│   ├── test_runner.py                  # Runner tests
│   ├── test_output.py                  # Output formatter tests
│   └── fixtures/
│       ├── positive/                   # Positive test cases (should trigger findings)
│       │   ├── llm_eval_vulnerable.py
│       │   ├── llm_exec_vulnerable.py
│       │   ├── llm_subprocess_vulnerable.py
│       │   ├── llm_os_system_vulnerable.py
│       │   ├── llm_compile_vulnerable.py
│       │   ├── llm_wrapper_vulnerable.py
│       │   └── llm_subprocess_popen_vulnerable.py
│       └── negative/                   # Negative test cases (should not trigger findings)
│           ├── safe_llm_usage.py
│           ├── safe_subprocess.py
│           ├── safe_string_ops.py
│           ├── safe_validation.py
│           ├── safe_template.py
│           └── no_llm_usage.py
├── .gitignore
├── README.md                           # Main documentation
├── setup.py                            # Setup configuration
├── pyproject.toml                      # Modern Python project config
├── requirements.txt                    # Runtime dependencies
├── requirements-dev.txt                # Development dependencies
├── vscode-integration.md               # VS Code integration contract
├── vscode-example-request.json         # Example VS Code request
└── vscode-example-response.json        # Example VS Code response
```

## Key Components

### Core Library (`llm_scan/`)
- **models.py**: Data classes for findings, scan results, requests/responses
- **config.py**: Configuration management with path resolution
- **runner.py**: Main entry point with CLI and library interfaces
- **engine/semgrep_engine.py**: Semgrep Python SDK wrapper (NO CLI subprocess calls)

### Output Formatters (`llm_scan/output/`)
- **sarif.py**: SARIF 2.1.0 output for GitHub Code Scanning
- **json.py**: JSON output for programmatic consumption
- **console.py**: Human-readable console output with colors

### Rule Packs (`llm_scan/rules/python/`)
- **llm-code-injection.yaml**: Rules for code injection via eval/exec/compile
- **llm-command-injection.yaml**: Rules for command injection via subprocess/os.system
- **llm-taint-sources.yaml**: Taint source detection for various LLM APIs
- **llm-complete-rules.yaml**: Complete taint flow rules (source → sink)

### Tests (`tests/`)
- **test_engine.py**: Tests for Semgrep engine integration
- **test_runner.py**: Tests for scan execution and VS Code integration
- **test_output.py**: Tests for all output formatters
- **fixtures/**: 13 test files (7 positive, 6 negative)

### CI/CD
- **.github/workflows/llm-scan.yml**: GitHub Actions workflow that runs scanner and uploads SARIF

### Documentation
- **README.md**: Complete usage guide, extensibility docs, examples
- **vscode-integration.md**: VS Code extension integration contract
- **vscode-example-*.json**: Example request/response payloads

## File Count Summary
- Python source files: 12
- YAML rule files: 4
- Test files: 3
- Test fixtures: 13
- Documentation files: 4
- Configuration files: 5
- **Total: 41 files**
