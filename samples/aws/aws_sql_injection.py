"""
Sample vulnerable AWS Bedrock application demonstrating SQL injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

import boto3
import json
import os
import sqlite3


def vulnerable_f_string_sql(user_query: str):
    """VULNERABLE: AWS Bedrock output concatenated into SQL using f-strings."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Generate SQL query for: {user_query}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    sql_query = body['output']['message']['content'][0]['text']
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via f-string
    cursor.execute(f"SELECT * FROM users WHERE {sql_query}")  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_string_concatenation_sql(user_request: str):
    """VULNERABLE: AWS Bedrock output concatenated into SQL using +."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Create SQL query: {user_request}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    query_part = body['output']['message']['content'][0]['text']
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via string concatenation
    cursor.execute("SELECT * FROM products WHERE name = " + query_part)  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_format_sql(user_input: str):
    """VULNERABLE: AWS Bedrock output used with .format() in SQL."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"SQL condition for: {user_input}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    condition = body['output']['message']['content'][0]['text']
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via .format()
    cursor.execute("SELECT * FROM orders WHERE {}".format(condition))  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_percent_format_sql(task: str):
    """VULNERABLE: AWS Bedrock output used with % formatting in SQL."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Generate SQL: {task}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    sql_part = body['output']['message']['content'][0]['text']
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via % formatting
    cursor.execute("SELECT * FROM customers WHERE %s" % sql_part)  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_invoke_model_to_sql(user_query: str):
    """VULNERABLE: InvokeModel output concatenated into SQL."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    body = json.dumps({
        "prompt": f"Generate SQL query for: {user_query}"
    })
    
    response = bedrock.invoke_model(
        modelId='amazon.titan-text-express-v1',
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    sql_query = response_body['completion']
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL injection via f-string
    cursor.execute(f"SELECT * FROM users WHERE {sql_query}")  # VULNERABILITY: SQL injection risk
    return cursor.fetchall()


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and SQL execution."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": "Generate a SQL SELECT query"}
        ]
    )
    
    # VULNERABILITY: Direct extraction and execution
    body = json.loads(response['body'].read())
    sql_query = body['output']['message']['content'][0]['text']
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(sql_query)  # CRITICAL: No validation
    return cursor.fetchall()


def safe_usage_example(user_query: str):
    """SAFE: Proper parameterized queries."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Extract search term from: {user_query}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    search_term = body['output']['message']['content'][0]['text'].strip()
    
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
    vulnerable_invoke_model_to_sql("find records")
    vulnerable_direct_extraction()
    safe_usage_example("find John Doe")
