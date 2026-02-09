"""
Forjador v5 - B.2: Complexity Classification & Parser Routing
Purpose: Classify documents into 11 tiers and select optimal parser
Version: 1.0.0
Date: 2026-02-09

This node performs:
- 11-tier complexity classification
- Parser selection (Docling, Gemini Vision, Pandas/CSV)
- Fallback chain definition
- Processing time estimation

Performance Target: < 0.5 seconds
"""

from typing import Any, Dict, List
import logging

from src.state.schemas import (
    ComplexityClassification,
    ComplexityTier,
    ParserType,
    FileFormat,
    FileMetadata,
)

logger = logging.getLogger(__name__)


# ============================================================================
# COMPLEXITY TIER DEFINITIONS
# ============================================================================

TIER_DEFINITIONS = {
    ComplexityTier.TIER_1: {
        "name": "Simple Structured CSV",
        "description": "Clean CSV with header row, minimal formatting",
        "avg_processing_time_s": 1.0,
        "primary_parser": ParserType.PANDAS,
        "fallback_parsers": [ParserType.DOCLING],
    },
    ComplexityTier.TIER_2: {
        "name": "Simple Excel Spreadsheet",
        "description": "Basic Excel file, single sheet, tabular data",
        "avg_processing_time_s": 2.0,
        "primary_parser": ParserType.PANDAS,
        "fallback_parsers": [ParserType.DOCLING],
    },
    ComplexityTier.TIER_3: {
        "name": "Standard PDF with Text",
        "description": "Digital PDF with extractable text, simple layout",
        "avg_processing_time_s": 3.0,
        "primary_parser": ParserType.DOCLING,
        "fallback_parsers": [ParserType.GEMINI_VISION, ParserType.PANDAS],
    },
    ComplexityTier.TIER_4: {
        "name": "PDF with Embedded Tables",
        "description": "PDF with complex table structures",
        "avg_processing_time_s": 5.0,
        "primary_parser": ParserType.DOCLING,
        "fallback_parsers": [ParserType.GEMINI_VISION],
    },
    ComplexityTier.TIER_5: {
        "name": "PDF with Images/Charts",
        "description": "PDF with embedded images, charts, graphs",
        "avg_processing_time_s": 7.0,
        "primary_parser": ParserType.DOCLING,
        "fallback_parsers": [ParserType.GEMINI_VISION],
    },
    ComplexityTier.TIER_6: {
        "name": "Multi-page Complex PDF",
        "description": "Large PDF with mixed content types",
        "avg_processing_time_s": 10.0,
        "primary_parser": ParserType.DOCLING,
        "fallback_parsers": [ParserType.GEMINI_VISION],
    },
    ComplexityTier.TIER_7: {
        "name": "Scanned PDF (OCR Needed)",
        "description": "Image-based PDF requiring OCR",
        "avg_processing_time_s": 15.0,
        "primary_parser": ParserType.GEMINI_VISION,
        "fallback_parsers": [ParserType.DOCLING],
    },
    ComplexityTier.TIER_8: {
        "name": "Poor Quality Scanned PDF",
        "description": "Low resolution, skewed, or degraded scans",
        "avg_processing_time_s": 20.0,
        "primary_parser": ParserType.GEMINI_VISION,
        "fallback_parsers": [ParserType.DOCLING],
    },
    ComplexityTier.TIER_9: {
        "name": "Handwritten Documents",
        "description": "Handwritten or mixed handwritten/printed",
        "avg_processing_time_s": 25.0,
        "primary_parser": ParserType.GEMINI_VISION,
        "fallback_parsers": [],
    },
    ComplexityTier.TIER_10: {
        "name": "Mixed Format Documents",
        "description": "Multiple formats, complex layouts, non-standard",
        "avg_processing_time_s": 25.0,
        "primary_parser": ParserType.GEMINI_VISION,
        "fallback_parsers": [ParserType.DOCLING],
    },
    ComplexityTier.TIER_11: {
        "name": "Corrupted or Damaged Files",
        "description": "Partially corrupted, password-protected, or damaged",
        "avg_processing_time_s": 30.0,
        "primary_parser": ParserType.GEMINI_VISION,
        "fallback_parsers": [ParserType.DOCLING, ParserType.PANDAS],
    },
}


# ============================================================================
# FEATURE EXTRACTION
# ============================================================================

def extract_document_features(metadata: FileMetadata) -> Dict[str, Any]:
    """
    Extract features from file metadata for classification.

    Features:
    - File format
    - File size
    - Page/line count
    - Text extractability (estimated)

    Args:
        metadata: FileMetadata object

    Returns:
        Dictionary of features
    """
    features = {
        "file_format": metadata.file_format.value,
        "file_size_mb": metadata.file_size_mb,
        "line_count": metadata.line_count or 0,
        "page_count": metadata.page_count or 0,
        "encoding": metadata.encoding,
    }

    # Estimate complexity indicators
    features["is_large"] = metadata.file_size_mb > 10
    features["is_multipage"] = (metadata.page_count or 0) > 10
    features["is_image_format"] = metadata.file_format in [
        FileFormat.PNG, FileFormat.JPG, FileFormat.JPEG
    ]

    return features


# ============================================================================
# CLASSIFICATION LOGIC
# ============================================================================

def classify_complexity_tier(features: Dict[str, Any]) -> ComplexityTier:
    """
    Classify document into one of 11 complexity tiers.

    Classification Rules (decision tree):
    1. Check file format first
    2. Then check size/complexity indicators
    3. Apply heuristics for edge cases

    Args:
        features: Document features dictionary

    Returns:
        ComplexityTier enum value
    """
    file_format = features["file_format"]
    file_size_mb = features["file_size_mb"]
    page_count = features["page_count"]
    is_image_format = features["is_image_format"]

    # Rule 1: CSV files -> TIER_1
    if file_format == "csv":
        return ComplexityTier.TIER_1

    # Rule 2: Simple Excel -> TIER_2
    if file_format == "xlsx" and file_size_mb < 5 and page_count == 0:
        return ComplexityTier.TIER_2

    # Rule 3: Complex Excel -> TIER_2 or TIER_4
    if file_format == "xlsx":
        if file_size_mb > 10:
            return ComplexityTier.TIER_4
        return ComplexityTier.TIER_2

    # Rule 4: Image files -> TIER_7 or TIER_8
    if is_image_format:
        if file_size_mb > 5:
            return ComplexityTier.TIER_8  # Likely high-res scan
        return ComplexityTier.TIER_7

    # Rule 5-11: PDF classification (most complex)
    if file_format == "pdf":
        # Simple PDF
        if page_count <= 5 and file_size_mb < 2:
            return ComplexityTier.TIER_3

        # PDF with tables
        if page_count <= 10 and file_size_mb < 5:
            return ComplexityTier.TIER_4

        # PDF with images (estimated by size)
        if page_count <= 20 and file_size_mb > 5:
            return ComplexityTier.TIER_5

        # Multi-page complex
        if page_count > 20:
            return ComplexityTier.TIER_6

        # Large file size -> likely scanned
        if file_size_mb > 20:
            return ComplexityTier.TIER_7

        # Very large -> poor quality scan
        if file_size_mb > 50:
            return ComplexityTier.TIER_8

        # Default to standard PDF
        return ComplexityTier.TIER_3

    # Rule 12: Unknown/corrupted -> TIER_11
    return ComplexityTier.TIER_11


def select_parser(tier: ComplexityTier) -> ParserType:
    """
    Select primary parser based on complexity tier.

    Args:
        tier: Complexity tier

    Returns:
        Primary ParserType
    """
    return TIER_DEFINITIONS[tier]["primary_parser"]


def get_fallback_parsers(tier: ComplexityTier) -> List[ParserType]:
    """
    Get fallback parser chain for complexity tier.

    Args:
        tier: Complexity tier

    Returns:
        List of fallback parsers in priority order
    """
    return TIER_DEFINITIONS[tier]["fallback_parsers"]


# ============================================================================
# MAIN CLASSIFICATION FUNCTION
# ============================================================================

def classify_and_route(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    B.2: Classify document complexity and select parser.

    This function analyzes file metadata and classifies the document into
    one of 11 complexity tiers, then selects the optimal parser.

    Args:
        state: Pipeline state dict with 'file_metadata' key

    Returns:
        Updated state dict with 'complexity_classification' key

    Performance: < 0.5 seconds

    Example:
        >>> state = {"file_metadata": metadata}
        >>> result = classify_and_route(state)
        >>> result["complexity_classification"].tier
        ComplexityTier.TIER_3
        >>> result["complexity_classification"].primary_parser
        ParserType.DOCLING
    """
    metadata = state.get("file_metadata")

    if not metadata:
        raise ValueError("file_metadata is required in state")

    logger.info("B.2: Classifying document complexity")

    # Extract features
    features = extract_document_features(metadata)

    # Classify tier
    tier = classify_complexity_tier(features)
    tier_info = TIER_DEFINITIONS[tier]

    # Select parser
    primary_parser = select_parser(tier)
    fallback_parsers = get_fallback_parsers(tier)

    # Create classification object
    classification = ComplexityClassification(
        tier=tier,
        tier_name=tier_info["name"],
        features=features,
        primary_parser=primary_parser,
        fallback_parsers=fallback_parsers,
        avg_processing_time_s=tier_info["avg_processing_time_s"],
        confidence=0.9,  # High confidence for rule-based classification
    )

    logger.info(
        f"B.2: Classified as {tier.value.upper()} ({tier_info['name']}) -> "
        f"Primary parser: {primary_parser.value}"
    )

    return {
        **state,
        "complexity_classification": classification,
    }


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "classify_and_route",
    "classify_complexity_tier",
    "select_parser",
    "get_fallback_parsers",
    "extract_document_features",
    "TIER_DEFINITIONS",
]
