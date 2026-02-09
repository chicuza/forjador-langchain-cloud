"""
Forjador v5 - B.11: Output Generation
Purpose: Generate JSON, CSV outputs and summary reports
Version: 1.0.0
Date: 2026-02-09

This node performs:
- JSON output generation (complete data)
- CSV output generation (tabular format)
- Summary report generation
- Quality metrics calculation

Performance Target: < 2 seconds
"""

import json
from typing import Any, Dict, List
from datetime import datetime
import logging
from pathlib import Path
import polars as pl

from src.state.schemas import FastenerSKU, SKUStatistics
from src.utils.dataframe_utils import (
    prepare_skus_for_export,
    calculate_sku_statistics,
    calculate_completeness_score,
)

logger = logging.getLogger(__name__)


# ============================================================================
# OUTPUT GENERATION FUNCTIONS
# ============================================================================

def generate_json_output(valid_skus: List[FastenerSKU]) -> Dict[str, Any]:
    """
    Generate JSON output with complete SKU data.

    Output Structure:
    {
        "metadata": {...},
        "skus": [...],
        "statistics": {...}
    }

    Args:
        valid_skus: List of validated FastenerSKU objects

    Returns:
        JSON-serializable dictionary
    """
    # Convert SKUs to dictionaries
    sku_dicts = []
    for sku in valid_skus:
        if isinstance(sku, FastenerSKU):
            sku_dict = sku.model_dump()
        else:
            sku_dict = sku
        sku_dicts.append(sku_dict)

    # Create output
    output = {
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "pipeline": "SPEC-01",
            "total_skus": len(sku_dicts),
        },
        "skus": sku_dicts,
    }

    return output


def generate_csv_output(valid_skus: List[FastenerSKU]) -> str:
    """
    Generate CSV output with tabular SKU data.

    CSV Columns:
    - tipo
    - dimensao
    - material
    - classe
    - quantidade
    - unidade
    - descricao_original
    - confidence
    - revestimento
    - norma

    Args:
        valid_skus: List of validated FastenerSKU objects

    Returns:
        CSV string
    """
    if not valid_skus:
        return "tipo,dimensao,material,classe,quantidade,unidade,descricao_original,confidence,revestimento,norma\n"

    # Convert to Polars DataFrame
    sku_dicts = []
    for sku in valid_skus:
        if isinstance(sku, FastenerSKU):
            sku_dict = sku.model_dump()
        else:
            sku_dict = sku
        sku_dicts.append(sku_dict)

    df = prepare_skus_for_export(sku_dicts)

    # Convert to CSV string
    csv_string = df.write_csv()

    return csv_string


def generate_summary_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary report with quality metrics.

    Summary includes:
    - Processing time
    - SKU counts (extracted, valid, invalid)
    - Quality metrics
    - Breakdown by type and material
    - Validation statistics

    Args:
        state: Complete pipeline state

    Returns:
        Summary report dictionary
    """
    # Extract data from state
    valid_skus = state.get("valid_skus", [])
    invalid_skus = state.get("invalid_skus", [])
    extracted_skus = state.get("extracted_skus", [])
    file_metadata = state.get("file_metadata")
    complexity_classification = state.get("complexity_classification")
    quality_gate = state.get("quality_gate")
    chunks = state.get("chunks", [])

    # Calculate processing time
    pipeline_started_at = state.get("pipeline_started_at")
    pipeline_completed_at = datetime.utcnow()
    if pipeline_started_at:
        if isinstance(pipeline_started_at, str):
            pipeline_started_at = datetime.fromisoformat(pipeline_started_at)
        processing_time_s = (pipeline_completed_at - pipeline_started_at).total_seconds()
    else:
        processing_time_s = 0.0

    # Calculate statistics
    total_extracted = len(extracted_skus)
    total_valid = len(valid_skus)
    total_invalid = len(invalid_skus)
    validation_rate = total_valid / total_extracted if total_extracted > 0 else 0.0

    # Calculate average confidence
    if valid_skus:
        confidences = [
            sku.confidence if isinstance(sku, FastenerSKU) else sku.get("confidence", 0.0)
            for sku in valid_skus
        ]
        avg_confidence = sum(confidences) / len(confidences)
    else:
        avg_confidence = 0.0

    # Get statistics by type and material
    if valid_skus:
        sku_dicts = [
            sku.model_dump() if isinstance(sku, FastenerSKU) else sku
            for sku in valid_skus
        ]
        df = pl.DataFrame(sku_dicts)
        stats = calculate_sku_statistics(df)
        completeness = calculate_completeness_score(df)
    else:
        stats = {
            "total_skus": 0,
            "skus_by_type": {},
            "skus_by_material": {},
            "total_quantity": 0,
        }
        completeness = 0.0

    # Build summary
    summary = {
        "file": {
            "path": state.get("input_file_path", "unknown"),
            "format": file_metadata.file_format.value if file_metadata else "unknown",
            "size_mb": file_metadata.file_size_mb if file_metadata else 0.0,
        },
        "processing": {
            "started_at": pipeline_started_at.isoformat() if pipeline_started_at else None,
            "completed_at": pipeline_completed_at.isoformat(),
            "total_time_s": round(processing_time_s, 2),
            "complexity_tier": complexity_classification.tier.value if complexity_classification else "unknown",
            "parser_used": complexity_classification.primary_parser.value if complexity_classification else "unknown",
            "chunks_created": len(chunks),
        },
        "quality": {
            "quality_gate_passed": quality_gate.passed if quality_gate else False,
            "quality_score": round(quality_gate.score, 3) if quality_gate else 0.0,
            "completeness_score": round(completeness, 3),
        },
        "extraction": {
            "total_extracted": total_extracted,
            "total_valid": total_valid,
            "total_invalid": total_invalid,
            "validation_rate": round(validation_rate, 3),
            "avg_confidence": round(avg_confidence, 3),
        },
        "statistics": {
            "total_quantity": stats.get("total_quantity", 0),
            "skus_by_type": stats.get("skus_by_type", {}),
            "skus_by_material": stats.get("skus_by_material", {}),
        },
        "warnings": state.get("warnings", []),
        "errors": state.get("errors", []),
    }

    return summary


# ============================================================================
# MAIN OUTPUT FUNCTION
# ============================================================================

def generate_outputs(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    B.11: Generate all outputs (JSON, CSV, summary).

    This is the final stage of the SPEC-01 pipeline. It generates all
    required outputs and prepares them for saving.

    Args:
        state: Complete pipeline state

    Returns:
        Updated state dict with output fields

    Performance: < 2 seconds

    Example:
        >>> state = {"valid_skus": [...], "invalid_skus": [...]}
        >>> result = generate_outputs(state)
        >>> result["json_output"]["metadata"]["total_skus"]
        145
    """
    valid_skus = state.get("valid_skus", [])

    logger.info(f"B.11: Generating outputs for {len(valid_skus)} valid SKUs")

    # Mark completion time
    state["pipeline_completed_at"] = datetime.utcnow()

    # Calculate total processing time
    if "pipeline_started_at" in state:
        start_time = state["pipeline_started_at"]
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        processing_time = (state["pipeline_completed_at"] - start_time).total_seconds()
        state["total_processing_time_s"] = processing_time
    else:
        state["total_processing_time_s"] = 0.0

    # Generate JSON output
    json_output = generate_json_output(valid_skus)
    logger.info("B.11: Generated JSON output")

    # Generate CSV output
    csv_output = generate_csv_output(valid_skus)
    logger.info("B.11: Generated CSV output")

    # Generate summary report
    summary = generate_summary_report(state)
    logger.info(
        f"B.11: Generated summary - "
        f"Processing time: {summary['processing']['total_time_s']:.2f}s, "
        f"Validation rate: {summary['extraction']['validation_rate']:.1%}"
    )

    # Update state metrics
    state["total_skus_extracted"] = len(state.get("extracted_skus", []))
    state["total_skus_valid"] = len(valid_skus)
    state["total_skus_invalid"] = len(state.get("invalid_skus", []))
    state["avg_confidence"] = summary["extraction"]["avg_confidence"]

    # Add outputs to state
    state["json_output"] = json_output
    state["csv_output"] = csv_output
    state["summary"] = summary

    # Mark current stage as complete
    state["current_stage"] = "COMPLETE"

    return state


def save_outputs_to_files(
    state: Dict[str, Any],
    output_dir: str = "./output"
) -> None:
    """
    Save outputs to files.

    Files created:
    - {filename}.json - Complete SKU data
    - {filename}.csv - Tabular SKU data
    - {filename}_summary.json - Summary report

    Args:
        state: Pipeline state with outputs
        output_dir: Directory to save outputs
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Get filename
    input_file = Path(state.get("input_file_path", "output"))
    stem = input_file.stem

    # Save JSON
    if "json_output" in state:
        json_path = output_path / f"{stem}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(state["json_output"], f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Saved JSON output: {json_path}")

    # Save CSV
    if "csv_output" in state:
        csv_path = output_path / f"{stem}.csv"
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(state["csv_output"])
        logger.info(f"Saved CSV output: {csv_path}")

    # Save summary
    if "summary" in state:
        summary_path = output_path / f"{stem}_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(state["summary"], f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Saved summary: {summary_path}")


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "generate_outputs",
    "generate_json_output",
    "generate_csv_output",
    "generate_summary_report",
    "save_outputs_to_files",
]
