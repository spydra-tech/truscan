"""
Sample vulnerable LlamaIndex application demonstrating document loader vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from llama_index.core import SimpleDirectoryReader, WebPageReader, PyPDFReader
import requests
import urllib.request
from flask import request


def vulnerable_web_page_reader_untrusted_url():
    """VULNERABLE: WebPageReader with untrusted URL (SSRF risk)."""
    # CRITICAL: SSRF and training data poisoning risk
    untrusted_url = request.args.get('url')  # From user input
    
    # VULNERABILITY: Untrusted URL in document loader
    loader = WebPageReader(untrusted_url)  # CRITICAL: SSRF risk
    documents = loader.load_data()
    
    return documents


def vulnerable_simple_directory_reader_untrusted_url():
    """VULNERABLE: SimpleDirectoryReader with untrusted URL."""
    # CRITICAL: SSRF risk
    untrusted_url = request.args.get('url')  # From user input
    
    # VULNERABILITY: Untrusted URL in document loader
    loader = SimpleDirectoryReader(untrusted_url)  # CRITICAL: SSRF risk
    documents = loader.load_data()
    
    return documents


def vulnerable_web_page_reader_requests():
    """VULNERABLE: WebPageReader with URL from requests.get()."""
    # CRITICAL: SSRF risk
    response = requests.get("https://untrusted-source.com/page.html")
    untrusted_url = response.url  # VULNERABILITY: Untrusted URL
    
    loader = WebPageReader(untrusted_url)  # CRITICAL: SSRF risk
    documents = loader.load_data()
    
    return documents


def vulnerable_pypdf_reader_untrusted_file():
    """VULNERABLE: PyPDFReader with user-controlled file (path traversal risk)."""
    # CRITICAL: Path traversal and training data poisoning risk
    user_file = request.files.get('file')  # From user input
    
    # VULNERABILITY: User-controlled file in document loader
    loader = PyPDFReader(user_file.filename)  # CRITICAL: Path traversal risk
    documents = loader.load_data()
    
    return documents


def vulnerable_simple_directory_reader_untrusted_file():
    """VULNERABLE: SimpleDirectoryReader with user-controlled file."""
    # CRITICAL: Path traversal risk
    user_path = request.args.get('path')  # From user input
    
    # VULNERABILITY: User-controlled path in document loader
    loader = SimpleDirectoryReader(user_path)  # CRITICAL: Path traversal risk
    documents = loader.load_data()
    
    return documents


def vulnerable_document_loader_to_prompt():
    """VULNERABLE: Document loader content flows into LLM prompts."""
    from openai import OpenAI
    
    # Load documents
    loader = WebPageReader("https://example.com/page.html")
    documents = loader.load_data()
    
    # CRITICAL: Document content in prompt without sanitization
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Summarize: {str(documents)}"}  # VULNERABILITY: Indirect prompt injection
        ]
    )
    
    return response.choices[0].message.content


def vulnerable_document_loader_to_index():
    """VULNERABLE: Document loader content flows into index."""
    from llama_index.core import VectorStoreIndex
    
    # Load from untrusted source
    untrusted_url = request.args.get('url')  # From user input
    loader = WebPageReader(untrusted_url)
    documents = loader.load_data()
    
    # CRITICAL: Untrusted documents in index
    index = VectorStoreIndex.from_documents(documents)  # VULNERABILITY: Training data poisoning
    
    return index


def vulnerable_loader_load_data_untrusted():
    """VULNERABLE: loader.load_data() with untrusted source."""
    untrusted_url = request.args.get('url')  # From user input
    loader = WebPageReader(untrusted_url)
    
    # VULNERABILITY: Load data from untrusted source
    documents = loader.load_data()  # CRITICAL: SSRF and training data poisoning risk
    
    return documents


def safe_usage_example():
    """SAFE: Proper URL validation and path sanitization."""
    import os
    from pathlib import Path
    
    # SAFE: Validate URL against allowlist
    ALLOWED_DOMAINS = ["trusted-source.com", "verified-dataset.org"]
    url = "https://trusted-source.com/data.html"
    
    domain = url.split("//")[1].split("/")[0]
    if domain not in ALLOWED_DOMAINS:
        raise ValueError("Untrusted domain")
    
    # SAFE: Use validated URL
    loader = WebPageReader(url)
    documents = loader.load_data()
    
    # SAFE: Sanitize document content before using in prompts
    from llama_index.core import VectorStoreIndex
    index = VectorStoreIndex.from_documents(documents)
    
    # SAFE: Sanitize query results
    query_result = index.query("What is this?")
    sanitized = str(query_result).replace("'", "''")  # Basic sanitization
    
    return sanitized


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    # vulnerable_web_page_reader_untrusted_url()  # Requires Flask context
    # vulnerable_simple_directory_reader_untrusted_url()  # Requires Flask context
    vulnerable_web_page_reader_requests()
    # vulnerable_pypdf_reader_untrusted_file()  # Requires Flask context
    # vulnerable_simple_directory_reader_untrusted_file()  # Requires Flask context
    vulnerable_document_loader_to_prompt()
    # vulnerable_document_loader_to_index()  # Requires Flask context
    # vulnerable_loader_load_data_untrusted()  # Requires Flask context
    safe_usage_example()
