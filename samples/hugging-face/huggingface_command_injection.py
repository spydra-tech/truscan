"""
Sample vulnerable Hugging Face application demonstrating command injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from transformers import pipeline, TextGenerationPipeline
import subprocess
import os


def vulnerable_pipeline_to_subprocess(user_request: str):
    """VULNERABLE: Pipeline output passed to subprocess.run()."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(f"What command should I run to: {user_request}")
    
    command = response[0]["generated_text"]
    
    # CRITICAL: Executing LLM output as shell command
    subprocess.run(command, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_pipeline_to_os_system(user_action: str):
    """VULNERABLE: Pipeline output passed to os.system()."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(f"Generate shell command for: {user_action}")
    
    cmd = response[0]["generated_text"]
    
    # CRITICAL: Shell injection risk
    os.system(cmd)  # VULNERABILITY: Command injection risk


def vulnerable_pipeline_to_subprocess_call(task: str):
    """VULNERABLE: Pipeline output passed to subprocess.call()."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(f"Command to execute: {task}")
    
    command = response[0]["generated_text"]
    
    # CRITICAL: Command injection risk
    subprocess.call(command, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_pipeline_to_subprocess_popen(instruction: str):
    """VULNERABLE: Pipeline output passed to subprocess.Popen()."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(f"Run this: {instruction}")
    
    cmd = response[0]["generated_text"]
    
    # CRITICAL: Command injection risk
    subprocess.Popen(cmd, shell=True)  # VULNERABILITY: Command injection risk


def vulnerable_text_generation_pipeline_to_command(user_request: str):
    """VULNERABLE: TextGenerationPipeline output to subprocess."""
    pipe = TextGenerationPipeline(model="gpt2", tokenizer="gpt2")
    response = pipe(f"What command should I run: {user_request}")
    
    command = response[0]["generated_text"]
    subprocess.run(command, shell=True)  # CRITICAL: Command injection risk


def vulnerable_question_answering_pipeline_to_command(user_query: str):
    """VULNERABLE: QuestionAnsweringPipeline output to command."""
    pipe = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
    response = pipe(user_query)
    
    command = response["answer"]
    os.system(command)  # CRITICAL: Command injection risk


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and command execution."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe("What command lists files?")
    
    # VULNERABILITY: Direct extraction and execution
    command = response[0]["generated_text"]
    subprocess.run(command, shell=True)  # CRITICAL: No validation


def safe_usage_example(user_request: str):
    """SAFE: Proper command validation and parameterization."""
    import shlex
    
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(f"Suggest a safe command for: {user_request}")
    
    suggested_command = response[0]["generated_text"]
    
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
    vulnerable_pipeline_to_subprocess("list files")
    vulnerable_pipeline_to_os_system("backup data")
    vulnerable_pipeline_to_subprocess_call("process files")
    vulnerable_pipeline_to_subprocess_popen("analyze logs")
    vulnerable_text_generation_pipeline_to_command("check directory")
    vulnerable_question_answering_pipeline_to_command("What command?")
    vulnerable_direct_extraction()
    safe_usage_example("check directory")
