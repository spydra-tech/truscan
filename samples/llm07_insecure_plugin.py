"""
OWASP LLM07: Insecure Plugin Design
====================================
This file demonstrates vulnerabilities where plugins or tools executed
by LLM lack proper authorization, validation, or sandboxing.
"""

import openai
from openai import OpenAI
import subprocess
import os
import sqlite3


# VULNERABILITY: LLM output used to execute actions without authorization
def vulnerable_execute_action(user_query: str):
    """Execute action based on LLM output without authorization."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"What action should I take: {user_query}"}]
    )
    action = response.choices[0].message.content
    # LLM07: No authorization check
    execute_action(action)  # Could be dangerous action


# VULNERABILITY: File operations without path validation
def vulnerable_file_operation(user_query: str):
    """File operation based on LLM output without path validation."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Save file: {user_query}"}]
    )
    filename = response.choices[0].message.content
    # LLM07: No path validation or whitelist
    with open(filename, 'w') as f:  # Path traversal risk
        f.write("data")


# VULNERABILITY: Database operations without authorization
def vulnerable_db_operation(user_query: str):
    """Database operation based on LLM output."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Database operation: {user_query}"}]
    )
    operation = response.choices[0].message.content
    # LLM07: No authorization or validation
    db = sqlite3.connect("database.db")
    db.execute(operation)  # Could be DELETE or DROP


# VULNERABILITY: System command execution without restrictions
def vulnerable_system_command(user_query: str):
    """System command based on LLM output."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Run command: {user_query}"}]
    )
    command = response.choices[0].message.content
    # LLM07: No command whitelist
    os.system(command)  # Could be rm -rf /


# VULNERABILITY: Network request without validation
def vulnerable_network_request(user_query: str):
    """Network request based on LLM output."""
    import requests
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Make request to: {user_query}"}]
    )
    url = response.choices[0].message.content
    # LLM07: No URL validation or whitelist
    requests.get(url)  # SSRF risk


# VULNERABILITY: Plugin execution without sandboxing
def vulnerable_plugin_execution(user_query: str):
    """Execute plugin code from LLM output."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Create plugin: {user_query}"}]
    )
    plugin_code = response.choices[0].message.content
    # LLM07: No sandboxing
    exec(plugin_code)  # Runs with full privileges


# VULNERABILITY: File deletion without authorization
def vulnerable_file_deletion(user_query: str):
    """Delete file based on LLM output."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Delete file: {user_query}"}]
    )
    filename = response.choices[0].message.content
    # LLM07: No authorization check
    os.remove(filename)  # Could delete critical files


# VULNERABILITY: User creation without permission check
def vulnerable_user_creation(user_query: str):
    """Create user based on LLM output."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Create user: {user_query}"}]
    )
    user_data = response.choices[0].message.content
    # LLM07: No permission check
    create_user(user_data)  # Could create admin users


# VULNERABILITY: Configuration change without validation
def vulnerable_config_change(user_query: str):
    """Change configuration based on LLM output."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Change config: {user_query}"}]
    )
    config = response.choices[0].message.content
    # LLM07: No validation
    update_config(config)  # Could break system


# Helper functions (not vulnerable, just for context)
def execute_action(action):
    """Placeholder for action execution."""
    pass


def create_user(user_data):
    """Placeholder for user creation."""
    pass


def update_config(config):
    """Placeholder for config update."""
    pass
