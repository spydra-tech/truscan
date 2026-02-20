"""
Concrete evals runner: tool-selection, tool-invocation presence, valid path, tool coverage.

Loads eval JSON (from generate-eval-tests), invokes the graph/agent per test case,
and computes metrics. Requires a runnable graph (e.g. LangGraph compiled graph).
"""

import importlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class EvalMetrics:
    """Aggregate metrics from running evals."""

    tool_selection_accuracy: float  # % of cases where expected_tool was in called tools
    tool_invocation_presence: float  # same as above (tool was called)
    valid_path_rate: Optional[float] = None  # % of runs where path respected graph edges (if graph_structure present)
    tool_coverage: Dict[str, float] = field(default_factory=dict)  # per-tool recall
    total_cases: int = 0
    passed_tool_selection: int = 0
    passed_valid_path: Optional[int] = None
    total_with_path: Optional[int] = None


def load_eval_json(path: str) -> Dict[str, Any]:
    """Load eval JSON (tool_manifest, test_cases, optional graph_structure, meta)."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_graph(spec: str) -> Any:
    """Load graph from 'module.path:attribute' (e.g. samples.langgraph.langgraph_multi_agent_app:graph)."""
    if ":" not in spec:
        raise ValueError("Graph spec must be 'module.path:attribute'")
    module_path, attr = spec.rsplit(":", 1)
    mod = importlib.import_module(module_path)
    return getattr(mod, attr)


def _extract_tool_calls_from_state(state: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    """Extract (tool_name, args) from LangGraph/LangChain state messages (AIMessage.tool_calls)."""
    out: List[Tuple[str, Dict[str, Any]]] = []
    messages = state.get("messages") or []
    for msg in messages:
        tool_calls = getattr(msg, "tool_calls", None) or msg.get("tool_calls") if isinstance(msg, dict) else None
        if not tool_calls:
            continue
        for tc in tool_calls:
            name = None
            args = {}
            if isinstance(tc, dict):
                name = tc.get("name") or tc.get("tool")
                args = tc.get("args") or {}
            else:
                name = getattr(tc, "name", None) or getattr(tc, "get", lambda k: None)("name")
                args = getattr(tc, "args", None) or getattr(tc, "get", lambda k: None)("args") or {}
            if name:
                out.append((name, args))
    return out


def _get_node_path_from_stream(graph: Any, initial_state: Dict[str, Any]) -> List[str]:
    """Stream graph and collect node execution order. LangGraph stream_mode='updates' yields {node_name: update}."""
    path: List[str] = []
    try:
        for chunk in graph.stream(initial_state, stream_mode="updates"):
            if isinstance(chunk, dict):
                for key in chunk:
                    if key not in ("__end__", "__start__"):
                        path.append(str(key))
    except Exception as e:
        logger.debug("Could not stream graph for path: %s", e)
    return path


def _allowed_edges(graph_structure: Dict[str, Any]) -> Set[Tuple[str, str]]:
    """Build set of (from, to) from graph_structure['edges']."""
    allowed: Set[Tuple[str, str]] = set()
    for e in graph_structure.get("edges") or []:
        from_n = e.get("from")
        to_n = e.get("to")
        if from_n is not None and to_n is not None:
            allowed.add((str(from_n), str(to_n)))
    return allowed


def _is_path_valid(path: List[str], allowed: Set[Tuple[str, str]]) -> bool:
    """Check that every consecutive (path[i], path[i+1]) is in allowed edges."""
    if len(path) < 2:
        return True
    for i in range(len(path) - 1):
        if (path[i], path[i + 1]) not in allowed:
            return False
    return True


def _build_initial_state(prompt: str, state_schema: Optional[str] = None) -> Dict[str, Any]:
    """Build initial state for LangGraph (messages + optional topic)."""
    try:
        from langchain_core.messages import HumanMessage
    except ImportError:
        raise ImportError("langchain_core is required for eval runner. pip install langchain-core")
    return {
        "messages": [HumanMessage(content=prompt)],
        "topic": "",
    }


def run_evals(
    eval_json_path: str,
    graph_spec: str,
    *,
    max_cases: Optional[int] = None,
    collect_path: bool = True,
) -> Tuple[EvalMetrics, List[Dict[str, Any]]]:
    """
    Load eval JSON, run each test case against the graph, and compute concrete metrics.

    Args:
        eval_json_path: Path to eval JSON (from generate-eval-tests).
        graph_spec: Graph to run, e.g. 'samples.langgraph.langgraph_multi_agent_app:graph'.
        max_cases: If set, run only this many cases (for quick smoke tests).
        collect_path: If True and graph_structure present, stream to collect node path for valid_path eval.

    Returns:
        (EvalMetrics, list of per-case results with keys: prompt, expected_tool, passed_tool_selection,
         passed_invocation, path_valid, path, tools_called, etc.)
    """
    data = load_eval_json(eval_json_path)
    tool_manifest = data.get("tool_manifest") or []
    test_cases = data.get("test_cases") or []
    graph_structure = data.get("graph_structure")

    if max_cases is not None:
        test_cases = test_cases[:max_cases]

    graph = _load_graph(graph_spec)
    allowed = _allowed_edges(graph_structure) if graph_structure else set()
    tool_names = {t["name"] for t in tool_manifest if isinstance(t, dict) and t.get("name")}

    results: List[Dict[str, Any]] = []
    passed_selection = 0
    passed_path_count = 0
    total_with_path = 0
    per_tool_correct: Dict[str, int] = {}
    per_tool_total: Dict[str, int] = {}

    for tc in test_cases:
        prompt = tc.get("prompt") or ""
        expected_tool = (tc.get("expected_tool") or "").strip()
        initial = _build_initial_state(prompt)

        tools_called: List[Tuple[str, Dict[str, Any]]] = []
        path: List[str] = []

        try:
            final_state = graph.invoke(initial)
            tools_called = _extract_tool_calls_from_state(final_state)
            if collect_path and graph_structure:
                path = _get_node_path_from_stream(graph, initial)
                if path:
                    total_with_path += 1
                    if _is_path_valid(path, allowed):
                        passed_path_count += 1
        except Exception as e:
            logger.warning("Eval run failed for prompt %s: %s", prompt[:50], e)

        called_names = [name for name, _ in tools_called]
        passed_tool_selection = expected_tool in called_names
        if passed_tool_selection:
            passed_selection += 1

        if expected_tool:
            per_tool_total[expected_tool] = per_tool_total.get(expected_tool, 0) + 1
            if passed_tool_selection:
                per_tool_correct[expected_tool] = per_tool_correct.get(expected_tool, 0) + 1

        path_valid: Optional[bool] = None
        if path and allowed:
            path_valid = _is_path_valid(path, allowed)

        eval_type = tc.get("eval_type") or "tool_selection"
        results.append({
            "prompt": prompt,
            "expected_tool": expected_tool,
            "eval_type": eval_type,
            "passed_tool_selection": passed_tool_selection,
            "passed_invocation": passed_tool_selection,
            "tools_called": [{"name": n, "args": a} for n, a in tools_called],
            "path": path,
            "path_valid": path_valid,
            "error": None,
        })

    total = len(results)
    tool_selection_accuracy = (passed_selection / total) if total else 0.0
    tool_invocation_presence = tool_selection_accuracy  # same definition
    valid_path_rate: Optional[float] = None
    if total_with_path and graph_structure:
        valid_path_rate = passed_path_count / total_with_path

    tool_coverage = {}
    for name in tool_names:
        tot = per_tool_total.get(name, 0)
        cor = per_tool_correct.get(name, 0)
        tool_coverage[name] = (cor / tot) if tot else 0.0

    metrics = EvalMetrics(
        tool_selection_accuracy=tool_selection_accuracy,
        tool_invocation_presence=tool_invocation_presence,
        valid_path_rate=valid_path_rate,
        tool_coverage=tool_coverage,
        total_cases=total,
        passed_tool_selection=passed_selection,
        passed_valid_path=passed_path_count if total_with_path else None,
        total_with_path=total_with_path or None,
    )
    return metrics, results


def main() -> int:
    """CLI entry point for running evals."""
    import argparse
    parser = argparse.ArgumentParser(description="Run concrete evals (tool-selection, valid path, coverage)")
    parser.add_argument("--eval-json", required=True, help="Path to eval JSON from generate-eval-tests")
    parser.add_argument("--graph", required=True, help="Graph spec: module.path:attribute (e.g. samples.langgraph.langgraph_multi_agent_app:graph)")
    parser.add_argument("--max-cases", type=int, default=None, help="Max test cases to run (default: all)")
    parser.add_argument("--no-path", action="store_true", help="Do not collect node path (skip valid_path eval)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    metrics, results = run_evals(
        args.eval_json,
        args.graph,
        max_cases=args.max_cases,
        collect_path=not args.no_path,
    )
    print("Eval results:")
    print(f"  Tool selection accuracy: {metrics.passed_tool_selection}/{metrics.total_cases} = {metrics.tool_selection_accuracy:.2%}")
    print(f"  Tool invocation presence: {metrics.tool_invocation_presence:.2%}")
    if metrics.valid_path_rate is not None:
        print(f"  Valid path rate: {metrics.passed_valid_path}/{metrics.total_with_path} = {metrics.valid_path_rate:.2%}")
    print("  Tool coverage (recall per tool):")
    for name, recall in sorted(metrics.tool_coverage.items()):
        print(f"    {name}: {recall:.2%}")
    if args.verbose:
        for i, r in enumerate(results):
            print(f"  Case {i+1}: eval_type={r.get('eval_type', 'tool_selection')} expected={r['expected_tool']} passed={r['passed_tool_selection']} path_valid={r.get('path_valid')} tools_called={[t['name'] for t in r['tools_called']]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
