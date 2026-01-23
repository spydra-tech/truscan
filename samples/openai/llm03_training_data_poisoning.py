"""
OWASP LLM03: Training Data Poisoning
=====================================
This file demonstrates vulnerabilities related to training data from
untrusted sources without proper validation.
"""

import requests
import urllib.request
import pickle
import json


# VULNERABILITY: Training data loaded from untrusted URL without validation
def vulnerable_load_from_url(url: str):
    """Load training data from URL without validation."""
    data = requests.get(url).text  # LLM03: Untrusted source
    train_model(data=data)  # No validation or checksum verification


# VULNERABILITY: Training data from user-provided URL
def vulnerable_user_url(user_url: str):
    """Training data from user-provided URL."""
    response = urllib.request.urlopen(user_url)  # LLM03: User-controlled
    training_data = response.read()
    train_model(data=training_data)  # No validation


# VULNERABILITY: Training data from external file without verification
def vulnerable_load_external_file(filename: str):
    """Load training data from external file."""
    with open(filename, 'r') as f:  # LLM03: External file
        data = f.read()
    train_model(data=data)  # No checksum or signature verification


# VULNERABILITY: Training data from temporary/download directory
def vulnerable_load_from_downloads():
    """Load training data from downloads folder."""
    import os
    download_path = os.path.join(os.path.expanduser("~"), "Downloads", "training_data.txt")
    with open(download_path, 'r') as f:  # LLM03: Untrusted location
        data = f.read()
    train_model(data=data)


# VULNERABILITY: Training data from user input
def vulnerable_user_provided_data(user_data: str):
    """Training data directly from user input."""
    train_model(data=user_data)  # LLM03: No validation or sanitization


# VULNERABILITY: Training data from pickle file without verification
def vulnerable_load_pickle(filename: str):
    """Load training data from pickle file."""
    with open(filename, 'rb') as f:  # LLM03: Unverified pickle
        data = pickle.load(f)
    train_model(data=data)  # No signature verification


# VULNERABILITY: Training data from JSON without schema validation
def vulnerable_load_json(url: str):
    """Load training data from JSON URL."""
    response = requests.get(url)
    data = json.loads(response.text)  # LLM03: No schema validation
    train_model(data=data)


# VULNERABILITY: Training data from multiple untrusted sources
def vulnerable_aggregate_sources(urls: list):
    """Aggregate training data from multiple untrusted sources."""
    all_data = []
    for url in urls:  # LLM03: Multiple untrusted sources
        data = requests.get(url).text
        all_data.append(data)  # No validation per source
    train_model(data="\n".join(all_data))


# Helper function (not vulnerable, just for context)
def train_model(data):
    """Placeholder for model training function."""
    pass
