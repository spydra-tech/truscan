"""
Sample vulnerable Hugging Face application demonstrating overreliance vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from transformers import pipeline
import sqlite3
import subprocess


def vulnerable_pipeline_output_no_validation_critical(user_input: str):
    """VULNERABLE: Pipeline output used in critical operations without validation."""
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(f"Generate SQL query: {user_input}")
    
    sql_query = response[0]["generated_text"]
    
    # CRITICAL: No validation before SQL execution
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(sql_query)  # VULNERABILITY: Overreliance on LLM output
    
    return cursor.fetchall()


def vulnerable_pipeline_output_no_validation_command(user_input: str):
    """VULNERABLE: Pipeline output used in command execution without validation."""
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(f"Generate command: {user_input}")
    
    command = response[0]["generated_text"]
    
    # CRITICAL: No validation before command execution
    subprocess.run(command, shell=True)  # VULNERABILITY: Overreliance on LLM output
    
    return command


def vulnerable_pipeline_output_no_validation_file(user_input: str):
    """VULNERABLE: Pipeline output used in file operations without validation."""
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(f"Generate filename: {user_input}")
    
    filename = response[0]["generated_text"]
    
    # CRITICAL: No validation before file operation
    with open(filename, 'w') as f:  # VULNERABILITY: Overreliance on LLM output
        f.write("data")
    
    return filename


def safe_usage_example(user_input: str):
    """SAFE: Proper validation and verification."""
    import re
    
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(f"Extract search term: {user_input}")
    
    search_term = response[0]["generated_text"].strip()
    
    # SAFE: Validate output
    if not search_term:
        raise ValueError("Empty output")
    
    if len(search_term) > 100:
        raise ValueError("Output too long")
    
    # SAFE: Verify format (e.g., alphanumeric only)
    if not re.match(r'^[a-zA-Z0-9\s]+$', search_term):
        raise ValueError("Invalid format")
    
    # SAFE: Use validated output in parameterized query
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = ?", (search_term,))  # SAFE: Parameterized
    
    return cursor.fetchall()


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_pipeline_output_no_validation_critical("find users")
    vulnerable_pipeline_output_no_validation_command("list files")
    vulnerable_pipeline_output_no_validation_file("save data")
    safe_usage_example("find John")
