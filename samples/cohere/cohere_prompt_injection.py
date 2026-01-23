"""
Sample vulnerable Cohere application demonstrating prompt injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

import cohere
from flask import request
import os


def vulnerable_chat_direct_user_input(user_input: str):
    """VULNERABLE: Direct user input in Cohere chat messages."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    # VULNERABILITY: User input directly inserted into prompt
    response = client.chat(
        messages=[
            {"role": "user", "content": user_input}  # CRITICAL: No sanitization
        ]
    )
    
    return response.text


def vulnerable_chat_without_role(user_input: str):
    """VULNERABLE: User input in chat messages without role."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    # VULNERABILITY: User input without role specification
    response = client.chat(
        messages=[
            {"content": user_input}  # CRITICAL: No sanitization
        ]
    )
    
    return response.text


def vulnerable_clientv2_chat(user_input: str):
    """VULNERABLE: ClientV2 chat with user input."""
    client = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
    
    # VULNERABILITY: User input in ClientV2 chat
    response = client.chat(
        messages=[
            {"role": "user", "content": user_input}  # CRITICAL: No validation
        ]
    )
    
    return response.text


def vulnerable_chat_variable_assignment(user_input: str):
    """VULNERABLE: Chat assigned to variable, then called with user input."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    # VULNERABILITY: User input in chat
    response = client.chat(
        messages=[
            {"role": "user", "content": user_input}  # CRITICAL: No sanitization
        ]
    )
    
    return response.text


def vulnerable_generate_direct_user_input(user_input: str):
    """VULNERABLE: Direct user input in Cohere generate prompt."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    # VULNERABILITY: User input directly in generate prompt
    response = client.generate(
        prompt=user_input  # CRITICAL: No sanitization
    )
    
    return response.generations[0].text


def vulnerable_generate_prompt_parameter(user_input: str):
    """VULNERABLE: User input in generate prompt parameter."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    # VULNERABILITY: User input in prompt parameter
    response = client.generate(
        prompt=user_input,  # CRITICAL: No validation
        max_tokens=100
    )
    
    return response.generations[0].text


def vulnerable_string_concatenation_chat(user_input: str):
    """VULNERABLE: User input concatenated into chat prompt."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    # VULNERABILITY: String concatenation in prompt
    prompt = "You are a helpful assistant. Answer this question: " + user_input
    response = client.chat(
        messages=[
            {"role": "user", "content": prompt}  # CRITICAL: Concatenation risk
        ]
    )
    
    return response.text


def vulnerable_f_string_chat(user_input: str):
    """VULNERABLE: F-string injection in chat prompt."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    # VULNERABILITY: F-string interpolation
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Process this request: {user_input}"}  # CRITICAL: F-string injection
        ]
    )
    
    return response.text


def vulnerable_f_string_generate(user_input: str):
    """VULNERABLE: F-string injection in generate prompt."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    # VULNERABILITY: F-string in generate prompt
    prompt = f"Answer this question: {user_input}"
    response = client.generate(
        prompt=prompt  # CRITICAL: F-string injection
    )
    
    return response.generations[0].text


def vulnerable_flask_request():
    """VULNERABLE: Flask request data in Cohere prompt."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    # VULNERABILITY: Request data directly in prompt
    user_query = request.args.get('query')  # From user input
    response = client.chat(
        messages=[
            {"role": "user", "content": user_query}  # CRITICAL: No validation
        ]
    )
    
    return response.text


def safe_usage_example(user_input: str):
    """SAFE: Proper input validation and sanitization."""
    import html
    
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    # SAFE: Input validation and sanitization
    if not user_input or len(user_input) > 1000:
        raise ValueError("Invalid input")
    
    sanitized = html.escape(user_input)
    
    response = client.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Answer this question: {sanitized}"}
        ],
        max_tokens=100  # SAFE: Token limit
    )
    
    return response.text


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_chat_direct_user_input("What is 2+2?")
    vulnerable_chat_without_role("Calculate fibonacci")
    vulnerable_clientv2_chat("Process this data")
    vulnerable_chat_variable_assignment("Generate text")
    vulnerable_generate_direct_user_input("What is the weather?")
    vulnerable_generate_prompt_parameter("Analyze this")
    vulnerable_string_concatenation_chat("Translate: Hello")
    vulnerable_f_string_chat("Generate code")
    vulnerable_f_string_generate("Create function")
    safe_usage_example("What is the weather?")
