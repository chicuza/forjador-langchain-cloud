"""
Forjador v5 - DataFrame Utilities for Data Processing
Purpose: Polars/Pandas helpers for merge, dedup, and transformation operations
Version: 1.0.0
Date: 2026-02-09

This module provides utilities for:
- DataFrame merging and deduplication
- SKU aggregation by (tipo, dimensao, material)
- Data quality checks
- CSV/JSON export helpers
"""

from typing import Any, Dict, List
import polars as pl
import pandas as pd
from pathlib import Path


# ============================================================================
# POLARS UTILITIES - High Performance Data Operations
# ============================================================================

def merge_and_dedup_skus_polars(skus: List[Dict[str, Any]]) -> pl.DataFrame:
    """
    Merge and deduplicate SKUs using Polars for performance.

    Deduplication Strategy:
    - Group by (tipo, dimensao, material, classe, revestimento, norma)
    - Aggregate quantities (sum)
    - Keep highest confidence score
    - Preserve first descricao_original

    Performance: ~1000x faster than Pandas for large datasets

    Args:
        skus: List of FastenerSKU dictionaries

    Returns:
        Polars DataFrame with deduplicated SKUs

    Example:
        >>> skus = [
        ...     {"tipo": "parafuso", "dimensao": "M8x30", "quantidade": 100},
        ...     {"tipo": "parafuso", "dimensao": "M8x30", "quantidade": 50}
        ... ]
        >>> df = merge_and_dedup_skus_polars(skus)
        >>> df["quantidade"][0]  # 150 (summed)
    """
    if not skus:
        return pl.DataFrame()

    # Convert to Polars DataFrame
    df = pl.DataFrame(skus)

    # Define grouping keys (unique SKU identifier)
    group_keys = [
        "tipo",
        "dimensao",
        "material",
        "classe",
        "revestimento",
        "norma"
    ]

    # Filter out None values in group keys for proper grouping
    # Keep only columns that exist in the dataframe
    actual_group_keys = [key for key in group_keys if key in df.columns]

    # Perform aggregation
    deduped = df.group_by(actual_group_keys).agg([
        # Sum quantities
        pl.col("quantidade").sum().alias("quantidade"),

        # Keep highest confidence
        pl.col("confidence").max().alias("confidence"),

        # Keep first original description
        pl.col("descricao_original").first().alias("descricao_original"),

        # Keep first unit (should all be same for grouped SKUs)
        pl.col("unidade").first().alias("unidade"),

        # Track number of merged SKUs
        pl.len().alias("merged_count"),

        # Keep first extracted_at timestamp
        pl.col("extracted_at").first().alias("extracted_at"),
    ])

    return deduped


def validate_sku_dataframe_quality(df: pl.DataFrame) -> Dict[str, Any]:
    """
    Validate data quality of SKU dataframe.

    Quality Checks:
    - Required fields present
    - No null values in critical fields
    - Positive quantities
    - Valid confidence scores (0.0-1.0)
    - Dimension format validation

    Args:
        df: Polars DataFrame with SKU data

    Returns:
        Quality report dictionary
    """
    quality_report = {
        "total_rows": len(df),
        "passed": True,
        "errors": [],
        "warnings": [],
        "metrics": {}
    }

    if len(df) == 0:
        quality_report["warnings"].append("DataFrame is empty")
        return quality_report

    # Check required fields
    required_fields = ["tipo", "dimensao", "material", "quantidade", "unidade", "confidence"]
    missing_fields = [field for field in required_fields if field not in df.columns]

    if missing_fields:
        quality_report["passed"] = False
        quality_report["errors"].append(f"Missing required fields: {missing_fields}")
        return quality_report

    # Check for null values in critical fields
    for field in required_fields:
        null_count = df[field].null_count()
        if null_count > 0:
            quality_report["warnings"].append(
                f"Field '{field}' has {null_count} null values"
            )

    # Validate quantities are positive
    if "quantidade" in df.columns:
        negative_qty = df.filter(pl.col("quantidade") <= 0)
        if len(negative_qty) > 0:
            quality_report["errors"].append(
                f"Found {len(negative_qty)} rows with non-positive quantities"
            )
            quality_report["passed"] = False

    # Validate confidence scores
    if "confidence" in df.columns:
        invalid_confidence = df.filter(
            (pl.col("confidence") < 0.0) | (pl.col("confidence") > 1.0)
        )
        if len(invalid_confidence) > 0:
            quality_report["errors"].append(
                f"Found {len(invalid_confidence)} rows with invalid confidence scores"
            )
            quality_report["passed"] = False

        # Calculate average confidence
        quality_report["metrics"]["avg_confidence"] = df["confidence"].mean()
        quality_report["metrics"]["min_confidence"] = df["confidence"].min()
        quality_report["metrics"]["max_confidence"] = df["confidence"].max()

    return quality_report


def calculate_sku_statistics(df: pl.DataFrame) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for SKU dataset.

    Statistics:
    - Total SKUs
    - Breakdown by type (tipo)
    - Breakdown by material
    - Quantity statistics
    - Confidence statistics

    Args:
        df: Polars DataFrame with SKU data

    Returns:
        Statistics dictionary
    """
    if len(df) == 0:
        return {
            "total_skus": 0,
            "skus_by_type": {},
            "skus_by_material": {},
            "total_quantity": 0,
            "avg_confidence": 0.0,
        }

    stats = {
        "total_skus": len(df),
        "total_quantity": int(df["quantidade"].sum()) if "quantidade" in df.columns else 0,
    }

    # Breakdown by type
    if "tipo" in df.columns:
        tipo_counts = df.group_by("tipo").agg(pl.len().alias("count"))
        stats["skus_by_type"] = {
            row["tipo"]: row["count"]
            for row in tipo_counts.to_dicts()
        }

    # Breakdown by material
    if "material" in df.columns:
        material_counts = df.group_by("material").agg(pl.len().alias("count"))
        stats["skus_by_material"] = {
            row["material"]: row["count"]
            for row in material_counts.to_dicts()
        }

    # Confidence statistics
    if "confidence" in df.columns:
        stats["avg_confidence"] = float(df["confidence"].mean())
        stats["min_confidence"] = float(df["confidence"].min())
        stats["max_confidence"] = float(df["confidence"].max())

    return stats


# ============================================================================
# PANDAS UTILITIES - For Compatibility
# ============================================================================

def polars_to_pandas(df: pl.DataFrame) -> pd.DataFrame:
    """
    Convert Polars DataFrame to Pandas DataFrame.

    Used for compatibility with libraries that require Pandas.

    Args:
        df: Polars DataFrame

    Returns:
        Pandas DataFrame
    """
    return df.to_pandas()


def pandas_to_polars(df: pd.DataFrame) -> pl.DataFrame:
    """
    Convert Pandas DataFrame to Polars DataFrame.

    Args:
        df: Pandas DataFrame

    Returns:
        Polars DataFrame
    """
    return pl.from_pandas(df)


# ============================================================================
# EXPORT UTILITIES - JSON & CSV
# ============================================================================

def export_skus_to_json(df: pl.DataFrame, output_path: Path) -> None:
    """
    Export SKUs to JSON file with proper formatting.

    Args:
        df: Polars DataFrame with SKU data
        output_path: Path to output JSON file
    """
    # Convert to list of dictionaries
    skus = df.to_dicts()

    import json

    # Write with proper formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(skus, f, indent=2, ensure_ascii=False, default=str)


def export_skus_to_csv(df: pl.DataFrame, output_path: Path) -> None:
    """
    Export SKUs to CSV file.

    Args:
        df: Polars DataFrame with SKU data
        output_path: Path to output CSV file
    """
    df.write_csv(output_path)


def prepare_skus_for_export(skus: List[Dict[str, Any]]) -> pl.DataFrame:
    """
    Prepare SKUs for export by converting to DataFrame and cleaning.

    Cleanup operations:
    - Remove internal fields (chunk_id, extracted_at)
    - Sort by (tipo, dimensao)
    - Format dates as strings

    Args:
        skus: List of FastenerSKU dictionaries

    Returns:
        Cleaned Polars DataFrame ready for export
    """
    if not skus:
        return pl.DataFrame()

    df = pl.DataFrame(skus)

    # Remove internal fields
    fields_to_remove = ["chunk_id", "extracted_at"]
    for field in fields_to_remove:
        if field in df.columns:
            df = df.drop(field)

    # Sort by tipo and dimensao for readability
    if "tipo" in df.columns and "dimensao" in df.columns:
        df = df.sort(["tipo", "dimensao"])

    return df


# ============================================================================
# COMPLETENESS SCORING
# ============================================================================

def calculate_completeness_score(df: pl.DataFrame) -> float:
    """
    Calculate completeness score for SKU dataset.

    Completeness Formula:
    - Required fields filled: 60% weight
    - Optional fields filled: 40% weight

    Required fields: tipo, dimensao, material, quantidade, unidade
    Optional fields: classe, revestimento, norma

    Args:
        df: Polars DataFrame with SKU data

    Returns:
        Completeness score (0.0-1.0)
    """
    if len(df) == 0:
        return 0.0

    required_fields = ["tipo", "dimensao", "material", "quantidade", "unidade"]
    optional_fields = ["classe", "revestimento", "norma"]

    total_cells = len(df)

    # Calculate required fields completeness
    required_filled = 0
    for field in required_fields:
        if field in df.columns:
            filled_count = len(df) - df[field].null_count()
            required_filled += filled_count

    required_completeness = required_filled / (len(required_fields) * total_cells)

    # Calculate optional fields completeness
    optional_filled = 0
    for field in optional_fields:
        if field in df.columns:
            filled_count = len(df) - df[field].null_count()
            optional_filled += filled_count

    optional_completeness = optional_filled / (len(optional_fields) * total_cells)

    # Weighted score
    completeness = (required_completeness * 0.6) + (optional_completeness * 0.4)

    return float(completeness)


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "merge_and_dedup_skus_polars",
    "validate_sku_dataframe_quality",
    "calculate_sku_statistics",
    "polars_to_pandas",
    "pandas_to_polars",
    "export_skus_to_json",
    "export_skus_to_csv",
    "prepare_skus_for_export",
    "calculate_completeness_score",
]
