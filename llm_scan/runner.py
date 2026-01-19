"""Main runner for the LLM scanner."""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import List, Optional

from .config import ScanConfig
from .enrich.uploader import StubUploader, Uploader
from .engine.semgrep_engine import SemgrepEngine
from .models import ScanRequest, ScanResponse, ScanResult
from .output.console import ConsoleFormatter
from .output.json import JSONFormatter
from .output.sarif import SARIFFormatter

# Configure logging
logger = logging.getLogger(__name__)


def find_files(
    paths: List[str],
    include_patterns: List[str],
    exclude_patterns: List[str],
    respect_gitignore: bool = True,
) -> List[str]:
    """
    Find files to scan based on paths and patterns.

    Args:
        paths: List of paths to scan
        include_patterns: Include patterns (e.g., ["*.py"])
        exclude_patterns: Exclude patterns
        respect_gitignore: Whether to respect .gitignore

    Returns:
        List of file paths
    """
    logger.info(f"Finding files to scan from {len(paths)} path(s)")
    logger.debug(f"Paths: {paths}")
    logger.debug(f"Include patterns: {include_patterns}")
    logger.debug(f"Exclude patterns: {exclude_patterns}")
    logger.debug(f"Respect .gitignore: {respect_gitignore}")
    
    scanned_files = []
    gitignore_patterns = []

    if respect_gitignore:
        # Try to load .gitignore patterns
        gitignore_path = Path(".gitignore")
        if gitignore_path.exists():
            logger.debug(f"Loading .gitignore patterns from {gitignore_path}")
            with open(gitignore_path) as f:
                gitignore_patterns = [
                    line.strip() for line in f if line.strip() and not line.startswith("#")
                ]
            logger.debug(f"Loaded {len(gitignore_patterns)} .gitignore patterns")
        else:
            logger.debug("No .gitignore file found")

    for path in paths:
        path_obj = Path(path)
        logger.debug(f"Processing path: {path}")
        if path_obj.is_file():
            logger.debug(f"Found file: {path_obj.absolute()}")
            scanned_files.append(str(path_obj.absolute()))
        elif path_obj.is_dir():
            logger.debug(f"Walking directory: {path}")
            file_count = 0
            # Walk directory
            for root, dirs, files in os.walk(path):
                # Filter directories based on exclude patterns
                original_dirs_count = len(dirs)
                dirs[:] = [
                    d
                    for d in dirs
                    if not any(
                        Path(root) / d == Path(exclude) or str(Path(root) / d).startswith(exclude)
                        for exclude in exclude_patterns
                    )
                ]
                if len(dirs) < original_dirs_count:
                    logger.debug(f"Excluded {original_dirs_count - len(dirs)} directory(ies) in {root}")

                for file in files:
                    file_path = Path(root) / file
                    file_str = str(file_path)

                    # Check exclude patterns
                    if any(
                        file_path.match(exclude) or file_str.startswith(exclude)
                        for exclude in exclude_patterns
                    ):
                        logger.debug(f"Excluded file (pattern): {file_str}")
                        continue

                    # Check gitignore
                    if respect_gitignore and gitignore_patterns:
                        if any(
                            file_path.match(pattern) or pattern in file_str
                            for pattern in gitignore_patterns
                        ):
                            logger.debug(f"Excluded file (.gitignore): {file_str}")
                            continue

                    # Check include patterns
                    if include_patterns:
                        if not any(
                            file_path.match(pattern) for pattern in include_patterns
                        ):
                            logger.debug(f"Excluded file (not in include patterns): {file_str}")
                            continue

                    scanned_files.append(file_str)
                    file_count += 1
            logger.debug(f"Found {file_count} file(s) in directory {path}")
        else:
            logger.warning(f"Path does not exist or is not a file/directory: {path}")

    logger.info(f"Found {len(scanned_files)} file(s) to scan")
    return scanned_files


def run_scan(config: ScanConfig, uploader: Optional[Uploader] = None) -> ScanResult:
    """
    Run a scan with the given configuration.

    Args:
        config: Scan configuration
        uploader: Optional uploader for results

    Returns:
        ScanResult object
    """
    logger.info("=" * 80)
    logger.info("Starting LLM Security Scan")
    logger.info("=" * 80)
    logger.info(f"Configuration:")
    logger.info(f"  Paths: {config.paths}")
    logger.info(f"  Rules directory: {config.rules_dir}")
    logger.info(f"  Include patterns: {config.include_patterns}")
    logger.info(f"  Exclude patterns: {config.exclude_patterns}")
    logger.info(f"  Respect .gitignore: {config.respect_gitignore}")
    logger.info(f"  Enabled rules: {config.enabled_rules}")
    logger.info(f"  Disabled rules: {config.disabled_rules}")
    logger.info(f"  Severity filter: {config.severity_filter}")
    logger.info(f"  Output format: {config.output_format}")
    
    start_time = time.time()

    # Find files to scan
    logger.info("")
    logger.info("Step 1: Discovering files to scan...")
    scanned_files = find_files(
        config.paths,
        config.include_patterns,
        config.exclude_patterns,
        config.respect_gitignore,
    )
    logger.info(f"✓ Found {len(scanned_files)} file(s) to scan")

    # Initialize engine
    logger.info("")
    logger.info("Step 2: Initializing Semgrep engine...")
    logger.debug(f"Resolved rules directory: {config.resolve_rules_dir()}")
    engine = SemgrepEngine(config)
    logger.info("✓ Engine initialized")

    # Run scan
    logger.info("")
    logger.info("Step 3: Running Semgrep scan...")
    logger.debug(f"Scanning {len(scanned_files)} file(s) with Semgrep")
    findings = engine.scan()
    logger.info(f"✓ Scan completed, found {len(findings)} finding(s)")

    # Get rules loaded (from rules directory)
    logger.info("")
    logger.info("Step 4: Collecting rule metadata...")
    rules_loaded = []
    rules_dir = Path(config.resolve_rules_dir())
    if rules_dir.exists():
        for rule_file in rules_dir.rglob("*.yaml"):
            rules_loaded.append(str(rule_file))
        logger.info(f"✓ Loaded {len(rules_loaded)} rule file(s)")
    else:
        logger.warning(f"Rules directory not found: {rules_dir}")

    scan_duration = time.time() - start_time

    # Group findings by severity
    findings_by_severity = {}
    for finding in findings:
        severity = finding.severity.value
        findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1

    logger.info("")
    logger.info("Step 5: Generating scan results...")
    result = ScanResult(
        findings=findings,
        scanned_files=scanned_files,
        rules_loaded=rules_loaded,
        scan_duration_seconds=scan_duration,
    )
    logger.info("✓ Results generated")

    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("Scan Summary")
    logger.info("=" * 80)
    logger.info(f"  Files scanned: {len(scanned_files)}")
    logger.info(f"  Rules loaded: {len(rules_loaded)}")
    logger.info(f"  Total findings: {len(findings)}")
    if findings_by_severity:
        logger.info("  Findings by severity:")
        for severity, count in sorted(findings_by_severity.items(), key=lambda x: ["critical", "high", "medium", "low", "info"].index(x[0]) if x[0] in ["critical", "high", "medium", "low", "info"] else 99):
            logger.info(f"    {severity.upper()}: {count}")
    logger.info(f"  Scan duration: {scan_duration:.2f}s")
    logger.info("=" * 80)

    # Optionally upload
    if uploader:
        logger.info("")
        logger.info("Step 6: Uploading results...")
        api_key = os.getenv("LLM_SCAN_API_KEY")
        if api_key:
            logger.debug("API key found in environment")
        else:
            logger.debug("No API key found in environment")
        uploader.upload(result, api_key)
        logger.info("✓ Upload completed")

    return result


def run_scan_for_vscode(request: ScanRequest) -> ScanResponse:
    """
    Run a scan for VS Code extension.

    Args:
        request: Scan request from VS Code

    Returns:
        ScanResponse object
    """
    logger.info("VS Code scan request received")
    logger.debug(f"Request: paths={request.paths}, rules_dir={request.rules_dir}")
    try:
        # Convert request to config
        config = ScanConfig(
            paths=request.paths,
            rules_dir=request.rules_dir or "llm_scan/rules",
            include_patterns=request.include_patterns,
            exclude_patterns=request.exclude_patterns,
            enabled_rules=request.enabled_rules,
            severity_filter=request.severity_filter,
            output_format=request.output_format,
        )

        result = run_scan(config)
        logger.info("VS Code scan completed successfully")
        return ScanResponse(success=True, result=result)

    except Exception as e:
        logger.error(f"VS Code scan failed: {e}", exc_info=True)
        return ScanResponse(success=False, error=str(e))


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LLM Security Scanner - Detect AI/LLM-specific vulnerabilities"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Paths to scan (files or directories)",
    )
    parser.add_argument(
        "--rules",
        default="llm_scan/rules/python",
        help="Path to rules directory (default: llm_scan/rules/python)",
    )
    parser.add_argument(
        "--format",
        choices=["sarif", "json", "console"],
        default="console",
        help="Output format (default: console)",
    )
    parser.add_argument(
        "--out",
        help="Output file path (required for sarif/json, optional for console)",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Include patterns (e.g., --include '*.py')",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude patterns (e.g., --exclude 'tests/')",
    )
    parser.add_argument(
        "--enable-rule",
        action="append",
        help="Enable specific rule IDs",
    )
    parser.add_argument(
        "--disable-rule",
        action="append",
        help="Disable specific rule IDs",
    )
    parser.add_argument(
        "--severity",
        action="append",
        choices=["critical", "high", "medium", "low", "info"],
        help="Filter by severity",
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Do not respect .gitignore",
    )
    parser.add_argument(
        "--upload",
        help="Upload endpoint URL (stub implementation)",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.WARNING
    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger.setLevel(log_level)

    # Build config
    from .models import Severity

    severity_filter = None
    if args.severity:
        severity_filter = [Severity(s) for s in args.severity]

    config = ScanConfig(
        paths=args.paths,
        rules_dir=args.rules,
        include_patterns=args.include or [],
        exclude_patterns=args.exclude or [],
        enabled_rules=args.enable_rule,
        disabled_rules=args.disable_rule,
        severity_filter=severity_filter,
        output_format=args.format,
        output_file=args.out,
        respect_gitignore=not args.no_gitignore,
    )

    # Setup uploader if requested
    uploader = None
    if args.upload:
        uploader = StubUploader(endpoint=args.upload)

    # Run scan
    try:
        logger.info("")
        result = run_scan(config, uploader)

        # Format output
        logger.info("")
        logger.info("Step 7: Formatting output...")
        if args.format == "sarif":
            logger.debug("Using SARIF formatter")
            formatter = SARIFFormatter()
            if args.out:
                logger.info(f"Writing SARIF output to {args.out}")
                formatter.write(result, args.out)
                logger.info("✓ SARIF output written")
            else:
                logger.error("--out is required for SARIF format")
                print("Error: --out is required for SARIF format")
                return 1
        elif args.format == "json":
            logger.debug("Using JSON formatter")
            formatter = JSONFormatter()
            if args.out:
                logger.info(f"Writing JSON output to {args.out}")
                formatter.write(result, args.out)
                logger.info("✓ JSON output written")
            else:
                # Print to stdout
                logger.debug("Writing JSON output to stdout")
                import json
                print(json.dumps(formatter.format(result), indent=2))
        else:  # console
            logger.debug("Using console formatter")
            formatter = ConsoleFormatter()
            output = formatter.format(result)
            print(output)
            if args.out:
                logger.info(f"Writing console output to {args.out}")
                formatter.write(result, args.out)
                logger.info("✓ Console output written")
        logger.info("✓ Output formatting completed")

        # Return exit code based on findings
        exit_code = 1 if result.findings else 0
        logger.info(f"Scan completed with exit code {exit_code}")
        return exit_code

    except Exception as e:
        logger.error(f"Scan failed with error: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
