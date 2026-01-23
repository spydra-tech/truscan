"""Configuration management for the scanner."""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .models import Severity

logger = logging.getLogger(__name__)


@dataclass
class ScanConfig:
    """Configuration for a scan."""

    paths: List[str]
    rules_dir: str
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    enabled_rules: Optional[List[str]] = None
    disabled_rules: Optional[List[str]] = None
    severity_filter: Optional[List[Severity]] = None
    output_format: str = "console"
    output_file: Optional[str] = None
    respect_gitignore: bool = True
    max_target_bytes: int = 1_000_000  # 1MB per file limit
    # AI filtering configuration
    enable_ai_filter: bool = False
    ai_provider: str = "openai"  # "openai", "anthropic", "local"
    ai_api_key: Optional[str] = None
    ai_model: str = "gpt-4"  # Model name for the provider
    ai_confidence_threshold: float = 0.7  # Only filter if confidence > threshold
    ai_batch_size: int = 10  # Process findings in batches
    ai_cache_enabled: bool = True  # Cache AI responses
    ai_analyze_rules: Optional[List[str]] = None  # Specific rules to analyze (None = all)

    @classmethod
    def from_dict(cls, data: dict) -> "ScanConfig":
        """Create config from dictionary."""
        severity_filter = None
        if "severity_filter" in data and data["severity_filter"]:
            severity_filter = [Severity(s) for s in data["severity_filter"]]

        return cls(
            paths=data["paths"],
            rules_dir=data.get("rules_dir", "llm_scan/rules"),
            include_patterns=data.get("include_patterns", []),
            exclude_patterns=data.get("exclude_patterns", []),
            enabled_rules=data.get("enabled_rules"),
            disabled_rules=data.get("disabled_rules"),
            severity_filter=severity_filter,
            output_format=data.get("output_format", "console"),
            output_file=data.get("output_file"),
            respect_gitignore=data.get("respect_gitignore", True),
            max_target_bytes=data.get("max_target_bytes", 1_000_000),
            enable_ai_filter=data.get("enable_ai_filter", False),
            ai_provider=data.get("ai_provider", "openai"),
            ai_api_key=data.get("ai_api_key"),
            ai_model=data.get("ai_model", "gpt-4"),
            ai_confidence_threshold=data.get("ai_confidence_threshold", 0.7),
            ai_batch_size=data.get("ai_batch_size", 10),
            ai_cache_enabled=data.get("ai_cache_enabled", True),
            ai_analyze_rules=data.get("ai_analyze_rules"),
        )

    def get_default_rules_dir(self) -> str:
        """Get default rules directory relative to package."""
        package_dir = Path(__file__).parent.parent
        return str(package_dir / "llm_scan" / "rules" / "python")

    def resolve_rules_dir(self) -> str:
        """Resolve rules directory path."""
        logger.debug(f"Resolving rules directory: {self.rules_dir}")
        if os.path.isabs(self.rules_dir):
            logger.debug(f"Rules directory is absolute: {self.rules_dir}")
            return self.rules_dir
        # Try relative to current working directory first
        if os.path.exists(self.rules_dir):
            resolved = os.path.abspath(self.rules_dir)
            logger.debug(f"Found rules directory (relative to CWD): {resolved}")
            return resolved
        # Fall back to package default
        default = self.get_default_rules_dir()
        logger.debug(f"Trying default rules directory: {default}")
        if os.path.exists(default):
            logger.debug(f"Using default rules directory: {default}")
            return default
        resolved = os.path.abspath(self.rules_dir)
        logger.debug(f"Using resolved rules directory: {resolved}")
        return resolved


@dataclass
class RulePack:
    """Metadata for a rule pack."""

    name: str
    languages: List[str]
    path: str
    version: str = "1.0.0"
    default_enabled: bool = True
    description: Optional[str] = None
