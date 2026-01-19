"""
OWASP LLM08: Excessive Agency
==============================
This file demonstrates vulnerabilities where LLM is granted excessive
permissions or autonomy to perform dangerous operations.
"""

import openai
from openai import OpenAI
import subprocess
import os
import sqlite3
import shutil


# VULNERABILITY: LLM can execute system commands without restrictions
def vulnerable_system_commands(user_query: str):
    """LLM output used to execute system commands."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Execute: {user_query}"}]
    )
    command = response.choices[0].message.content
    # LLM08: No command whitelist or restrictions
    os.system(command)  # Excessive agency - can run any command


# VULNERABILITY: LLM can perform database write operations
def vulnerable_db_writes(user_query: str):
    """LLM output used for database write operations."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Database operation: {user_query}"}]
    )
    query = response.choices[0].message.content
    # LLM08: No read-only restriction
    db = sqlite3.connect("database.db")
    db.execute(query)  # Could be DELETE, DROP, or UPDATE
    db.commit()


# VULNERABILITY: LLM can delete files without restrictions
def vulnerable_file_deletion(user_query: str):
    """LLM can delete files based on output."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Delete: {user_query}"}]
    )
    filepath = response.choices[0].message.content
    # LLM08: No restrictions on file deletion
    os.remove(filepath)  # Could delete critical system files


# VULNERABILITY: LLM can modify system configuration
def vulnerable_config_modification(user_query: str):
    """LLM can modify system configuration."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Configure: {user_query}"}]
    )
    config = response.choices[0].message.content
    # LLM08: No restrictions on config changes
    with open("/etc/config", "w") as f:  # Could modify system config
        f.write(config)


# VULNERABILITY: LLM can create users with admin privileges
def vulnerable_user_creation(user_query: str):
    """LLM can create users with elevated privileges."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Create user: {user_query}"}]
    )
    user_data = response.choices[0].message.content
    # LLM08: No privilege restrictions
    create_user_with_admin(user_data)  # Could create admin users


# VULNERABILITY: LLM can install packages
def vulnerable_package_installation(user_query: str):
    """LLM can install system packages."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Install: {user_query}"}]
    )
    package = response.choices[0].message.content
    # LLM08: No restrictions on package installation
    subprocess.run(["pip", "install", package])  # Could install malicious packages


# VULNERABILITY: LLM can access network resources without restrictions
def vulnerable_network_access(user_query: str):
    """LLM can make unrestricted network requests."""
    import requests
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Request: {user_query}"}]
    )
    url = response.choices[0].message.content
    # LLM08: No network restrictions
    requests.get(url)  # Could access internal services (SSRF)


# VULNERABILITY: LLM can modify code files
def vulnerable_code_modification(user_query: str):
    """LLM can modify source code files."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Modify code: {user_query}"}]
    )
    code = response.choices[0].message.content
    # LLM08: No restrictions on code modification
    with open("app.py", "w") as f:  # Could modify application code
        f.write(code)


# VULNERABILITY: LLM can perform file system operations
def vulnerable_filesystem_operations(user_query: str):
    """LLM can perform unrestricted file system operations."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"File operation: {user_query}"}]
    )
    operation = response.choices[0].message.content
    # LLM08: No restrictions
    shutil.rmtree(operation)  # Could delete entire directories


# VULNERABILITY: LLM can execute arbitrary code
def vulnerable_code_execution(user_query: str):
    """LLM can execute arbitrary code."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Execute code: {user_query}"}]
    )
    code = response.choices[0].message.content
    # LLM08: No sandboxing or restrictions
    exec(code)  # Could execute malicious code


# Helper function (not vulnerable, just for context)
def create_user_with_admin(user_data):
    """Placeholder for user creation with admin privileges."""
    pass
