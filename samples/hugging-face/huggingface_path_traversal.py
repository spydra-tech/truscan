"""
Sample vulnerable Hugging Face application demonstrating path traversal vulnerabilities.
This file contains multiple vulnerabilities that should be detected by the scanner.
"""

from transformers import pipeline
import os
import shutil
from pathlib import Path


def vulnerable_pipeline_to_file_write(user_input: str):
    """VULNERABLE: Pipeline output used in file write operations."""
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(f"Generate filename for: {user_input}")
    
    filename = response[0]["generated_text"].strip()
    
    # CRITICAL: Path traversal risk
    with open(filename, 'w') as f:  # VULNERABILITY: Path traversal risk
        f.write("data")
    
    return filename


def vulnerable_pipeline_to_path_write_text(user_input: str):
    """VULNERABLE: Pipeline output used in Path.write_text()."""
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(f"Generate path for: {user_input}")
    
    filepath = response[0]["generated_text"].strip()
    
    # CRITICAL: Path traversal risk
    Path(filepath).write_text("data")  # VULNERABILITY: Path traversal risk
    
    return filepath


def vulnerable_pipeline_to_shutil_copy(user_input: str):
    """VULNERABLE: Pipeline output used in shutil.copy()."""
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(f"Generate destination path: {user_input}")
    
    dest_path = response[0]["generated_text"].strip()
    
    # CRITICAL: Path traversal risk
    shutil.copy("source.txt", dest_path)  # VULNERABILITY: Path traversal risk
    
    return dest_path


def vulnerable_pipeline_to_os_remove(user_input: str):
    """VULNERABLE: Pipeline output used in os.remove()."""
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(f"Generate file to delete: {user_input}")
    
    filepath = response[0]["generated_text"].strip()
    
    # CRITICAL: Path traversal risk
    os.remove(filepath)  # VULNERABILITY: Path traversal risk
    
    return filepath


def safe_usage_example(user_input: str):
    """SAFE: Proper path validation and sanitization."""
    from pathlib import Path
    import os
    
    pipe = pipeline("text-generation", model="gpt2", max_length=50)
    response = pipe(f"Generate filename for: {user_input}")
    
    filename = response[0]["generated_text"].strip()
    
    # SAFE: Validate and sanitize path
    # Remove path traversal sequences
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")
    
    # SAFE: Restrict to safe directory
    SAFE_DIR = "/tmp/safe_output"
    os.makedirs(SAFE_DIR, exist_ok=True)
    
    # SAFE: Use Path for safe path joining
    safe_path = Path(SAFE_DIR) / filename
    
    # SAFE: Ensure path is within safe directory
    if not str(safe_path.resolve()).startswith(os.path.abspath(SAFE_DIR)):
        raise ValueError("Path traversal detected")
    
    safe_path.write_text("data")
    
    return str(safe_path)


if __name__ == "__main__":
    # Example usage (DO NOT RUN IN PRODUCTION)
    vulnerable_pipeline_to_file_write("save file")
    vulnerable_pipeline_to_path_write_text("write path")
    vulnerable_pipeline_to_shutil_copy("copy to")
    # vulnerable_pipeline_to_os_remove("delete file")  # Would actually delete
    safe_usage_example("save file")
