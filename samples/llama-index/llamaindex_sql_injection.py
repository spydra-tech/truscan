"""
Sample vulnerable LlamaIndex application demonstrating SQL injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
CVE-2025-1793: SQL injection in Text-to-SQL engines (CVSS 9.8)
CVE-2024-23751: SQL injection in Text-to-SQL engines (CVSS 9.8)
"""

from llama_index.core.query_engine import NLSQLTableQueryEngine, SQLTableRetrieverQueryEngine, PGVectorSQLQueryEngine
from llama_index.core.retrievers import NLSQLRetriever
from flask import request
import sqlite3


def vulnerable_nlsql_table_query_engine(user_input: str):
    """VULNERABLE: NLSQLTableQueryEngine with user input (CVE-2025-1793, CVE-2024-23751)."""
    # CRITICAL: NLSQLTableQueryEngine generates SQL from natural language
    conn = sqlite3.connect("example.db")
    engine = NLSQLTableQueryEngine(conn)
    
    # VULNERABILITY: User input directly in query
    result = engine.query(user_input)  # CRITICAL: SQL injection risk (CVE-2025-1793, CVE-2024-23751)
    
    return result


def vulnerable_sql_table_retriever_query_engine(user_input: str):
    """VULNERABLE: SQLTableRetrieverQueryEngine with user input."""
    from llama_index.core import VectorStoreIndex
    
    # CRITICAL: SQLTableRetrieverQueryEngine generates SQL
    index = VectorStoreIndex.from_documents([])
    engine = SQLTableRetrieverQueryEngine(index)
    
    # VULNERABILITY: User input in query
    result = engine.query(user_input)  # CRITICAL: SQL injection risk
    
    return result


def vulnerable_pgvector_sql_query_engine(user_input: str):
    """VULNERABLE: PGVectorSQLQueryEngine with user input."""
    # CRITICAL: PGVectorSQLQueryEngine generates SQL
    engine = PGVectorSQLQueryEngine()
    
    # VULNERABILITY: User input in query
    result = engine.query(user_input)  # CRITICAL: SQL injection risk
    
    return result


def vulnerable_nlsql_retriever(user_input: str):
    """VULNERABLE: NLSQLRetriever with user input."""
    conn = sqlite3.connect("example.db")
    retriever = NLSQLRetriever(conn)
    
    # VULNERABILITY: User input in retriever
    result = retriever.retrieve(user_input)  # CRITICAL: SQL injection risk
    
    return result


def vulnerable_sql_engine_variable(user_input: str):
    """VULNERABLE: SQL engine assigned to variable, then queried."""
    conn = sqlite3.connect("example.db")
    sql_engine = NLSQLTableQueryEngine(conn)
    
    # VULNERABILITY: User input in query
    result = sql_engine.query(user_input)  # CRITICAL: SQL injection risk
    
    return result


def vulnerable_query_engine_sql_output(user_input: str):
    """VULNERABLE: Query engine output concatenated into SQL."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    # Query with user input
    response = query_engine.query(user_input)
    
    # CRITICAL: Query engine output in SQL
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE name = '{str(response)}'")  # VULNERABILITY: SQL injection
    
    return cursor.fetchall()


def vulnerable_flask_request():
    """VULNERABLE: Flask request data in SQL query engine."""
    conn = sqlite3.connect("example.db")
    engine = NLSQLTableQueryEngine(conn)
    
    # VULNERABILITY: Request data directly in query
    user_query = request.args.get('query')  # From user input
    result = engine.query(user_query)  # CRITICAL: No validation
    
    return result


def safe_usage_example():
    """SAFE: Proper input validation and parameterized queries."""
    import re
    
    conn = sqlite3.connect("example.db")
    
    # SAFE: Validate input before query
    user_query = "What is the total sales?"  # From trusted source
    
    # SAFE: Whitelist allowed query patterns
    ALLOWED_PATTERNS = [r'^What is the', r'^Show me', r'^List']
    if not any(re.match(pattern, user_query) for pattern in ALLOWED_PATTERNS):
        raise ValueError("Query not allowed")
    
    # SAFE: Use parameterized queries instead of Text-to-SQL
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales WHERE amount > ?", (100,))  # SAFE: Parameterized
    
    return cursor.fetchall()


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_nlsql_table_query_engine("What is the total?")
    vulnerable_sql_table_retriever_query_engine("Show me data")
    vulnerable_pgvector_sql_query_engine("Query database")
    vulnerable_nlsql_retriever("Retrieve records")
    vulnerable_sql_engine_variable("Get information")
    vulnerable_query_engine_sql_output("Find user")
    safe_usage_example()
