"""
Sample vulnerable LlamaIndex application demonstrating model denial of service vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import ServiceContext


def vulnerable_query_engine_no_token_limit(user_input: str):
    """VULNERABLE: Query engine without max_tokens limit."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    # CRITICAL: No token limit - can exhaust resources
    query_engine = index.as_query_engine()  # VULNERABILITY: No token limit
    
    result = query_engine.query(user_input)
    return result


def vulnerable_retriever_query_engine_no_limit(user_input: str):
    """VULNERABLE: RetrieverQueryEngine without max_tokens limit."""
    from llama_index.core.query_engine import RetrieverQueryEngine
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    retriever = index.as_retriever()
    
    # CRITICAL: No token limit
    engine = RetrieverQueryEngine(retriever)  # VULNERABILITY: No token limit
    
    result = engine.query(user_input)
    return result


def vulnerable_index_query_no_limit(user_input: str):
    """VULNERABLE: Index query without max_tokens limit."""
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    # CRITICAL: No token limit
    result = index.query(user_input)  # VULNERABILITY: No token limit
    
    return result


def safe_usage_example(user_input: str):
    """SAFE: Proper token limits in ServiceContext."""
    from llama_index.llms.openai import OpenAI
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    # SAFE: Set max_tokens limit in ServiceContext
    llm = OpenAI(model="gpt-3.5-turbo", max_tokens=100)  # SAFE: Token limit set
    service_context = ServiceContext.from_defaults(llm=llm)
    
    query_engine = index.as_query_engine(service_context=service_context)
    
    result = query_engine.query(user_input)
    return result


def safe_usage_service_context_max_tokens(user_input: str):
    """SAFE: Using ServiceContext.from_defaults with max_tokens."""
    from llama_index.llms.openai import OpenAI
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    # SAFE: ServiceContext with max_tokens
    llm = OpenAI(model="gpt-3.5-turbo")
    service_context = ServiceContext.from_defaults(
        llm=llm,
        max_tokens=100  # SAFE: Token limit in service context
    )
    
    query_engine = index.as_query_engine(service_context=service_context)
    
    result = query_engine.query(user_input)
    return result


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_query_engine_no_token_limit("What is this?")
    vulnerable_retriever_query_engine_no_limit("Query documents")
    vulnerable_index_query_no_limit("Search index")
    safe_usage_example("What is this?")
    safe_usage_service_context_max_tokens("Query data")
