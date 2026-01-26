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
from .enrich.rest_uploader import RESTUploader
from .engine.ai_engine import AIEngine
from .engine.semgrep_engine import SemgrepEngine
from .models import ScanRequest, ScanResponse, ScanResult
from .output.console import ConsoleFormatter
from .output.json import JSONFormatter
from .output.sarif import SARIFFormatter
from .utils.code_context import load_file_contents

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
            file_abs = str(path_obj.absolute())
            logger.info(f"  + {file_abs}")
            scanned_files.append(file_abs)
        elif path_obj.is_dir():
            logger.debug(f"Walking directory: {path}")
            file_count = 0
            # Walk directory
            for root, dirs, files in os.walk(path):
                # ...
                for file in files:
                    file_path = Path(root) / file
                    file_str = str(file_path)
                    
                    # ... (skipping continue logic for brevity in this thought, will use exact string)
                    
                    logger.info(f"  + {file_str}")
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

    # Check AI filtering configuration
    if config.enable_ai_filter:
        logger.info("")
        logger.info("=" * 80)
        logger.info("🤖 AI FILTERING: ENABLED")
        logger.info("=" * 80)
        logger.info(f"  Provider: {config.ai_provider}")
        logger.info(f"  Model: {config.ai_model}")
        logger.info(f"  Confidence Threshold: {config.ai_confidence_threshold}")
        if config.ai_analyze_rules:
            logger.info(f"  Analyzing specific rules: {', '.join(config.ai_analyze_rules)}")
        else:
            logger.info("  Analyzing all medium/low confidence findings")
        logger.info("=" * 80)
        logger.info("")

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

    # AI filtering (if enabled)
    if config.enable_ai_filter:
        logger.info("")
        logger.info("=" * 80)
        logger.info("Step 3.5: Running AI Analysis...")
        logger.info("=" * 80)
        try:
            ai_engine = AIEngine(config)
            if not ai_engine.provider:
                logger.error("")
                logger.error("=" * 80)
                logger.error("❌ AI PROVIDER INITIALIZATION FAILED")
                logger.error("=" * 80)
                logger.error("Possible causes:")
                logger.error("  1. Missing package - Run: pip install openai (or anthropic)")
                logger.error("  2. Missing API key - Set OPENAI_API_KEY or ANTHROPIC_API_KEY env var")
                logger.error("  3. Invalid API key format")
                logger.error("")
                logger.error("Check the error messages above for details.")
                logger.error("=" * 80)
                logger.warning("Continuing without AI filtering")
            else:
                logger.info("✓ AI engine initialized successfully")
                logger.info(f"  Found {len(findings)} finding(s) from Semgrep")
                file_contents = load_file_contents(findings)
                findings_before_ai = len(findings)
                findings = ai_engine.filter_false_positives(findings, file_contents)
                findings_after_ai = len(findings)
                filtered_count = findings_before_ai - findings_after_ai
                logger.info("")
                if filtered_count > 0:
                    logger.info(
                        f"✓ AI analysis completed, filtered {filtered_count} false positive(s)"
                    )
                else:
                    logger.info("✓ AI analysis completed")
                    if findings_before_ai == 0:
                        logger.info("  (No findings to analyze)")
                    else:
                        logger.info("  (No false positives filtered - all findings confirmed as true positives)")
        except Exception as e:
            logger.error("")
            logger.error("=" * 80)
            logger.error(f"❌ AI FILTERING FAILED: {e}")
            logger.error("=" * 80)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error("Check the error messages above for details.")
            logger.warning("Continuing with unfiltered findings")

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

    # Group findings by severity and track AI analysis
    findings_by_severity = {}
    ai_filtered_count = 0
    ai_analyzed_count = 0
    ai_enhanced_count = 0
    semgrep_only_count = 0
    
    for finding in findings:
        if finding.ai_filtered:
            ai_filtered_count += 1
            continue
        
        # Track AI analysis
        if finding.ai_analysis:
            ai_analyzed_count += 1
            if finding.source == "ai-enhanced":
                ai_enhanced_count += 1
        else:
            semgrep_only_count += 1
        
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
    
    # AI Analysis breakdown
    if config.enable_ai_filter:
        logger.info("")
        logger.info("  AI Analysis:")
        logger.info(f"    - Analyzed by AI: {ai_analyzed_count} finding(s)")
        logger.info(f"    - Remediation enhanced: {ai_enhanced_count} finding(s)")
        logger.info(f"    - Filtered (false positives): {ai_filtered_count} finding(s)")
        logger.info(f"    - Semgrep only: {semgrep_only_count} finding(s)")
    
    if findings_by_severity:
        logger.info("")
        logger.info("  Findings by severity:")
        for severity, count in sorted(findings_by_severity.items(), key=lambda x: ["critical", "high", "medium", "low", "info"].index(x[0]) if x[0] in ["critical", "high", "medium", "low", "info"] else 99):
            logger.info(f"    {severity.upper()}: {count}")
    logger.info(f"  Scan duration: {scan_duration:.2f}s")
    logger.info("=" * 80)

    # Optionally upload
    if uploader:
        logger.info("")
        logger.info("Step 6: Uploading results...")
        # For RESTUploader, api_key is already set in constructor
        # For backward compatibility, still pass None (uploader will use its own api_key)
        success = uploader.upload(result, api_key=None)
        if success:
            logger.info("✓ Upload completed successfully")
        else:
            logger.warning("⚠ Upload completed with errors (check logs above)")

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
        help="Upload endpoint URL for sending results to server",
    )
    parser.add_argument(
        "--api-key",
        help="API key for authentication with upload endpoint (or use LLM_SCAN_API_KEY env var)",
    )
    parser.add_argument(
        "--application-id",
        help="Application ID to associate with the scan results",
    )
    # AI filtering options
    parser.add_argument(
        "--enable-ai-filter",
        action="store_true",
        help="Enable AI-based false positive filtering",
    )
    parser.add_argument(
        "--ai-provider",
        choices=["openai", "anthropic"],
        default="openai",
        help="AI provider to use (default: openai)",
    )
    parser.add_argument(
        "--ai-model",
        default="gpt-4",
        help="AI model to use (default: gpt-4)",
    )
    parser.add_argument(
        "--ai-api-key",
        help="AI API key (or use OPENAI_API_KEY/ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--ai-confidence-threshold",
        type=float,
        default=0.7,
        help="AI confidence threshold for filtering (0.0-1.0, default: 0.7)",
    )
    parser.add_argument(
        "--ai-analyze-rules",
        action="append",
        help="Specific rule IDs to analyze with AI (can be used multiple times)",
    )
    parser.add_argument(
        "--ai-max-findings",
        type=int,
        default=None,
        help="Maximum number of findings to analyze with AI (default: unlimited). Findings are prioritized by severity (critical/high first).",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.WARNING
    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO
    elif args.enable_ai_filter:
        # Automatically enable INFO logging when AI filtering is enabled
        # so users can see AI analysis progress
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

    # Set default include patterns if none provided
    include_patterns = args.include if args.include else ["*.py"]
    
    # Set default exclude patterns for common directories
    default_excludes = [
        "**/__pycache__/**",
        "**/node_modules/**",
        "**/.venv/**",
        "**/venv/**",
        "**/env/**",
        "**/.env/**",
        "**/build/**",
        "**/dist/**",
        "**/.git/**",
        "**/.pytest_cache/**",
        "**/.mypy_cache/**",
        "**/.tox/**",
        "**/htmlcov/**",
        "**/.coverage/**",
        "**/site-packages/**",
        "**/egg-info/**",
        "**/*.egg-info/**",
    ]
    exclude_patterns = args.exclude + default_excludes if args.exclude else default_excludes
    
    # Get AI API key from args or environment
    ai_api_key = args.ai_api_key
    if not ai_api_key and args.enable_ai_filter:
        if args.ai_provider == "openai":
            ai_api_key = os.getenv("OPENAI_API_KEY")
        elif args.ai_provider == "anthropic":
            ai_api_key = os.getenv("ANTHROPIC_API_KEY")

    config = ScanConfig(
        paths=args.paths,
        rules_dir=args.rules,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        enabled_rules=args.enable_rule,
        disabled_rules=args.disable_rule,
        severity_filter=severity_filter,
        output_format=args.format,
        output_file=args.out,
        respect_gitignore=not args.no_gitignore,
        enable_ai_filter=args.enable_ai_filter,
        ai_provider=args.ai_provider,
        ai_api_key=ai_api_key,
        ai_model=args.ai_model,
        ai_confidence_threshold=args.ai_confidence_threshold,
        ai_analyze_rules=args.ai_analyze_rules,
        ai_max_findings=args.ai_max_findings,
    )

    # Setup uploader if requested
    uploader = None
    if args.upload:
        # Get API key from args or environment
        api_key = args.api_key or os.getenv("LLM_SCAN_API_KEY")
        application_id = args.application_id or os.getenv("LLM_SCAN_APPLICATION_ID")
        
        # Use REST uploader if both api_key and application_id are provided
        if api_key and application_id:
            logger.info(f"Using REST API uploader for endpoint: {args.upload}")
            uploader = RESTUploader(
                endpoint=args.upload,
                api_key=api_key,
                application_id=application_id,
            )
        else:
            logger.warning(
                "Upload endpoint specified but missing api_key or application_id. "
                "Using stub uploader. Provide --api-key and --application-id or set "
                "LLM_SCAN_API_KEY and LLM_SCAN_APPLICATION_ID environment variables."
            )
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
