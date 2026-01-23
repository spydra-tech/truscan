"""
Sample vulnerable AWS Bedrock application demonstrating prompt injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

import boto3
import json
import os
from flask import request


def vulnerable_converse_direct_user_input(user_input: str):
    """VULNERABLE: Direct user input in AWS Bedrock Converse API."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # VULNERABILITY: User input directly inserted into prompt
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": user_input}  # CRITICAL: No sanitization
        ]
    )
    
    body = json.loads(response['body'].read())
    return body['output']['message']['content'][0]['text']


def vulnerable_converse_string_concatenation(user_input: str):
    """VULNERABLE: User input concatenated into AWS Bedrock Converse prompt."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # VULNERABILITY: String concatenation in prompt
    prompt = "You are a helpful assistant. Answer this question: " + user_input
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": prompt}  # CRITICAL: Concatenation risk
        ]
    )
    
    body = json.loads(response['body'].read())
    return body['output']['message']['content'][0]['text']


def vulnerable_converse_f_string_injection(user_input: str):
    """VULNERABLE: F-string injection in AWS Bedrock Converse prompt."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # VULNERABILITY: F-string interpolation
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": f"Process this request: {user_input}"}  # CRITICAL: F-string injection
        ]
    )
    
    body = json.loads(response['body'].read())
    return body['output']['message']['content'][0]['text']


def vulnerable_invoke_model_user_input(user_input: str):
    """VULNERABLE: User input in AWS Bedrock InvokeModel API."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # VULNERABILITY: User input directly in InvokeModel body
    body = json.dumps({
        "prompt": user_input  # CRITICAL: No validation
    })
    
    response = bedrock.invoke_model(
        modelId='amazon.titan-text-express-v1',
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['completion']


def vulnerable_invoke_model_concatenation(user_input: str):
    """VULNERABLE: User input concatenated into InvokeModel prompt."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # VULNERABILITY: F-string in InvokeModel body
    prompt = f"Answer this question: {user_input}"
    body = json.dumps({
        "prompt": prompt  # CRITICAL: Concatenation risk
    })
    
    response = bedrock.invoke_model(
        modelId='amazon.titan-text-express-v1',
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['completion']


def vulnerable_bedrock_agent(user_input: str):
    """VULNERABLE: User input in AWS Bedrock Agent invocation (CRITICAL)."""
    agent = boto3.client(
        'bedrock-agent-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # CRITICAL VULNERABILITY: User input in Bedrock Agent
    # Agents can execute tools and access resources
    response = agent.invoke_agent(
        agentId='agent-id-123',
        agentAliasId='alias-id-123',
        inputText=user_input  # CRITICAL: Agent tool execution risk
    )
    
    return response


def vulnerable_flask_request():
    """VULNERABLE: Flask request data in AWS Bedrock prompt."""
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # VULNERABILITY: Request data directly in prompt
    user_query = request.args.get('query')  # From user input
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "user", "content": user_query}  # CRITICAL: No validation
        ]
    )
    
    body = json.loads(response['body'].read())
    return body['output']['message']['content'][0]['text']


def safe_usage_example(user_input: str):
    """SAFE: Proper input validation and sanitization."""
    import html
    
    bedrock = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # SAFE: Input validation and sanitization
    if not user_input or len(user_input) > 1000:
        raise ValueError("Invalid input")
    
    sanitized = html.escape(user_input)
    
    response = bedrock.converse(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Answer this question: {sanitized}"}
        ],
        inferenceConfig={
            "maxTokens": 100  # SAFE: Token limit
        }
    )
    
    body = json.loads(response['body'].read())
    return body['output']['message']['content'][0]['text']


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_converse_direct_user_input("What is 2+2?")
    vulnerable_converse_string_concatenation("Calculate fibonacci")
    vulnerable_converse_f_string_injection("Process this data")
    vulnerable_invoke_model_user_input("What is the weather?")
    vulnerable_invoke_model_concatenation("Analyze this")
    vulnerable_bedrock_agent("Execute this task")
    safe_usage_example("What is the weather?")
