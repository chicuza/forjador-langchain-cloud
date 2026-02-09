"""
Forjador v5 - B.4: Quality Gate with Retry Logic
Purpose: Validate parsed content quality and trigger fallback if needed
Version: 1.0.0
Date: 2026-02-09

This node performs:
- Content quality scoring (threshold: 0.85)
- Completeness validation
- Confidence assessment
- Retry logic with fallback parsers

Performance Target: < 1 second
"""

from typing import Any, Dict
import logging
import re

from src.state.schemas import QualityGateResult, ParsedContent

logger = logging.getLogger(__name__)


# ============================================================================
# QUALITY SCORING CONFIGURATION
# ============================================================================

QUALITY_THRESHOLD = 0.85  # SPEC-01 requirement
MAX_RETRIES = 2  # Maximum fallback attempts

# Component weights for quality score
WEIGHTS = {
    "completeness": 0.40,  # 40% - Is content complete?
    "confidence": 0.30,    # 30% - Parser confidence
    "structure": 0.30,     # 30% - Is structure valid?
}


# ============================================================================
# QUALITY METRICS CALCULATION
# ============================================================================

def calculate_content_completeness(content: str) -> float:
    """
    Calculate content completeness score.

    Completeness Indicators:
    - Presence of expected sections (header, items, footer)
    - Minimum content length
    - Presence of SKU-related keywords
    - Line item patterns

    Args:
        content: Parsed text content

    Returns:
        Completeness score (0.0-1.0)
    """
    if not content or len(content) == 0:
        return 0.0

    score = 0.0

    # Check 1: Minimum content length (should have at least some content)
    if len(content) > 100:
        score += 0.2
    if len(content) > 500:
        score += 0.1

    # Check 2: Presence of SKU-related keywords (weighted)
    sku_keywords = [
        r'\b(?:parafuso|porca|arruela|bucha|chumbador)\b',  # Fastener types
        r'\bM\d+\b',  # Metric dimensions (M8, M10, etc.)
        r'\b(?:quantidade|qtd|qty)\b',  # Quantity indicators
        r'\b(?:material|aço|inox)\b',  # Materials
        r'\b(?:classe|class)\b',  # Class indicators
    ]

    keyword_matches = 0
    for pattern in sku_keywords:
        if re.search(pattern, content, re.IGNORECASE):
            keyword_matches += 1

    # Each keyword adds to score
    score += min(keyword_matches * 0.1, 0.4)

    # Check 3: Line item structure patterns
    line_item_patterns = [
        r'\n\s*\d+[\.\)]\s+',  # "1. ", "12) "
        r'\n\s*(?:Item|ITEM)\s+\d+',  # "Item 1", "ITEM 12"
        r'\|\s*\w+\s*\|',  # Table cells
    ]

    for pattern in line_item_patterns:
        if re.search(pattern, content):
            score += 0.1
            break

    # Check 4: Multiple lines (indicates structured content)
    line_count = content.count('\n')
    if line_count > 5:
        score += 0.1
    if line_count > 20:
        score += 0.1

    return min(score, 1.0)


def calculate_structure_validity(content: str) -> float:
    """
    Calculate structure validity score.

    Structure Indicators:
    - Well-formed lines (not too many empty lines)
    - Consistent formatting
    - No excessive special characters/noise
    - Reasonable line lengths

    Args:
        content: Parsed text content

    Returns:
        Structure validity score (0.0-1.0)
    """
    if not content or len(content) == 0:
        return 0.0

    score = 1.0  # Start with perfect score, deduct for issues

    lines = content.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]

    if len(lines) == 0:
        return 0.0

    # Check 1: Ratio of empty to non-empty lines (should be balanced)
    empty_ratio = (len(lines) - len(non_empty_lines)) / len(lines)
    if empty_ratio > 0.7:  # More than 70% empty lines
        score -= 0.3
    elif empty_ratio > 0.5:
        score -= 0.1

    # Check 2: Average line length (should be reasonable)
    if non_empty_lines:
        avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines)
        if avg_line_length < 10:  # Too short
            score -= 0.2
        elif avg_line_length > 200:  # Too long
            score -= 0.1

    # Check 3: Special character ratio (should be low)
    special_char_count = sum(1 for c in content if not c.isalnum() and c not in ' \n\t.,;:-')
    special_char_ratio = special_char_count / len(content)
    if special_char_ratio > 0.3:  # More than 30% special chars
        score -= 0.3
    elif special_char_ratio > 0.2:
        score -= 0.1

    # Check 4: Presence of common OCR artifacts
    ocr_artifacts = ['###', '~~~', '***', '...', '???']
    artifact_count = sum(content.count(artifact) for artifact in ocr_artifacts)
    if artifact_count > 10:
        score -= 0.2

    return max(score, 0.0)


def calculate_quality_score(
    content: str,
    parser_confidence: float = 1.0
) -> float:
    """
    Calculate overall quality score.

    Quality Score Formula:
    score = (completeness * 0.4) + (confidence * 0.3) + (structure * 0.3)

    Args:
        content: Parsed text content
        parser_confidence: Parser confidence score (0.0-1.0)

    Returns:
        Overall quality score (0.0-1.0)
    """
    completeness = calculate_content_completeness(content)
    structure = calculate_structure_validity(content)

    quality_score = (
        completeness * WEIGHTS["completeness"] +
        parser_confidence * WEIGHTS["confidence"] +
        structure * WEIGHTS["structure"]
    )

    return quality_score


# ============================================================================
# MAIN QUALITY GATE FUNCTION
# ============================================================================

def evaluate_quality_gate(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    B.4: Evaluate quality gate and determine if retry is needed.

    Quality Gate Logic:
    1. Calculate quality score from parsed content
    2. If score >= 0.85: PASS, continue to next stage
    3. If score < 0.85: FAIL, trigger fallback parser retry
    4. Max 2 retries allowed

    Args:
        state: Pipeline state dict with 'parsed_content' key

    Returns:
        Updated state dict with 'quality_gate' key

    Performance: < 1 second

    Example:
        >>> state = {"parsed_content": parsed_content}
        >>> result = evaluate_quality_gate(state)
        >>> result["quality_gate"].passed
        True
    """
    parsed_content = state.get("parsed_content")

    if not parsed_content:
        raise ValueError("parsed_content is required in state")

    logger.info("B.4: Evaluating quality gate")

    # Extract content and metadata
    content = parsed_content.raw_content if isinstance(parsed_content, ParsedContent) else parsed_content.get("raw_content", "")
    parser_confidence = parsed_content.confidence if isinstance(parsed_content, ParsedContent) else parsed_content.get("confidence", 1.0)
    retry_count = parsed_content.retry_count if isinstance(parsed_content, ParsedContent) else parsed_content.get("retry_count", 0)

    # Calculate quality metrics
    completeness = calculate_content_completeness(content)
    structure = calculate_structure_validity(content)
    overall_score = calculate_quality_score(content, parser_confidence)

    # Determine if quality gate passed
    passed = overall_score >= QUALITY_THRESHOLD
    should_retry = not passed and retry_count < MAX_RETRIES
    max_retries_reached = retry_count >= MAX_RETRIES

    # Create quality gate result
    quality_gate = QualityGateResult(
        passed=passed,
        score=overall_score,
        content_completeness=completeness,
        confidence=parser_confidence,
        structure_validity=structure,
        should_retry=should_retry,
        retry_count=retry_count,
        max_retries_reached=max_retries_reached,
    )

    # Log result
    if passed:
        logger.info(
            f"B.4: Quality gate PASSED - Score: {overall_score:.3f} "
            f"(completeness: {completeness:.2f}, structure: {structure:.2f}, "
            f"confidence: {parser_confidence:.2f})"
        )
    else:
        logger.warning(
            f"B.4: Quality gate FAILED - Score: {overall_score:.3f} < {QUALITY_THRESHOLD} "
            f"(retry: {should_retry}, attempts: {retry_count}/{MAX_RETRIES})"
        )

    return {
        **state,
        "quality_gate": quality_gate,
    }


def should_retry_with_fallback(state: Dict[str, Any]) -> bool:
    """
    Check if pipeline should retry with fallback parser.

    This is used in LCEL RunnableBranch for conditional routing.

    Args:
        state: Pipeline state dict with 'quality_gate' key

    Returns:
        True if retry is needed, False otherwise
    """
    quality_gate = state.get("quality_gate")

    if not quality_gate:
        return False

    return quality_gate.should_retry


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "evaluate_quality_gate",
    "calculate_quality_score",
    "calculate_content_completeness",
    "calculate_structure_validity",
    "should_retry_with_fallback",
    "QUALITY_THRESHOLD",
    "MAX_RETRIES",
]
