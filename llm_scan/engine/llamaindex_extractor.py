"""AST-based extraction of LlamaIndex FunctionTool definitions from Python files."""

import ast
import logging
from pathlib import Path
from typing import List, Optional

from ..models import MCPToolDefinition, MCPToolParameter

logger = logging.getLogger(__name__)

# LlamaIndex uses FunctionTool.from_defaults(function) to wrap functions
# We need to find:
# 1. Calls to FunctionTool.from_defaults(function_ref)
# 2. The function definition that function_ref points to


def _is_functiontool_from_defaults(node: ast.AST) -> bool:
    """Return True if this is FunctionTool.from_defaults(...) call."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    # FunctionTool.from_defaults(...)
    if isinstance(func, ast.Attribute):
        if func.attr == "from_defaults":
            # FunctionTool.from_defaults (direct import: from llama_index.core.tools import FunctionTool)
            if isinstance(func.value, ast.Name) and func.value.id == "FunctionTool":
                return True
            # llama_index.core.tools.FunctionTool.from_defaults or tools.FunctionTool.from_defaults
            if isinstance(func.value, ast.Attribute):
                if func.value.attr == "FunctionTool":
                    return True
                # Handle nested: llama_index.core.tools.FunctionTool
                # Walk up the attribute chain to find "FunctionTool"
                current = func.value
                while isinstance(current, ast.Attribute):
                    if current.attr == "FunctionTool":
                        return True
                    current = getattr(current, "value", None)
                    if not isinstance(current, ast.Attribute):
                        break
    return False


def _get_function_name_from_call(call_node: ast.Call) -> Optional[str]:
    """Extract function name from FunctionTool.from_defaults(function_name)."""
    # Check positional argument first: FunctionTool.from_defaults(function_name)
    if call_node.args:
        arg = call_node.args[0]
        if isinstance(arg, ast.Name):
            return arg.id
    # Handle keyword argument: FunctionTool.from_defaults(fn=function_name)
    for keyword in call_node.keywords:
        if keyword.arg == "fn" and isinstance(keyword.value, ast.Name):
            return keyword.value.id
    return None


def _annotation_to_type(annotation: Optional[ast.AST]) -> str:
    """Infer a simple type string from an AST annotation."""
    if annotation is None:
        return "str"
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        return annotation.value
    if isinstance(annotation, ast.Subscript):  # List[str], Optional[str], etc.
        if isinstance(annotation.value, ast.Name):
            return annotation.value.id
    return "str"


def _extract_tool_from_function(
    node: ast.FunctionDef,
    file_path: str,
) -> MCPToolDefinition:
    """Build MCPToolDefinition from a function node."""
    name = node.name
    description = ast.get_docstring(node) or ""
    parameters: List[MCPToolParameter] = []
    for arg in node.args.args:
        if arg.arg == "self":
            continue
        param_type = _annotation_to_type(arg.annotation)
        parameters.append(MCPToolParameter(name=arg.arg, type=param_type))
    return MCPToolDefinition(
        name=name,
        description=description.strip(),
        parameters=parameters,
        decorator="llamaindex_tool",
        source_file=file_path,
        line=node.lineno,
    )


def extract_from_file(
    file_path: str, source: Optional[str] = None
) -> List[MCPToolDefinition]:
    """
    Extract LlamaIndex FunctionTool definitions from a single Python file.

    Looks for FunctionTool.from_defaults(function_ref) calls and extracts
    the referenced function definitions.

    Args:
        file_path: Path to the .py file (used for reporting).
        source: File contents. If None, file is read from disk.

    Returns:
        List of MCPToolDefinition (compatible with eval prompt generator).
    """
    if source is None:
        try:
            source = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logger.debug("Could not read %s: %s", file_path, e)
            return []
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        logger.debug("Syntax error in %s: %s", file_path, e)
        return []

    # First pass: find all FunctionTool.from_defaults() calls and collect function names
    tool_function_names: set[str] = set()
    for node in ast.walk(tree):
        if _is_functiontool_from_defaults(node):
            func_name = _get_function_name_from_call(node)
            if func_name:
                tool_function_names.add(func_name)

    # Second pass: find function definitions that match those names
    tools: List[MCPToolDefinition] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in tool_function_names:
                tools.append(_extract_tool_from_function(node, file_path))

    return tools


def extract_from_files(file_paths: List[str]) -> List[MCPToolDefinition]:
    """
    Extract LlamaIndex tool definitions from multiple Python files.

    Args:
        file_paths: List of paths to .py files (non-.py are skipped).

    Returns:
        Combined list of MCPToolDefinition from all files.
    """
    all_tools: List[MCPToolDefinition] = []
    for path in file_paths:
        if not path.endswith(".py"):
            continue
        all_tools.extend(extract_from_file(path))
    return all_tools
