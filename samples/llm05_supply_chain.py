"""
OWASP LLM05: Supply Chain Vulnerabilities
==========================================
This file demonstrates vulnerabilities related to untrusted models,
libraries, or plugins from external sources.
"""

import importlib
import requests
import pickle
import torch
from transformers import AutoModel, AutoTokenizer


# VULNERABILITY: Model loaded from untrusted URL without verification
def vulnerable_load_model_from_url(url: str):
    """Load model from URL without checksum or signature verification."""
    model_data = requests.get(url).content  # LLM05: Untrusted source
    model = pickle.loads(model_data)  # No verification
    return model


# VULNERABILITY: Model downloaded without checksum verification
def vulnerable_download_model(url: str):
    """Download model without verifying checksum or signature."""
    response = requests.get(url)
    with open("model.pkl", "wb") as f:
        f.write(response.content)
    # LLM05: No checksum verification
    model = pickle.load(open("model.pkl", "rb"))
    return model


# VULNERABILITY: Model from untrusted HuggingFace repository
def vulnerable_load_huggingface(repo: str):
    """Load model from HuggingFace without verification."""
    # LLM05: No signature verification
    model = AutoModel.from_pretrained(repo)  # Could be malicious
    tokenizer = AutoTokenizer.from_pretrained(repo)
    return model, tokenizer


# VULNERABILITY: Plugin code loaded from LLM output
def vulnerable_plugin_from_llm(user_query: str):
    """Load and execute plugin code from LLM output."""
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Write a plugin to: {user_query}"}]
    )
    plugin_code = response.choices[0].message.content  # LLM05: Untrusted code
    
    # Execute without verification
    exec(plugin_code)  # CRITICAL: Code injection


# VULNERABILITY: Dynamic module import from LLM output
def vulnerable_dynamic_import(user_query: str):
    """Import module dynamically based on LLM output."""
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Import module: {user_query}"}]
    )
    module_name = response.choices[0].message.content
    # LLM05: No whitelist check
    module = importlib.import_module(module_name)  # Could import malicious module
    return module


# VULNERABILITY: Plugin loaded from user-provided path
def vulnerable_load_user_plugin(plugin_path: str):
    """Load plugin from user-provided path."""
    # LLM05: No path validation or signature check
    with open(plugin_path, 'rb') as f:
        plugin = pickle.load(f)  # Could be malicious
    return plugin


# VULNERABILITY: Model weights loaded without verification
def vulnerable_load_weights(url: str):
    """Load model weights from URL without verification."""
    weights = requests.get(url).content
    # LLM05: No checksum or signature verification
    model = torch.load(weights)  # Could be tampered
    return model


# VULNERABILITY: Dependency installed from untrusted source
def vulnerable_install_dependency(package_url: str):
    """Install Python package from untrusted URL."""
    import subprocess
    # LLM05: No signature verification
    subprocess.run(["pip", "install", package_url])  # Could install malicious package


# VULNERABILITY: Code execution from external script
def vulnerable_exec_external_script(url: str):
    """Download and execute external script."""
    script = requests.get(url).text  # LLM05: Untrusted source
    exec(script)  # CRITICAL: No verification


# VULNERABILITY: Model loaded from GitHub without verification
def vulnerable_load_from_github(repo: str, file: str):
    """Load model file from GitHub without verification."""
    url = f"https://raw.githubusercontent.com/{repo}/{file}"
    model_data = requests.get(url).content  # LLM05: No checksum
    model = pickle.loads(model_data)
    return model
