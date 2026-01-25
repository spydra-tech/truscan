"""AI engine for filtering false positives and analyzing findings."""

import hashlib
import json
import logging
from collections import defaultdict
from typing import Dict, List, Optional

from ..config import ScanConfig
from ..models import AIVerdict, Finding, Severity
from ..utils.code_context import extract_snippet_context, load_file_contents
from .ai_providers import AIProvider, create_provider

logger = logging.getLogger(__name__)
# Ensure AI engine logs are visible when AI filtering is enabled
# (logging level will be set by runner.py)

# System prompt for AI analysis
SYSTEM_PROMPT = """You are a security code reviewer specializing in LLM application vulnerabilities.
Analyze Semgrep findings and determine if they are true positives or false positives.
Additionally, provide enhanced remediation guidance that is:
1. Specific to the code context shown
2. Actionable with concrete steps
3. Framework-aware (Flask, Django, FastAPI, etc.)
4. Includes code examples when helpful
5. Considers the actual vulnerability pattern in the code

Respond ONLY with valid JSON in the specified format."""

# Prompt template for analyzing a finding
FINDING_ANALYSIS_PROMPT_TEMPLATE = """
Semgrep Finding:
- Rule ID: {rule_id}
- Message: {message}
- Severity: {severity}
- Category: {category}
- CWE: {cwe}
- Location: {file_path}:{start_line}:{start_column}

Rule Description:
{rule_description}

Original Remediation Guidance (from rule):
{remediation}

Code Context:
{code_context}

Tasks:
1. Determine if this is a true positive or false positive. Consider:
   - Is the vulnerability actually exploitable in this context?
   - Are there mitigations (validation, sanitization, framework protections)?
   - Is the code pattern actually dangerous here?
   - Could an attacker realistically exploit this?

2. Provide enhanced remediation guidance that is:
   - Specific to this exact code pattern
   - Actionable with step-by-step instructions
   - Framework-aware (if Flask/Django/FastAPI detected)
   - Includes code examples showing the fix
   - More detailed than the generic rule guidance

Respond in JSON format:
{{
    "is_false_positive": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation of why this is/isn't a false positive",
    "enhanced_remediation": "detailed, context-specific remediation guidance with code examples",
    "suggested_severity": "critical|high|medium|low" (optional, only if different from current),
    "additional_context": {{}}
}}
"""


class AIEngine:
    """AI engine for analyzing and filtering security findings."""

    def __init__(self, config: ScanConfig):
        """
        Initialize AI engine.

        Args:
            config: Scan configuration with AI settings
        """
        self.config = config
        self.provider: Optional[AIProvider] = None
        self.cache: Dict[str, AIVerdict] = {}

        if config.enable_ai_filter:
            try:
                logger.info(f"Initializing AI provider: {config.ai_provider}...")
                logger.debug(f"API key provided: {'Yes' if config.ai_api_key else 'No (will use env var)'}")
                
                self.provider = create_provider(
                    provider_name=config.ai_provider,
                    api_key=config.ai_api_key,
                    model=config.ai_model,
                )
                logger.info(
                    f"✓ AI engine initialized with provider: {config.ai_provider}, "
                    f"model: {config.ai_model}"
                )
            except ImportError as e:
                logger.error(f"❌ Missing required package: {e}")
                package_name = "openai" if config.ai_provider == "openai" else "anthropic"
                logger.error(f"   Install with: pip install {package_name}")
                logger.error(f"   Or install all AI dependencies: pip install -r requirements-ai.txt")
                logger.warning("Continuing without AI filtering")
                self.provider = None
            except ValueError as e:
                logger.error(f"❌ Invalid AI provider configuration: {e}")
                logger.warning("Continuing without AI filtering")
                self.provider = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize AI engine: {e}")
                logger.error(f"   Error type: {type(e).__name__}")
                logger.warning("Continuing without AI filtering")
                self.provider = None

    def filter_false_positives(
        self,
        findings: List[Finding],
        file_contents: Optional[Dict[str, str]] = None,
    ) -> List[Finding]:
        """
        Filter false positives from findings using AI.

        Args:
            findings: List of findings from Semgrep
            file_contents: Optional pre-loaded file contents

        Returns:
            Filtered list of findings
        """
        if not self.provider:
            logger.warning("⚠ AI provider not initialized, skipping AI filtering")
            logger.warning("  This may be due to:")
            logger.warning("  - Missing API key (set OPENAI_API_KEY or ANTHROPIC_API_KEY)")
            logger.warning("  - Missing package (pip install openai or anthropic)")
            logger.warning("  - API initialization error")
            return findings

        if not findings:
            logger.info("ℹ No findings to analyze with AI")
            logger.info("  (Semgrep found 0 findings, so AI analysis is not needed)")
            return findings

        logger.info(f"🔍 Starting AI analysis for {len(findings)} finding(s)")
        logger.info("  AI will: 1) Filter false positives, 2) Generate enhanced remediation")

        # Load file contents if not provided
        if file_contents is None:
            file_contents = load_file_contents(findings)

        # Filter findings to analyze based on configuration
        findings_to_analyze = self._filter_findings_for_analysis(findings)
        
        if not findings_to_analyze:
            logger.info("ℹ No findings selected for AI analysis")
            logger.info("  Reasons: All findings are high confidence or excluded by --ai-analyze-rules")
            logger.info("  AI analysis skipped - all findings will be kept")
            return findings

        logger.info(
            f"📊 Analyzing {len(findings_to_analyze)} finding(s) with AI "
            f"(filtered from {len(findings)} total)"
        )
        logger.info(f"  Using {self.config.ai_provider} model: {self.config.ai_model}")
        logger.info(f"  Confidence threshold: {self.config.ai_confidence_threshold}")
        logger.info(f"  Batch size: {self.config.ai_batch_size}")
        if self.config.ai_max_findings:
            logger.info(f"  Max findings limit: {self.config.ai_max_findings} (prioritized by severity)")

        # Group findings by file for batch processing
        findings_by_file = defaultdict(list)
        for finding in findings_to_analyze:
            findings_by_file[finding.location.file_path].append(finding)

        # Process findings
        filtered_findings = []
        analyzed_count = 0
        filtered_count = 0
        remediation_enhanced_count = 0

        for file_path, file_findings in findings_by_file.items():
            # Process in batches
            for i in range(0, len(file_findings), self.config.ai_batch_size):
                batch = file_findings[i : i + self.config.ai_batch_size]
                batch_num = (i // self.config.ai_batch_size) + 1
                total_batches = (len(file_findings) + self.config.ai_batch_size - 1) // self.config.ai_batch_size
                logger.info(f"  Processing batch {batch_num}/{total_batches} for {file_path} ({len(batch)} finding(s))")
                
                for finding in batch:
                    finding_num = analyzed_count + 1
                    logger.info(f"  🤖 [{finding_num}/{len(findings_to_analyze)}] Analyzing: {finding.rule_id} at {finding.location.file_path}:{finding.location.start_line}")
                    verdict = self._analyze_finding(finding, file_contents.get(file_path, ""))
                    if verdict:
                        finding.ai_analysis = verdict
                        analyzed_count += 1
                        
                        # Log AI analysis details
                        logger.info(f"    📋 AI Analysis Results:")
                        logger.info(f"      Verdict: {'False Positive' if verdict.is_false_positive else 'True Positive'}")
                        logger.info(f"      Confidence: {verdict.confidence:.2f}")
                        logger.info(f"      Reasoning: {verdict.reasoning}")
                        
                        if verdict.suggested_severity:
                            logger.info(f"      Suggested Severity: {verdict.suggested_severity.value} (original: {finding.severity.value})")
                        
                        # Apply enhanced remediation if provided
                        if verdict.enhanced_remediation:
                            finding.remediation = verdict.enhanced_remediation
                            finding.source = "ai-enhanced"
                            remediation_enhanced_count += 1
                            logger.info(f"    ✨ Enhanced Remediation:")
                            # Log remediation in chunks to avoid overwhelming logs
                            remediation_lines = verdict.enhanced_remediation.split('\n')
                            for line in remediation_lines[:10]:  # First 10 lines
                                logger.info(f"      {line}")
                            if len(remediation_lines) > 10:
                                logger.info(f"      ... ({len(remediation_lines) - 10} more lines)")
                        
                        if verdict.additional_context:
                            logger.info(f"    📝 Additional Context: {verdict.additional_context}")

                        # Filter if high confidence false positive
                        if (
                            verdict.is_false_positive
                            and verdict.confidence >= self.config.ai_confidence_threshold
                        ):
                            finding.ai_filtered = True
                            filtered_count += 1
                            logger.info(f"    🚫 Filtered as false positive (confidence: {verdict.confidence:.2f} >= threshold: {self.config.ai_confidence_threshold})")
                        else:
                            logger.info(f"    ✓ Confirmed as true positive (confidence: {verdict.confidence:.2f})")
                            filtered_findings.append(finding)
                    else:
                        # If analysis failed, keep the finding
                        filtered_findings.append(finding)

        # Add findings that weren't analyzed
        analyzed_rule_ids = {f.rule_id for f in findings_to_analyze}
        for finding in findings:
            if finding.rule_id not in analyzed_rule_ids:
                filtered_findings.append(finding)

        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ AI ANALYSIS COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   📊 Analyzed: {analyzed_count} finding(s)")
        logger.info(f"   🚫 Filtered (false positives): {filtered_count} finding(s)")
        logger.info(f"   ✨ Remediation enhanced: {remediation_enhanced_count} finding(s)")
        logger.info(f"   ✓ Remaining (true positives): {len(filtered_findings)} finding(s)")
        if self.config.ai_cache_enabled and analyzed_count > 0:
            logger.info(f"   💾 Cache entries: {len(self.cache)}")
        logger.info("=" * 80)

        return filtered_findings

    def _filter_findings_for_analysis(self, findings: List[Finding]) -> List[Finding]:
        """Filter findings that should be analyzed by AI."""
        filtered = []
        skipped_high_confidence = 0
        skipped_not_in_list = 0
        included_count = 0

        for finding in findings:
            # Check if rule explicitly requested for analysis
            if self.config.ai_analyze_rules:
                if finding.rule_id not in self.config.ai_analyze_rules:
                    # Also check if rule recommends AI analysis
                    ai_recommended = finding.metadata.get("ai_analysis_recommended", False)
                    if not ai_recommended:
                        skipped_not_in_list += 1
                        continue
                # If in the list or recommended, include it regardless of confidence
                filtered.append(finding)
                included_count += 1
                continue

            # If no explicit rules specified, use confidence-based filtering
            # Default to "medium" if confidence is not specified (to be safe)
            rule_confidence = finding.metadata.get("confidence", "medium")
            ai_recommended = finding.metadata.get("ai_analysis_recommended", False)
            
            logger.info(
                f"Finding {finding.rule_id} - confidence: {rule_confidence}, "
                f"ai_recommended: {ai_recommended}"
            )
            
            # Include if:
            # 1. Rule explicitly recommends AI analysis, OR
            # 2. Confidence is medium or low (not high)
            if ai_recommended:
                # Always include if recommended
                filtered.append(finding)
                included_count += 1
            elif rule_confidence in ("medium", "low"):
                # Include medium/low confidence findings
                filtered.append(finding)
                included_count += 1
            else:
                # Skip high confidence findings (unless recommended)
                skipped_high_confidence += 1
                logger.debug(f"Skipping {finding.rule_id} - high confidence, not recommended for AI")

        # Sort by severity (critical, high, medium, low, info) to prioritize important findings
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        filtered.sort(key=lambda f: severity_order.get(f.severity, 99))
        
        # Apply maximum limit if configured
        original_count = len(filtered)
        if self.config.ai_max_findings and len(filtered) > self.config.ai_max_findings:
            filtered = filtered[:self.config.ai_max_findings]
            logger.info(f"  ⚠ Limited to {self.config.ai_max_findings} finding(s) (from {original_count} eligible)")
            logger.info(f"    Priority: Critical/High severity findings analyzed first")
        
        if skipped_high_confidence > 0 or skipped_not_in_list > 0:
            logger.info(f"  Filtering summary:")
            if skipped_high_confidence > 0:
                logger.info(f"    - Skipped {skipped_high_confidence} high confidence finding(s)")
            if skipped_not_in_list > 0:
                logger.info(f"    - Skipped {skipped_not_in_list} finding(s) not in --ai-analyze-rules")
            logger.info(f"    - Selected {len(filtered)} finding(s) for AI analysis")
            if self.config.ai_max_findings and original_count > self.config.ai_max_findings:
                logger.info(f"    - Limited from {original_count} to {len(filtered)} due to --ai-max-findings")
        else:
            logger.info(f"  Selected {len(filtered)} finding(s) for AI analysis")
            if self.config.ai_max_findings and original_count > self.config.ai_max_findings:
                logger.info(f"    (Limited from {original_count} eligible findings)")

        return filtered

    def _analyze_finding(
        self,
        finding: Finding,
        file_content: str,
    ) -> Optional[AIVerdict]:
        """
        Analyze a single finding with AI.

        Args:
            finding: Finding to analyze
            file_content: Full file content

        Returns:
            AIVerdict or None if analysis failed
        """
        # Check cache
        cache_key = self._get_cache_key(finding, file_content)
        if self.config.ai_cache_enabled and cache_key in self.cache:
            logger.info(f"    💾 Using cached AI analysis")
            return self.cache[cache_key]

        logger.info(f"    → Sending to AI provider...")

        # Build prompt
        code_context = extract_snippet_context(
            snippet=finding.location.snippet,
            file_path=finding.location.file_path,
            line_number=finding.location.start_line,
            context_lines=50,
        )

        rule_description = finding.metadata.get("description", "No description available")
        remediation = finding.remediation or "No remediation guidance available"

        prompt = FINDING_ANALYSIS_PROMPT_TEMPLATE.format(
            rule_id=finding.rule_id,
            message=finding.message,
            severity=finding.severity.value,
            category=finding.category.value,
            cwe=finding.cwe or "N/A",
            file_path=finding.location.file_path,
            start_line=finding.location.start_line,
            start_column=finding.location.start_column,
            rule_description=rule_description,
            remediation=remediation,
            code_context=code_context,
        )

        try:
            # Call AI provider with timeout protection
            try:
                response = self.provider.analyze(prompt, SYSTEM_PROMPT)
                logger.info(f"    ✓ AI analysis received")
            except Exception as api_error:
                error_msg = str(api_error)
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    logger.error(f"  AI API call timed out for {finding.rule_id}")
                    raise TimeoutError(f"AI API call timed out: {api_error}")
                elif "rate limit" in error_msg.lower():
                    logger.warning(f"  AI API rate limit hit for {finding.rule_id}, will retry on next scan")
                    raise
                else:
                    raise

            # Parse response
            # Validate suggested_severity before converting to enum
            suggested_severity_value = response.get("suggested_severity")
            suggested_severity = None
            if suggested_severity_value:
                # Check if it's a valid Severity enum value (case-insensitive)
                severity_str = str(suggested_severity_value).lower().strip()
                if severity_str in [s.value for s in Severity]:
                    try:
                        suggested_severity = Severity(severity_str)
                    except (ValueError, KeyError):
                        # Invalid severity value, ignore it
                        logger.debug(f"    Invalid suggested_severity: {suggested_severity_value}, ignoring")
                        suggested_severity = None
                else:
                    # Not a valid severity value (e.g., "none"), ignore it
                    logger.debug(f"    Invalid suggested_severity: {suggested_severity_value}, ignoring")
                    suggested_severity = None
            
            verdict = AIVerdict(
                is_false_positive=response.get("is_false_positive", False),
                confidence=float(response.get("confidence", 0.5)),
                reasoning=response.get("reasoning", "No reasoning provided"),
                enhanced_remediation=response.get("enhanced_remediation"),
                suggested_severity=suggested_severity,
                additional_context=response.get("additional_context", {}),
            )

            # Cache result
            if self.config.ai_cache_enabled:
                self.cache[cache_key] = verdict

            return verdict

        except Exception as e:
            logger.error(f"    ❌ AI analysis failed: {e}")
            return None

    def _get_cache_key(self, finding: Finding, file_content: str) -> str:
        """Generate cache key for a finding."""
        # Use rule ID + code snippet hash
        snippet = finding.location.snippet or ""
        content_hash = hashlib.md5(
            f"{finding.rule_id}:{snippet}:{finding.location.start_line}".encode()
        ).hexdigest()
        return f"{finding.rule_id}:{content_hash}"
