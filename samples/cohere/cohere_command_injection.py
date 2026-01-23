"""
Sample vulnerable Cohere application demonstrating command injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

import cohere
import os
import subprocess


def vulnerable_chat_to_subprocess(user_request: str):
    """VULNERABLE: Cohere chat output passed to subprocess.run()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"What command should I run to: {user_request}"}
        ]
    )
    
    command = response.text
    
    # CRITICAL: Executing LLM output as shell command
    subprocess.run(command, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_chat_to_os_system(user_action: str):
    """VULNERABLE: Cohere chat output passed to os.system()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Generate shell command for: {user_action}"}
        ]
    )
    
    cmd = response.text
    
    # CRITICAL: Shell injection risk
    os.system(cmd)  # VULNERABILITY: Command injection risk


def vulnerable_chat_to_subprocess_call(task: str):
    """VULNERABLE: Cohere chat output passed to subprocess.call()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Command to execute: {task}"}
        ]
    )
    
    command = response.text
    
    # CRITICAL: Command injection risk
    subprocess.call(command, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_chat_to_subprocess_popen(instruction: str):
    """VULNERABLE: Cohere chat output passed to subprocess.Popen()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Run this: {instruction}"}
        ]
    )
    
    cmd = response.text
    
    # CRITICAL: Command injection risk
    subprocess.Popen(cmd, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_chat_message_content_to_command(user_request: str):
    """VULNERABLE: Cohere chat message.content to command execution."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"What command should I run: {user_request}"}
        ]
    )
    
    command = response.message.content
    subprocess.run(command, shell=True)  # CRITICAL: Command injection risk


def vulnerable_generate_to_subprocess(user_request: str):
    """VULNERABLE: Cohere generate output passed to subprocess."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.generate(
        prompt=f"What command should I run to: {user_request}"
    )
    
    command = response.generations[0].text
    subprocess.run(command, shell=True)  # CRITICAL: Command injection risk


def vulnerable_generate_to_os_system(user_action: str):
    """VULNERABLE: Cohere generate output passed to os.system()."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.generate(
        prompt=f"Generate shell command for: {user_action}"
    )
    
    cmd = response.generations[0].text
    os.system(cmd)  # CRITICAL: Command injection risk


def vulnerable_clientv2_chat_to_command(user_request: str):
    """VULNERABLE: ClientV2 chat output to command execution."""
    client = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"What command: {user_request}"}
        ]
    )
    
    command = response.text
    subprocess.run(command, shell=True)  # CRITICAL: Command injection risk


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and command execution."""
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": "What command lists files?"}
        ]
    )
    
    # VULNERABILITY: Direct extraction and execution
    command = response.text
    subprocess.run(command, shell=True)  # CRITICAL: No validation


def safe_usage_example(user_request: str):
    """SAFE: Proper command validation and parameterization."""
    import shlex
    
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    
    response = client.chat(
        messages=[
            {"role": "user", "content": f"Suggest a safe command for: {user_request}"}
        ]
    )
    
    suggested_command = response.text
    
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
    vulnerable_chat_to_subprocess("list files")
    vulnerable_chat_to_os_system("backup data")
    vulnerable_chat_to_subprocess_call("process files")
    vulnerable_chat_to_subprocess_popen("analyze logs")
    vulnerable_chat_message_content_to_command("check directory")
    vulnerable_generate_to_subprocess("list directory")
    vulnerable_generate_to_os_system("backup files")
    vulnerable_clientv2_chat_to_command("execute task")
    vulnerable_direct_extraction()
    safe_usage_example("check directory")
