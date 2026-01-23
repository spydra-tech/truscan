"""
Sample vulnerable AWS Bedrock application demonstrating code injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

import boto3
import json
import os


def vulnerable_eval_execution(user_input: str):
    """VULNERABLE: AWS Bedrock output passed to eval()."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Generate Python code for: {user_input}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    code = body['output']['message']['content'][0]['text']
    
    # CRITICAL: Executing untrusted LLM output
    eval(code)  # VULNERABILITY: Code injection risk


def vulnerable_exec_execution(task: str):
    """VULNERABLE: AWS Bedrock output passed to exec()."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Write Python code to: {task}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    code_str = body['output']['message']['content'][0]['text']
    
    # CRITICAL: Executing untrusted code
    exec(code_str)  # VULNERABILITY: Code injection risk


def vulnerable_compile_execution(description: str):
    """VULNERABLE: AWS Bedrock output passed to compile()."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Generate code for: {description}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    code = body['output']['message']['content'][0]['text']
    
    # CRITICAL: Compiling untrusted code
    compile(code, "<string>", "exec")  # VULNERABILITY: Code injection risk


def vulnerable_invoke_model_to_eval(user_input: str):
    """VULNERABLE: InvokeModel output passed to eval()."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    body = json.dumps({
        "prompt": f"Generate Python code for: {user_input}"
    })
    
    response = bedrock.invoke_model(
        modelId='amazon.titan-text-express-v1',
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    code = response_body['completion']
    
    # CRITICAL: Executing untrusted LLM output
    eval(code)  # VULNERABILITY: Code injection risk


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and execution pattern."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": "Generate a Python function"}
        ]
    )
    
    # VULNERABILITY: Direct extraction and execution
    body = json.loads(response['body'].read())
    code = body['output']['message']['content'][0]['text']
    eval(code)  # CRITICAL: No validation


def safe_usage_example(user_input: str):
    """SAFE: Proper validation and safe parsing."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Generate JSON data for: {user_input}"}
        ]
    )
    
    body = json.loads(response['body'].read())
    output_text = body['output']['message']['content'][0]['text']
    
    # SAFE: Parse JSON instead of executing code
    try:
        data = json.loads(output_text)
        # Validate and use data safely
        return data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON response")


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_eval_execution("calculate fibonacci")
    vulnerable_exec_execution("process data")
    vulnerable_compile_execution("analyze dataset")
    vulnerable_invoke_model_to_eval("create function")
    vulnerable_direct_extraction()
    safe_usage_example("user preferences")
