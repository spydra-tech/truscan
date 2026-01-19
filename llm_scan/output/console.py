"""Console output formatter for human-readable output."""

from collections import defaultdict
from typing import Dict, List

from ..models import Finding, ScanResult


class ConsoleFormatter:
    """Formatter for console output."""

    SEVERITY_COLORS = {
        "critical": "\033[91m",  # Red
        "high": "\033[93m",  # Yellow
        "medium": "\033[94m",  # Blue
        "low": "\033[96m",  # Cyan
        "info": "\033[97m",  # White
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, result: ScanResult, use_color: bool = True) -> str:
        """
        Format scan result for console output.

        Args:
            result: Scan result to format
            use_color: Whether to use ANSI color codes

        Returns:
            Formatted string
        """
        if not result.findings:
            return f"\n{self.BOLD if use_color else ''}✓ No issues found{self.RESET if use_color else ''}\n"

        # Group findings by file
        findings_by_file = defaultdict(list)
        for finding in result.findings:
            findings_by_file[finding.location.file_path].append(finding)

        output = []
        output.append(
            f"\n{self.BOLD if use_color else ''}Scan Results{self.RESET if use_color else ''}\n"
        )
        output.append("=" * 80)
        output.append(
            f"Found {len(result.findings)} issue(s) in {len(findings_by_file)} file(s)\n"
        )

        # Sort files alphabetically
        for file_path in sorted(findings_by_file.keys()):
            findings = findings_by_file[file_path]
            output.append(f"\n{self.BOLD if use_color else ''}{file_path}{self.RESET if use_color else ''}")
            output.append("-" * 80)

            # Sort findings by line number
            findings.sort(key=lambda f: f.location.start_line)

            for finding in findings:
                severity_color = (
                    self.SEVERITY_COLORS.get(finding.severity.value, "")
                    if use_color
                    else ""
                )
                output.append(
                    f"  {severity_color}[{finding.severity.value.upper()}]{self.RESET if use_color else ''} "
                    f"{finding.rule_id}"
                )
                output.append(
                    f"    Line {finding.location.start_line}:{finding.location.start_column} - {finding.message}"
                )
                if finding.location.snippet:
                    # Show snippet with context
                    snippet_lines = finding.location.snippet.strip().split("\n")
                    for snippet_line in snippet_lines[:3]:  # Limit to 3 lines
                        output.append(f"    {snippet_line}")
                if finding.remediation:
                    output.append(f"    Remediation: {finding.remediation}")
                output.append("")

        output.append("=" * 80)
        output.append(
            f"\nScanned {len(result.scanned_files)} file(s) in {result.scan_duration_seconds:.2f}s"
        )
        output.append(f"Loaded {len(result.rules_loaded)} rule(s)\n")

        return "\n".join(output)

    def write(self, result: ScanResult, output_path: str) -> None:
        """Write console output to file."""
        formatted = self.format(result, use_color=False)
        with open(output_path, "w") as f:
            f.write(formatted)
