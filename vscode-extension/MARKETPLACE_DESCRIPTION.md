# LLM Security Scanner

Detect AI/LLM-specific security vulnerabilities in your Python code directly within VS Code. This extension automatically installs **semgrep** - no manual setup required!

## 🔍 Features

### **Zero-Configuration Setup**
- ✅ **Automatic semgrep Installation**: semgrep is automatically installed when you install the extension - no manual setup needed!
- ✅ **Works Out of the Box**: Just install and start scanning - the extension handles all dependencies
- ✅ **Smart Environment Detection**: Automatically creates virtual environments if your Python is externally-managed

### **Comprehensive Vulnerability Detection**
- 🎯 **OWASP LLM Top 10 Coverage**: Detects all categories of LLM-specific vulnerabilities
- 🔒 **Framework Support**: Works with OpenAI, Anthropic, LangChain, Hugging Face, LlamaIndex, Cohere, Azure OpenAI, and AWS Bedrock
- ⚡ **Real-time Scanning**: Automatically scans files on save and when opened
- 📊 **Severity-based Filtering**: Focus on critical and high-severity issues first

### **VS Code Integration**
- ⚠️ **Problems Panel Integration**: Findings appear directly in VS Code's Problems panel
- 🎨 **Severity Indicators**: 
  - 🔴 **Errors** (Critical/High severity)
  - 🟡 **Warnings** (Medium severity)
  - 🔵 **Information** (Low/Info severity)
- 🖱️ **Clickable Navigation**: Click any finding to jump directly to the vulnerable code
- 💡 **Remediation Guidance**: View detailed remediation suggestions for each finding

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

1. **Install from Marketplace**: Search for "LLM Security Scanner" in VS Code Extensions
2. **Open a Python Project**: The extension automatically activates
3. **Start Scanning**: Files are scanned automatically on save!

**That's it!** semgrep is installed automatically - no manual configuration needed.

### Usage

- **Automatic Scanning**: Files are scanned automatically when saved or opened
- **Manual Scanning**: 
  - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
  - Type "LLM Security: Scan Workspace" or "LLM Security: Scan Current File"
- **View Results**: Open the **Problems** panel (`Ctrl+Shift+M` / `Cmd+Shift+M`) to see all findings

## 📋 Requirements

- **VS Code 1.74.0** or higher
- **Python 3.11+** installed
- **That's it!** semgrep is installed automatically by the extension

## ⚙️ Configuration

Configure the extension via VS Code Settings (`Ctrl+,` / `Cmd+,`):

```json
{
  "llmSecurityScanner.enabled": true,
  "llmSecurityScanner.pythonPath": "python3",
  "llmSecurityScanner.severityFilter": ["critical", "high", "medium"],
  "llmSecurityScanner.scanOnSave": true,
  "llmSecurityScanner.scanOnOpen": true
}
```

### Settings

- **`llmSecurityScanner.enabled`**: Enable/disable the extension
- **`llmSecurityScanner.pythonPath`**: Path to Python interpreter (default: `python3`)
- **`llmSecurityScanner.severityFilter`**: Array of severity levels to show
- **`llmSecurityScanner.scanOnSave`**: Automatically scan files on save (default: `true`)
- **`llmSecurityScanner.scanOnOpen`**: Scan files when opened (default: `true`)
- **`llmSecurityScanner.autoInstallDependencies`**: Controls llm-scan installation (semgrep is always installed)

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

## 🔗 Commands

Access via Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`):

- **LLM Security: Scan Workspace** - Scan entire workspace for vulnerabilities
- **LLM Security: Scan Current File** - Scan only the currently active file
- **LLM Security: Clear Results** - Clear all diagnostic results
- **LLM Security: Install Dependencies** - Manually trigger dependency installation

## 🛡️ Why Use This Extension?

**Security First**: LLM applications face unique security challenges that traditional security scanners miss. This extension specifically targets LLM-specific vulnerabilities.

**Zero Configuration**: No need to install semgrep manually or configure complex setups. Just install the extension and start scanning.

**Developer-Friendly**: Integrated directly into your workflow - no need to run separate security scans or switch tools.

**Comprehensive**: Covers all OWASP LLM Top 10 categories with hundreds of detection rules.

**Real-time Feedback**: Get immediate feedback as you code, catching vulnerabilities before they reach production.

## 📝 Release Notes

### Version 1.0.0

- Initial release
- **Automatic semgrep installation** - No manual setup required!
- Support for all OWASP LLM Top 10 categories
- Integration with VS Code Problems panel
- Automatic scanning on save/open
- Support for 8+ LLM frameworks
- Virtual environment auto-creation for externally-managed Python

## 🔗 Resources

- **Documentation**: [GitHub Repository](https://github.com/your-org/code-scan2)
- **OWASP LLM Top 10**: [Official Guide](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- **Support**: [Issues](https://github.com/your-org/code-scan2/issues)
- **License**: MIT License

## 💬 Feedback

Found a bug? Have a feature request? Please open an issue on [GitHub](https://github.com/your-org/code-scan2/issues).

---

**Made with ❤️ by Spydra**

For questions, issues, or contributions, please visit our [GitHub repository](https://github.com/your-org/code-scan2).
