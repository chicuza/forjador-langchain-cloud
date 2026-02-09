"""
Forjador v5 - SPEC-01 MVP LCEL Pipeline
Purpose: Complete 6-stage data pipeline for industrial fastener SKU extraction
Version: 1.0.0
Date: 2026-02-09

This module implements the complete SPEC-01 pipeline using LangChain LCEL:
B.1 → B.2 → B.3 → B.4 → B.5 → B.6 → B.7 → B.11

Pipeline Stages:
- B.1: File Validation & Metadata Extraction
- B.2: Complexity Classification & Parser Routing
- B.3: Document Parsing (3 parsers: Docling, Gemini Vision, Pandas)
- B.4: Quality Gate (threshold 0.85) with retry logic
- B.5: Intelligent Chunking (~3500 chars, ~250 overlap)
- B.6: Structured SKU Extraction (Gemini 2.5 Flash + Pydantic)
- B.7: Hybrid Validation (YAML + Pydantic)
- B.11: Output Generation (JSON + CSV)

Performance Target: < 25 seconds end-to-end
"""

import logging
from typing import Any, Dict
from datetime import datetime

from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda,
    RunnableBranch,
)

# Import pipeline nodes
from src.nodes.b01_file_validation import validate_file_and_extract_metadata
from src.nodes.b02_complexity_routing import classify_and_route
from src.parsers.parser_factory import parse_document, retry_with_fallback_parser
from src.nodes.b04_quality_gate import evaluate_quality_gate, should_retry_with_fallback
from src.nodes.b05_chunking import chunk_parsed_content
from src.nodes.b06_extraction import extract_skus
from src.nodes.b07_hybrid_validation import validate_skus_batch
from src.nodes.b11_output import generate_outputs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# PIPELINE STATE INITIALIZATION
# ============================================================================

def initialize_pipeline_state(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize pipeline state with metadata and tracking fields.

    Args:
        input_data: Initial input (must contain 'input_file_path')

    Returns:
        Initialized state dictionary
    """
    return {
        **input_data,
        "pipeline_started_at": datetime.utcnow(),
        "current_stage": "B.1",
        "errors": [],
        "warnings": [],
    }


# ============================================================================
# QUALITY GATE RETRY LOGIC
# ============================================================================

def quality_gate_branch_logic(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle quality gate pass/fail logic.

    If quality gate passes: continue to chunking
    If quality gate fails: retry with fallback parser

    Args:
        state: Pipeline state with quality_gate result

    Returns:
        Updated state
    """
    quality_gate = state.get("quality_gate")

    if not quality_gate:
        logger.warning("Quality gate result not found, continuing...")
        return state

    if quality_gate.passed:
        logger.info("Quality gate PASSED, continuing to chunking")
        state["current_stage"] = "B.5"
        return state
    else:
        if quality_gate.should_retry:
            logger.warning("Quality gate FAILED, retrying with fallback parser")
            # Retry parsing
            state = retry_with_fallback_parser(state)
            # Re-evaluate quality gate
            state = evaluate_quality_gate(state)
            state["current_stage"] = "B.4-retry"
            return state
        else:
            logger.error("Quality gate FAILED and max retries reached")
            state["warnings"].append("Quality gate failed after max retries")
            state["current_stage"] = "B.5"
            return state


# ============================================================================
# STAGE TRACKING WRAPPERS
# ============================================================================

def wrap_with_stage_tracking(func, stage_name: str):
    """
    Wrap a pipeline function with stage tracking.

    Args:
        func: Function to wrap
        stage_name: Stage name (e.g., "B.1", "B.2")

    Returns:
        Wrapped function that updates current_stage
    """
    def wrapped(state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"=== Stage {stage_name} Starting ===")
        state["current_stage"] = stage_name
        result = func(state)
        logger.info(f"=== Stage {stage_name} Complete ===")
        return result

    return wrapped


# ============================================================================
# MAIN LCEL PIPELINE
# ============================================================================

def create_forjador_pipeline():
    """
    Create the complete SPEC-01 LCEL pipeline.

    Pipeline Flow:
    1. B.1: File Validation → metadata
    2. B.2: Complexity Classification → parser selection
    3. B.3: Document Parsing → raw content
    4. B.4: Quality Gate → pass/retry decision
    5. B.5: Chunking → document chunks
    6. B.6: Extraction → FastenerSKU objects
    7. B.7: Validation → valid/invalid SKUs
    8. B.11: Output → JSON + CSV + summary

    Returns:
        LCEL Runnable pipeline
    """
    pipeline = (
        # Initialize state
        RunnableLambda(initialize_pipeline_state)

        # B.1: File Validation & Metadata Extraction (< 1s)
        | RunnablePassthrough.assign(
            file_metadata=RunnableLambda(
                wrap_with_stage_tracking(validate_file_and_extract_metadata, "B.1")
            )
        )

        # B.2: Complexity Classification & Parser Routing (< 0.5s)
        | RunnablePassthrough.assign(
            complexity_classification=RunnableLambda(
                wrap_with_stage_tracking(classify_and_route, "B.2")
            )
        )

        # B.3: Document Parsing (< 5s)
        | RunnablePassthrough.assign(
            parsed_content=RunnableLambda(
                wrap_with_stage_tracking(parse_document, "B.3")
            )
        )

        # B.4: Quality Gate (< 1s)
        | RunnablePassthrough.assign(
            quality_gate=RunnableLambda(
                wrap_with_stage_tracking(evaluate_quality_gate, "B.4")
            )
        )

        # B.4: Quality Gate Branch - Pass/Retry
        | RunnableBranch(
            # Branch 1: Quality gate passed - continue
            (
                lambda x: x.get("quality_gate") and x["quality_gate"].passed,
                RunnablePassthrough()
            ),
            # Branch 2: Quality gate failed - retry with fallback
            (
                lambda x: x.get("quality_gate") and x["quality_gate"].should_retry,
                RunnableLambda(quality_gate_branch_logic)
            ),
            # Default: Continue anyway (max retries reached)
            RunnablePassthrough()
        )

        # B.5: Intelligent Chunking (< 2s)
        | RunnablePassthrough.assign(
            chunks=RunnableLambda(
                wrap_with_stage_tracking(chunk_parsed_content, "B.5")
            )
        )

        # B.6: Structured SKU Extraction (< 10s)
        | RunnablePassthrough.assign(
            extracted_skus=RunnableLambda(
                wrap_with_stage_tracking(extract_skus, "B.6")
            )
        )

        # B.7: Hybrid Validation (< 3s)
        | RunnableLambda(
            wrap_with_stage_tracking(validate_skus_batch, "B.7")
        )

        # B.11: Output Generation (< 2s)
        | RunnableLambda(
            wrap_with_stage_tracking(generate_outputs, "B.11")
        )
    )

    return pipeline


# ============================================================================
# PIPELINE EXECUTION
# ============================================================================

def run_pipeline(input_file_path: str) -> Dict[str, Any]:
    """
    Run the complete SPEC-01 pipeline on a file.

    Args:
        input_file_path: Path to input file (PDF, Excel, CSV, or image)

    Returns:
        Complete pipeline result with outputs

    Performance: < 25 seconds for typical 100-line purchase order

    Example:
        >>> result = run_pipeline("purchase_order.pdf")
        >>> result["summary"]["extraction"]["total_valid"]
        145
        >>> result["json_output"]
        {...}
    """
    logger.info("=" * 80)
    logger.info(f"Starting SPEC-01 Pipeline: {input_file_path}")
    logger.info("=" * 80)

    # Create pipeline
    pipeline = create_forjador_pipeline()

    # Execute pipeline
    try:
        result = pipeline.invoke({"input_file_path": input_file_path})

        # Log summary
        summary = result.get("summary", {})
        processing_time = summary.get("processing", {}).get("total_time_s", 0.0)
        extraction = summary.get("extraction", {})
        total_valid = extraction.get("total_valid", 0)
        validation_rate = extraction.get("validation_rate", 0.0)

        logger.info("=" * 80)
        logger.info("Pipeline Complete!")
        logger.info(f"Processing Time: {processing_time:.2f}s")
        logger.info(f"Valid SKUs: {total_valid}")
        logger.info(f"Validation Rate: {validation_rate:.1%}")
        logger.info("=" * 80)

        return result

    except Exception as e:
        logger.error(f"Pipeline execution error: {e}", exc_info=True)
        raise


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "create_forjador_pipeline",
    "run_pipeline",
]


# Create the graph instance for LangGraph Platform Cloud compatibility
graph = create_forjador_pipeline()


# ============================================================================
# CLI INTERFACE (for testing)
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.agent <input_file_path>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Run pipeline
    result = run_pipeline(input_file)

    # Print summary
    print("\n" + "=" * 80)
    print("PIPELINE RESULT SUMMARY")
    print("=" * 80)
    print(f"\nFile: {result['input_file_path']}")
    print(f"\nProcessing Time: {result['total_processing_time_s']:.2f}s")
    print(f"\nExtraction:")
    print(f"  - Total Extracted: {result['total_skus_extracted']}")
    print(f"  - Valid: {result['total_skus_valid']}")
    print(f"  - Invalid: {result['total_skus_invalid']}")
    print(f"  - Avg Confidence: {result['avg_confidence']:.3f}")
    print("\n" + "=" * 80)
