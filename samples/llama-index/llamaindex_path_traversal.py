"""
Sample vulnerable LlamaIndex application demonstrating path traversal vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from pathlib import Path
import os
import shutil


def vulnerable_query_engine_to_file_write(user_input: str):
    """VULNERABLE: Query engine output used in file write operations."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(f"Generate filename for: {user_input}")
    filename = str(response).strip()
    
    # CRITICAL: Path traversal risk
    with open(filename, 'w') as f:  # VULNERABILITY: Path traversal risk
        f.write("data")
    
    return filename


def vulnerable_query_engine_to_path_write_text(user_input: str):
    """VULNERABLE: Query engine output used in Path.write_text()."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(f"Generate path for: {user_input}")
    filepath = str(response).strip()
    
    # CRITICAL: Path traversal risk
    Path(filepath).write_text("data")  # VULNERABILITY: Path traversal risk
    
    return filepath


def vulnerable_query_engine_to_shutil_copy(user_input: str):
    """VULNERABLE: Query engine output used in shutil.copy()."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(f"Generate destination path: {user_input}")
    dest_path = str(response).strip()
    
    # CRITICAL: Path traversal risk
    shutil.copy("source.txt", dest_path)  # VULNERABILITY: Path traversal risk
    
    return dest_path


def vulnerable_query_engine_to_os_remove(user_input: str):
    """VULNERABLE: Query engine output used in os.remove()."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(f"Generate file to delete: {user_input}")
    filepath = str(response).strip()
    
    # CRITICAL: Path traversal risk
    os.remove(filepath)  # VULNERABILITY: Path traversal risk
    
    return filepath


def vulnerable_index_query_to_file_ops(user_input: str):
    """VULNERABLE: Index query output to file operations."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    response = index.query(f"Generate filename: {user_input}")
    filename = str(response).strip()
    
    # CRITICAL: Path traversal risk
    with open(filename, 'w') as f:  # VULNERABILITY: Path traversal risk
        f.write("data")
    
    return filename


def safe_usage_example(user_input: str):
    """SAFE: Proper path validation and sanitization."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(f"Generate filename for: {user_input}")
    filename = str(response).strip()
    
    # SAFE: Validate and sanitize path
    # Remove path traversal sequences
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")
    
    # SAFE: Restrict to safe directory
    SAFE_DIR = "/tmp/safe_output"
    os.makedirs(SAFE_DIR, exist_ok=True)
    
    # SAFE: Use Path for safe path joining
    safe_path = Path(SAFE_DIR) / filename
    
    # SAFE: Ensure path is within safe directory
    if not str(safe_path.resolve()).startswith(os.path.abspath(SAFE_DIR)):
        raise ValueError("Path traversal detected")
    
    safe_path.write_text("data")
    
    return str(safe_path)


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_query_engine_to_file_write("save file")
    vulnerable_query_engine_to_path_write_text("write path")
    vulnerable_query_engine_to_shutil_copy("copy to")
    # vulnerable_query_engine_to_os_remove("delete file")  # Would actually delete
    vulnerable_index_query_to_file_ops("save data")
    safe_usage_example("save file")
