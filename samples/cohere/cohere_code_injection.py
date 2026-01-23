"""
Sample vulnerable Cohere application demonstrating code injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

import cohere
import os


def vulnerable_chat_to_eval(user_input: str):
    """VULNERABLE: Cohere chat output passed to eval()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Generate Python code for: {user_input}"}
        ]
    )
    
    code = response.text
    
    # CRITICAL: Executing untrusted LLM output
    eval(code)  # VULNERABILITY: Code injection risk


def vulnerable_chat_to_exec(task: str):
    """VULNERABLE: Cohere chat output passed to exec()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Write Python code to: {task}"}
        ]
    )
    
    code_str = response.text
    
    # CRITICAL: Executing untrusted code
    exec(code_str)  # VULNERABILITY: Code injection risk


def vulnerable_chat_to_compile(description: str):
    """VULNERABLE: Cohere chat output passed to compile()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Generate code for: {description}"}
        ]
    )
    
    code = response.text
    
    # CRITICAL: Compiling untrusted code
    compile(code, "<string>", "exec")  # VULNERABILITY: Code injection risk


def vulnerable_chat_message_content_to_eval(user_input: str):
    """VULNERABLE: Cohere chat message.content to eval()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Generate Python code: {user_input}"}
        ]
    )
    
    code = response.message.content
    
    # CRITICAL: Executing untrusted LLM output
    eval(code)  # VULNERABILITY: Code injection risk


def vulnerable_generate_to_eval(user_input: str):
    """VULNERABLE: Cohere generate output passed to eval()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.generate(
        prompt=f"Generate Python code for: {user_input}"
    )
    
    code = response.generations[0].text
    
    # CRITICAL: Executing untrusted LLM output
    eval(code)  # VULNERABILITY: Code injection risk


def vulnerable_generate_to_exec(task: str):
    """VULNERABLE: Cohere generate output passed to exec()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.generate(
        prompt=f"Write Python code to: {task}"
    )
    
    code_str = response.generations[0].text
    
    # CRITICAL: Executing untrusted code
    exec(code_str)  # VULNERABILITY: Code injection risk


def vulnerable_generate_to_compile(description: str):
    """VULNERABLE: Cohere generate output passed to compile()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.generate(
        prompt=f"Generate code for: {description}"
    )
    
    code = response.generations[0].text
    
    # CRITICAL: Compiling untrusted code
    compile(code, "<string>", "exec")  # VULNERABILITY: Code injection risk


def vulnerable_clientv2_chat_to_eval(user_input: str):
    """VULNERABLE: ClientV2 chat output to eval()."""
    client = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Generate Python code: {user_input}"}
        ]
    )
    
    code = response.text
    eval(code)  # CRITICAL: Code injection risk


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and execution pattern."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": "Generate a Python function"}
        ]
    )
    
    # VULNERABILITY: Direct extraction and execution
    code = response.text
    eval(code)  # CRITICAL: No validation


def safe_usage_example(user_input: str):
    """SAFE: Proper validation and safe parsing."""
    import json
    
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Generate JSON data for: {user_input}"}
        ]
    )
    
    output_text = response.text
    
    # SAFE: Parse JSON instead of executing code
    try:
        data = json.loads(output_text)
        # Validate and use data safely
        return data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON response")


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_chat_to_eval("calculate fibonacci")
    vulnerable_chat_to_exec("process data")
    vulnerable_chat_to_compile("analyze dataset")
    vulnerable_chat_message_content_to_eval("create function")
    vulnerable_generate_to_eval("generate code")
    vulnerable_generate_to_exec("write code")
    vulnerable_generate_to_compile("compile code")
    vulnerable_clientv2_chat_to_eval("create Python")
    vulnerable_direct_extraction()
    safe_usage_example("user preferences")
