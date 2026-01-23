"""
Sample vulnerable LlamaIndex application demonstrating code injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
CVE-2023-39662: PandasQueryEngine RCE via exec()
CVE-2024-3098: safe_eval bypass in exec_utils
"""

from llama_index.core.query_engine import PandasQueryEngine, PythonCodeQueryEngine
from llama_index.core.utils import exec_utils
import pandas as pd
from flask import request


def vulnerable_pandas_query_engine_direct(user_input: str):
    """VULNERABLE: PandasQueryEngine with user input (CVE-2023-39662)."""
    # CRITICAL: PandasQueryEngine uses exec() internally
    df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
    engine = PandasQueryEngine(df)
    
    # VULNERABILITY: User input directly passed to query engine
    result = engine.query(user_input)  # CRITICAL: Arbitrary code execution risk (CVE-2023-39662)
    
    return result


def vulnerable_pandas_query_engine_variable(user_input: str):
    """VULNERABLE: PandasQueryEngine assigned to variable, then queried with user input."""
    df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
    pandas_engine = PandasQueryEngine(df)
    
    # VULNERABILITY: User input in query
    result = pandas_engine.query(user_input)  # CRITICAL: Code execution risk
    
    return result


def vulnerable_pandas_query_engine_retrieve(user_input: str):
    """VULNERABLE: PandasQueryEngine.retrieve() with user input."""
    df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
    engine = PandasQueryEngine(df)
    
    # VULNERABILITY: User input in retrieve
    result = engine.retrieve(user_input)  # CRITICAL: Code execution risk
    
    return result


def vulnerable_safe_eval_llm_output(llm_output: str):
    """VULNERABLE: safe_eval with LLM output (CVE-2024-3098)."""
    # CRITICAL: safe_eval can be bypassed with malicious input
    result = exec_utils.safe_eval(llm_output)  # VULNERABILITY: safe_eval bypass risk (CVE-2024-3098)
    
    return result


def vulnerable_safe_eval_direct(llm_output: str):
    """VULNERABLE: Direct safe_eval() call with LLM output."""
    from llama_index.core.utils import exec_utils
    
    # VULNERABILITY: safe_eval with LLM output
    result = exec_utils.safe_eval(llm_output)  # CRITICAL: safe_eval bypass risk
    
    return result


def vulnerable_query_engine_to_eval(user_input: str):
    """VULNERABLE: Query engine output passed to eval()."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    # Load documents and create index
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    # Query with user input
    response = query_engine.query(user_input)
    
    # CRITICAL: Executing query engine output
    eval(str(response))  # VULNERABILITY: Code injection risk
    
    return response


def vulnerable_query_engine_to_exec(user_input: str):
    """VULNERABLE: Query engine output passed to exec()."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(user_input)
    
    # CRITICAL: Executing query engine output
    exec(str(response))  # VULNERABILITY: Code injection risk
    
    return response


def vulnerable_query_engine_to_compile(user_input: str):
    """VULNERABLE: Query engine output passed to compile()."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query(user_input)
    
    # CRITICAL: Compiling query engine output
    compile(str(response), "<string>", "exec")  # VULNERABILITY: Code injection risk
    
    return response


def vulnerable_python_code_query_engine(user_input: str):
    """VULNERABLE: PythonCodeQueryEngine with user input."""
    # CRITICAL: PythonCodeQueryEngine executes Python code
    engine = PythonCodeQueryEngine()
    
    # VULNERABILITY: User input in PythonCodeQueryEngine
    result = engine.query(user_input)  # CRITICAL: Code execution risk
    
    return result


def vulnerable_flask_request():
    """VULNERABLE: Flask request data in PandasQueryEngine."""
    df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
    engine = PandasQueryEngine(df)
    
    # VULNERABILITY: Request data directly in query
    user_query = request.args.get('query')  # From user input
    result = engine.query(user_query)  # CRITICAL: No validation
    
    return result


def safe_usage_example():
    """SAFE: Proper validation and restricted usage."""
    import re
    
    # SAFE: Only use with trusted, validated input
    df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
    
    # SAFE: Validate input before query
    user_query = "What is the sum of col1?"  # From trusted source
    
    # SAFE: Whitelist allowed operations
    ALLOWED_PATTERNS = [r'^sum\(', r'^mean\(', r'^count\(']
    if not any(re.match(pattern, user_query) for pattern in ALLOWED_PATTERNS):
        raise ValueError("Query not allowed")
    
    # SAFE: Use alternative that doesn't execute code
    # Instead of PandasQueryEngine, use safe query methods
    result = df.query("col1 > 0")  # SAFE: Pandas query without exec()
    
    return result


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_pandas_query_engine_direct("What is the sum?")
    vulnerable_pandas_query_engine_variable("Calculate mean")
    vulnerable_pandas_query_engine_retrieve("Get data")
    vulnerable_safe_eval_llm_output("print('hello')")
    vulnerable_safe_eval_direct("__import__('os').system('ls')")
    vulnerable_query_engine_to_eval("Generate code")
    vulnerable_query_engine_to_exec("Create function")
    vulnerable_query_engine_to_compile("Compile this")
    vulnerable_python_code_query_engine("Execute Python")
    safe_usage_example()
