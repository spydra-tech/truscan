"""
Sample vulnerable AWS Bedrock application demonstrating command injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

import boto3
import json
import os
import subprocess


def vulnerable_subprocess_execution(user_request: str):
    """VULNERABLE: AWS Bedrock output passed to subprocess.run()."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"What command should I run to: {user_request}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    command = body['output']['message']['content'][0]['text']
    
    # CRITICAL: Executing LLM output as shell command
    subprocess.run(command, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_os_system(user_action: str):
    """VULNERABLE: AWS Bedrock output passed to os.system()."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Generate shell command for: {user_action}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    cmd = body['output']['message']['content'][0]['text']
    
    # CRITICAL: Shell injection risk
    os.system(cmd)  # VULNERABILITY: Command injection risk


def vulnerable_subprocess_call(task: str):
    """VULNERABLE: AWS Bedrock output passed to subprocess.call()."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Command to execute: {task}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    command = body['output']['message']['content'][0]['text']
    
    # CRITICAL: Command injection risk
    subprocess.call(command, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_subprocess_popen(instruction: str):
    """VULNERABLE: AWS Bedrock output passed to subprocess.Popen()."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Run this: {instruction}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    cmd = body['output']['message']['content'][0]['text']
    
    # CRITICAL: Command injection risk
    subprocess.Popen(cmd, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_invoke_model_to_command(user_request: str):
    """VULNERABLE: InvokeModel output passed to subprocess."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    body = json.dumps({
        "prompt": f"What command should I run to: {user_request}"
    })
    
    response = bedrock.invoke_model(
        modelId='amazon.titan-text-express-v1',
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    command = response_body['completion']
    
    # CRITICAL: Command injection risk
    subprocess.run(command, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and command execution."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": "What command lists files?"}
        ]
    )
    
    # VULNERABILITY: Direct extraction and execution
    body = json.loads(response['body'].read())
    command = body['output']['message']['content'][0]['text']
    subprocess.run(command, shell=True)  # CRITICAL: No validation


def safe_usage_example(user_request: str):
    """SAFE: Proper command validation and parameterization."""
    import shlex
    
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Suggest a safe command for: {user_request}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    suggested_command = body['output']['message']['content'][0]['text']
    
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
    vulnerable_invoke_model_to_command("check directory")
    vulnerable_direct_extraction()
    safe_usage_example("check directory")
