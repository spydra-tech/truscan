"""
Sample vulnerable Hugging Face application demonstrating SQL injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from transformers import pipeline, TextGenerationPipeline
import sqlite3


def vulnerable_f_string_sql(user_query: str):
    """VULNERABLE: Pipeline output concatenated into SQL using f-strings."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(f"Generate SQL query for: {user_query}")
    
    sql_query = response[0]["generated_text"]
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via f-string
    cursor.execute(f"SELECT * FROM users WHERE {sql_query}")  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_string_concatenation_sql(user_request: str):
    """VULNERABLE: Pipeline output concatenated into SQL using +."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(f"Create SQL query: {user_request}")
    
    query_part = response[0]["generated_text"]
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via string concatenation
    cursor.execute("SELECT * FROM products WHERE name = " + query_part)  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_format_sql(user_input: str):
    """VULNERABLE: Pipeline output used with .format() in SQL."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(f"SQL condition for: {user_input}")
    
    condition = response[0]["generated_text"]
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via .format()
    cursor.execute("SELECT * FROM orders WHERE {}".format(condition))  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_percent_format_sql(task: str):
    """VULNERABLE: Pipeline output used with % formatting in SQL."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(f"Generate SQL: {task}")
    
    sql_part = response[0]["generated_text"]
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via % formatting
    cursor.execute("SELECT * FROM customers WHERE %s" % sql_part)  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_text_generation_pipeline_to_sql(user_query: str):
    """VULNERABLE: TextGenerationPipeline output to SQL."""
    pipe = TextGenerationPipeline(model="gpt2", tokenizer="gpt2")
    response = pipe(f"Generate SQL query: {user_query}")
    
    sql_query = response[0]["generated_text"]
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE {sql_query}")  # CRITICAL: SQL injection risk
    return cursor.fetchall()


def vulnerable_question_answering_pipeline_to_sql(user_query: str):
    """VULNERABLE: QuestionAnsweringPipeline output to SQL."""
    pipe = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
    response = pipe(user_query)
    
    sql_part = response["answer"]
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE name = {sql_part}")  # CRITICAL: SQL injection risk
    return cursor.fetchall()


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and SQL execution."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe("Generate a SQL SELECT query")
    
    # VULNERABILITY: Direct extraction and execution
    sql_query = response[0]["generated_text"]
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(sql_query)  # CRITICAL: No validation
    return cursor.fetchall()


def safe_usage_example(user_query: str):
    """SAFE: Proper parameterized queries."""
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(f"Extract search term from: {user_query}")
    
    search_term = response[0]["generated_text"].strip()
    
    # SAFE: Validate and sanitize
    if not search_term or len(search_term) > 100:
        raise ValueError("Invalid search term")
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # SAFE: Use parameterized queries
    cursor.execute("SELECT * FROM users WHERE name = ?", (search_term,))  # SAFE: Parameterized
    return cursor.fetchall()


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_f_string_sql("find users")
    vulnerable_string_concatenation_sql("search products")
    vulnerable_format_sql("filter orders")
    vulnerable_percent_format_sql("query customers")
    vulnerable_text_generation_pipeline_to_sql("find records")
    vulnerable_question_answering_pipeline_to_sql("What is the name?")
    vulnerable_direct_extraction()
    safe_usage_example("find John Doe")
