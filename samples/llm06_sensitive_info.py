"""
OWASP LLM06: Sensitive Information Disclosure
=============================================
This file demonstrates vulnerabilities where sensitive data (secrets, PII,
credentials) are included in prompts or exposed in LLM responses.
"""

import openai
from openai import OpenAI
import os
import logging


# VULNERABILITY: API key included in prompt
def vulnerable_api_key_in_prompt(user_query: str):
    """API key included in LLM prompt."""
    api_key = os.getenv("SECRET_API_KEY")
    # LLM06: Secret in prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Query: {user_query}, API Key: {api_key}"}]
    )
    return response.choices[0].message.content


# VULNERABILITY: Password in prompt
def vulnerable_password_in_prompt(username: str, password: str):
    """Password included in LLM prompt."""
    # LLM06: Credential in prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Login as {username} with password {password}"}]
    )
    return response.choices[0].message.content


# VULNERABILITY: PII in prompt
def vulnerable_pii_in_prompt(user_query: str, ssn: str, credit_card: str):
    """Personally Identifiable Information in prompt."""
    # LLM06: PII in prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"User query: {user_query}, SSN: {ssn}, Credit Card: {credit_card}"
        }]
    )
    return response.choices[0].message.content


# VULNERABILITY: Database credentials in prompt
def vulnerable_db_credentials_in_prompt(query: str):
    """Database credentials included in prompt."""
    db_user = "admin"
    db_password = "secret123"
    # LLM06: Credentials in prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Generate SQL for: {query}. DB: {db_user}/{db_password}"
        }]
    )
    return response.choices[0].message.content


# VULNERABILITY: LLM response logged without sanitization
def vulnerable_log_response(user_query: str):
    """LLM response logged with potential sensitive data."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_query}]
    )
    content = response.choices[0].message.content
    # LLM06: Response logged without sanitization
    logging.info(f"LLM Response: {content}")  # Could contain sensitive data
    return content


# VULNERABILITY: LLM response printed to console
def vulnerable_print_response(user_query: str):
    """LLM response printed to console."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_query}]
    )
    content = response.choices[0].message.content
    # LLM06: Response printed (could be logged)
    print(f"Response: {content}")  # Could expose sensitive data
    return content


# VULNERABILITY: Token/secret in prompt
def vulnerable_token_in_prompt(user_query: str):
    """Authentication token included in prompt."""
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # JWT token
    # LLM06: Token in prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Query: {user_query}, Token: {token}"}]
    )
    return response.choices[0].message.content


# VULNERABILITY: Private key in prompt
def vulnerable_private_key_in_prompt(user_query: str):
    """Private key included in prompt."""
    private_key = "-----BEGIN RSA PRIVATE KEY-----\n..."
    # LLM06: Private key in prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Query: {user_query}, Key: {private_key}"}]
    )
    return response.choices[0].message.content


# VULNERABILITY: Environment variables with secrets in prompt
def vulnerable_env_vars_in_prompt(user_query: str):
    """Environment variables with secrets in prompt."""
    # LLM06: Secrets from environment
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Query: {user_query}, Config: {os.environ}"
        }]
    )
    return response.choices[0].message.content


# VULNERABILITY: User data with PII in prompt
def vulnerable_user_data_in_prompt(user_query: str, user_data: dict):
    """User data dictionary with PII in prompt."""
    # LLM06: PII in prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Query: {user_query}, User Data: {user_data}"
        }]
    )
    return response.choices[0].message.content
