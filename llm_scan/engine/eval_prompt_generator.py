"""Generate evaluation test cases from MCP tool manifest using AI (manifest-only payload)."""

import json
import logging
import time
from typing import List, Optional

from ..config import ScanConfig
from ..models import EvalTestCase, MCPToolDefinition
from .ai_providers import AIProvider, create_provider

logger = logging.getLogger(__name__)

EVAL_SYSTEM_PROMPT = """You are an expert at writing evaluation test cases for AI agents that use MCP (Model Context Protocol) tools.

Given a list of MCP tools (each with name, description, and parameters), generate natural-language user prompts that would cause a typical LLM agent to call each tool.

For each tool, produce 1-3 short user prompts that a user might say and that should lead the agent to invoke that specific tool (and optionally with reasonable arguments).

Respond ONLY with valid JSON in this exact format (no markdown, no explanation):
{
  "test_cases": [
    {
      "prompt": "the user prompt text",
      "expected_tool": "tool_name",
      "ground_truth": "Brief description of expected behavior (e.g. Agent should call tool X with ...)"
    }
  ]
}
"""

# Max tools per AI request to stay within context limits
MAX_TOOLS_PER_REQUEST = 30


def _build_user_prompt(manifest_list: List[dict], max_prompts_per_tool: int) -> str:
    """Build user prompt containing only the tool manifest (no paths, no source code)."""
    manifest_json = json.dumps(manifest_list, indent=2)
    return f"""Generate evaluation test cases for the following MCP tools.

Generate up to {max_prompts_per_tool} natural-language user prompt(s) per tool that would lead an agent to call that tool. Vary the prompts (e.g. different phrasings, different example inputs).

MCP tools (name, description, parameters only):
{manifest_json}

Respond with a single JSON object containing a "test_cases" array as specified in the system prompt."""


def _parse_ai_response(response: dict) -> List[EvalTestCase]:
    """Parse AI response into EvalTestCase list. Returns empty list on parse failure."""
    if not isinstance(response, dict):
        return []
    raw = response.get("test_cases")
    if not isinstance(raw, list):
        return []
    cases: List[EvalTestCase] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        prompt = item.get("prompt")
        expected_tool = item.get("expected_tool")
        ground_truth = item.get("ground_truth")
        if not prompt or not expected_tool or not ground_truth:
            continue
        cases.append(
            EvalTestCase(
                prompt=str(prompt).strip(),
                expected_tool=str(expected_tool).strip(),
                ground_truth=str(ground_truth).strip(),
                expected_args=item.get("expected_args"),
                category=item.get("category"),
            )
        )
    return cases


def generate_eval_tests(
    tools: List[MCPToolDefinition],
    config: ScanConfig,
    max_prompts_per_tool: int = 3,
) -> List[EvalTestCase]:
    """
    Generate evaluation test cases from tool manifest using AI.

    Only the tool manifest (name, description, parameters) is sent to the AI; no source code or paths.

    Args:
        tools: List of extracted MCP tool definitions.
        config: Scan config (used for AI provider, model, api_key).
        max_prompts_per_tool: Max prompts to generate per tool.

    Returns:
        List of EvalTestCase. Empty on failure or if tools is empty.
    """
    if not tools:
        return []
    manifest_list = [t.to_manifest_dict() for t in tools]
    all_cases: List[EvalTestCase] = []
    provider: Optional[AIProvider] = None
    try:
        provider = create_provider(
            config.ai_provider,
            api_key=config.ai_api_key,
            model=config.ai_model,
        )
    except Exception as e:
        logger.error("Failed to create AI provider for eval test generation: %s", e)
        return []

    # Batch by MAX_TOOLS_PER_REQUEST
    for i in range(0, len(manifest_list), MAX_TOOLS_PER_REQUEST):
        batch = manifest_list[i : i + MAX_TOOLS_PER_REQUEST]
        user_prompt = _build_user_prompt(batch, max_prompts_per_tool)
        try:
            response = provider.analyze(user_prompt, system_prompt=EVAL_SYSTEM_PROMPT)
            all_cases.extend(_parse_ai_response(response))
        except json.JSONDecodeError as e:
            logger.warning("Eval test generation: AI response was not valid JSON: %s", e)
        except Exception as e:
            logger.warning("Eval test generation request failed: %s", e)
    return all_cases


def run_eval_test_generation(
    scanned_files: List[str],
    config: ScanConfig,
    max_prompts_per_tool: int = 3,
) -> tuple:
    """
    Extract tools from files, then generate eval test cases via AI.

    Returns:
        (tool_manifest, test_cases, duration_seconds, ai_model_used).
    """
    from .mcp_extractor import extract_from_files

    start = time.time()
    tools = extract_from_files(scanned_files)
    if not tools:
        return [], [], time.time() - start, None
    cases = generate_eval_tests(tools, config, max_prompts_per_tool)
    duration = time.time() - start
    return tools, cases, duration, config.ai_model
