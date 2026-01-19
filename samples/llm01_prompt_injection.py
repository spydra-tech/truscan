"""
OWASP LLM01: Prompt Injection
================================
This file demonstrates prompt injection vulnerabilities where user input
is directly inserted into LLM prompts without sanitization.
"""

import openai
from openai import OpenAI
from anthropic import Anthropic
from flask import request


# VULNERABILITY: Direct user input in prompt without sanitization
def vulnerable_chat_1(user_input: str):
    """User input directly passed to LLM prompt."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}]  # LLM01: No sanitization
    )
    return response.choices[0].message.content


# VULNERABILITY: String concatenation in prompt
def vulnerable_chat_2(user_input: str):
    """User input concatenated into prompt."""
    prompt = f"Answer this question: {user_input}"  # LLM01: Concatenation
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# VULNERABILITY: F-string with user input
def vulnerable_chat_3(user_input: str):
    """User input in f-string prompt."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Process: {user_input}"}]  # LLM01: F-string
    )
    return response.choices[0].message.content


# VULNERABILITY: OpenAI v1 client with direct input
def vulnerable_chat_4(user_input: str):
    """OpenAI v1 client with unsanitized input."""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_input}]  # LLM01: Direct input
    )
    return response.choices[0].message.content


# VULNERABILITY: Anthropic API with direct input
def vulnerable_chat_5(user_input: str):
    """Anthropic API with unsanitized input."""
    client = Anthropic()
    response = client.messages.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": user_input}]  # LLM01: Direct input
    )
    return response.content[0].text


# VULNERABILITY: Flask request data directly in prompt
def vulnerable_api_endpoint():
    """Flask endpoint with request data in prompt."""
    user_query = request.json.get('query')  # From untrusted source
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_query}]  # LLM01: Request data
    )
    return {"response": response.choices[0].message.content}


# VULNERABILITY: System prompt injection via user input
def vulnerable_system_prompt(user_input: str):
    """System prompt with user input."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant. User says: {user_input}"},  # LLM01
            {"role": "user", "content": "What is 2+2?"}
        ]
    )
    return response.choices[0].message.content


# VULNERABILITY: Multi-turn conversation with unsanitized input
def vulnerable_conversation(user_messages: list):
    """Conversation with unsanitized messages."""
    messages = [{"role": "user", "content": msg} for msg in user_messages]  # LLM01: No validation
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content
