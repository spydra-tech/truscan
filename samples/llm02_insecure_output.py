"""
OWASP LLM02: Insecure Output Handling
=======================================
This file demonstrates insecure handling of LLM output, leading to
code injection, command injection, and XSS vulnerabilities.
"""

import openai
from openai import OpenAI
import subprocess
import os
from flask import render_template_string


# VULNERABILITY: LLM output passed to eval()
def vulnerable_code_execution(user_query: str):
    """LLM output executed as code."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Generate Python code for: {user_query}"}]
    )
    code = response.choices[0].message.content  # LLM02: Untrusted output
    eval(code)  # CRITICAL: Code injection


# VULNERABILITY: LLM output passed to exec()
def vulnerable_exec(user_query: str):
    """LLM output executed with exec()."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Write code to: {user_query}"}]
    )
    code = response.choices[0].message.content
    exec(code)  # LLM02: Code injection


# VULNERABILITY: LLM output passed to compile()
def vulnerable_compile(user_query: str):
    """LLM output compiled and executed."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Create a function to: {user_query}"}]
    )
    code = response.choices[0].message.content
    compiled_code = compile(code, '<string>', 'exec')  # LLM02: Code injection
    exec(compiled_code)


# VULNERABILITY: LLM output passed to subprocess.run()
def vulnerable_subprocess(user_query: str):
    """LLM output used as shell command."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"What command should I run to: {user_query}"}]
    )
    command = response.choices[0].message.content
    subprocess.run(command, shell=True)  # LLM02: Command injection


# VULNERABILITY: LLM output passed to os.system()
def vulnerable_os_system(user_query: str):
    """LLM output used with os.system()."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Run command to: {user_query}"}]
    )
    command = response.choices[0].message.content
    os.system(command)  # LLM02: Command injection


# VULNERABILITY: LLM output rendered in HTML without escaping (XSS)
def vulnerable_html_render(user_query: str):
    """LLM output rendered in HTML template."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_query}]
    )
    content = response.choices[0].message.content
    # LLM02: XSS - content not escaped
    return render_template_string("<div>{{ content }}</div>", content=content)


# VULNERABILITY: LLM output used in SQL query
def vulnerable_sql_query(user_query: str):
    """LLM output used in SQL query."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Generate SQL query for: {user_query}"}]
    )
    query = response.choices[0].message.content
    # LLM02: SQL injection risk
    db.execute(query)  # Assuming db object exists


# VULNERABILITY: LLM output used in file path
def vulnerable_file_operation(user_query: str):
    """LLM output used for file operations."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Save to file: {user_query}"}]
    )
    filename = response.choices[0].message.content
    with open(filename, 'w') as f:  # LLM02: Path traversal risk
        f.write("data")


# VULNERABILITY: LLM output used in URL
def vulnerable_url_request(user_query: str):
    """LLM output used as URL."""
    import requests
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Fetch from URL: {user_query}"}]
    )
    url = response.choices[0].message.content
    requests.get(url)  # LLM02: SSRF risk
