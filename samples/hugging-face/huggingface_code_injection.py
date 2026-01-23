"""
Sample vulnerable Hugging Face application demonstrating code injection vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from transformers import pipeline, TextGenerationPipeline


def vulnerable_pipeline_to_eval(user_input: str):
    """VULNERABLE: Pipeline output passed to eval()."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(f"Generate Python code for: {user_input}")
    
    code = response[0]["generated_text"]
    
    # CRITICAL: Executing untrusted LLM output
    eval(code)  # VULNERABILITY: Code injection risk


def vulnerable_pipeline_to_exec(task: str):
    """VULNERABLE: Pipeline output passed to exec()."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(f"Write Python code to: {task}")
    
    code_str = response[0]["generated_text"]
    
    # CRITICAL: Executing untrusted code
    exec(code_str)  # VULNERABILITY: Code injection risk


def vulnerable_pipeline_to_compile(description: str):
    """VULNERABLE: Pipeline output passed to compile()."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe(f"Generate code for: {description}")
    
    code = response[0]["generated_text"]
    
    # CRITICAL: Compiling untrusted code
    compile(code, "<string>", "exec")  # VULNERABILITY: Code injection risk


def vulnerable_text_generation_pipeline(user_input: str):
    """VULNERABLE: TextGenerationPipeline output to eval()."""
    pipe = TextGenerationPipeline(model="gpt2", tokenizer="gpt2")
    response = pipe(f"Generate Python code: {user_input}")
    
    code = response[0]["generated_text"]
    eval(code)  # CRITICAL: Code injection risk


def vulnerable_direct_extraction():
    """VULNERABLE: Direct extraction and execution pattern."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe("Generate a Python function")
    
    # VULNERABILITY: Direct extraction and execution
    code = response[0]["generated_text"]
    eval(code)  # CRITICAL: No validation


def vulnerable_pipeline_variable_pattern():
    """VULNERABLE: Pipeline assigned to variable, output to eval()."""
    pipe = pipeline("text-generation", model="gpt2")
    response = pipe("Create Python code")
    
    code = response[0]["generated_text"]
    eval(code)  # CRITICAL: Code injection risk


def safe_usage_example(user_input: str):
    """SAFE: Proper validation and safe parsing."""
    import json
    import ast
    
    pipe = pipeline("text-generation", model="gpt2", max_length=100)
    response = pipe(f"Generate JSON data for: {user_input}")
    
    output_text = response[0]["generated_text"]
    
    # SAFE: Parse JSON instead of executing code
    try:
        # Try to extract JSON from output
        data = json.loads(output_text)
        # Validate and use data safely
        return data
    except json.JSONDecodeError:
        # SAFE: Fallback - don't execute code
        raise ValueError("Invalid JSON response")


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_pipeline_to_eval("calculate fibonacci")
    vulnerable_pipeline_to_exec("process data")
    vulnerable_pipeline_to_compile("analyze dataset")
    vulnerable_text_generation_pipeline("create function")
    vulnerable_direct_extraction()
    vulnerable_pipeline_variable_pattern()
    safe_usage_example("user preferences")
