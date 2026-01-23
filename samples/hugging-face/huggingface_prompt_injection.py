"""
Sample vulnerable Hugging Face application demonstrating prompt injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from transformers import pipeline, AutoTokenizer
from flask import request
import os


def vulnerable_pipeline_direct_user_input(user_input: str):
    """VULNERABLE: Direct user input in Hugging Face pipeline."""
    # VULNERABILITY: User input directly passed to pipeline
    pipe = pipeline("text-generation", model="gpt2")
    result = pipe(user_input)  # CRITICAL: No sanitization
    
    return result[0]["generated_text"]


def vulnerable_pipeline_question_answering(user_input: str):
    """VULNERABLE: User input in question-answering pipeline."""
    # VULNERABILITY: User input in question-answering
    pipe = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
    result = pipe(user_input)  # CRITICAL: No validation
    
    return result["answer"]


def vulnerable_pipeline_text2text(user_input: str):
    """VULNERABLE: User input in text2text-generation pipeline."""
    # VULNERABILITY: User input in text2text-generation
    pipe = pipeline("text2text-generation", model="t5-small")
    result = pipe(user_input)  # CRITICAL: No sanitization
    
    return result[0]["generated_text"]


def vulnerable_pipeline_variable_assignment(user_input: str):
    """VULNERABLE: Pipeline assigned to variable then called with user input."""
    # VULNERABILITY: Pipeline variable pattern
    pipe = pipeline("text-generation", model="gpt2")
    result = pipe(user_input)  # CRITICAL: No validation
    
    return result[0]["generated_text"]


def vulnerable_tokenizer_user_input(user_input: str):
    """VULNERABLE: User input in tokenizer."""
    from transformers import AutoTokenizer
    
    # VULNERABILITY: User input in tokenizer
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    tokens = tokenizer(user_input)  # CRITICAL: No sanitization
    
    return tokens


def vulnerable_tokenizer_encode(user_input: str):
    """VULNERABLE: User input in tokenizer.encode()."""
    from transformers import AutoTokenizer
    
    # VULNERABILITY: User input in tokenizer.encode()
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    encoded = tokenizer.encode(user_input)  # CRITICAL: No validation
    
    return encoded


def vulnerable_tokenizer_tokenize(user_input: str):
    """VULNERABLE: User input in tokenizer.tokenize()."""
    from transformers import AutoTokenizer
    
    # VULNERABILITY: User input in tokenizer.tokenize()
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    tokens = tokenizer.tokenize(user_input)  # CRITICAL: No sanitization
    
    return tokens


def vulnerable_flask_request():
    """VULNERABLE: Flask request data in pipeline."""
    # VULNERABILITY: Request data directly in pipeline
    user_query = request.args.get('query')  # From user input
    pipe = pipeline("text-generation", model="gpt2")
    result = pipe(user_query)  # CRITICAL: No validation
    
    return result[0]["generated_text"]


def safe_usage_example(user_input: str):
    """SAFE: Proper input validation and sanitization."""
    import html
    
    # SAFE: Input validation and sanitization
    if not user_input or len(user_input) > 1000:
        raise ValueError("Invalid input")
    
    sanitized = html.escape(user_input)
    
    pipe = pipeline(
        "text-generation",
        model="gpt2",
        max_length=100  # SAFE: Token limit
    )
    result = pipe(sanitized)
    
    # SAFE: Sanitize output before use
    output = result[0]["generated_text"]
    return html.escape(output)


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_pipeline_direct_user_input("What is 2+2?")
    vulnerable_pipeline_question_answering("What is the capital of France?")
    vulnerable_pipeline_text2text("Translate: Hello")
    vulnerable_pipeline_variable_assignment("Generate text")
    vulnerable_tokenizer_user_input("Tokenize this")
    vulnerable_tokenizer_encode("Encode this")
    vulnerable_tokenizer_tokenize("Tokenize this")
    safe_usage_example("What is the weather?")
