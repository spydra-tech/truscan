"""
Sample vulnerable Hugging Face application demonstrating sensitive information disclosure vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from transformers import pipeline
import logging


def vulnerable_pipeline_logging(user_input: str):
    """VULNERABLE: Pipeline output logged without sanitization."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(user_input)
    
    output = response[0]["generated_text"]
    
    # CRITICAL: Logging pipeline output (may contain sensitive info)
    logging.info(f"Pipeline output: {output}")  # VULNERABILITY: Sensitive info disclosure
    
    return output


def vulnerable_model_response_logging(user_input: str):
    """VULNERABLE: Model response logged without sanitization."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(user_input)
    
    # CRITICAL: Logging full response (may contain sensitive info)
    logging.debug(f"Model response: {response}")  # VULNERABILITY: Sensitive info disclosure
    
    return response[0]["generated_text"]


def vulnerable_pipeline_output_print(user_input: str):
    """VULNERABLE: Pipeline output printed to console."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(user_input)
    
    output = response[0]["generated_text"]
    
    # CRITICAL: Printing pipeline output (may contain sensitive info)
    print(f"Output: {output}")  # VULNERABILITY: Sensitive info disclosure
    
    return output


def safe_usage_example(user_input: str):
    """SAFE: Proper logging with sanitization."""
    import re
    
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(user_input)
    
    output = response[0]["generated_text"]
    
    # SAFE: Sanitize before logging
    # Remove potential sensitive patterns
    sanitized = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', output)  # Credit cards
    sanitized = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', sanitized)  # SSN
    sanitized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', sanitized)  # Emails
    
    # SAFE: Log sanitized output
    logging.info(f"Pipeline output (sanitized): {sanitized}")
    
    return output


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_pipeline_logging("Generate text with sensitive info")
    vulnerable_model_response_logging("Generate response")
    vulnerable_pipeline_output_print("Generate output")
    safe_usage_example("Generate text")
