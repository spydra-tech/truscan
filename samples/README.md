# Sample Vulnerable Files

This directory contains sample Python files that demonstrate various LLM security vulnerabilities. These files are used for testing the scanner and understanding vulnerability patterns.

## OWASP LLM Top 10 Examples

### LLM01: Prompt Injection
**File:** `llm01_prompt_injection.py`

Demonstrates prompt injection vulnerabilities where user input is directly inserted into LLM prompts without sanitization:
- Direct user input in prompts
- String concatenation in prompts
- F-string injection
- Flask request data in prompts
- System prompt injection

### LLM02: Insecure Output Handling
**File:** `llm02_insecure_output.py`

Demonstrates insecure handling of LLM output:
- LLM output passed to `eval()`, `exec()`, `compile()`
- LLM output passed to `subprocess.run()`, `os.system()`
- LLM output rendered in HTML without escaping (XSS)
- LLM output used in SQL queries
- LLM output used for file operations
- LLM output used in URLs (SSRF risk)

### LLM03: Training Data Poisoning
**File:** `llm03_training_data_poisoning.py`

Demonstrates vulnerabilities related to training data from untrusted sources:
- Training data loaded from URLs without validation
- Training data from user-provided sources
- Training data from external files without verification
- Training data from pickle files without checksums
- Training data from JSON without schema validation

### LLM04: Model Denial of Service
**File:** `llm04_model_dos.py`

Demonstrates resource exhaustion vulnerabilities:
- No rate limiting on LLM API calls
- Missing `max_tokens` limits
- Rapid API calls without throttling
- Very long prompts without size limits
- Recursive LLM calls without depth limits
- Batch processing without concurrency limits
- No timeout on API calls

### LLM05: Supply Chain Vulnerabilities
**File:** `llm05_supply_chain.py`

Demonstrates vulnerabilities related to untrusted models, libraries, or plugins:
- Models loaded from untrusted URLs without verification
- Models downloaded without checksum verification
- Models from untrusted HuggingFace repositories
- Plugin code loaded from LLM output
- Dynamic module imports from LLM output
- Model weights loaded without verification

### LLM06: Sensitive Information Disclosure
**File:** `llm06_sensitive_info.py`

Demonstrates sensitive data exposure:
- API keys included in prompts
- Passwords in prompts
- PII (SSN, credit cards) in prompts
- Database credentials in prompts
- LLM responses logged without sanitization
- Tokens and private keys in prompts

### LLM07: Insecure Plugin Design
**File:** `llm07_insecure_plugin.py`

Demonstrates plugin execution vulnerabilities:
- Actions executed without authorization
- File operations without path validation
- Database operations without authorization
- System commands without restrictions
- Network requests without validation
- Plugin execution without sandboxing

### LLM08: Excessive Agency
**File:** `llm08_excessive_agency.py`

Demonstrates overprivileged LLM actions:
- System command execution without restrictions
- Database write operations without limits
- File deletion without restrictions
- System configuration modification
- User creation with admin privileges
- Package installation capabilities
- Unrestricted network access
- Code modification capabilities

### LLM09: Overreliance
**File:** `llm09_overreliance.py`

Demonstrates blind trust in LLM output:
- Output returned without validation
- Critical decisions based solely on LLM output
- Medical diagnosis without verification
- Financial calculations without verification
- Legal advice without disclaimers
- Code generation without review
- Data extraction without validation

### LLM10: Model Theft
**File:** `llm10_model_theft.py`

Demonstrates unauthorized model access:
- Model files exposed via unauthenticated endpoints
- Model weights exposed for download
- Model loading without access control
- Training data exposed
- Model checkpoints exposed
- Model architecture exposed
- Model inference endpoints allowing extraction

## General Vulnerable Examples

### `vulnerable_app.py`
A comprehensive example containing multiple vulnerability types:
- Code injection (eval/exec/compile)
- Command injection (subprocess/os.system)
- Multiple LLM API patterns (OpenAI legacy, v1, Anthropic)

### `vulnerable_api.py`
Flask API endpoints with LLM vulnerabilities:
- API endpoints with prompt injection
- LLM output used unsafely in responses

### `vulnerable_chatbot.py`
Chatbot implementation with security issues:
- Unsanitized user input
- Insecure output handling

### `vulnerable_script.py`
Command-line script with vulnerabilities:
- Direct LLM output execution
- Command injection patterns

### `vulnerable_workflow.py`
Workflow automation with security issues:
- LLM-driven automation without validation
- Overreliance on LLM output

## Testing the Scanner

To test the scanner against these samples:

```bash
# Scan all OWASP examples
python -m llm_scan.runner samples/llm*.py --format console

# Scan a specific vulnerability category
python -m llm_scan.runner samples/llm01_prompt_injection.py --format console --verbose

# Scan with OWASP rules only
python -m llm_scan.runner samples/ --rules llm_scan/rules/python/llm-owasp-top10.yaml --format console

# Generate SARIF output
python -m llm_scan.runner samples/ --format sarif --out samples-results.sarif
```

## Expected Findings

When scanning these files, you should see findings for:
- **LLM01**: Multiple prompt injection patterns
- **LLM02**: Code/command injection, XSS risks
- **LLM03**: Untrusted training data sources
- **LLM04**: Missing rate limits and token limits
- **LLM05**: Untrusted model/plugin loading
- **LLM06**: Secrets/PII in prompts
- **LLM07**: Unauthorized plugin execution
- **LLM08**: Overprivileged operations
- **LLM09**: Missing validation/verification
- **LLM10**: Unprotected model endpoints

## Notes

⚠️ **Warning**: These files contain intentionally vulnerable code patterns. Do not use them in production or copy their patterns into real applications.

These samples are designed to:
1. Test the scanner's detection capabilities
2. Educate developers about LLM security risks
3. Serve as test cases for rule development
