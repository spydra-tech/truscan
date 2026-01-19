# OWASP LLM Top 10 Rules - Metadata Documentation

This document describes the comprehensive metadata included in all OWASP LLM Top 10 rules.

## Metadata Fields

Each rule in `llm_scan/rules/python/llm-owasp-top10.yaml` includes the following metadata fields:

### Core Identification
- **`category`**: Always `"security"` for security-related rules
- **`subcategory`**: Specific vulnerability type (e.g., `injection`, `code-injection`, `denial-of-service`)
- **`owasp`**: OWASP category identifier (e.g., `"LLM01"`, `"LLM02"`)
- **`owasp-title`**: Human-readable OWASP category name (e.g., `"Prompt Injection"`)
- **`owasp-url`**: Direct link to OWASP documentation for the category

### Vulnerability Classification
- **`cwe`**: Array of CWE identifiers (e.g., `["CWE-79", "CWE-94"]`)
- **`cwe-url`**: Array of CWE documentation URLs corresponding to each CWE ID
- **`tags`**: Array of tags for filtering and categorization:
  - OWASP category tag (e.g., `"llm01"`, `"llm02"`)
  - Vulnerability type tags (e.g., `"prompt-injection"`, `"code-injection"`)
  - Technology tags (e.g., `"llm"`, `"ai-security"`, `"python"`)
  - Additional context tags

### Risk Assessment
- **`confidence`**: Detection confidence level (`"high"`, `"medium"`, `"low"`)
- **`impact`**: Potential impact if exploited (`"critical"`, `"high"`, `"medium"`, `"low"`)
- **`likelihood`**: Likelihood of exploitation (`"high"`, `"medium"`, `"low"`)

### Documentation
- **`description`**: Detailed description of the vulnerability and attack vector
- **`remediation`**: Specific remediation guidance and best practices
- **`examples`**: Object with reference to vulnerable code examples:
  - `vulnerable`: Path to sample file demonstrating the vulnerability
- **`references`**: Array of external documentation URLs:
  - OWASP documentation links
  - CWE documentation
  - Additional security resources

### Technology Stack
- **`technology`**: Array of technologies/libraries this rule applies to:
  - Programming languages (e.g., `"python"`)
  - LLM providers (e.g., `"openai"`, `"anthropic"`)
  - Frameworks (e.g., `"flask"`, `"django"`)
  - ML libraries (e.g., `"pytorch"`, `"tensorflow"`)

## Metadata by OWASP Category

### LLM01: Prompt Injection
- **CWE**: CWE-79, CWE-94
- **Subcategory**: `injection`
- **Impact**: `critical`
- **Likelihood**: `high`
- **Confidence**: `high`
- **Tags**: `owasp`, `llm01`, `prompt-injection`, `injection`, `input-validation`, `llm`, `ai-security`

### LLM02: Insecure Output Handling
- **CWE**: CWE-94 (code injection), CWE-78 (command injection), CWE-79 (XSS)
- **Subcategory**: `code-injection`, `command-injection`, `xss`
- **Impact**: `critical` (code/command), `high` (XSS)
- **Likelihood**: `high` (code/command), `medium` (XSS)
- **Confidence**: `high`
- **Tags**: `owasp`, `llm02`, `insecure-output`, `code-injection`, `command-injection`, `xss`, `llm`, `ai-security`

### LLM03: Training Data Poisoning
- **CWE**: CWE-502, CWE-506
- **Subcategory**: `data-poisoning`
- **Impact**: `high`
- **Likelihood**: `medium`
- **Confidence**: `medium`
- **Tags**: `owasp`, `llm03`, `training-data`, `data-poisoning`, `supply-chain`, `llm`, `ai-security`, `ml-security`

### LLM04: Model Denial of Service
- **CWE**: CWE-400, CWE-770
- **Subcategory**: `denial-of-service`
- **Impact**: `medium`
- **Likelihood**: `high`
- **Confidence**: `high`
- **Tags**: `owasp`, `llm04`, `dos`, `denial-of-service`, `rate-limiting`, `token-limit`, `resource-exhaustion`, `llm`, `ai-security`

### LLM05: Supply Chain Vulnerabilities
- **CWE**: CWE-494, CWE-502
- **Subcategory**: `supply-chain`
- **Impact**: `critical`
- **Likelihood**: `medium`
- **Confidence**: `high`
- **Tags**: `owasp`, `llm05`, `supply-chain`, `untrusted-model`, `plugin`, `model-verification`, `llm`, `ai-security`

### LLM06: Sensitive Information Disclosure
- **CWE**: CWE-200, CWE-312, CWE-359
- **Subcategory**: `information-disclosure`
- **Impact**: `high` (in prompt), `medium` (in logs)
- **Likelihood**: `medium` (in prompt), `high` (in logs)
- **Confidence**: `medium` (in prompt), `high` (in logs)
- **Tags**: `owasp`, `llm06`, `sensitive-info`, `secrets`, `pii`, `credentials`, `logging`, `llm`, `ai-security`, `data-leakage`

### LLM07: Insecure Plugin Design
- **CWE**: CWE-284, CWE-306, CWE-22
- **Subcategory**: `authorization`, `path-traversal`
- **Impact**: `critical`
- **Likelihood**: `medium`
- **Confidence**: `high`
- **Tags**: `owasp`, `llm07`, `plugin`, `authorization`, `access-control`, `path-traversal`, `file-access`, `llm`, `ai-security`

### LLM08: Excessive Agency
- **CWE**: CWE-250, CWE-284
- **Subcategory**: `excessive-privileges`
- **Impact**: `critical`
- **Likelihood**: `medium`
- **Confidence**: `high`
- **Tags**: `owasp`, `llm08`, `excessive-agency`, `privilege-escalation`, `system-commands`, `database`, `write-operations`, `llm`, `ai-security`

### LLM09: Overreliance
- **CWE**: CWE-345, CWE-754
- **Subcategory**: `validation`
- **Impact**: `high` (general), `critical` (critical decisions)
- **Likelihood**: `high` (general), `medium` (critical decisions)
- **Confidence**: `high`
- **Tags**: `owasp`, `llm09`, `overreliance`, `validation`, `trust`, `critical-decision`, `automation`, `llm`, `ai-security`

### LLM10: Model Theft
- **CWE**: CWE-200, CWE-497
- **Subcategory**: `access-control`
- **Impact**: `high`
- **Likelihood**: `medium` (exposed endpoint), `low` (no access control)
- **Confidence**: `high` (exposed endpoint), `medium` (no access control)
- **Tags**: `owasp`, `llm10`, `model-theft`, `intellectual-property`, `access-control`, `llm`, `ai-security`

## Usage Examples

### Filtering by OWASP Category
```bash
# Scan for specific OWASP category
semgrep --config=llm_scan/rules/python/llm-owasp-top10.yaml \
  --include-tags=llm01 \
  samples/
```

### Filtering by Impact
Rules can be filtered by impact level in custom tooling that reads the metadata.

### Accessing Metadata Programmatically
```python
import json
import subprocess

result = subprocess.run(
    ["semgrep", "--config=llm_scan/rules/python/llm-owasp-top10.yaml", 
     "--json", "samples/"],
    capture_output=True
)
data = json.loads(result.stdout)

for finding in data["results"]:
    metadata = finding["extra"]["metadata"]
    print(f"OWASP: {metadata['owasp']} - {metadata['owasp-title']}")
    print(f"Impact: {metadata['impact']}, Likelihood: {metadata['likelihood']}")
    print(f"CWE: {metadata['cwe']}")
    print(f"Tags: {metadata['tags']}")
```

## Benefits of Comprehensive Metadata

1. **Better Reporting**: Rich metadata enables detailed vulnerability reports with context
2. **Risk Prioritization**: Impact and likelihood fields help prioritize remediation
3. **Filtering**: Tags enable filtering by vulnerability type, technology, or OWASP category
4. **Documentation**: Direct links to OWASP and CWE documentation
5. **Examples**: References to sample vulnerable code for testing and education
6. **Remediation**: Specific guidance for fixing each vulnerability type
7. **Technology Awareness**: Technology tags help identify which rules apply to your stack

## Statistics

- **Total Rules**: 20 rules covering all 10 OWASP LLM categories
- **CWE Mappings**: 15+ unique CWE identifiers
- **Tags**: 50+ unique tags across all rules
- **References**: 30+ external documentation links
- **Sample Files**: 10 sample files demonstrating each category
