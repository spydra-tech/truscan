"""SARIF output formatter for GitHub Code Scanning."""

import json
from typing import Dict, List

from ..models import Finding, ScanResult


class SARIFFormatter:
    """Formatter for SARIF (Static Analysis Results Interchange Format) output."""

    TOOL_NAME = "llm-scan"
    TOOL_VERSION = "0.1.0"

    def format(self, result: ScanResult) -> Dict:
        """
        Format scan result as SARIF.

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
                            "informationUri": "https://github.com/yourorg/llm-scan",
                            "rules": self._extract_rules(result.findings),
                        }
                    },
                    "results": self._format_results(result.findings),
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

    def _format_results(self, findings: List[Finding]) -> List[Dict]:
        """Format findings as SARIF results."""
        results = []
        for finding in findings:
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
                                "uri": finding.location.file_path,
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
                    thread_flows.append(
                        {
                            "locations": [
                                {
                                    "location": {
                                        "physicalLocation": {
                                            "artifactLocation": {
                                                "uri": step.file_path,
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

    def write(self, result: ScanResult, output_path: str) -> None:
        """Write SARIF output to file."""
        sarif_data = self.format(result)
        with open(output_path, "w") as f:
            json.dump(sarif_data, f, indent=2)
