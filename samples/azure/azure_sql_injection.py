"""
Sample vulnerable Azure OpenAI Service application demonstrating SQL injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from openai import AzureOpenAI
import os
import sqlite3


def vulnerable_f_string_sql(user_query: str):
    """VULNERABLE: Azure OpenAI output concatenated into SQL using f-strings."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Generate SQL query for: {user_query}"}
        ]
    )
    
    sql_query = response.choices[0].message.content
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via f-string
    cursor.execute(f"SELECT * FROM users WHERE {sql_query}")  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_string_concatenation_sql(user_request: str):
    """VULNERABLE: Azure OpenAI output concatenated into SQL using +."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Create SQL query: {user_request}"}
        ]
    )
    
    query_part = response.choices[0].message.content
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via string concatenation
    cursor.execute("SELECT * FROM products WHERE name = " + query_part)  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_format_sql(user_input: str):
    """VULNERABLE: Azure OpenAI output used with .format() in SQL."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"SQL condition for: {user_input}"}
        ]
    )
    
    condition = response.choices[0].message.content
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via .format()
    cursor.execute("SELECT * FROM orders WHERE {}".format(condition))  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_percent_format_sql(task: str):
    """VULNERABLE: Azure OpenAI output used with % formatting in SQL."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Generate SQL: {task}"}
        ]
    )
    
    sql_part = response.choices[0].message.content
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via % formatting
    cursor.execute("SELECT * FROM customers WHERE %s" % sql_part)  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and SQL execution."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": "Generate a SQL SELECT query"}
        ]
    )
    
    # VULNERABILITY: Direct extraction and execution
    sql_query = response.choices[0].message.content
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(sql_query)  # CRITICAL: No validation
    return cursor.fetchall()


def safe_usage_example(user_query: str):
    """SAFE: Proper parameterized queries."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Extract search term from: {user_query}"}
        ]
    )
    
    search_term = response.choices[0].message.content.strip()
    
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
    vulnerable_direct_extraction()
    safe_usage_example("find John Doe")
