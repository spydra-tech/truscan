"""
Sample vulnerable Hugging Face application demonstrating training data poisoning vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from transformers import Trainer, TrainingArguments
import requests
import urllib.request
from flask import request
import sys


def vulnerable_trainer_with_web_data():
    """VULNERABLE: Trainer with data from web request."""
    # CRITICAL: Training data from untrusted web source
    response = requests.get("https://untrusted-source.com/training-data.txt")
    training_data = response.text  # VULNERABILITY: Untrusted data source
    
    # VULNERABILITY: Data used for training without validation
    trainer = Trainer(
        train_dataset=training_data,  # CRITICAL: Training data poisoning risk
        args=TrainingArguments(output_dir="./results")
    )
    
    return trainer


def vulnerable_trainer_with_urlopen():
    """VULNERABLE: Trainer with data from urllib.request.urlopen()."""
    # CRITICAL: Training data from URL without validation
    with urllib.request.urlopen("https://untrusted-source.com/data.txt") as f:
        training_data = f.read().decode()  # VULNERABILITY: Untrusted data source
    
    trainer = Trainer(
        train_dataset=training_data,  # CRITICAL: Training data poisoning risk
        args=TrainingArguments(output_dir="./results")
    )
    
    return trainer


def vulnerable_trainer_with_flask_file():
    """VULNERABLE: Trainer with data from Flask file upload."""
    # CRITICAL: Training data from user file upload
    uploaded_file = request.files.get('training_data')  # VULNERABILITY: User-provided data
    training_data = uploaded_file.read().decode()  # CRITICAL: No validation
    
    trainer = Trainer(
        train_dataset=training_data,  # CRITICAL: Training data poisoning risk
        args=TrainingArguments(output_dir="./results")
    )
    
    return trainer


def vulnerable_trainer_with_input():
    """VULNERABLE: Trainer with data from input()."""
    # CRITICAL: Training data from user input
    training_data = input("Enter training data: ")  # VULNERABILITY: User input
    
    trainer = Trainer(
        train_dataset=training_data,  # CRITICAL: Training data poisoning risk
        args=TrainingArguments(output_dir="./results")
    )
    
    return trainer


def vulnerable_trainer_with_sys_argv():
    """VULNERABLE: Trainer with data from sys.argv."""
    # CRITICAL: Training data from command line arguments
    training_data = sys.argv[1]  # VULNERABILITY: Command line input
    
    trainer = Trainer(
        train_dataset=training_data,  # CRITICAL: Training data poisoning risk
        args=TrainingArguments(output_dir="./results")
    )
    
    return trainer


def vulnerable_model_train_method(training_data):
    """VULNERABLE: Model.train() with untrusted data."""
    from transformers import AutoModelForCausalLM
    
    # CRITICAL: Model trained with untrusted data
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    model.train(training_data)  # VULNERABILITY: Training data poisoning risk
    
    return model


def vulnerable_model_fit_method(training_data):
    """VULNERABLE: Model.fit() with untrusted data."""
    from transformers import AutoModelForCausalLM
    
    # CRITICAL: Model fitted with untrusted data
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    model.fit(training_data)  # VULNERABILITY: Training data poisoning risk
    
    return model


def safe_usage_example():
    """SAFE: Proper data validation and trusted sources."""
    # SAFE: Load from trusted, verified source
    TRUSTED_DATA_SOURCE = "https://trusted-dataset-repo.com/verified-data.txt"
    
    # SAFE: Validate data source
    if not TRUSTED_DATA_SOURCE.startswith("https://trusted-dataset-repo.com"):
        raise ValueError("Untrusted data source")
    
    response = requests.get(TRUSTED_DATA_SOURCE)
    
    # SAFE: Validate and sanitize data
    training_data = response.text
    if not training_data or len(training_data) < 100:
        raise ValueError("Invalid training data")
    
    # SAFE: Additional validation (schema, checksums, etc.)
    # ... data validation logic ...
    
    trainer = Trainer(
        train_dataset=training_data,  # SAFE: Validated data
        args=TrainingArguments(output_dir="./results")
    )
    
    return trainer


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_trainer_with_web_data()
    vulnerable_trainer_with_urlopen()
    # vulnerable_trainer_with_flask_file()  # Requires Flask context
    # vulnerable_trainer_with_input()  # Requires interactive input
    vulnerable_trainer_with_sys_argv()
    # vulnerable_model_train_method("untrusted data")  # Requires model
    # vulnerable_model_fit_method("untrusted data")  # Requires model
    safe_usage_example()
