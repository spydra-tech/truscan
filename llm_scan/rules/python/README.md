# LLM Security Scanner Rules - Hierarchical Structure

This directory contains LLM security vulnerability detection rules organized in a hierarchical structure by:
1. **LLM Framework** (e.g., `openai/`, `anthropic/`, `cohere/`)
2. **Python Web Framework** (e.g., `flask/`, `django/`, `generic/`)
3. **Vulnerability Type** (e.g., `prompt-injection.yaml`, `code-injection.yaml`)

## Directory Structure

```
python/
├── openai/
│   ├── flask/
│   │   └── xss.yaml
│   ├── django/
│   │   └── xss.yaml
│   └── generic/
│       ├── prompt-injection.yaml
│       ├── code-injection.yaml
│       ├── command-injection.yaml
│       ├── sql-injection.yaml
│       ├── path-traversal.yaml
│       ├── ssrf.yaml
│       ├── training-data-poisoning.yaml
│       ├── model-dos.yaml
│       └── sensitive-info-disclosure.yaml
├── anthropic/
│   ├── flask/
│   ├── django/
│   └── generic/
├── cohere/
│   ├── flask/
│   ├── django/
│   └── generic/
├── huggingface/
│   ├── flask/
│   ├── django/
│   └── generic/
├── llama_index/
│   ├── flask/
│   ├── django/
│   └── generic/
├── langchain/
│   ├── flask/
│   ├── django/
│   └── generic/
├── google/
│   ├── flask/
│   ├── django/
│   └── generic/
└── azure/
    ├── flask/
    ├── django/
    └── generic/
```

## Vulnerability Categories

### OWASP LLM Top 10 Coverage

All rules are mapped to the **OWASP Top 10 for LLM Applications**:

1. **LLM01: Prompt Injection** (`prompt-injection.yaml`)
   - Direct user input in prompts
   - String concatenation in prompts
   - F-string injection

2. **LLM02: Insecure Output Handling**
   - **Code Injection** (`code-injection.yaml`) - LLM output → eval/exec/compile
   - **Command Injection** (`command-injection.yaml`) - LLM output → subprocess/os.system
   - **XSS** (`xss.yaml`) - LLM output → HTML templates (framework-specific)
   - **SQL Injection** (`sql-injection.yaml`) - LLM output → SQL queries
   - **Path Traversal** (`path-traversal.yaml`) - LLM output → file operations
   - **SSRF** (`ssrf.yaml`) - LLM output → URL/network requests

3. **LLM03: Training Data Poisoning** (`training-data-poisoning.yaml`)
   - Training data from untrusted URLs
   - Training data from untrusted files

4. **LLM04: Model Denial of Service** (`model-dos.yaml`)
   - Missing rate limiting
   - Missing max_tokens limits
   - Resource exhaustion

5. **LLM05: Supply Chain Vulnerabilities** (to be added)
   - Untrusted models
   - Untrusted plugins
   - Model verification

6. **LLM06: Sensitive Information Disclosure** (`sensitive-info-disclosure.yaml`)
   - Secrets/PII in prompts
   - Unsanitized logging

7. **LLM07: Insecure Plugin Design** (to be added)
   - Plugin execution without authorization
   - File operations without validation

8. **LLM08: Excessive Agency** (to be added)
   - Overprivileged operations
   - System command execution

9. **LLM09: Overreliance** (to be added)
   - Missing output validation
   - Blind trust in LLM output

10. **LLM10: Model Theft** (to be added)
    - Unprotected model endpoints
    - Model exposure

## Framework-Specific Rules

### Flask (`flask/`)
- XSS detection for `render_template()` and `render_template_string()`
- Request data → prompt injection patterns
- LLM output → Flask responses

### Django (`django/`)
- XSS detection for `render()` and `render_to_string()`
- Request data → prompt injection patterns
- LLM output → Django responses

### Generic (`generic/`)
- Framework-agnostic vulnerabilities
- Core injection patterns
- Taint analysis

## Rule File Naming Convention

- `prompt-injection.yaml` - LLM01: Prompt Injection
- `code-injection.yaml` - LLM02: Code Injection
- `command-injection.yaml` - LLM02: Command Injection
- `xss.yaml` - LLM02: XSS (framework-specific)
- `sql-injection.yaml` - LLM02: SQL Injection
- `path-traversal.yaml` - LLM02/LLM07: Path Traversal
- `ssrf.yaml` - LLM02: SSRF
- `training-data-poisoning.yaml` - LLM03: Training Data Poisoning
- `model-dos.yaml` - LLM04: Model Denial of Service
- `sensitive-info-disclosure.yaml` - LLM06: Sensitive Information Disclosure
- `supply-chain.yaml` - LLM05: Supply Chain (to be added)
- `insecure-plugin-design.yaml` - LLM07: Insecure Plugin Design (to be added)
- `excessive-agency.yaml` - LLM08: Excessive Agency (to be added)
- `overreliance.yaml` - LLM09: Overreliance (to be added)
- `model-theft.yaml` - LLM10: Model Theft (to be added)

## Usage

### Scan All Rules
```bash
python -m llm_scan.runner . --rules llm_scan/rules/python
```

### Scan Specific LLM Framework
```bash
python -m llm_scan.runner . --rules llm_scan/rules/python/openai
```

### Scan Specific Framework + Web Framework
```bash
python -m llm_scan.runner . --rules llm_scan/rules/python/openai/flask
```

### Scan Specific Vulnerability Type
```bash
python -m llm_scan.runner . --rules llm_scan/rules/python/openai/generic/prompt-injection.yaml
```

## Adding New Rules

### For a New LLM Framework

1. Create directory structure:
```bash
mkdir -p llm_scan/rules/python/{framework}/{flask,django,generic}
```

2. Copy and adapt rules from `openai/` as a template

3. Update patterns to match the new framework's API:
   - OpenAI: `openai.ChatCompletion.create()`, `$CLIENT.chat.completions.create()`
   - Anthropic: `$CLIENT.messages.create()`
   - Cohere: `cohere.Client.generate()`
   - etc.

4. Update metadata:
   - `technology` field should include the new framework
   - `tags` should include the framework name

### For a New Vulnerability Type

1. Create new YAML file in appropriate directories
2. Follow existing rule structure
3. Map to OWASP category if applicable
4. Add comprehensive metadata

## Rule Metadata Standards

Each rule should include:

```yaml
metadata:
  category: security
  subcategory: <vulnerability-type>
  owasp: "LLM##"  # OWASP category if applicable
  owasp-title: "<Title>"
  owasp-url: "<URL>"
  cwe: ["CWE-###"]
  cwe-url: ["<URL>"]
  tags: ["owasp", "llm##", "<tags>", "<framework>"]
  technology: ["python", "<llm-framework>", "<web-framework>", "llm"]
  confidence: "high" | "medium" | "low"
  impact: "critical" | "high" | "medium" | "low"
  likelihood: "high" | "medium" | "low"
  description: "<Detailed description>"
  remediation: "<Remediation guidance>"
  examples:
    vulnerable: "samples/<file>.py"
  references:
    - "<URL>"
```

## Current Status

### ✅ Completed
- OpenAI rules (generic, flask, django)
  - Prompt Injection
  - Code Injection
  - Command Injection
  - XSS (Flask & Django)
  - SQL Injection
  - Path Traversal
  - SSRF
  - Training Data Poisoning
  - Model DoS
  - Sensitive Info Disclosure

### 🚧 In Progress
- Anthropic rules
- Additional OWASP categories (LLM05, LLM07-LLM10)

### 📋 Planned
- Cohere rules
- Hugging Face rules
- LlamaIndex rules
- LangChain rules
- Google (Gemini) rules
- Azure OpenAI rules
- Additional vulnerability patterns

## Testing

Test rules against sample files in `samples/`:
```bash
python -m llm_scan.runner samples/ --rules llm_scan/rules/python/openai --format console
```

## Contributing

When adding new rules:
1. Follow the hierarchical structure
2. Include comprehensive metadata
3. Map to OWASP categories where applicable
4. Add test cases in `samples/`
5. Update this README
