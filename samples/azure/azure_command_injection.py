"""
Sample vulnerable Azure OpenAI Service application demonstrating command injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from openai import AzureOpenAI
import os
import subprocess


def vulnerable_subprocess_execution(user_request: str):
    """VULNERABLE: Azure OpenAI output passed to subprocess.run()."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"What command should I run to: {user_request}"}
        ]
    )
    
    command = response.choices[0].message.content
    
    # CRITICAL: Executing LLM output as shell command
    subprocess.run(command, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_os_system(user_action: str):
    """VULNERABLE: Azure OpenAI output passed to os.system()."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Generate shell command for: {user_action}"}
        ]
    )
    
    cmd = response.choices[0].message.content
    
    # CRITICAL: Shell injection risk
    os.system(cmd)  # VULNERABILITY: Command injection risk


def vulnerable_subprocess_call(task: str):
    """VULNERABLE: Azure OpenAI output passed to subprocess.call()."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Command to execute: {task}"}
        ]
    )
    
    command = response.choices[0].message.content
    
    # CRITICAL: Command injection risk
    subprocess.call(command, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_subprocess_popen(instruction: str):
    """VULNERABLE: Azure OpenAI output passed to subprocess.Popen()."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Run this: {instruction}"}
        ]
    )
    
    cmd = response.choices[0].message.content
    
    # CRITICAL: Command injection risk
    subprocess.Popen(cmd, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and command execution."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": "What command lists files?"}
        ]
    )
    
    # VULNERABILITY: Direct extraction and execution
    command = response.choices[0].message.content
    subprocess.run(command, shell=True)  # CRITICAL: No validation


def safe_usage_example(user_request: str):
    """SAFE: Proper command validation and parameterization."""
    import shlex
    
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15"
    )
    
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "user", "content": f"Suggest a safe command for: {user_request}"}
        ]
    )
    
    suggested_command = response.choices[0].message.content
    
    # SAFE: Validate against allowlist instead of executing
    ALLOWED_COMMANDS = ['ls', 'pwd', 'date']
    
    # Parse and validate
    parts = shlex.split(suggested_command)
    if parts and parts[0] in ALLOWED_COMMANDS:
        # SAFE: Use parameterized subprocess call
        subprocess.run(parts, shell=False)  # SAFE: No shell, parameterized
    else:
        raise ValueError(f"Command not allowed: {suggested_command}")


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_subprocess_execution("list files")
    vulnerable_os_system("backup data")
    vulnerable_subprocess_call("process files")
    vulnerable_subprocess_popen("analyze logs")
    vulnerable_direct_extraction()
    safe_usage_example("check directory")
