# LLM Security Scanner

Detect AI/LLM-specific security vulnerabilities in your Python code directly within Visual Studio. This extension integrates seamlessly with Visual Studio's Error List to show security findings based on the **OWASP Top 10 for LLM Applications**.

## 🔍 Features

### **Comprehensive Vulnerability Detection**
- **OWASP LLM Top 10 Coverage**: Detects all categories of LLM-specific vulnerabilities
- **Framework Support**: Works with OpenAI, Anthropic, LangChain, Hugging Face, LlamaIndex, Cohere, Azure OpenAI, and AWS Bedrock
- **Real-time Scanning**: Automatically scans files on save and when opened
- **Severity-based Filtering**: Focus on critical and high-severity issues first

### **Visual Studio Integration**
- **Error List Integration**: Findings appear directly in Visual Studio's Error List panel
- **Severity Indicators**: 
  - 🔴 **Errors** (Critical/High severity)
  - 🟡 **Warnings** (Medium severity)
  - 🔵 **Messages** (Low/Info severity)
- **Clickable Navigation**: Click any finding to jump directly to the vulnerable code
- **Detailed Information**: View rule ID, CWE classification, OWASP category, and remediation guidance

### **Security Categories Detected**
- **Prompt Injection**: Detects various prompt injection attack vectors
- **Insecure Output Handling**: Identifies unsafe handling of LLM outputs
- **Training Data Poisoning**: Flags potential data poisoning risks
- **Model Denial of Service**: Detects resource exhaustion vulnerabilities
- **Supply Chain Vulnerabilities**: Identifies insecure dependencies
- **Sensitive Information Disclosure**: Finds exposed API keys and secrets
- **Insecure Plugin Design**: Detects unsafe plugin implementations
- **Excessive Agency**: Flags over-privileged LLM actions
- **Overreliance**: Identifies critical dependencies on LLM outputs
- **Model Theft**: Detects potential model extraction risks

## 🚀 Quick Start

### Installation
1. Install the extension from the Visual Studio Marketplace
2. Restart Visual Studio
3. Open a Python project with LLM-related code
4. The extension automatically activates and starts scanning

### Usage
- **Automatic Scanning**: Files are scanned automatically when saved or opened
- **Manual Scanning**: Right-click on files or folders in Solution Explorer → "Scan with LLM Security Scanner"
- **View Results**: Open **View → Error List** (Ctrl+\\, E) to see all findings

## 📋 Requirements

- **Visual Studio 2022** (17.0 or later)
- **Python 3.11+** installed
- **LLM Security Scanner** Python package installed:
  ```bash
  pip install -e .
  pip install semgrep
  ```

## ⚙️ Configuration

Configure the extension via **Tools → Options → LLM Security Scanner**:

- **Python Path**: Path to Python interpreter (default: `python3`)
- **Rules Directory**: Custom rules directory (optional)
- **Auto-scan on Save**: Automatically scan files when saved (default: enabled)
- **Auto-scan on Open**: Scan files when opened (default: enabled)
- **Severity Filter**: Choose which severity levels to display

## 🎯 Example Findings

### Prompt Injection
```python
# ⚠️ VULNERABLE CODE
user_input = request.GET.get('prompt')
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": user_input}]  # ❌ User input directly in prompt
)

# ✅ SECURE CODE
user_input = request.GET.get('prompt')
sanitized = sanitize_input(user_input)  # Sanitize first
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": sanitized}]
)
```

### Insecure Output Handling
```python
# ⚠️ VULNERABLE CODE
llm_output = llm.generate(prompt)
exec(llm_output)  # ❌ Executing untrusted LLM output

# ✅ SECURE CODE
llm_output = llm.generate(prompt)
validated = validate_and_sanitize(llm_output)  # Validate first
process_safely(validated)  # Process safely
```

## 📚 Supported Frameworks

- **OpenAI** (GPT-3, GPT-4, ChatGPT API)
- **Anthropic** (Claude API)
- **LangChain** (All components)
- **Hugging Face** (Transformers, Pipelines)
- **LlamaIndex** (Data loaders, query engines)
- **Cohere** (Generate, Embed, Classify)
- **Azure OpenAI Service**
- **AWS Bedrock**

## 🔗 Resources

- **Documentation**: [GitHub Repository](https://github.com/your-org/llm-security-scanner)
- **OWASP LLM Top 10**: [Official Guide](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- **Support**: [Issues](https://github.com/your-org/llm-security-scanner/issues)
- **License**: MIT License

## 🛡️ Why Use This Extension?

**Security First**: LLM applications face unique security challenges that traditional security scanners miss. This extension specifically targets LLM-specific vulnerabilities.

**Developer-Friendly**: Integrated directly into your workflow - no need to run separate security scans or switch tools.

**Comprehensive**: Covers all OWASP LLM Top 10 categories with hundreds of detection rules.

**Framework-Agnostic**: Works with all major LLM frameworks and APIs.

**Real-time Feedback**: Get immediate feedback as you code, catching vulnerabilities before they reach production.

## 📝 Release Notes

### Version 1.0.0
- Initial release
- Support for all OWASP LLM Top 10 categories
- Integration with Visual Studio Error List
- Automatic scanning on save/open
- Support for 8+ LLM frameworks

---

**Made with ❤️ by Spydra**

For questions, issues, or contributions, please visit our [GitHub repository](https://github.com/your-org/llm-security-scanner).
