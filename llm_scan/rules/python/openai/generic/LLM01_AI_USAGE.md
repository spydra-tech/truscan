# LLM01: Prompt Injection - AI-Enhanced Detection

This rule file (`prompt-injection.yaml`) is designed to work with AI analysis to provide accurate detection of prompt injection vulnerabilities while minimizing false positives.

## How It Works

1. **Semgrep** catches potential prompt injection patterns broadly (with medium confidence)
2. **AI** analyzes each finding to determine if it's actually exploitable based on:
   - Code context and surrounding logic
   - Input validation and sanitization
   - Framework-specific security mechanisms
   - Whether the vulnerability is actually exploitable

## Usage

### Basic Usage (AI Auto-Analysis)

The rules include `ai_analysis_recommended: true` in metadata, so they will be automatically analyzed when AI filtering is enabled:

```bash
python -m llm_scan.runner . \
  --enable-ai-filter \
  --ai-provider openai \
  --ai-model gpt-4
```

### Explicit Rule Selection

You can also explicitly specify which rules to analyze:

```bash
python -m llm_scan.runner . \
  --enable-ai-filter \
  --ai-provider openai \
  --ai-model gpt-4 \
  --ai-analyze-rules openai-llm01-prompt-injection-direct \
  --ai-analyze-rules openai-llm01-prompt-injection-concatenation \
  --ai-analyze-rules openai-llm01-prompt-injection-indirect \
  --ai-analyze-rules openai-llm01-prompt-injection-template
```

### Without AI (Traditional Semgrep Only)

You can still use these rules without AI, but expect more false positives:

```bash
python -m llm_scan.runner . \
  --rules llm_scan/rules/python/openai/generic/prompt-injection.yaml
```

## Rules Included

1. **`openai-llm01-prompt-injection-direct`**
   - Detects user input directly inserted into OpenAI prompts
   - Confidence: Medium (AI will verify exploitability)

2. **`openai-llm01-prompt-injection-concatenation`**
   - Detects user input concatenated into prompts (f-strings, + operator)
   - Confidence: Medium (AI will verify exploitability)

3. **`openai-llm01-prompt-injection-indirect`**
   - Detects untrusted data (web requests, files, APIs) flowing into prompts
   - Uses taint analysis
   - Confidence: Medium (AI will verify if data is actually untrusted)

4. **`openai-llm01-prompt-injection-template`**
   - Detects template formatting (.format(), %) with user input
   - Confidence: Medium (AI will verify if user input is present)

## What AI Analysis Provides

For each finding, AI will:

1. **Determine if it's a false positive** - Check if sanitization/validation prevents exploitation
2. **Assess exploitability** - Consider code context, framework protections, business logic
3. **Provide enhanced remediation** - Context-specific, actionable guidance with code examples
4. **Adjust severity** - Suggest if severity should be higher/lower based on actual risk

## Example Output

With AI analysis enabled, you'll see:

```
[ERROR] openai-llm01-prompt-injection-direct [AI: ENHANCED]
    Line 42:5 - LLM01: Potential Prompt Injection - User input directly inserted into OpenAI prompt
    AI Analysis: ✓ Confidence: 0.85 - This is a true positive. User input from request.form is directly inserted without sanitization...
    Remediation (AI-Enhanced): 
    1. Sanitize user input using html.escape() or markupsafe.escape()
    2. Use parameterized prompt templates
    3. Example fix:
       sanitized_input = html.escape(user_input)
       messages = [{"role": "user", "content": f"Process this: {sanitized_input}"}]
```

## Benefits

- **Reduced False Positives**: AI filters out findings where sanitization/validation prevents exploitation
- **Better Remediation**: Context-specific guidance instead of generic advice
- **Accurate Severity**: AI adjusts severity based on actual exploitability
- **Framework Awareness**: AI understands Flask, Django, FastAPI protections

## Cost Considerations

- Each analyzed finding costs ~$0.01-0.10 (depending on model)
- Caching is enabled by default to avoid re-analyzing identical patterns
- Only medium/low confidence findings are analyzed by default
- Rules with `ai_analysis_recommended: true` are automatically analyzed

## Best Practices

1. **Start with AI enabled** for LLM01 rules to get accurate results
2. **Review AI reasoning** to understand why findings are/aren't false positives
3. **Use enhanced remediation** - it's context-specific and actionable
4. **Monitor costs** - if scanning large codebases, consider analyzing specific rules only
