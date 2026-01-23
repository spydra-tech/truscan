"""
OWASP LLM09: Overreliance
==========================
This file demonstrates vulnerabilities where LLM output is blindly trusted
without validation, verification, or human oversight.
"""

import openai
from openai import OpenAI
import json


# VULNERABILITY: LLM output returned without validation
def vulnerable_no_validation(user_query: str):
    """LLM output returned without any validation."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_query}]
    )
    result = response.choices[0].message.content
    # LLM09: No validation
    return result  # Could be incorrect or malicious


# VULNERABILITY: Critical decision based solely on LLM output
def vulnerable_critical_decision(user_query: str):
    """Critical decision made based solely on LLM output."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Should I approve this transaction: {user_query}"}]
    )
    decision = response.choices[0].message.content
    # LLM09: No human oversight
    if decision.lower() == "approve":
        approve_transaction(user_query)  # CRITICAL: No human approval


# VULNERABILITY: Medical diagnosis without verification
def vulnerable_medical_diagnosis(symptoms: str):
    """Medical diagnosis based solely on LLM output."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Diagnose: {symptoms}"}]
    )
    diagnosis = response.choices[0].message.content
    # LLM09: No medical professional verification
    return diagnosis  # Should require doctor verification


# VULNERABILITY: Financial calculation without verification
def vulnerable_financial_calculation(transaction: dict):
    """Financial calculation based solely on LLM output."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Calculate tax for: {transaction}"}]
    )
    tax_amount = response.choices[0].message.content
    # LLM09: No verification or audit
    return float(tax_amount)  # Could be incorrect


# VULNERABILITY: Legal advice without disclaimers
def vulnerable_legal_advice(question: str):
    """Legal advice based solely on LLM output."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Legal question: {question}"}]
    )
    advice = response.choices[0].message.content
    # LLM09: No lawyer verification
    return advice  # Should require legal professional review


# VULNERABILITY: Code generation without review
def vulnerable_code_generation(requirement: str):
    """Code generated and used without review."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Generate code: {requirement}"}]
    )
    code = response.choices[0].message.content
    # LLM09: No code review
    exec(code)  # Could contain vulnerabilities


# VULNERABILITY: Data extraction without validation
def vulnerable_data_extraction(text: str):
    """Data extracted from LLM output without validation."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Extract email addresses from: {text}"}]
    )
    emails = response.choices[0].message.content
    # LLM09: No validation of extracted data
    return emails.split(",")  # Could be incorrect


# VULNERABILITY: Translation without human review
def vulnerable_translation(text: str, target_lang: str):
    """Translation used without human review."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Translate to {target_lang}: {text}"}]
    )
    translation = response.choices[0].message.content
    # LLM09: No human review for critical translations
    return translation  # Could be incorrect for important content


# VULNERABILITY: JSON parsing without schema validation
def vulnerable_json_parsing(user_query: str):
    """JSON parsed from LLM output without schema validation."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Return JSON for: {user_query}"}]
    )
    json_str = response.choices[0].message.content
    # LLM09: No schema validation
    return json.loads(json_str)  # Could be malformed or incorrect structure


# VULNERABILITY: Factual information without verification
def vulnerable_factual_info(question: str):
    """Factual information returned without verification."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}]
    )
    answer = response.choices[0].message.content
    # LLM09: No fact-checking
    return answer  # Could be hallucinated or incorrect


# Helper function (not vulnerable, just for context)
def approve_transaction(transaction_data):
    """Placeholder for transaction approval."""
    pass
