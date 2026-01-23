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

## LangChain-Specific Vulnerabilities

### `langchain_template_injection.py`
LangChain template injection vulnerabilities (CVE-2023-44467, CVE-2023-46229):
- Direct user input in `ChatPromptTemplate.from_template()`
- User input concatenated into template strings
- Template attribute access patterns (`{{obj.__globals__}}`)
- User input in `from_messages()`

### `langchain_palchain_injection.py`
PALChain code execution vulnerabilities (CVE-2023-46229):
- PALChain execution with user input
- PALChain output passed to `eval()`/`exec()`/`compile()`
- Double code execution risks

### `langchain_python_repl.py`
PythonREPLChain code execution vulnerabilities:
- PythonREPLChain with user input
- PythonREPLChain output to `eval()`/`exec()`
- Arbitrary Python code execution

### `langchain_code_injection.py`
Chain output code injection vulnerabilities:
- LLMChain output to `eval()`/`exec()`/`compile()`
- Sequential chain output to code execution
- Chain output used unsafely

### `langchain_chain_injection.py`
Chain prompt injection vulnerabilities:
- `LLMChain.run()` with user input
- Chain `invoke()` with user input
- Sequential chains with user input

### `langchain_agent_excessive_agency.py`
Agent excessive agency vulnerabilities (LLM08):
- Agents with `PythonREPLTool()` (arbitrary code execution)
- Agents with `ShellTool()` (arbitrary command execution)
- Agents with both dangerous tools
- Agent execution with user input

### `langchain_agent_tools.py`
Agent tool configuration vulnerabilities:
- Agents with many tools (excessive permissions)
- Agents with file operation tools
- Agents with network operation tools

### `langchain_agent_file_ops.py`
Agent file operation vulnerabilities:
- Agents with unrestricted file tools
- File operations with user input
- Unauthorized file access risks

### `langchain_agent_network.py`
Agent network operation vulnerabilities (SSRF):
- Agents with unrestricted HTTP request tools
- SSRF attacks via agent network tools
- Data exfiltration risks

## Azure OpenAI Service-Specific Vulnerabilities

### `azure_prompt_injection.py`
Azure OpenAI Service prompt injection vulnerabilities (LLM01):
- Direct user input in `AzureOpenAI().chat.completions.create()`
- User input concatenated into prompts
- F-string injection in prompts
- User input in system prompts (critical)
- Flask request data in prompts

### `azure_code_injection.py`
Azure OpenAI Service code injection vulnerabilities (LLM02):
- Chat output passed to `eval()`/`exec()`/`compile()`
- Direct extraction and code execution
- Arbitrary code execution risks

### `azure_command_injection.py`
Azure OpenAI Service command injection vulnerabilities (LLM02):
- Chat output passed to `subprocess.run()`/`os.system()`
- Direct extraction and command execution
- Shell injection risks

### `azure_sql_injection.py`
Azure OpenAI Service SQL injection vulnerabilities (LLM02):
- Chat output concatenated into SQL queries (f-strings, +, .format(), %)
- Direct extraction and SQL execution
- SQL injection risks

## AWS Bedrock-Specific Vulnerabilities

### `aws_prompt_injection.py`
AWS Bedrock prompt injection vulnerabilities (LLM01):
- Direct user input in `boto3.client('bedrock-runtime').converse()`
- User input in `invoke_model()` body
- User input concatenated into prompts (f-strings, +)
- User input in Bedrock Agent `invoke_agent()` (critical - agents can execute tools)
- Flask request data in prompts

### `aws_code_injection.py`
AWS Bedrock code injection vulnerabilities (LLM02):
- Converse/InvokeModel output passed to `eval()`/`exec()`/`compile()`
- Direct extraction from JSON response body and code execution
- Arbitrary code execution risks

### `aws_command_injection.py`
AWS Bedrock command injection vulnerabilities (LLM02):
- Converse/InvokeModel output passed to `subprocess.run()`/`os.system()`
- Direct extraction from JSON response body and command execution
- Shell injection risks

### `aws_sql_injection.py`
AWS Bedrock SQL injection vulnerabilities (LLM02):
- Converse/InvokeModel output concatenated into SQL queries (f-strings, +, .format(), %)
- Direct extraction from JSON response body and SQL execution
- SQL injection risks

## Hugging Face-Specific Vulnerabilities

### `huggingface_prompt_injection.py`
Hugging Face prompt injection vulnerabilities (LLM01):
- Direct user input in `pipeline()` calls (text-generation, question-answering, text2text-generation)
- User input in tokenizer (`AutoTokenizer`, `tokenizer.encode()`, `tokenizer.tokenize()`)
- Flask request data in pipelines

### `huggingface_code_injection.py`
Hugging Face code injection vulnerabilities (LLM02):
- Pipeline output passed to `eval()`/`exec()`/`compile()`
- `TextGenerationPipeline` output to code execution
- Direct extraction and code execution

### `huggingface_command_injection.py`
Hugging Face command injection vulnerabilities (LLM02):
- Pipeline output passed to `subprocess.run()`/`os.system()`/`subprocess.call()`/`subprocess.Popen()`
- `TextGenerationPipeline` and `QuestionAnsweringPipeline` output to command execution
- Shell injection risks

### `huggingface_sql_injection.py`
Hugging Face SQL injection vulnerabilities (LLM02):
- Pipeline output concatenated into SQL queries (f-strings, +, .format(), %)
- `TextGenerationPipeline` and `QuestionAnsweringPipeline` output to SQL
- SQL injection risks

### `huggingface_supply_chain.py`
Hugging Face supply chain vulnerabilities (LLM05):
- Model loading without `use_safetensors=True` (pickle deserialization RCE) (CVE-2025-14921, CVE-2025-14924, CVE-2025-14926)
- `trust_remote_code=True` with untrusted models (remote code execution)
- Model loaded from untrusted sources
- Direct `torch.load()` and `pickle.load()` with untrusted files

### `huggingface_training_poisoning.py`
Hugging Face training data poisoning vulnerabilities (LLM03):
- `Trainer` with data from web requests (`requests.get()`, `urllib.request.urlopen()`)
- `Trainer` with data from Flask file uploads
- `Trainer` with data from `input()` or `sys.argv`
- `model.train()` and `model.fit()` with untrusted data

### `huggingface_model_dos.py`
Hugging Face model denial of service vulnerabilities (LLM04):
- Text generation pipelines without `max_length` or `max_new_tokens`
- `model.generate()` without token limits
- Resource exhaustion risks

### `huggingface_sensitive_info.py`
Hugging Face sensitive information disclosure vulnerabilities (LLM06):
- Pipeline output logged without sanitization
- Model response logged to console/files
- Sensitive data exposure risks

### `huggingface_path_traversal.py`
Hugging Face path traversal vulnerabilities (LLM02):
- Pipeline output used in file operations (`open()`, `Path.write_text()`, `shutil.copy()`, `os.remove()`)
- Path traversal risks

### `huggingface_overreliance.py`
Hugging Face overreliance vulnerabilities (LLM09):
- Pipeline output used in critical operations (SQL, commands, files) without validation
- Overreliance on LLM output without verification

## LlamaIndex-Specific Vulnerabilities

### `llamaindex_code_injection.py`
LlamaIndex code injection vulnerabilities (LLM02):
- `PandasQueryEngine` with user input (CVE-2023-39662 - RCE via exec())
- `safe_eval()` with LLM output (CVE-2024-3098 - safe_eval bypass)
- Query engine output passed to `eval()`/`exec()`/`compile()`
- `PythonCodeQueryEngine` with user input

### `llamaindex_sql_injection.py`
LlamaIndex SQL injection vulnerabilities (LLM02):
- `NLSQLTableQueryEngine` with user input (CVE-2025-1793, CVE-2024-23751 - CVSS 9.8)
- `SQLTableRetrieverQueryEngine` with user input
- `PGVectorSQLQueryEngine` with user input
- `NLSQLRetriever` with user input
- Query engine output concatenated into SQL queries

### `llamaindex_prompt_injection.py`
LlamaIndex prompt injection vulnerabilities (LLM01):
- Query engine with user input (`query()`, `retrieve()`)
- Vector store query with user input
- `ServiceContext` with user-controlled LLM config
- Query results flow into LLM prompts (indirect prompt injection)

### `llamaindex_vector_store.py`
LlamaIndex vector store and index vulnerabilities (LLM01/LLM03):
- Index query with user input
- Index created from untrusted documents (training data poisoning)
- Index query results flow into LLM prompts (indirect prompt injection)
- `VectorStoreIndex` and `PropertyGraphIndex` with untrusted data

### `llamaindex_document_loader.py`
LlamaIndex document loader vulnerabilities (LLM01/LLM03):
- `WebPageReader` with untrusted URL (SSRF risk)
- `SimpleDirectoryReader` with untrusted URL or file path (path traversal risk)
- `PyPDFReader` with user-controlled file (path traversal risk)
- Document loader content flows into LLM prompts or indexes (indirect prompt injection)

### `llamaindex_command_injection.py`
LlamaIndex command injection vulnerabilities (LLM02):
- Query engine output passed to `subprocess.run()`/`os.system()`/`subprocess.call()`/`subprocess.Popen()`
- Index query output to command execution
- Shell injection risks

### `llamaindex_path_traversal.py`
LlamaIndex path traversal vulnerabilities (LLM02):
- Query engine output used in file operations (`open()`, `Path.write_text()`, `shutil.copy()`, `os.remove()`)
- Index query output to file operations
- Path traversal risks

### `llamaindex_sensitive_info.py`
LlamaIndex sensitive information disclosure vulnerabilities (LLM06):
- Query engine response logged without sanitization
- Index content or documents logged without sanitization
- Sensitive data exposure risks

### `llamaindex_model_dos.py`
LlamaIndex model denial of service vulnerabilities (LLM04):
- Query engine without `max_tokens` limit in `ServiceContext`
- `RetrieverQueryEngine` without token limits
- Resource exhaustion risks

## Cohere-Specific Vulnerabilities

### `cohere_prompt_injection.py`
Cohere prompt injection vulnerabilities (LLM01):
- Direct user input in `cohere.Client().chat()` messages
- Direct user input in `cohere.ClientV2().chat()` messages
- Direct user input in `cohere.Client().generate()` prompts
- User input concatenated into chat/generate prompts (f-strings, +)
- Flask request data in prompts

### `cohere_code_injection.py`
Cohere code injection vulnerabilities (LLM02):
- Chat output (`response.text`, `response.message.content`) passed to `eval()`/`exec()`/`compile()`
- Generate output (`response.generations[0].text`) passed to `eval()`/`exec()`/`compile()`
- ClientV2 chat output to code execution
- Direct extraction and code execution

### `cohere_command_injection.py`
Cohere command injection vulnerabilities (LLM02):
- Chat output passed to `subprocess.run()`/`os.system()`/`subprocess.call()`/`subprocess.Popen()`
- Generate output to command execution
- ClientV2 chat output to command execution
- Shell injection risks

### `cohere_sql_injection.py`
Cohere SQL injection vulnerabilities (LLM02):
- Chat/generate output concatenated into SQL queries (f-strings, +, .format(), %)
- `response.text`, `response.message.content`, `response.generations[0].text` to SQL
- Direct extraction and SQL execution
- SQL injection risks

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

When scanning LangChain-specific files, you should see findings for:
- **LLM01**: Template injection (CVE-2023-44467), chain prompt injection
- **LLM02**: PALChain code execution (CVE-2023-46229), PythonREPLChain, chain output to eval/exec
- **LLM08**: Agent excessive agency (PythonREPLTool, ShellTool, file/network tools)

When scanning Azure OpenAI Service-specific files, you should see findings for:
- **LLM01**: Prompt injection (direct input, concatenation, system prompt injection)
- **LLM02**: Code injection (output to eval/exec/compile), command injection (output to subprocess/os.system), SQL injection (output to SQL queries)

When scanning AWS Bedrock-specific files, you should see findings for:
- **LLM01**: Prompt injection (Converse API, InvokeModel API, Bedrock Agent invocation)
- **LLM02**: Code injection (output to eval/exec/compile), command injection (output to subprocess/os.system), SQL injection (output to SQL queries)

When scanning Hugging Face-specific files, you should see findings for:
- **LLM01**: Prompt injection (pipeline with user input, tokenizer with user input)
- **LLM02**: Code injection (pipeline output to eval/exec/compile), command injection (pipeline output to subprocess/os.system), SQL injection (pipeline output to SQL queries), path traversal (pipeline output to file operations)
- **LLM03**: Training data poisoning (Trainer with untrusted data sources)
- **LLM04**: Model denial of service (missing max_length/max_new_tokens limits)
- **LLM05**: Supply chain vulnerabilities (pickle deserialization RCE, trust_remote_code, untrusted model sources) (CVE-2025-14921, CVE-2025-14924, CVE-2025-14926)
- **LLM06**: Sensitive information disclosure (pipeline output logging)
- **LLM09**: Overreliance (pipeline output used without validation)

When scanning LlamaIndex-specific files, you should see findings for:
- **LLM01**: Prompt injection (query engines with user input, vector stores, ServiceContext, indirect prompt injection via query results)
- **LLM02**: Code injection (PandasQueryEngine with user input - CVE-2023-39662, safe_eval bypass - CVE-2024-3098, query engine output to eval/exec/compile), SQL injection (Text-to-SQL engines with user input - CVE-2025-1793, CVE-2024-23751), command injection (query engine output to subprocess/os.system), path traversal (query engine output to file operations)
- **LLM03**: Training data poisoning (index created from untrusted documents, document loaders with untrusted URLs/files)
- **LLM04**: Model denial of service (query engines without max_tokens limit)
- **LLM06**: Sensitive information disclosure (query engine response logging, index content logging)

When scanning Cohere-specific files, you should see findings for:
- **LLM01**: Prompt injection (direct input in `co.chat()` and `co.generate()`, string concatenation)
- **LLM02**: Code injection (chat/generate output to eval/exec/compile), command injection (chat/generate output to subprocess/os.system), SQL injection (chat/generate output to SQL queries)

## Notes

⚠️ **Warning**: These files contain intentionally vulnerable code patterns. Do not use them in production or copy their patterns into real applications.

These samples are designed to:
1. Test the scanner's detection capabilities
2. Educate developers about LLM security risks
3. Serve as test cases for rule development
