"""
Sample vulnerable LlamaIndex application demonstrating command injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import subprocess
import os


def vulnerable_query_engine_to_subprocess(user_input: str):
    """VULNERABLE: Query engine output passed to subprocess.run()."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    # Query with user input
    response = query_engine.query(user_input)
    
    # CRITICAL: Executing query engine output as shell command
    subprocess.run(str(response), shell=True)  # VULNERABILITY: Command injection risk
    
    return response


def vulnerable_query_engine_to_os_system(user_input: str):
    """VULNERABLE: Query engine output passed to os.system()."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(user_input)
    
    # CRITICAL: Shell injection risk
    os.system(str(response))  # VULNERABILITY: Command injection risk
    
    return response


def vulnerable_query_engine_to_subprocess_call(user_input: str):
    """VULNERABLE: Query engine output passed to subprocess.call()."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(user_input)
    
    # CRITICAL: Command injection risk
    subprocess.call(str(response), shell=True)  # VULNERABILITY: Command injection risk
    
    return response


def vulnerable_query_engine_to_subprocess_popen(user_input: str):
    """VULNERABLE: Query engine output passed to subprocess.Popen()."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(user_input)
    
    # CRITICAL: Command injection risk
    subprocess.Popen(str(response), shell=True)  # VULNERABILITY: Command injection risk
    
    return response


def vulnerable_index_query_to_command(user_input: str):
    """VULNERABLE: Index query output to command execution."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    response = index.query(user_input)
    
    # CRITICAL: Command injection risk
    subprocess.run(str(response), shell=True)  # VULNERABILITY: Command injection risk
    
    return response


def vulnerable_query_engine_retrieve_to_command(user_input: str):
    """VULNERABLE: Query engine retrieve output to command execution."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.retrieve(user_input)
    
    # CRITICAL: Command injection risk
    os.system(str(response))  # VULNERABILITY: Command injection risk
    
    return response


def safe_usage_example(user_input: str):
    """SAFE: Proper command validation and parameterization."""
    import shlex
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(user_input)
    suggested_command = str(response)
    
    # SAFE: Validate against allowlist instead of executing
    ALLOWED_COMMANDS = ['ls', 'pwd', 'date']
    
    # Parse and validate
    parts = shlex.split(suggested_command)
    if parts and parts[0] in ALLOWED_COMMANDS:
        # SAFE: Use parameterized subprocess call
        subprocess.run(parts, shell=False)  # SAFE: No shell, parameterized
    else:
        raise ValueError(f"Command not allowed: {suggested_command}")
    
    return response


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_query_engine_to_subprocess("What command should I run?")
    vulnerable_query_engine_to_os_system("Generate command")
    vulnerable_query_engine_to_subprocess_call("Execute command")
    vulnerable_query_engine_to_subprocess_popen("Run command")
    vulnerable_index_query_to_command("What to execute?")
    vulnerable_query_engine_retrieve_to_command("Get command")
    safe_usage_example("Suggest safe command")
