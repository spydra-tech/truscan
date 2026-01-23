"""
Sample vulnerable Azure OpenAI Service application demonstrating code injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from openai import AzureOpenAI
import os


def vulnerable_eval_execution(user_input: str):
    """VULNERABLE: Azure OpenAI output passed to eval()."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Generate Python code for: {user_input}"}
        ]
    )
    
    code = response.choices[0].message.content
    
    # CRITICAL: Executing untrusted LLM output
    eval(code)  # VULNERABILITY: Code injection risk


def vulnerable_exec_execution(task: str):
    """VULNERABLE: Azure OpenAI output passed to exec()."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Write Python code to: {task}"}
        ]
    )
    
    code_str = response.choices[0].message.content
    
    # CRITICAL: Executing untrusted code
    exec(code_str)  # VULNERABILITY: Code injection risk


def vulnerable_compile_execution(description: str):
    """VULNERABLE: Azure OpenAI output passed to compile()."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Generate code for: {description}"}
        ]
    )
    
    code = response.choices[0].message.content
    
    # CRITICAL: Compiling untrusted code
    compile(code, "<string>", "exec")  # VULNERABILITY: Code injection risk


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and execution pattern."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": "Generate a Python function"}
        ]
    )
    
    # VULNERABILITY: Direct extraction and execution
    code = response.choices[0].message.content
    eval(code)  # CRITICAL: No validation


def safe_usage_example(user_input: str):
    """SAFE: Proper validation and safe parsing."""
    import json
    import ast
    
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Generate JSON data for: {user_input}"}
        ],
        response_format={"type": "json_object"}  # SAFE: Structured output
    )
    
    # SAFE: Parse JSON instead of executing code
    try:
        data = json.loads(response.choices[0].message.content)
        # Validate and use data safely
        return data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON response")


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_eval_execution("calculate fibonacci")
    vulnerable_exec_execution("process data")
    vulnerable_compile_execution("analyze dataset")
    vulnerable_direct_extraction()
    safe_usage_example("user preferences")
