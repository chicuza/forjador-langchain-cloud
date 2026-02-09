"""
Forjador v5 - Intelligent Chunking Utilities
Purpose: Semantic chunking with boundary detection for SKU extraction
Version: 1.0.0
Date: 2026-02-09

This module provides intelligent chunking for document processing:
- Semantic boundary detection (preserve line items)
- Configurable chunk size and overlap
- Metadata enrichment for traceability
- Performance target: < 2 seconds for 5000-line documents
"""

from typing import List
from dataclasses import dataclass
import re
from src.state.schemas import DocumentChunk


# ============================================================================
# CHUNKING CONFIGURATION
# ============================================================================

# SPEC-01 Requirements
DEFAULT_CHUNK_SIZE = 3500  # characters
DEFAULT_CHUNK_OVERLAP = 250  # characters

# Semantic separators (in priority order)
# These separators help preserve SKU line items across chunks
SEMANTIC_SEPARATORS = [
    "\n\n\n",  # Triple newline (section breaks)
    "\n\n",    # Double newline (paragraph breaks)
    "\n",      # Single newline (line breaks - preserve SKU items)
    ". ",      # Sentence boundaries
    "; ",      # List separators
    ", ",      # Phrase separators
    " ",       # Word boundaries
    ""         # Character level (last resort)
]


# ============================================================================
# CHUNKING STRATEGIES
# ============================================================================

@dataclass
class ChunkConfig:
    """Configuration for chunking strategy"""
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    separators: List[str] = None
    preserve_line_items: bool = True  # Crucial for SKU extraction

    def __post_init__(self):
        if self.separators is None:
            self.separators = SEMANTIC_SEPARATORS


def chunk_text_recursive(
    text: str,
    config: ChunkConfig = None,
    source_file: str = ""
) -> List[DocumentChunk]:
    """
    Recursively chunk text using semantic separators.

    Strategy:
    1. Try to split on highest priority separator
    2. If chunks still too large, try next separator
    3. Continue until chunks are within size limits
    4. Add overlap between chunks for context preservation

    Args:
        text: Text content to chunk
        config: Chunking configuration
        source_file: Source file path for metadata

    Returns:
        List of DocumentChunk objects with metadata

    Example:
        >>> text = "Item 1: PARAFUSO M8\\nItem 2: PORCA M10\\n..." * 100
        >>> chunks = chunk_text_recursive(text)
        >>> len(chunks)  # Depends on text length
        >>> chunks[0].chunk_size <= 3500
        True
    """
    if config is None:
        config = ChunkConfig()

    if not text or len(text) == 0:
        return []

    chunks = []
    separators = config.separators.copy()

    def _split_text_with_separator(
        text: str,
        separator: str,
        remaining_separators: List[str]
    ) -> List[str]:
        """Recursively split text using separators"""

        # Base case: no separator or empty text
        if not separator and not remaining_separators:
            # Last resort: split by character
            return [text[i:i + config.chunk_size]
                    for i in range(0, len(text), config.chunk_size - config.chunk_overlap)]

        # Split by current separator
        if separator:
            splits = text.split(separator)
        else:
            splits = [text]

        # Merge splits into chunks
        merged_chunks = []
        current_chunk = ""

        for i, split in enumerate(splits):
            # Add separator back (except for last split)
            if i < len(splits) - 1 and separator:
                split = split + separator

            # Check if adding this split exceeds chunk size
            if len(current_chunk) + len(split) <= config.chunk_size:
                current_chunk += split
            else:
                # Current chunk is full, save it
                if current_chunk:
                    merged_chunks.append(current_chunk)

                # Check if split itself is too large
                if len(split) > config.chunk_size:
                    # Need to split further with next separator
                    if remaining_separators:
                        next_sep = remaining_separators[0]
                        next_remaining = remaining_separators[1:]
                        sub_chunks = _split_text_with_separator(
                            split, next_sep, next_remaining
                        )
                        merged_chunks.extend(sub_chunks)
                    else:
                        # Force split at chunk size
                        merged_chunks.extend([
                            split[i:i + config.chunk_size]
                            for i in range(0, len(split), config.chunk_size)
                        ])
                    current_chunk = ""
                else:
                    current_chunk = split

        # Add remaining chunk
        if current_chunk:
            merged_chunks.append(current_chunk)

        return merged_chunks

    # Perform recursive splitting
    raw_chunks = _split_text_with_separator(
        text,
        separators[0] if separators else "",
        separators[1:] if len(separators) > 1 else []
    )

    # Add overlap between chunks
    overlapped_chunks = []
    for i, chunk_text in enumerate(raw_chunks):
        # Add overlap from previous chunk
        if i > 0 and config.chunk_overlap > 0:
            prev_chunk = raw_chunks[i - 1]
            overlap = prev_chunk[-config.chunk_overlap:]
            chunk_text = overlap + chunk_text

        overlapped_chunks.append(chunk_text)

    # Convert to DocumentChunk objects
    for i, chunk_text in enumerate(overlapped_chunks):
        # Detect which separator was used
        separators_used = []
        for sep in config.separators:
            if sep and sep in chunk_text:
                separators_used.append(repr(sep))  # repr for visibility (e.g., '\\n')

        # Check if chunk starts with separator
        starts_with_separator = False
        for sep in config.separators:
            if sep and chunk_text.startswith(sep):
                starts_with_separator = True
                break

        chunk = DocumentChunk(
            chunk_id=f"chunk_{i:04d}",
            index=i,
            content=chunk_text,
            source_file=source_file,
            chunk_size=len(chunk_text),
            overlap_size=config.chunk_overlap if i > 0 else 0,
            starts_with_separator=starts_with_separator,
            separators_used=separators_used[:5]  # Limit to 5 for readability
        )

        chunks.append(chunk)

    return chunks


def detect_line_item_boundaries(text: str) -> List[int]:
    """
    Detect line item boundaries in purchase orders.

    Common patterns for line items:
    - "Item 1:", "1.", "1)", "[1]"
    - "SKU:", "Part:", "Material:"
    - Numbered lists
    - Table rows

    Args:
        text: Text content to analyze

    Returns:
        List of character positions where line items start
    """
    boundaries = []

    # Patterns for line item detection
    patterns = [
        r'\n\s*(?:Item|ITEM)\s+\d+',  # "Item 1", "ITEM 12"
        r'\n\s*\d+\.',  # "1.", "12."
        r'\n\s*\d+\)',  # "1)", "12)"
        r'\n\s*\[\d+\]',  # "[1]", "[12]"
        r'\n\s*(?:SKU|Part|Material|Tipo|Código):',  # Field labels
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            boundaries.append(match.start())

    # Sort and deduplicate
    boundaries = sorted(set(boundaries))

    return boundaries


def chunk_with_line_item_preservation(
    text: str,
    config: ChunkConfig = None,
    source_file: str = ""
) -> List[DocumentChunk]:
    """
    Chunk text while preserving line item boundaries.

    This is optimized for purchase orders and BOMs where each line
    represents a SKU. We never want to split a line item across chunks.

    Strategy:
    1. Detect line item boundaries
    2. Create chunks that respect these boundaries
    3. Add overlap while preserving complete line items

    Args:
        text: Text content to chunk
        config: Chunking configuration
        source_file: Source file path

    Returns:
        List of DocumentChunk objects
    """
    if config is None:
        config = ChunkConfig()

    if not text or len(text) == 0:
        return []

    # Detect line item boundaries
    boundaries = detect_line_item_boundaries(text)

    if not boundaries:
        # No line items detected, use standard chunking
        return chunk_text_recursive(text, config, source_file)

    # Add start and end boundaries
    boundaries = [0] + boundaries + [len(text)]

    # Create chunks respecting line item boundaries
    chunks = []
    current_chunk_start = 0
    current_chunk_text = ""

    for i in range(1, len(boundaries)):
        boundary = boundaries[i]
        line_item = text[boundaries[i-1]:boundary]

        # Check if adding this line item exceeds chunk size
        if len(current_chunk_text) + len(line_item) > config.chunk_size:
            # Save current chunk if not empty
            if current_chunk_text:
                chunks.append(current_chunk_text)
                current_chunk_start = boundaries[i-1]

            # Start new chunk with overlap
            if chunks and config.chunk_overlap > 0:
                # Find previous line items for overlap
                overlap_start = max(0, current_chunk_start - config.chunk_overlap)
                # Find nearest boundary
                overlap_boundary = max([b for b in boundaries if b <= overlap_start] + [0])
                overlap_text = text[overlap_boundary:current_chunk_start]
                current_chunk_text = overlap_text + line_item
            else:
                current_chunk_text = line_item
        else:
            current_chunk_text += line_item

    # Add final chunk
    if current_chunk_text:
        chunks.append(current_chunk_text)

    # Convert to DocumentChunk objects
    result = []
    for i, chunk_text in enumerate(chunks):
        chunk = DocumentChunk(
            chunk_id=f"chunk_{i:04d}",
            index=i,
            content=chunk_text,
            source_file=source_file,
            chunk_size=len(chunk_text),
            overlap_size=config.chunk_overlap if i > 0 else 0,
            starts_with_separator=True,  # Preserved line item boundaries
            separators_used=["line_item_boundary"]
        )
        result.append(chunk)

    return result


# ============================================================================
# MAIN CHUNKING FUNCTION
# ============================================================================

def chunk_document(
    text: str,
    source_file: str = "",
    preserve_line_items: bool = True,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[DocumentChunk]:
    """
    Main chunking function with automatic strategy selection.

    Args:
        text: Text content to chunk
        source_file: Source file path for metadata
        preserve_line_items: Whether to preserve line item boundaries
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks in characters

    Returns:
        List of DocumentChunk objects

    Performance: < 2 seconds for 5000-line documents
    """
    config = ChunkConfig(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        preserve_line_items=preserve_line_items
    )

    if preserve_line_items:
        return chunk_with_line_item_preservation(text, config, source_file)
    else:
        return chunk_text_recursive(text, config, source_file)


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "ChunkConfig",
    "chunk_document",
    "chunk_text_recursive",
    "chunk_with_line_item_preservation",
    "detect_line_item_boundaries",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_CHUNK_OVERLAP",
]
