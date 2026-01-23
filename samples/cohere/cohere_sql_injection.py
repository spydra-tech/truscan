"""
Sample vulnerable Cohere application demonstrating SQL injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

import cohere
import os
import sqlite3


def vulnerable_f_string_sql(user_query: str):
    """VULNERABLE: Cohere output concatenated into SQL using f-strings."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Generate SQL query for: {user_query}"}
        ]
    )
    
    sql_query = response.text
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via f-string
    cursor.execute(f"SELECT * FROM users WHERE {sql_query}")  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_string_concatenation_sql(user_request: str):
    """VULNERABLE: Cohere output concatenated into SQL using +."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Create SQL query: {user_request}"}
        ]
    )
    
    query_part = response.text
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via string concatenation
    cursor.execute("SELECT * FROM products WHERE name = " + query_part)  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_format_sql(user_input: str):
    """VULNERABLE: Cohere output used with .format() in SQL."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"SQL condition for: {user_input}"}
        ]
    )
    
    condition = response.text
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via .format()
    cursor.execute("SELECT * FROM orders WHERE {}".format(condition))  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_percent_format_sql(task: str):
    """VULNERABLE: Cohere output used with % formatting in SQL."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Generate SQL: {task}"}
        ]
    )
    
    sql_part = response.text
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via % formatting
    cursor.execute("SELECT * FROM customers WHERE %s" % sql_part)  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_chat_message_content_to_sql(user_query: str):
    """VULNERABLE: Cohere chat message.content to SQL."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Generate SQL query: {user_query}"}
        ]
    )
    
    sql_query = response.message.content
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE {sql_query}")  # CRITICAL: SQL injection risk
    return cursor.fetchall()


def vulnerable_generate_to_sql(user_query: str):
    """VULNERABLE: Cohere generate output to SQL."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.generate(
        prompt=f"Generate SQL query for: {user_query}"
    )
    
    sql_query = response.generations[0].text
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE {sql_query}")  # CRITICAL: SQL injection risk
    return cursor.fetchall()


def vulnerable_clientv2_chat_to_sql(user_query: str):
    """VULNERABLE: ClientV2 chat output to SQL."""
    client = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Generate SQL: {user_query}"}
        ]
    )
    
    sql_query = response.text
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE {sql_query}")  # CRITICAL: SQL injection risk
    return cursor.fetchall()


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and SQL execution."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": "Generate a SQL SELECT query"}
        ]
    )
    
    # VULNERABILITY: Direct extraction and execution
    sql_query = response.text
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(sql_query)  # CRITICAL: No validation
    return cursor.fetchall()


def safe_usage_example(user_query: str):
    """SAFE: Proper parameterized queries."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Extract search term from: {user_query}"}
        ]
    )
    
    search_term = response.text.strip()
    
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
    vulnerable_chat_message_content_to_sql("find records")
    vulnerable_generate_to_sql("get data")
    vulnerable_clientv2_chat_to_sql("query database")
    vulnerable_direct_extraction()
    safe_usage_example("find John Doe")
