"""SARIF output formatter for GitHub Code Scanning."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from ..models import Finding, ScanResult


def _to_relative_uri(file_path: str, root_path: Optional[str] = None) -> str:
    """Convert absolute path to URI relative to root (forward slashes)."""
    if not file_path or file_path == "unknown":
        return file_path
    root = Path(root_path or os.getcwd()).resolve()
    path_obj = Path(file_path).resolve()
    try:
        rel = path_obj.relative_to(root)
    except ValueError:
        # path not under root (e.g. different drive), return as-is but normalized
        return path_obj.as_posix()
    return rel.as_posix()


class SARIFFormatter:
    """Formatter for SARIF (Static Analysis Results Interchange Format) output."""

    TOOL_NAME = "trusys-llm-scan"
    TOOL_VERSION = "1.0.5"

    def format(self, result: ScanResult, root_path: Optional[str] = None) -> Dict:
        """
        Format scan result as SARIF.

        Args:
            result: Scan result with findings.
            root_path: Base path for relative artifact URIs (default: cwd). Use repo root in CI.

        Returns:
            SARIF JSON structure
        """
        # SARIF version 2.1.0
        sarif = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": self.TOOL_NAME,
                            "version": self.TOOL_VERSION,
                            "informationUri": "https://github.com/spydra-tech/truscan",
                            "rules": self._extract_rules(result.findings),
                        }
                    },
                    "results": self._format_results(result.findings, root_path),
                    "invocations": [
                        {
                            "executionSuccessful": True,
                            "exitCode": 0 if not result.findings else 1,
                        }
                    ],
                }
            ],
        }

        return sarif

    def _extract_rules(self, findings: List[Finding]) -> List[Dict]:
        """Extract unique rules from findings."""
        rules = {}
        for finding in findings:
            if finding.rule_id not in rules:
                rules[finding.rule_id] = {
                    "id": finding.rule_id,
                    "name": finding.rule_id,
                    "shortDescription": {
                        "text": finding.message,
                    },
                    "fullDescription": {
                        "text": finding.message,
                    },
                    "defaultConfiguration": {
                        "level": self._severity_to_sarif_level(finding.severity),
                    },
                    "properties": {
                        "category": finding.category.value,
                    },
                }
                if finding.cwe:
                    rules[finding.rule_id]["properties"]["cwe"] = finding.cwe
                if finding.remediation:
                    rules[finding.rule_id]["help"] = {
                        "text": finding.remediation,
                    }

        return list(rules.values())

    def _format_results(self, findings: List[Finding], root_path: Optional[str] = None) -> List[Dict]:
        """Format findings as SARIF results. Artifact URIs are relative to root_path."""
        results = []
        for finding in findings:
            uri = _to_relative_uri(finding.location.file_path, root_path)
            result = {
                "ruleId": finding.rule_id,
                "level": self._severity_to_sarif_level(finding.severity),
                "message": {
                    "text": finding.message,
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": uri,
                            },
                            "region": {
                                "startLine": finding.location.start_line,
                                "startColumn": finding.location.start_column,
                                "endLine": finding.location.end_line,
                                "endColumn": finding.location.end_column,
                            },
                        }
                    }
                ],
            }

            # Add code snippet if available
            if finding.location.snippet:
                result["locations"][0]["physicalLocation"]["region"]["snippet"] = {
                    "text": finding.location.snippet,
                }

            # Add dataflow path if available
            if finding.dataflow_path:
                code_flows = []
                thread_flows = []
                for step in finding.dataflow_path:
                    step_uri = _to_relative_uri(step.file_path, root_path)
                    thread_flows.append(
                        {
                            "locations": [
                                {
                                    "location": {
                                        "physicalLocation": {
                                            "artifactLocation": {
                                                "uri": step_uri,
                                            },
                                            "region": {
                                                "startLine": step.start_line,
                                                "startColumn": step.start_column,
                                                "endLine": step.end_line,
                                                "endColumn": step.end_column,
                                            },
                                        },
                                        "message": {"text": step.message},
                                    }
                                }
                            ]
                        }
                    )
                code_flows.append({"threadFlows": thread_flows})
                result["codeFlows"] = code_flows

            results.append(result)

        return results

    def _severity_to_sarif_level(self, severity) -> str:
        """Convert severity to SARIF level."""
        mapping = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
            "info": "note",
        }
        return mapping.get(severity.value, "warning")

    def write(self, result: ScanResult, output_path: str, root_path: Optional[str] = None) -> None:
        """Write SARIF output to file. Artifact URIs are relative to root_path (default: cwd)."""
        sarif_data = self.format(result, root_path=root_path)
        with open(output_path, "w") as f:
            json.dump(sarif_data, f, indent=2)
