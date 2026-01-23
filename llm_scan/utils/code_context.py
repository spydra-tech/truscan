"""Utilities for extracting code context for AI analysis."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_code_context(
    file_path: str,
    line_number: int,
    context_lines: int = 50,
    max_file_size: int = 1_000_000,  # 1MB
) -> Optional[str]:
    """
    Extract surrounding code context for AI analysis.

    Args:
        file_path: Path to the source file
        line_number: Line number of the finding
        context_lines: Number of lines before/after to include
        max_file_size: Maximum file size to read (bytes)

    Returns:
        Code context string or None if file can't be read
    """
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            logger.warning(f"File not found: {file_path}")
            return None

        # Check file size
        file_size = file_path_obj.stat().st_size
        if file_size > max_file_size:
            logger.warning(
                f"File too large ({file_size} bytes > {max_file_size}): {file_path}"
            )
            return None

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        # Calculate context range
        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(lines), line_number + context_lines)

        # Extract context
        context_lines_list = lines[start_line:end_line]
        context = "".join(context_lines_list)

        # Add line numbers for reference
        numbered_context = []
        for i, line in enumerate(context_lines_list, start=start_line + 1):
            numbered_context.append(f"{i:4d} | {line}")

        return "".join(numbered_context)

    except Exception as e:
        logger.error(f"Error extracting code context from {file_path}: {e}")
        return None


def extract_snippet_context(
    snippet: Optional[str],
    file_path: str,
    line_number: int,
    context_lines: int = 20,
) -> str:
    """
    Extract context around a code snippet.

    Args:
        snippet: The code snippet from the finding
        file_path: Path to the source file
        line_number: Line number of the finding
        context_lines: Number of lines before/after to include

    Returns:
        Combined snippet and context
    """
    context = extract_code_context(file_path, line_number, context_lines)
    if not context:
        return snippet or ""

    if snippet:
        return f"```python\n{context}\n```\n\nSnippet:\n```python\n{snippet}\n```"
    return f"```python\n{context}\n```"


def load_file_contents(findings: list) -> dict:
    """
    Load file contents for all files referenced in findings.

    Args:
        findings: List of Finding objects

    Returns:
        Dictionary mapping file paths to their contents
    """
    file_contents = {}
    unique_files = set(f.location.file_path for f in findings)

    for file_path in unique_files:
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    file_contents[file_path] = f.read()
        except Exception as e:
            logger.warning(f"Could not load file {file_path}: {e}")

    return file_contents
