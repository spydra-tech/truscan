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

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
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
