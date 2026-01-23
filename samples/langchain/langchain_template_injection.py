"""
LangChain Template Injection Vulnerabilities (CVE-2023-44467, CVE-2023-46229)

This file demonstrates template injection vulnerabilities in LangChain prompt templates.
These vulnerabilities allow attackers to access Python object internals and execute code.

Vulnerabilities:
1. Direct user input in template constructors
2. Template concatenation with user input
3. Template attribute access patterns
"""

from langchain.prompts import ChatPromptTemplate, PromptTemplate
from flask import request
import html

# ============================================================================
# VULNERABLE: Direct user input in template constructor
# ============================================================================
def vulnerable_direct_template_injection():
    """VULNERABLE: User input directly in template constructor."""
    user_input = request.args.get('prompt')  # User-controlled input
    
    # VULNERABLE: Direct template injection
    template = ChatPromptTemplate.from_template(user_input)
    # Attacker can inject: "{{obj.__globals__}}" to access globals
    
    # VULNERABLE: Direct PromptTemplate injection
    prompt_template = PromptTemplate.from_template(user_input)
    
    return template, prompt_template


# ============================================================================
# VULNERABLE: Template concatenation with user input
# ============================================================================
def vulnerable_template_concatenation():
    """VULNERABLE: User input concatenated into template string."""
    user_input = request.form.get('user_message')
    
    # VULNERABLE: F-string in template
    template_str = f"User said: {user_input}"
    template = ChatPromptTemplate.from_template(template_str)
    
    # VULNERABLE: String concatenation
    template_str2 = "Template: " + user_input + " - Process this"
    template2 = PromptTemplate.from_template(template_str2)
    
    return template, template2


# ============================================================================
# VULNERABLE: Template with attribute access patterns
# ============================================================================
def vulnerable_template_attribute_access():
    """VULNERABLE: Template with attribute access allowing object traversal."""
    # VULNERABLE: Template with __globals__ access
    malicious_template = "{{obj.__globals__['os'].system('rm -rf /')}}"
    template = PromptTemplate.from_template(malicious_template)
    
    # VULNERABLE: Template with indexing
    malicious_template2 = "{{obj['__class__']['__bases__'][0]['__subclasses__']()}}"
    template2 = ChatPromptTemplate.from_template(malicious_template2)
    
    return template, template2


# ============================================================================
# VULNERABLE: from_messages with user input
# ============================================================================
def vulnerable_from_messages():
    """VULNERABLE: User input in from_messages."""
    user_input = request.json.get('message')
    
    # VULNERABLE: User input in messages
    template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant"),
        ("user", user_input)  # User-controlled
    ])
    
    return template


# ============================================================================
# SAFE: Proper template usage with variables
# ============================================================================
def safe_template_usage():
    """SAFE: Using template variables instead of direct injection."""
    user_input = request.args.get('prompt')
    
    # SAFE: Use template variables
    template = PromptTemplate.from_template("User said: {user_input}")
    
    # SAFE: Format with sanitized input
    sanitized_input = html.escape(user_input)  # Sanitize first
    formatted = template.format(user_input=sanitized_input)
    
    return formatted
