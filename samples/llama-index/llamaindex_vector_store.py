"""
Sample vulnerable LlamaIndex application demonstrating vector store and index vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from llama_index.core import VectorStoreIndex, PropertyGraphIndex
from llama_index.core.vector_stores import SimpleVectorStore
import requests
import urllib.request
from flask import request


def vulnerable_index_query_user_input(user_input: str):
    """VULNERABLE: Index query with user input."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    # VULNERABILITY: User input in index query
    result = index.query(user_input)  # CRITICAL: Prompt injection risk
    
    return result


def vulnerable_index_retrieve_user_input(user_input: str):
    """VULNERABLE: Index retrieve with user input."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    # VULNERABILITY: User input in retrieve
    result = index.retrieve(user_input)  # CRITICAL: Prompt injection risk
    
    return result


def vulnerable_index_from_documents_untrusted_web():
    """VULNERABLE: Index created from untrusted web data."""
    # CRITICAL: Training data poisoning risk
    response = requests.get("https://untrusted-source.com/data.txt")
    untrusted_data = response.text  # VULNERABILITY: Untrusted data source
    
    from llama_index.core import Document
    documents = [Document(text=untrusted_data)]
    
    # VULNERABILITY: Index from untrusted documents
    index = VectorStoreIndex.from_documents(documents)  # CRITICAL: Training data poisoning risk
    
    return index


def vulnerable_index_from_documents_urlopen():
    """VULNERABLE: Index created from urllib.request.urlopen data."""
    # CRITICAL: Training data poisoning risk
    with urllib.request.urlopen("https://untrusted-source.com/data.txt") as f:
        untrusted_data = f.read().decode()  # VULNERABILITY: Untrusted data source
    
    from llama_index.core import Document
    documents = [Document(text=untrusted_data)]
    
    # VULNERABILITY: Index from untrusted documents
    index = VectorStoreIndex.from_documents(documents)  # CRITICAL: Training data poisoning risk
    
    return index


def vulnerable_property_graph_index_untrusted():
    """VULNERABLE: PropertyGraphIndex from untrusted documents."""
    # CRITICAL: Training data poisoning risk
    response = requests.get("https://untrusted-source.com/graph-data.json")
    untrusted_data = response.json()  # VULNERABILITY: Untrusted data source
    
    from llama_index.core import Document
    documents = [Document(text=str(untrusted_data))]
    
    # VULNERABILITY: PropertyGraphIndex from untrusted documents
    index = PropertyGraphIndex.from_documents(documents)  # CRITICAL: Training data poisoning risk
    
    return index


def vulnerable_index_results_to_prompt(user_input: str):
    """VULNERABLE: Index query results flow into LLM prompts."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    from openai import OpenAI
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    # Query with user input
    query_result = index.query(user_input)
    
    # CRITICAL: Query results in prompt without sanitization
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Answer based on: {str(query_result)}"}  # VULNERABILITY: Indirect prompt injection
        ]
    )
    
    return response.choices[0].message.content


def vulnerable_vector_store_query_untrusted(user_input: str):
    """VULNERABLE: Vector store query with user input."""
    vector_store = SimpleVectorStore()
    
    # VULNERABILITY: User input in vector store query
    result = vector_store.query(user_input)  # CRITICAL: Prompt injection risk
    
    return result


def vulnerable_vector_store_retrieve_untrusted(user_input: str):
    """VULNERABLE: Vector store retrieve with user input."""
    vector_store = SimpleVectorStore()
    
    # VULNERABILITY: User input in retrieve
    result = vector_store.retrieve(user_input)  # CRITICAL: Prompt injection risk
    
    return result


def safe_usage_example():
    """SAFE: Proper data validation and trusted sources."""
    import html
    
    # SAFE: Load from trusted source
    TRUSTED_DATA_SOURCE = "https://trusted-dataset-repo.com/verified-data.txt"
    
    # SAFE: Validate data source
    if not TRUSTED_DATA_SOURCE.startswith("https://trusted-dataset-repo.com"):
        raise ValueError("Untrusted data source")
    
    response = requests.get(TRUSTED_DATA_SOURCE)
    
    # SAFE: Validate and sanitize data
    data = response.text
    if not data or len(data) < 100:
        raise ValueError("Invalid data")
    
    sanitized_data = html.escape(data)
    
    from llama_index.core import Document
    documents = [Document(text=sanitized_data)]
    
    # SAFE: Index from validated data
    index = VectorStoreIndex.from_documents(documents)
    
    # SAFE: Sanitize query results before using in prompts
    query_result = index.query("What is this?")
    sanitized_result = html.escape(str(query_result))
    
    return sanitized_result


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_index_query_user_input("What is this?")
    vulnerable_index_retrieve_user_input("Retrieve data")
    vulnerable_index_from_documents_untrusted_web()
    vulnerable_index_from_documents_urlopen()
    vulnerable_property_graph_index_untrusted()
    vulnerable_index_results_to_prompt("Summarize")
    vulnerable_vector_store_query_untrusted("Find similar")
    vulnerable_vector_store_retrieve_untrusted("Get vectors")
    safe_usage_example()
