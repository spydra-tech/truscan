"""
OWASP LLM10: Model Theft
=========================
This file demonstrates vulnerabilities where proprietary models or training
data can be accessed, copied, or extracted without authorization.
"""

from flask import Flask, send_file, request
import os
import pickle
import torch

app = Flask(__name__)


# VULNERABILITY: Model file exposed via unauthenticated endpoint
@app.route("/model", methods=["GET"])
def vulnerable_model_endpoint():
    """Model file exposed without authentication."""
    # LLM10: No authentication check
    return send_file("model.pkl")  # Anyone can download the model


# VULNERABILITY: Model weights exposed via download endpoint
@app.route("/download", methods=["GET"])
def vulnerable_download_endpoint():
    """Model weights exposed for download."""
    # LLM10: No authorization
    return send_file("weights.pt")  # Model weights accessible to anyone


# VULNERABILITY: Model loading without access control
def vulnerable_load_model(model_path: str):
    """Model loaded without checking permissions."""
    # LLM10: No access control check
    with open(model_path, "rb") as f:
        model = pickle.load(f)  # Could be proprietary model
    return model


# VULNERABILITY: Model endpoint without authentication
@app.route("/api/model", methods=["GET"])
def vulnerable_api_model():
    """Model API endpoint without authentication."""
    # LLM10: No authentication required
    model_data = load_model_data()
    return {"model": model_data}  # Model data exposed


# VULNERABILITY: Training data exposed
@app.route("/training-data", methods=["GET"])
def vulnerable_training_data():
    """Training data exposed without protection."""
    # LLM10: No access control
    return send_file("training_data.json")  # Training data accessible


# VULNERABILITY: Model checkpoint exposed
@app.route("/checkpoint", methods=["GET"])
def vulnerable_checkpoint():
    """Model checkpoint exposed."""
    # LLM10: No authorization
    return send_file("checkpoint.ckpt")  # Checkpoint file accessible


# VULNERABILITY: Model architecture exposed
@app.route("/architecture", methods=["GET"])
def vulnerable_architecture():
    """Model architecture exposed."""
    # LLM10: No protection
    architecture = get_model_architecture()
    return {"architecture": architecture}  # Architecture details exposed


# VULNERABILITY: Model inference endpoint allows extraction
@app.route("/infer", methods=["POST"])
def vulnerable_inference():
    """Model inference endpoint that could be used for extraction."""
    # LLM10: No rate limiting or extraction protection
    data = request.json
    result = model_inference(data["input"])
    return {"result": result}  # Could be used to extract model via queries


# VULNERABILITY: Model file accessible via direct path
def vulnerable_direct_access():
    """Model file accessible via direct file system access."""
    # LLM10: No file permissions or encryption
    model_path = "/models/proprietary_model.pkl"
    if os.path.exists(model_path):
        return pickle.load(open(model_path, "rb"))  # No access control


# VULNERABILITY: Model serialization without encryption
def vulnerable_model_serialization(model):
    """Model serialized without encryption."""
    # LLM10: No encryption
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)  # Model stored in plain text


# Helper functions (not vulnerable, just for context)
def load_model_data():
    """Placeholder for loading model data."""
    return {"layers": 10, "parameters": 1000000}


def get_model_architecture():
    """Placeholder for getting model architecture."""
    return {"type": "transformer", "layers": 12}


def model_inference(input_data):
    """Placeholder for model inference."""
    return "result"
