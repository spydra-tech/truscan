"""AST-based extraction of LangGraph graph structures from Python files.

LangGraph uses StateGraph to create graphs with nodes (agents, tools, functions)
and edges. This extractor parses the graph structure to extract:
- Graph nodes (agents, tools, functions)
- Graph edges (conditional and direct)
- Tools used in the graph (via ToolNode or bound to agents)
- State schema
- Entry point
"""

import ast
import logging
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple, Any

from ..models import MCPToolDefinition, MCPToolParameter

logger = logging.getLogger(__name__)


def _is_stategraph_call(node: ast.AST) -> bool:
    """Return True if this is StateGraph(...) call."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name) and func.id == "StateGraph":
        return True
    if isinstance(func, ast.Attribute) and func.attr == "StateGraph":
        return True
    return False


def _is_add_node_call(node: ast.AST) -> bool:
    """Return True if this is workflow.add_node(...) call."""
    if not isinstance(node, ast.Call):
        return False
    func = getattr(node, "func", None)
    return isinstance(func, ast.Attribute) and func.attr == "add_node"


def _is_add_edge_call(node: ast.AST) -> bool:
    """Return True if this is workflow.add_edge(...) or add_conditional_edges(...) call."""
    if not isinstance(node, ast.Call):
        return False
    func = getattr(node, "func", None)
    return isinstance(func, ast.Attribute) and func.attr in (
        "add_edge",
        "add_conditional_edges",
    )


def _is_set_entry_point_call(node: ast.AST) -> bool:
    """Return True if this is workflow.set_entry_point(...) call."""
    if not isinstance(node, ast.Call):
        return False
    func = getattr(node, "func", None)
    return isinstance(func, ast.Attribute) and func.attr == "set_entry_point"


def _is_tool_decorator(decorator: ast.AST) -> bool:
    """Return True if this decorator is @tool (LangChain/LangGraph style)."""
    if isinstance(decorator, ast.Call):
        func = decorator.func
        if isinstance(func, ast.Name) and func.id == "tool":
            return True
        if isinstance(func, ast.Attribute) and func.attr == "tool":
            return True
    if isinstance(decorator, ast.Name) and decorator.id == "tool":
        return True
    if isinstance(decorator, ast.Attribute) and decorator.attr == "tool":
        return True
    return False


def _is_toolnode_call(node: ast.AST) -> bool:
    """Return True if this is ToolNode(...) call."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name) and func.id == "ToolNode":
        return True
    if isinstance(func, ast.Attribute) and func.attr == "ToolNode":
        return True
    return False


def _extract_tools_from_toolnode(call_node: ast.Call) -> List[str]:
    """Extract tool names/references from ToolNode([tool1, tool2, ...])."""
    tools = []
    if not call_node.args:
        return tools
    tools_arg = call_node.args[0]
    if isinstance(tools_arg, (ast.List, ast.Tuple)):
        for elt in tools_arg.elts:
            if isinstance(elt, ast.Name):
                tools.append(elt.id)
            elif isinstance(elt, ast.Call):
                if isinstance(elt.func, ast.Name):
                    tools.append(elt.func.id)
    return tools


def _find_function_definition(tree: ast.AST, func_name: str) -> Optional[ast.FunctionDef]:
    """Find a function definition by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == func_name:
                return node
    return None


def _annotation_to_type(annotation: Optional[ast.AST]) -> str:
    """Infer a simple type string from an AST annotation."""
    if annotation is None:
        return "str"
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        return annotation.value
    if isinstance(annotation, ast.Subscript):
        if isinstance(annotation.value, ast.Name):
            return annotation.value.id
    return "str"


def _extract_graph_structure(tree: ast.AST, source: Optional[str] = None) -> Dict[str, Any]:
    """Extract nodes, edges, entry_point, and state_schema from a LangGraph AST."""
    structure: Dict[str, Any] = {
        "nodes": [],
        "edges": [],
        "entry_point": None,
        "state_schema": None,
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # StateGraph(StateClass) -> state_schema
            if isinstance(node.value, ast.Call) and _is_stategraph_call(node.value):
                if node.value.args and isinstance(node.value.args[0], ast.Name):
                    structure["state_schema"] = node.value.args[0].id
        if isinstance(node, ast.Call):
            if _is_add_node_call(node) and node.args and isinstance(node.args[0], ast.Constant):
                if isinstance(node.args[0].value, str):
                    structure["nodes"].append(node.args[0].value)
            elif _is_set_entry_point_call(node) and node.args and isinstance(node.args[0], ast.Constant):
                if isinstance(node.args[0].value, str):
                    structure["entry_point"] = node.args[0].value
            elif _is_add_edge_call(node):
                func_attr = getattr(node.func, "attr", None)
                if func_attr == "add_edge" and len(node.args) >= 2:
                    from_node = node.args[0].value if isinstance(node.args[0], ast.Constant) else None
                    to_arg = node.args[1]
                    to_node = to_arg.value if isinstance(to_arg, ast.Constant) else (to_arg.id if isinstance(to_arg, ast.Name) else None)
                    if from_node is not None and to_node is not None:
                        structure["edges"].append({"from": from_node, "to": to_node})
                elif func_attr == "add_conditional_edges" and len(node.args) >= 3:
                    from_node = node.args[0].value if isinstance(node.args[0], ast.Constant) else None
                    if isinstance(node.args[2], ast.Dict):
                        for k, v in zip(node.args[2].keys, node.args[2].values):
                            cond = k.value if isinstance(k, ast.Constant) else None
                            to_node = v.value if isinstance(v, ast.Constant) else (v.id if isinstance(v, ast.Name) else None)
                            if from_node is not None and to_node is not None:
                                structure["edges"].append({
                                    "from": from_node,
                                    "to": to_node,
                                    "condition": cond,
                                })
    return structure


def extract_from_file(
    file_path: str, source: Optional[str] = None
) -> List[MCPToolDefinition]:
    """
    Extract LangGraph graph structure and tools from a single Python file.

    Parses StateGraph creation, nodes, edges, and tools to extract:
    - All tools used in the graph (via ToolNode or @tool decorated functions)
    - Tools referenced in tool lists

    Args:
        file_path: Path to the .py file (used for reporting).
        source: File contents. If None, file is read from disk.

    Returns:
        List of MCPToolDefinition representing tools found in the graph.
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
    tool_variables: Dict[str, List[str]] = {}  # Track tool variables
    
    # First pass: Extract @tool decorated functions
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                if _is_tool_decorator(decorator):
                    description = ast.get_docstring(node) or ""
                    parameters = []
                    for arg in node.args.args:
                        if arg.arg == "self":
                            continue
                        param_type = _annotation_to_type(arg.annotation)
                        parameters.append(MCPToolParameter(name=arg.arg, type=param_type))
                    tools.append(MCPToolDefinition(
                        name=node.name,
                        description=description.strip(),
                        parameters=parameters,
                        decorator="langgraph_tool",
                        source_file=file_path,
                        line=node.lineno,
                    ))
                    break

    # Second pass: Find ToolNode calls and extract tool references
    # Use a visitor to track assignments
    class ToolNodeVisitor(ast.NodeVisitor):
        def __init__(self):
            self.tool_nodes = []
        def visit_Assign(self, node):
            if isinstance(node.value, ast.Call) and _is_toolnode_call(node.value):
                tool_names = _extract_tools_from_toolnode(node.value)
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        tool_variables[target.id] = tool_names
            self.generic_visit(node)
    
    visitor = ToolNodeVisitor()
    visitor.visit(tree)

    # Third pass: Extract tools from variable assignments (e.g., tools = [tool1, tool2])
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and ('tool' in target.id.lower() or target.id.endswith('s')):
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        tool_refs = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Name):
                                tool_refs.append(elt.id)
                            elif isinstance(elt, ast.Call):
                                if isinstance(elt.func, ast.Name):
                                    tool_refs.append(elt.func.id)
                        if tool_refs:
                            tool_variables[target.id] = tool_refs

    # Fourth pass: Extract tools referenced in ToolNode or tool lists
    # Try to find function definitions for referenced tool names
    seen_tool_names = {tool.name for tool in tools}
    for tool_var_name, tool_refs in tool_variables.items():
        for tool_ref in tool_refs:
            if tool_ref in seen_tool_names:
                continue
            func_def = _find_function_definition(tree, tool_ref)
            if func_def:
                description = ast.get_docstring(func_def) or ""
                parameters = []
                for arg in func_def.args.args:
                    if arg.arg == "self":
                        continue
                    param_type = _annotation_to_type(arg.annotation)
                    parameters.append(MCPToolParameter(name=arg.arg, type=param_type))
                tools.append(MCPToolDefinition(
                    name=tool_ref,
                    description=description.strip(),
                    parameters=parameters,
                    decorator="langgraph_tool",
                    source_file=file_path,
                    line=func_def.lineno,
                ))
                seen_tool_names.add(tool_ref)

    return tools


def extract_from_file_with_structure(
    file_path: str, source: Optional[str] = None
) -> Tuple[List[MCPToolDefinition], Dict[str, Any]]:
    """
    Extract tools and graph structure (nodes, edges, entry_point, state_schema) from a LangGraph file.
    """
    if source is None:
        try:
            source = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logger.debug("Could not read %s: %s", file_path, e)
            return [], {}
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        logger.debug("Syntax error in %s: %s", file_path, e)
        return [], {}
    tools = extract_from_file(file_path, source=source)
    graph_structure = _extract_graph_structure(tree, source=source)
    return tools, graph_structure


def extract_from_files_with_structure(
    file_paths: List[str],
) -> Tuple[List[MCPToolDefinition], Optional[Dict[str, Any]]]:
    """
    Extract LangGraph tools and combined graph structure from multiple Python files.
    Tools are merged from all files; graph structure is from the first file that has one.
    """
    all_tools: List[MCPToolDefinition] = []
    combined_structure: Optional[Dict[str, Any]] = None
    for path in file_paths:
        if not path.endswith(".py"):
            continue
        tools, structure = extract_from_file_with_structure(path)
        all_tools.extend(tools)
        if structure and (structure.get("nodes") or structure.get("entry_point")):
            combined_structure = structure
    return all_tools, combined_structure


def extract_from_files(file_paths: List[str]) -> List[MCPToolDefinition]:
    """
    Extract LangGraph tool definitions from multiple Python files.

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
