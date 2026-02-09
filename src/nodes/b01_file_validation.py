"""
Forjador v5 - B.1: File Validation & Metadata Extraction
Purpose: Validate file format, size, encoding and extract metadata
Version: 1.0.0
Date: 2026-02-09

This node performs:
- File format validation (PDF, Excel, CSV, Images)
- File size validation (max 100 MB)
- Line count validation (max 5000 lines)
- Encoding detection
- Metadata extraction

Performance Target: < 1 second
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import logging
import mimetypes

from src.state.schemas import FileMetadata, FileFormat

logger = logging.getLogger(__name__)


# ============================================================================
# FILE VALIDATION FUNCTIONS
# ============================================================================

def detect_file_format(file_path: str) -> FileFormat:
    """
    Detect file format from extension and MIME type.

    Args:
        file_path: Path to file

    Returns:
        FileFormat enum value

    Raises:
        ValueError: If file format is not supported
    """
    path = Path(file_path)
    extension = path.suffix.lower().lstrip('.')

    # Map extension to FileFormat
    format_mapping = {
        'pdf': FileFormat.PDF,
        'xlsx': FileFormat.XLSX,
        'csv': FileFormat.CSV,
        'png': FileFormat.PNG,
        'jpg': FileFormat.JPG,
        'jpeg': FileFormat.JPEG,
    }

    if extension not in format_mapping:
        # Try MIME type detection as fallback
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if 'pdf' in mime_type:
                return FileFormat.PDF
            elif 'spreadsheet' in mime_type or 'excel' in mime_type:
                return FileFormat.XLSX
            elif 'csv' in mime_type:
                return FileFormat.CSV
            elif 'png' in mime_type:
                return FileFormat.PNG
            elif 'jpeg' in mime_type or 'jpg' in mime_type:
                return FileFormat.JPG

        raise ValueError(
            f"Unsupported file format: {extension}. "
            f"Supported formats: {', '.join(format_mapping.keys())}"
        )

    return format_mapping[extension]


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to file

    Returns:
        File size in MB
    """
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return round(size_mb, 2)


def detect_encoding(file_path: str) -> str:
    """
    Detect file encoding for text files.

    Args:
        file_path: Path to file

    Returns:
        Detected encoding (utf-8, latin-1, etc.) or "binary" for non-text files
    """
    file_format = detect_file_format(file_path)

    # Binary formats
    if file_format in [FileFormat.PDF, FileFormat.XLSX, FileFormat.PNG, FileFormat.JPG, FileFormat.JPEG]:
        return "binary"

    # Text formats - detect encoding
    try:
        # Try UTF-8 first
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Read first 1KB
        return "utf-8"
    except UnicodeDecodeError:
        # Try Latin-1
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                f.read(1024)
            return "latin-1"
        except:
            # Try to detect with chardet if available
            try:
                import chardet
                with open(file_path, 'rb') as f:
                    raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                return result['encoding'] or "unknown"
            except ImportError:
                return "unknown"


def count_lines(file_path: str) -> int:
    """
    Count lines in text file.

    For non-text files (PDF, Excel, Images), returns 0.

    Args:
        file_path: Path to file

    Returns:
        Number of lines
    """
    file_format = detect_file_format(file_path)

    # Only count lines for CSV files
    if file_format == FileFormat.CSV:
        try:
            encoding = detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding if encoding != "binary" else "utf-8") as f:
                return sum(1 for _ in f)
        except Exception as e:
            logger.warning(f"Could not count lines: {e}")
            return 0

    # For Excel, try to count rows
    elif file_format == FileFormat.XLSX:
        try:
            import openpyxl
            workbook = openpyxl.load_workbook(file_path, read_only=True)
            sheet = workbook.active
            return sheet.max_row
        except Exception as e:
            logger.warning(f"Could not count Excel rows: {e}")
            return 0

    # For PDF, try to estimate from page count
    elif file_format == FileFormat.PDF:
        try:
            # Estimate ~50 lines per page
            page_count = count_pdf_pages(file_path)
            return page_count * 50
        except Exception as e:
            logger.warning(f"Could not estimate PDF lines: {e}")
            return 0

    return 0


def count_pdf_pages(file_path: str) -> int:
    """
    Count pages in PDF file.

    Args:
        file_path: Path to PDF file

    Returns:
        Number of pages
    """
    try:
        import pypdf
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            return len(reader.pages)
    except ImportError:
        # Try with PyPDF2 if pypdf is not available
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return len(reader.pages)
        except ImportError:
            logger.warning("PyPDF or PyPDF2 not available, cannot count PDF pages")
            return 0
    except Exception as e:
        logger.warning(f"Could not count PDF pages: {e}")
        return 0


def get_creation_date(file_path: str) -> datetime:
    """
    Get file creation date.

    Args:
        file_path: Path to file

    Returns:
        File creation datetime
    """
    stat = os.stat(file_path)
    # Use modification time as creation time (more reliable cross-platform)
    timestamp = stat.st_mtime
    return datetime.fromtimestamp(timestamp)


# ============================================================================
# MAIN VALIDATION FUNCTION
# ============================================================================

def validate_file_and_extract_metadata(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    B.1: Validate file and extract metadata.

    This is the entry point for the LCEL pipeline. It validates the input
    file and extracts metadata required for downstream processing.

    Validation Rules:
    - File must exist
    - Format must be supported (PDF, Excel, CSV, Images)
    - Size must be <= 100 MB
    - Line count must be <= 5000 (for text files)

    Args:
        state: Pipeline state dict with 'input_file_path' key

    Returns:
        Updated state dict with 'file_metadata' key

    Performance: < 1 second

    Example:
        >>> state = {"input_file_path": "/data/purchase_order.pdf"}
        >>> result = validate_file_and_extract_metadata(state)
        >>> result["file_metadata"]["is_valid"]
        True
    """
    file_path = state.get("input_file_path")

    if not file_path:
        raise ValueError("input_file_path is required in state")

    path = Path(file_path)

    logger.info(f"B.1: Validating file: {path.name}")

    validation_errors = []

    # Check file exists
    if not path.exists():
        validation_errors.append(f"File does not exist: {file_path}")
        return {
            **state,
            "file_metadata": FileMetadata(
                file_path=file_path,
                file_format=FileFormat.PDF,  # Default
                file_size_mb=0.0,
                is_valid=False,
                validation_errors=validation_errors,
            )
        }

    # Extract metadata
    try:
        file_format = detect_file_format(file_path)
        file_size_mb = get_file_size_mb(file_path)
        encoding = detect_encoding(file_path)
        line_count = count_lines(file_path)
        created_at = get_creation_date(file_path)

        # Additional metadata for PDFs
        page_count = None
        if file_format == FileFormat.PDF:
            page_count = count_pdf_pages(file_path)

        # Validation checks
        if file_size_mb > 100:
            validation_errors.append(
                f"File size {file_size_mb:.2f} MB exceeds maximum 100 MB"
            )

        if line_count > 5000:
            validation_errors.append(
                f"Line count {line_count} exceeds maximum 5000 lines"
            )

        is_valid = len(validation_errors) == 0

        # Create FileMetadata object
        metadata = FileMetadata(
            file_path=str(path.absolute()),
            file_format=file_format,
            file_size_mb=file_size_mb,
            line_count=line_count,
            page_count=page_count,
            encoding=encoding,
            created_at=created_at,
            is_valid=is_valid,
            validation_errors=validation_errors,
        )

        logger.info(
            f"B.1: File validation {'passed' if is_valid else 'FAILED'} - "
            f"{file_format.value.upper()}, {file_size_mb:.2f} MB, "
            f"{line_count or page_count or 0} lines/pages"
        )

        return {
            **state,
            "file_metadata": metadata,
        }

    except Exception as e:
        logger.error(f"B.1: Validation error: {e}", exc_info=True)
        validation_errors.append(f"Validation error: {str(e)}")

        return {
            **state,
            "file_metadata": FileMetadata(
                file_path=file_path,
                file_format=FileFormat.PDF,  # Default
                file_size_mb=0.0,
                is_valid=False,
                validation_errors=validation_errors,
            )
        }


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "validate_file_and_extract_metadata",
    "detect_file_format",
    "get_file_size_mb",
    "detect_encoding",
    "count_lines",
    "count_pdf_pages",
    "get_creation_date",
]
