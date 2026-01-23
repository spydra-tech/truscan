"""
Sample vulnerable Hugging Face application demonstrating supply chain vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
CVE-2025-14921, CVE-2025-14924, CVE-2025-14926: Pickle deserialization RCE
"""

from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import pickle
import os


def vulnerable_pickle_deserialization_no_safetensors():
    """VULNERABLE: Model loading without safetensors (uses pickle by default)."""
    # CRITICAL: Model loaded without use_safetensors=True
    # PyTorch uses pickle as default, allowing RCE during deserialization
    model = AutoModel.from_pretrained("gpt2")  # VULNERABILITY: Pickle deserialization risk (CVE-2025-14921)
    
    return model


def vulnerable_pipeline_no_safetensors():
    """VULNERABLE: Pipeline without safetensors."""
    # CRITICAL: Pipeline without use_safetensors=True
    pipe = pipeline("text-generation", model="gpt2")  # VULNERABILITY: Pickle deserialization risk (CVE-2025-14924)
    
    return pipe


def vulnerable_tokenizer_no_safetensors():
    """VULNERABLE: Tokenizer loading without safetensors."""
    # CRITICAL: Tokenizer without use_safetensors=True
    tokenizer = AutoTokenizer.from_pretrained("gpt2")  # VULNERABILITY: Pickle deserialization risk
    
    return tokenizer


def vulnerable_trust_remote_code_untrusted_model():
    """VULNERABLE: trust_remote_code=True with potentially untrusted model."""
    # CRITICAL: trust_remote_code=True allows execution of custom code from model repo
    model = AutoModel.from_pretrained(
        "untrusted-user/malicious-model",
        trust_remote_code=True  # VULNERABILITY: Remote code execution risk
    )
    
    return model


def vulnerable_tokenizer_trust_remote_code():
    """VULNERABLE: Tokenizer with trust_remote_code=True."""
    # CRITICAL: trust_remote_code=True in tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        "untrusted-user/malicious-tokenizer",
        trust_remote_code=True  # VULNERABILITY: Remote code execution risk
    )
    
    return tokenizer


def vulnerable_untrusted_model_source(user_provided_model: str):
    """VULNERABLE: Model loaded from untrusted source."""
    # CRITICAL: Model from user-provided or untrusted source
    model = AutoModel.from_pretrained(user_provided_model)  # VULNERABILITY: Supply chain risk
    
    return model


def vulnerable_torch_load_pickle():
    """VULNERABLE: Direct torch.load() with pickle files."""
    # CRITICAL: torch.load() uses pickle by default
    model = torch.load("untrusted_model.pth")  # VULNERABILITY: Pickle deserialization RCE (CVE-2025-14926)
    
    return model


def vulnerable_torch_load_pickle_file():
    """VULNERABLE: torch.load() with file object."""
    # CRITICAL: torch.load() with file object
    with open("untrusted_model.pth", "rb") as f:
        model = torch.load(f)  # VULNERABILITY: Pickle deserialization RCE
    
    return model


def vulnerable_pickle_load_direct():
    """VULNERABLE: Direct pickle.load() with untrusted file."""
    # CRITICAL: Direct pickle deserialization
    with open("untrusted_data.pkl", "rb") as f:
        data = pickle.load(f)  # VULNERABILITY: Pickle deserialization RCE
    
    return data


def safe_usage_example():
    """SAFE: Proper model loading with safetensors."""
    # SAFE: Use safetensors format
    model = AutoModel.from_pretrained(
        "gpt2",
        use_safetensors=True  # SAFE: Uses safetensors instead of pickle
    )
    
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    # SAFE: Pipeline with safetensors
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        use_safetensors=True  # SAFE: Explicit safetensors usage
    )
    
    return pipe


def safe_usage_trusted_model():
    """SAFE: Loading from trusted source only."""
    # SAFE: Only load from trusted, verified sources
    TRUSTED_MODELS = ["gpt2", "bert-base-uncased", "distilbert-base-uncased"]
    
    model_name = "gpt2"  # From trusted list
    if model_name not in TRUSTED_MODELS:
        raise ValueError(f"Untrusted model: {model_name}")
    
    model = AutoModel.from_pretrained(
        model_name,
        use_safetensors=True,  # SAFE: Use safetensors
        trust_remote_code=False  # SAFE: Don't trust remote code
    )
    
    return model


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_pickle_deserialization_no_safetensors()
    vulnerable_pipeline_no_safetensors()
    vulnerable_tokenizer_no_safetensors()
    vulnerable_trust_remote_code_untrusted_model()
    vulnerable_tokenizer_trust_remote_code()
    vulnerable_untrusted_model_source("user-provided-model")
    vulnerable_torch_load_pickle()
    vulnerable_torch_load_pickle_file()
    vulnerable_pickle_load_direct()
    safe_usage_example()
    safe_usage_trusted_model()
