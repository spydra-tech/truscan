"""
Sample vulnerable Hugging Face application demonstrating model denial of service vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from transformers import pipeline, TextGenerationPipeline, AutoModelForCausalLM, AutoTokenizer


def vulnerable_pipeline_no_token_limit():
    """VULNERABLE: Text generation pipeline without max_length or max_new_tokens."""
    # CRITICAL: No token limit - can exhaust resources
    pipe = pipeline("text-generation", model="gpt2")  # VULNERABILITY: No token limit
    
    result = pipe("Generate a long story")
    return result[0]["generated_text"]


def vulnerable_pipeline_text2text_no_limit():
    """VULNERABLE: Text2text generation pipeline without token limit."""
    # CRITICAL: No token limit
    pipe = pipeline("text2text-generation", model="t5-small")  # VULNERABILITY: No token limit
    
    result = pipe("Translate this very long text")
    return result[0]["generated_text"]


def vulnerable_text_generation_pipeline_no_limit():
    """VULNERABLE: TextGenerationPipeline without token limit."""
    # CRITICAL: No token limit
    pipe = TextGenerationPipeline(model="gpt2", tokenizer="gpt2")  # VULNERABILITY: No token limit
    
    result = pipe("Generate text")
    return result[0]["generated_text"]


def vulnerable_model_generate_no_limit():
    """VULNERABLE: Model.generate() without max_length or max_new_tokens."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    # CRITICAL: Model generation without token limit
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    inputs = tokenizer("Generate text", return_tensors="pt")
    outputs = model.generate(inputs.input_ids)  # VULNERABILITY: No token limit
    
    return tokenizer.decode(outputs[0])


def vulnerable_model_call_no_limit():
    """VULNERABLE: Model(**inputs) without max_length or max_new_tokens."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    # CRITICAL: Model call without token limit
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    inputs = tokenizer("Generate text", return_tensors="pt")
    outputs = model(**inputs)  # VULNERABILITY: No token limit in generation
    
    return outputs


def safe_usage_example():
    """SAFE: Proper token limits and rate limiting."""
    # SAFE: Pipeline with token limit
    pipe = pipeline(
        "text-generation",
        model="gpt2",
        max_length=100  # SAFE: Token limit set
    )
    
    result = pipe("Generate a short story", max_length=100)  # SAFE: Additional limit
    return result[0]["generated_text"]


def safe_usage_max_new_tokens():
    """SAFE: Using max_new_tokens instead of max_length."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    # SAFE: Model generation with max_new_tokens
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    inputs = tokenizer("Generate text", return_tensors="pt")
    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=50  # SAFE: Token limit set
    )
    
    return tokenizer.decode(outputs[0])


def safe_usage_both_limits():
    """SAFE: Using both max_length and max_new_tokens."""
    # SAFE: Pipeline with both limits
    pipe = pipeline(
        "text-generation",
        model="gpt2",
        max_length=200,  # SAFE: Total length limit
        max_new_tokens=50  # SAFE: New tokens limit
    )
    
    result = pipe("Generate text")
    return result[0]["generated_text"]


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_pipeline_no_token_limit()
    vulnerable_pipeline_text2text_no_limit()
    vulnerable_text_generation_pipeline_no_limit()
    # vulnerable_model_generate_no_limit()  # Requires model download
    # vulnerable_model_call_no_limit()  # Requires model download
    safe_usage_example()
    # safe_usage_max_new_tokens()  # Requires model download
    safe_usage_both_limits()
