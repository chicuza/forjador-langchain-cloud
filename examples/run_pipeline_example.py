"""
Forjador v5 - Pipeline Usage Examples
Purpose: Demonstrate how to use the SPEC-01 data pipeline
Version: 1.0.0
Date: 2026-02-09
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import run_pipeline
from src.utils.queue_processor import SimpleFileQueue
from src.nodes.b11_output import save_outputs_to_files


def example_1_single_file():
    """
    Example 1: Process a single file

    This is the simplest way to use the pipeline.
    """
    print("=" * 80)
    print("Example 1: Process a Single File")
    print("=" * 80)

    # Path to your file
    input_file = "purchase_order.pdf"

    # Run pipeline
    result = run_pipeline(input_file)

    # Print summary
    summary = result["summary"]
    print(f"\nProcessing Time: {summary['processing']['total_time_s']:.2f}s")
    print(f"Valid SKUs: {summary['extraction']['total_valid']}")
    print(f"Validation Rate: {summary['extraction']['validation_rate']:.1%}")

    # Save outputs
    save_outputs_to_files(result, output_dir="./output")

    print(f"\nOutputs saved to ./output/")


def example_2_queue_processor():
    """
    Example 2: Process multiple files using queue

    This is useful for batch processing many files.
    """
    print("=" * 80)
    print("Example 2: Queue Processor (Batch Processing)")
    print("=" * 80)

    # Initialize queue
    queue = SimpleFileQueue(
        input_dir="./queue/input",
        processing_dir="./queue/processing",
        output_dir="./queue/output",
        error_dir="./queue/error",
    )

    # Check queue status
    status = queue.get_queue_status()
    print(f"\nQueue Status:")
    print(f"  - Pending: {status['pending']}")
    print(f"  - Processing: {status['processing']}")
    print(f"  - Completed: {status['completed']}")
    print(f"  - Failed: {status['failed']}")

    if status['pending'] == 0:
        print("\nNo files in queue. Add files to ./queue/input/ to process them.")
        return

    # Process all files in queue
    print(f"\nProcessing {status['pending']} files...")

    queue.run_queue_processor(
        pipeline_func=run_pipeline,
        max_jobs=None,  # Process all
        poll_interval_s=5
    )

    # Final metrics
    metrics = queue.get_metrics()
    print(f"\nProcessing Complete!")
    print(f"  - Total Processed: {metrics['total_processed']}")
    print(f"  - Succeeded: {metrics['total_succeeded']}")
    print(f"  - Failed: {metrics['total_failed']}")
    print(f"  - Avg Time: {metrics['avg_processing_time_s']:.2f}s")


def example_3_custom_processing():
    """
    Example 3: Custom processing with pipeline steps

    This shows how to access individual pipeline components.
    """
    print("=" * 80)
    print("Example 3: Custom Processing")
    print("=" * 80)

    from src.nodes.b01_file_validation import validate_file_and_extract_metadata
    from src.nodes.b02_complexity_routing import classify_and_route

    # Step 1: Validate file
    state = {"input_file_path": "purchase_order.pdf"}
    state = validate_file_and_extract_metadata(state)

    print(f"\nFile Metadata:")
    metadata = state["file_metadata"]
    print(f"  - Format: {metadata.file_format.value}")
    print(f"  - Size: {metadata.file_size_mb:.2f} MB")
    print(f"  - Valid: {metadata.is_valid}")

    # Step 2: Classify complexity
    state = classify_and_route(state)

    print(f"\nComplexity Classification:")
    classification = state["complexity_classification"]
    print(f"  - Tier: {classification.tier.value}")
    print(f"  - Name: {classification.tier_name}")
    print(f"  - Primary Parser: {classification.primary_parser.value}")
    print(f"  - Est. Time: {classification.avg_processing_time_s:.1f}s")

    # Continue with full pipeline if needed
    result = run_pipeline(state["input_file_path"])
    print(f"\nFull pipeline completed in {result['total_processing_time_s']:.2f}s")


def example_4_error_handling():
    """
    Example 4: Error handling and validation

    This shows how to handle errors and invalid SKUs.
    """
    print("=" * 80)
    print("Example 4: Error Handling")
    print("=" * 80)

    try:
        # Process file
        result = run_pipeline("purchase_order.pdf")

        # Check for invalid SKUs
        invalid_skus = result.get("invalid_skus", [])

        if invalid_skus:
            print(f"\nFound {len(invalid_skus)} invalid SKUs:")

            for sku, validation_result in invalid_skus[:5]:  # Show first 5
                print(f"\n  SKU: {sku.descricao_original[:60]}...")
                print(f"  Errors:")
                for error in validation_result.errors:
                    print(f"    - {error}")

        # Check warnings
        warnings = result.get("warnings", [])
        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for warning in warnings:
                print(f"  - {warning}")

        # Check errors
        errors = result.get("errors", [])
        if errors:
            print(f"\nErrors ({len(errors)}):")
            for error in errors:
                print(f"  - {error}")

    except Exception as e:
        print(f"\nPipeline Error: {e}")
        import traceback
        traceback.print_exc()


def example_5_statistics():
    """
    Example 5: Extract and display statistics

    This shows how to access detailed statistics from the pipeline.
    """
    print("=" * 80)
    print("Example 5: Detailed Statistics")
    print("=" * 80)

    # Process file
    result = run_pipeline("purchase_order.pdf")

    # Access summary statistics
    summary = result["summary"]

    print(f"\nFile Information:")
    print(f"  - Path: {summary['file']['path']}")
    print(f"  - Format: {summary['file']['format']}")
    print(f"  - Size: {summary['file']['size_mb']:.2f} MB")

    print(f"\nProcessing Details:")
    print(f"  - Started: {summary['processing']['started_at']}")
    print(f"  - Completed: {summary['processing']['completed_at']}")
    print(f"  - Total Time: {summary['processing']['total_time_s']:.2f}s")
    print(f"  - Complexity Tier: {summary['processing']['complexity_tier']}")
    print(f"  - Parser Used: {summary['processing']['parser_used']}")
    print(f"  - Chunks Created: {summary['processing']['chunks_created']}")

    print(f"\nQuality Metrics:")
    print(f"  - Quality Gate Passed: {summary['quality']['quality_gate_passed']}")
    print(f"  - Quality Score: {summary['quality']['quality_score']:.3f}")
    print(f"  - Completeness Score: {summary['quality']['completeness_score']:.3f}")

    print(f"\nExtraction Results:")
    print(f"  - Total Extracted: {summary['extraction']['total_extracted']}")
    print(f"  - Valid: {summary['extraction']['total_valid']}")
    print(f"  - Invalid: {summary['extraction']['total_invalid']}")
    print(f"  - Validation Rate: {summary['extraction']['validation_rate']:.1%}")
    print(f"  - Avg Confidence: {summary['extraction']['avg_confidence']:.3f}")

    print(f"\nSKU Statistics:")
    stats = summary['statistics']
    print(f"  - Total Quantity: {stats['total_quantity']:,}")

    print(f"\n  By Type:")
    for tipo, count in stats['skus_by_type'].items():
        print(f"    - {tipo}: {count}")

    print(f"\n  By Material:")
    for material, count in list(stats['skus_by_material'].items())[:5]:  # Top 5
        print(f"    - {material}: {count}")


def setup_queue_directories():
    """
    Setup queue directories for batch processing
    """
    print("Setting up queue directories...")

    dirs = [
        "./queue/input",
        "./queue/processing",
        "./queue/output",
        "./queue/error",
        "./output",
        "./test_data",
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    print(f"Created directories:")
    for dir_path in dirs:
        print(f"  - {dir_path}")


if __name__ == "__main__":
    # Setup directories
    setup_queue_directories()

    # Run examples
    print("\nForjador v5 - Pipeline Examples")
    print("\nAvailable examples:")
    print("  1. Process a single file")
    print("  2. Queue processor (batch)")
    print("  3. Custom processing")
    print("  4. Error handling")
    print("  5. Detailed statistics")
    print("\nRun with: python examples/run_pipeline_example.py")
    print("\nNote: Update file paths in the script before running.")
