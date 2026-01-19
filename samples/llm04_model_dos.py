"""
OWASP LLM04: Model Denial of Service
====================================
This file demonstrates vulnerabilities that can lead to resource exhaustion
through excessive token usage, long prompts, or rapid API calls.
"""

import openai
from openai import OpenAI
from anthropic import Anthropic
import time


# VULNERABILITY: No rate limiting on LLM API calls
def vulnerable_no_rate_limit(user_input: str):
    """LLM API call without rate limiting."""
    # LLM04: No rate limiting protection
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}]
    )
    return response.choices[0].message.content


# VULNERABILITY: No max_tokens limit set
def vulnerable_no_token_limit(user_input: str):
    """LLM API call without max_tokens limit."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}]
        # LLM04: Missing max_tokens parameter
    )
    return response.choices[0].message.content


# VULNERABILITY: Rapid API calls in loop without throttling
def vulnerable_rapid_calls(queries: list):
    """Multiple LLM calls without rate limiting."""
    results = []
    for query in queries:  # LLM04: No throttling
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}]
        )
        results.append(response.choices[0].message.content)
    return results


# VULNERABILITY: Very long prompt without size limit
def vulnerable_long_prompt(user_input: str):
    """LLM call with potentially unlimited prompt size."""
    # LLM04: No prompt size validation
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input * 10000}]  # Could be huge
    )
    return response.choices[0].message.content


# VULNERABILITY: Recursive LLM calls without depth limit
def vulnerable_recursive_call(query: str, depth: int = 0):
    """Recursive LLM calls that could exhaust resources."""
    if depth > 100:  # LLM04: High limit, but no early termination
        return "Max depth reached"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}]
    )
    result = response.choices[0].message.content
    
    # Recursive call without proper resource limits
    return vulnerable_recursive_call(result, depth + 1)


# VULNERABILITY: Batch processing without concurrency limits
def vulnerable_batch_process(queries: list):
    """Batch processing without concurrency control."""
    import concurrent.futures
    
    def process_query(query):
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}]
        )
    
    # LLM04: Unlimited concurrent requests
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_query, queries))
    return results


# VULNERABILITY: OpenAI v1 client without limits
def vulnerable_v1_client(user_input: str):
    """OpenAI v1 client without max_tokens."""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_input}]
        # LLM04: Missing max_tokens
    )
    return response.choices[0].message.content


# VULNERABILITY: Anthropic API without limits
def vulnerable_anthropic(user_input: str):
    """Anthropic API without max_tokens."""
    client = Anthropic()
    response = client.messages.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": user_input}]
        # LLM04: Missing max_tokens
    )
    return response.content[0].text


# VULNERABILITY: No timeout on LLM API calls
def vulnerable_no_timeout(user_input: str):
    """LLM API call without timeout."""
    # LLM04: Could hang indefinitely
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}],
        timeout=None  # No timeout protection
    )
    return response.choices[0].message.content
