"""
Sample vulnerable LlamaIndex application demonstrating prompt injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import ServiceContext
from flask import request


def vulnerable_query_engine_user_input(user_input: str):
    """VULNERABLE: Query engine with user input."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    # VULNERABILITY: User input directly in query
    result = query_engine.query(user_input)  # CRITICAL: Prompt injection risk
    
    return result


def vulnerable_query_engine_retrieve(user_input: str):
    """VULNERABLE: Query engine.retrieve() with user input."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    # VULNERABILITY: User input in retrieve
    result = query_engine.retrieve(user_input)  # CRITICAL: Prompt injection risk
    
    return result


def vulnerable_index_as_query_engine(user_input: str):
    """VULNERABLE: Index.as_query_engine().query() with user input."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    # VULNERABILITY: User input in index query
    result = index.as_query_engine().query(user_input)  # CRITICAL: Prompt injection risk
    
    return result


def vulnerable_retriever_query_engine(user_input: str):
    """VULNERABLE: RetrieverQueryEngine with user input."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    retriever = index.as_retriever()
    engine = RetrieverQueryEngine(retriever)
    
    # VULNERABILITY: User input in query
    result = engine.query(user_input)  # CRITICAL: Prompt injection risk
    
    return result


def vulnerable_vector_store_query(user_input: str):
    """VULNERABLE: Vector store query with user input."""
    from llama_index.core.vector_stores import SimpleVectorStore
    
    vector_store = SimpleVectorStore()
    
    # VULNERABILITY: User input in vector store query
    result = vector_store.query(user_input)  # CRITICAL: Prompt injection risk
    
    return result


def vulnerable_vector_store_retrieve(user_input: str):
    """VULNERABLE: Vector store retrieve with user input."""
    from llama_index.core.vector_stores import SimpleVectorStore
    
    vector_store = SimpleVectorStore()
    
    # VULNERABILITY: User input in retrieve
    result = vector_store.retrieve(user_input)  # CRITICAL: Prompt injection risk
    
    return result


def vulnerable_vector_store_similarity_search(user_input: str):
    """VULNERABLE: Vector store similarity_search with user input."""
    from llama_index.core.vector_stores import SimpleVectorStore
    
    vector_store = SimpleVectorStore()
    
    # VULNERABILITY: User input in similarity search
    result = vector_store.similarity_search(user_input)  # CRITICAL: Prompt injection risk
    
    return result


def vulnerable_service_context_user_input(user_input: str):
    """VULNERABLE: ServiceContext with user-controlled LLM config."""
    from llama_index.llms.openai import OpenAI
    
    # VULNERABILITY: User input in LLM configuration
    llm = OpenAI(model=user_input)  # CRITICAL: User-controlled model
    service_context = ServiceContext.from_defaults(llm=llm)  # VULNERABILITY: Service context injection
    
    return service_context


def vulnerable_query_results_to_prompt(user_input: str):
    """VULNERABLE: Query results flow into LLM prompts."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    from openai import OpenAI
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    # Query with user input
    query_result = query_engine.query(user_input)
    
    # CRITICAL: Query results in prompt without sanitization
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Summarize: {str(query_result)}"}  # VULNERABILITY: Indirect prompt injection
        ]
    )
    
    return response.choices[0].message.content


def vulnerable_flask_request():
    """VULNERABLE: Flask request data in query engine."""
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    # VULNERABILITY: Request data directly in query
    user_query = request.args.get('query')  # From user input
    result = query_engine.query(user_query)  # CRITICAL: No validation
    
    return result


def safe_usage_example(user_input: str):
    """SAFE: Proper input validation and sanitization."""
    import html
    
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    
    # SAFE: Input validation
    if not user_input or len(user_input) > 1000:
        raise ValueError("Invalid input")
    
    sanitized = html.escape(user_input)
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    result = query_engine.query(sanitized)
    
    # SAFE: Sanitize results before using in prompts
    sanitized_result = html.escape(str(result))
    
    return sanitized_result


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_query_engine_user_input("What is this?")
    vulnerable_query_engine_retrieve("Retrieve data")
    vulnerable_index_as_query_engine("Query index")
    vulnerable_retriever_query_engine("Search documents")
    vulnerable_vector_store_query("Find similar")
    vulnerable_vector_store_retrieve("Get vectors")
    vulnerable_vector_store_similarity_search("Similar items")
    vulnerable_service_context_user_input("gpt-4")
    vulnerable_query_results_to_prompt("Summarize documents")
    safe_usage_example("What is the weather?")
