"""AST-based extraction of LangChain @tool definitions from Python files."""

import ast
import logging
from pathlib import Path
from typing import List, Optional

from ..models import MCPToolDefinition, MCPToolParameter

logger = logging.getLogger(__name__)

# LangChain uses @tool from langchain.tools or langchain_core.tools
# We match decorators that are "tool" (Name or Attribute) so we catch
# "from langchain.tools import tool" and "from langchain_core.tools import tool"
DECORATOR_ATTR = "tool"


def _is_langchain_tool_decorator(decorator: ast.AST) -> bool:
    """Return True if this decorator is @tool (LangChain style)."""
    # @tool or @tool("name") -> Call with func=Name('tool') or Attribute(attr='tool')
    if isinstance(decorator, ast.Call):
        func = decorator.func
        if isinstance(func, ast.Name) and func.id == DECORATOR_ATTR:
            return True
        if isinstance(func, ast.Attribute) and func.attr == DECORATOR_ATTR:
            return True
    # @tool (no parentheses)
    if isinstance(decorator, ast.Name) and decorator.id == DECORATOR_ATTR:
        return True
    if isinstance(decorator, ast.Attribute) and decorator.attr == DECORATOR_ATTR:
        return True
    return False


def _get_tool_name_from_decorator(decorator: ast.AST, default_name: str) -> str:
    """If decorator is @tool("custom_name"), return that name; else default_name."""
    if isinstance(decorator, ast.Call):
        if decorator.args and isinstance(decorator.args[0], ast.Constant):
            if isinstance(decorator.args[0].value, str):
                return decorator.args[0].value
    return default_name


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
    decorator: ast.AST,
) -> MCPToolDefinition:
    """Build MCPToolDefinition from a @tool-decorated function node."""
    default_name = node.name
    name = _get_tool_name_from_decorator(decorator, default_name)
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
        decorator="langchain_tool",
        source_file=file_path,
        line=node.lineno,
    )


def extract_from_file(
    file_path: str, source: Optional[str] = None
) -> List[MCPToolDefinition]:
    """
    Extract LangChain tool definitions from a single Python file.

    Looks for @tool decorator (from langchain.tools or langchain_core.tools).
    Supports @tool and @tool("custom_name").

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
    tools: List[MCPToolDefinition] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                if _is_langchain_tool_decorator(decorator):
                    tools.append(_extract_tool_from_function(node, file_path, decorator))
                    break
    return tools


def extract_from_files(file_paths: List[str]) -> List[MCPToolDefinition]:
    """
    Extract LangChain tool definitions from multiple Python files.

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
