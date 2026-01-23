"""
Sample vulnerable LlamaIndex application demonstrating sensitive information disclosure vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import logging


def vulnerable_query_engine_logging(user_input: str):
    """VULNERABLE: Query engine response logged without sanitization."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(user_input)
    
    # CRITICAL: Logging query engine response (may contain sensitive info)
    logging.info(f"Query engine response: {response}")  # VULNERABILITY: Sensitive info disclosure
    
    return response


def vulnerable_query_engine_debug_logging(user_input: str):
    """VULNERABLE: Query engine response logged with debug level."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(user_input)
    
    # CRITICAL: Debug logging of response
    logging.debug(f"Query engine response: {response}")  # VULNERABILITY: Sensitive info disclosure
    
    return response


def vulnerable_query_engine_print(user_input: str):
    """VULNERABLE: Query engine response printed to console."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(user_input)
    
    # CRITICAL: Printing query engine response
    print(f"Response: {response}")  # VULNERABILITY: Sensitive info disclosure
    
    return response


def vulnerable_index_content_logging():
    """VULNERABLE: Index content or documents logged without sanitization."""
    from llama_index.core import SimpleDirectoryReader
    
    loader = SimpleDirectoryReader("data")
    documents = loader.load_data()
    
    # CRITICAL: Logging documents (may contain sensitive info)
    logging.info(f"Documents: {documents}")  # VULNERABILITY: Sensitive info disclosure
    
    index = VectorStoreIndex.from_documents(documents)
    
    # CRITICAL: Logging index query results
    result = index.query("What is this?")
    logging.debug(f"Index result: {result}")  # VULNERABILITY: Sensitive info disclosure
    
    return result


def vulnerable_query_engine_retrieve_logging(user_input: str):
    """VULNERABLE: Query engine retrieve response logged."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.retrieve(user_input)
    
    # CRITICAL: Logging retrieve response
    logging.info(f"Retrieve response: {response}")  # VULNERABILITY: Sensitive info disclosure
    
    return response


def safe_usage_example(user_input: str):
    """SAFE: Proper logging with sanitization."""
    import re
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(user_input)
    output = str(response)
    
    # SAFE: Sanitize before logging
    # Remove potential sensitive patterns
    sanitized = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', output)  # Credit cards
    sanitized = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', sanitized)  # SSN
    sanitized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', sanitized)  # Emails
    
    # SAFE: Log sanitized output
    logging.info(f"Query engine response (sanitized): {sanitized}")
    
    return response


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_query_engine_logging("What is the user's email?")
    vulnerable_query_engine_debug_logging("Get user data")
    vulnerable_query_engine_print("Show information")
    vulnerable_index_content_logging()
    vulnerable_query_engine_retrieve_logging("Retrieve data")
    safe_usage_example("What is this?")
