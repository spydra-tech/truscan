"""Data models for findings and scan results."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(str, Enum):
    """Severity levels for findings."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Category(str, Enum):
    """Vulnerability categories."""

    CODE_INJECTION = "code-injection"
    COMMAND_INJECTION = "command-injection"
    PROMPT_INJECTION = "prompt-injection"
    DATA_EXPOSURE = "data-exposure"
    INSECURE_DESERIALIZATION = "insecure-deserialization"
    OTHER = "other"


@dataclass
class Location:
    """Source code location."""

    file_path: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    snippet: Optional[str] = None


@dataclass
class DataflowStep:
    """A step in a dataflow path."""

    file_path: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    message: str


@dataclass
class AIVerdict:
    """AI analysis verdict for a finding."""

    is_false_positive: bool
    confidence: float  # 0.0 to 1.0
    reasoning: str
    suggested_severity: Optional[Severity] = None
    enhanced_remediation: Optional[str] = None  # AI-generated remediation guidance
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Finding:
    """A security finding."""

    rule_id: str
    message: str
    severity: Severity
    category: Category
    location: Location
    cwe: Optional[str] = None
    remediation: Optional[str] = None
    dataflow_path: List[DataflowStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    ai_analysis: Optional[AIVerdict] = None
    ai_filtered: bool = False
    source: str = "semgrep"  # Track source: "semgrep" or "ai-enhanced"

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        result = {
            "rule_id": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "location": {
                "file_path": self.location.file_path,
                "start_line": self.location.start_line,
                "start_column": self.location.start_column,
                "end_line": self.location.end_line,
                "end_column": self.location.end_column,
                "snippet": self.location.snippet,
            },
            "cwe": self.cwe,
            "remediation": self.remediation,
            "dataflow_path": [
                {
                    "file_path": step.file_path,
                    "start_line": step.start_line,
                    "start_column": step.start_column,
                    "end_line": step.end_line,
                    "end_column": step.end_column,
                    "message": step.message,
                }
                for step in self.dataflow_path
            ],
            "metadata": self.metadata,
        }
        
        # Add source tracking
        result["source"] = self.source
        
        # Add AI analysis if present
        if self.ai_analysis:
            result["ai_analysis"] = {
                "is_false_positive": self.ai_analysis.is_false_positive,
                "confidence": self.ai_analysis.confidence,
                "reasoning": self.ai_analysis.reasoning,
                "suggested_severity": (
                    self.ai_analysis.suggested_severity.value
                    if self.ai_analysis.suggested_severity
                    else None
                ),
                "enhanced_remediation": self.ai_analysis.enhanced_remediation,
                "additional_context": self.ai_analysis.additional_context,
            }
            result["ai_filtered"] = self.ai_filtered
            # If AI provided enhanced remediation, use it
            if self.ai_analysis.enhanced_remediation:
                result["remediation"] = self.ai_analysis.enhanced_remediation
                result["remediation_source"] = "ai-enhanced"
            elif self.remediation:
                result["remediation_source"] = "semgrep"
        
        return result


@dataclass
class ScanResult:
    """Complete scan result."""

    findings: List[Finding]
    scanned_files: List[str]
    rules_loaded: List[str]
    scan_duration_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert scan result to dictionary."""
        return {
            "findings": [f.to_dict() for f in self.findings],
            "scanned_files": self.scanned_files,
            "rules_loaded": self.rules_loaded,
            "scan_duration_seconds": self.scan_duration_seconds,
            "metadata": self.metadata,
        }


@dataclass
class ScanRequest:
    """Request for a scan (used by VS Code extension)."""

    paths: List[str]
    rules_dir: Optional[str] = None
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    enabled_rules: Optional[List[str]] = None
    severity_filter: Optional[List[Severity]] = None
    output_format: str = "json"


@dataclass
class ScanResponse:
    """Response from a scan (used by VS Code extension)."""

    success: bool
    result: Optional[ScanResult] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert scan response to dictionary."""
        if self.success and self.result:
            return {
                "success": True,
                "result": self.result.to_dict(),
            }
        return {
            "success": False,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# FastMCP evaluation test generation
# ---------------------------------------------------------------------------


@dataclass
class MCPToolParameter:
    """Parameter of an MCP tool."""

    name: str
    type: str  # e.g. "str", "int"

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "type": self.type}


@dataclass
class MCPToolDefinition:
    """Extracted FastMCP tool/resource/prompt handler definition."""

    name: str
    description: str
    parameters: List[MCPToolParameter]
    decorator: str  # "tool" | "async_tool" | "resource" | "prompt"
    source_file: Optional[str] = None
    line: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "name": self.name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "decorator": self.decorator,
        }
        if self.source_file is not None:
            d["source_file"] = self.source_file
        if self.line is not None:
            d["line"] = self.line
        return d

    def to_manifest_dict(self) -> Dict[str, Any]:
        """Minimal dict for AI payload (no paths)."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "decorator": self.decorator,
        }


@dataclass
class EvalTestCase:
    """Single evaluation test case: prompt + expected tool + ground truth."""

    prompt: str
    expected_tool: str
    ground_truth: str
    expected_args: Optional[Dict[str, Any]] = None
    category: Optional[str] = None  # e.g. "tool-invocation", "security"

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "prompt": self.prompt,
            "expected_tool": self.expected_tool,
            "ground_truth": self.ground_truth,
        }
        if self.expected_args is not None:
            d["expected_args"] = self.expected_args
        if self.category is not None:
            d["category"] = self.category
        return d


@dataclass
class EvalTestResult:
    """Result of eval test generation: manifest + test cases + metadata."""

    tool_manifest: List[MCPToolDefinition]
    test_cases: List[EvalTestCase]
    generation_duration_seconds: Optional[float] = None
    ai_model_used: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_manifest": [t.to_dict() for t in self.tool_manifest],
            "test_cases": [tc.to_dict() for tc in self.test_cases],
            "meta": {
                "generation_duration_seconds": self.generation_duration_seconds,
                "ai_model_used": self.ai_model_used,
            },
        }
