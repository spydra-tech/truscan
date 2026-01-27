"""JSON output formatter."""

import json
from typing import Dict

from ..models import ScanResult


class JSONFormatter:
    """Formatter for JSON output."""

    def format(self, result: ScanResult) -> Dict:
        """
        Format scan result as JSON.

        Returns:
            JSON-serializable dictionary
        """
        return {
            "version": "1.0",
            "tool": {
                "name": "trusys-llm-scan",
                "version": "1.0.5",
            },
            "runs": [
                {
                    "findings": result.to_dict()["findings"],
                    "scanned_files": result.scanned_files,
                    "rules_loaded": result.rules_loaded,
                    "scan_duration_seconds": result.scan_duration_seconds,
                    "metadata": result.metadata,
                }
            ],
        }

    def write(self, result: ScanResult, output_path: str) -> None:
        """Write JSON output to file."""
        json_data = self.format(result)
        with open(output_path, "w") as f:
            json.dump(json_data, f, indent=2)
