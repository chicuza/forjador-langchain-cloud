"""
Forjador v5 - B.5: Intelligent Chunking
Purpose: Chunk documents while preserving SKU line items
Version: 1.0.0
Date: 2026-02-09

This node performs:
- Intelligent text chunking (~3500 chars)
- Semantic boundary detection
- Line item preservation
- Overlap management (~250 chars)

Performance Target: < 2 seconds
"""

from typing import Any, Dict, List
import logging

from src.state.schemas import DocumentChunk, ParsedContent
from src.utils.chunking_utils import (
    chunk_document,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
)

logger = logging.getLogger(__name__)


# ============================================================================
# MAIN CHUNKING FUNCTION
# ============================================================================

def chunk_parsed_content(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    B.5: Chunk parsed content into smaller pieces for extraction.

    Chunking Strategy:
    1. Use semantic separators (\\n\\n, \\n, etc.)
    2. Preserve line item boundaries (critical for SKU extraction)
    3. Add overlap between chunks for context
    4. Target chunk size: ~3500 chars
    5. Target overlap: ~250 chars

    Args:
        state: Pipeline state dict with 'parsed_content' key

    Returns:
        Updated state dict with 'chunks' key

    Performance: < 2 seconds for 5000-line documents

    Example:
        >>> state = {"parsed_content": parsed_content}
        >>> result = chunk_parsed_content(state)
        >>> len(result["chunks"])
        5  # Depends on content length
    """
    parsed_content = state.get("parsed_content")

    if not parsed_content:
        raise ValueError("parsed_content is required in state")

    logger.info("B.5: Chunking document")

    # Extract content and metadata
    if isinstance(parsed_content, ParsedContent):
        content = parsed_content.raw_content
        source_file = state.get("input_file_path", "unknown")
    else:
        content = parsed_content.get("raw_content", "")
        source_file = parsed_content.get("source_file", state.get("input_file_path", "unknown"))

    # Validate content
    if not content or len(content) == 0:
        logger.warning("B.5: Empty content, returning empty chunks list")
        return {
            **state,
            "chunks": [],
        }

    # Perform chunking
    chunks = chunk_document(
        text=content,
        source_file=source_file,
        preserve_line_items=True,  # Critical for SKU extraction
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    )

    # Log statistics
    total_chunks = len(chunks)
    total_chars = sum(chunk.chunk_size for chunk in chunks)
    avg_chunk_size = total_chars / total_chunks if total_chunks > 0 else 0

    logger.info(
        f"B.5: Created {total_chunks} chunks - "
        f"Total: {total_chars:,} chars, Avg: {avg_chunk_size:.0f} chars/chunk"
    )

    # Warn if too many chunks (might indicate issue)
    if total_chunks > 50:
        logger.warning(
            f"B.5: Large number of chunks ({total_chunks}). "
            f"This may indicate very long document or chunking issues."
        )

    return {
        **state,
        "chunks": chunks,
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_chunk_by_id(chunks: List[DocumentChunk], chunk_id: str) -> DocumentChunk:
    """
    Get chunk by ID.

    Args:
        chunks: List of DocumentChunk objects
        chunk_id: Chunk ID to find

    Returns:
        DocumentChunk object

    Raises:
        ValueError: If chunk not found
    """
    for chunk in chunks:
        if chunk.chunk_id == chunk_id:
            return chunk

    raise ValueError(f"Chunk not found: {chunk_id}")


def get_chunk_context(
    chunks: List[DocumentChunk],
    chunk_index: int,
    context_size: int = 1
) -> str:
    """
    Get context around a chunk (previous and next chunks).

    Useful for providing additional context to LLM during extraction.

    Args:
        chunks: List of DocumentChunk objects
        chunk_index: Index of target chunk
        context_size: Number of chunks before/after to include

    Returns:
        Combined context string
    """
    if not chunks or chunk_index < 0 or chunk_index >= len(chunks):
        return ""

    # Get context chunks
    start_idx = max(0, chunk_index - context_size)
    end_idx = min(len(chunks), chunk_index + context_size + 1)

    context_chunks = chunks[start_idx:end_idx]

    # Combine content
    context = "\n\n---\n\n".join(chunk.content for chunk in context_chunks)

    return context


def validate_chunks(chunks: List[DocumentChunk]) -> Dict[str, Any]:
    """
    Validate chunk quality.

    Quality Checks:
    - All chunks have content
    - Chunk sizes are reasonable
    - No duplicate chunk IDs
    - Overlaps are as expected

    Args:
        chunks: List of DocumentChunk objects

    Returns:
        Validation report dictionary
    """
    report = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {
            "total_chunks": len(chunks),
            "empty_chunks": 0,
            "avg_chunk_size": 0,
            "min_chunk_size": 0,
            "max_chunk_size": 0,
        }
    }

    if not chunks:
        report["warnings"].append("No chunks created")
        return report

    # Check for empty chunks
    empty_chunks = [chunk for chunk in chunks if not chunk.content or len(chunk.content) == 0]
    if empty_chunks:
        report["errors"].append(f"Found {len(empty_chunks)} empty chunks")
        report["valid"] = False

    # Check for duplicate IDs
    chunk_ids = [chunk.chunk_id for chunk in chunks]
    if len(chunk_ids) != len(set(chunk_ids)):
        report["errors"].append("Duplicate chunk IDs found")
        report["valid"] = False

    # Calculate statistics
    chunk_sizes = [chunk.chunk_size for chunk in chunks]
    report["stats"]["empty_chunks"] = len(empty_chunks)
    report["stats"]["avg_chunk_size"] = sum(chunk_sizes) / len(chunk_sizes)
    report["stats"]["min_chunk_size"] = min(chunk_sizes)
    report["stats"]["max_chunk_size"] = max(chunk_sizes)

    # Check chunk size range
    for chunk in chunks:
        if chunk.chunk_size > DEFAULT_CHUNK_SIZE * 1.5:  # Allow 50% overage
            report["warnings"].append(
                f"Chunk {chunk.chunk_id} exceeds size limit: {chunk.chunk_size} chars"
            )

    return report


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "chunk_parsed_content",
    "get_chunk_by_id",
    "get_chunk_context",
    "validate_chunks",
]
