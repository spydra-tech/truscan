"""AST-based extraction of FastMCP tool definitions from Python files."""

import ast
import logging
from pathlib import Path
from typing import List, Optional

from ..models import MCPToolDefinition, MCPToolParameter

logger = logging.getLogger(__name__)

MCP_DECORATORS = {"tool", "async_tool", "resource", "prompt"}


def _get_decorator_type(decorator: ast.AST) -> Optional[str]:
    """Return 'tool' | 'async_tool' | 'resource' | 'prompt' if this is an MCP decorator, else None."""
    # @mcp.tool() or @server.tool() -> Call with func=Attribute(attr='tool')
    if isinstance(decorator, ast.Call):
        func = decorator.func
        if isinstance(func, ast.Attribute) and func.attr in MCP_DECORATORS:
            return func.attr
    # @mcp.tool (no parentheses)
    if isinstance(decorator, ast.Attribute) and decorator.attr in MCP_DECORATORS:
        return decorator.attr
    return None


def _annotation_to_type(annotation: Optional[ast.AST]) -> str:
    """Infer a simple type string from an AST annotation."""
    if annotation is None:
        return "str"
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        return annotation.value
    return "str"


def _extract_tool_from_function(
    node: ast.FunctionDef,
    file_path: str,
    decorator_type: str,
) -> MCPToolDefinition:
    """Build MCPToolDefinition from a decorated function node."""
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
        decorator=decorator_type,
        source_file=file_path,
        line=node.lineno,
    )


def extract_from_file(file_path: str, source: Optional[str] = None) -> List[MCPToolDefinition]:
    """
    Extract MCP tool definitions from a single Python file.

    Args:
        file_path: Path to the .py file (used for reporting).
        source: File contents. If None, file is read from disk.

    Returns:
        List of MCPToolDefinition (possibly empty).
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
    tools: List[MCPToolDefinition] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                dec_type = _get_decorator_type(decorator)
                if dec_type:
                    tools.append(_extract_tool_from_function(node, file_path, dec_type))
                    break
    return tools


def extract_from_files(file_paths: List[str]) -> List[MCPToolDefinition]:
    """
    Extract MCP tool definitions from multiple Python files.

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
