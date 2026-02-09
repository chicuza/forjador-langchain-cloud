"""
Forjador v5 - File-Based Queue Processor
Purpose: Simple file-based job queue for SPEC-01 (no database required)
Version: 1.0.0
Date: 2026-02-09

This module provides a lightweight queue system for processing files:
- Poll input directory for new files
- Move files through processing stages
- Track processing metrics
- Handle errors gracefully
- Support for PDF, Excel, CSV files
"""

import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# SIMPLE FILE QUEUE
# ============================================================================

class SimpleFileQueue:
    """
    File-based job queue for SPEC-01 pipeline.

    Directory Structure:
    - queue/input/       - New files to process
    - queue/processing/  - Files currently being processed
    - queue/output/      - Successfully processed files + results
    - queue/error/       - Failed files + error logs

    Features:
    - Automatic directory creation
    - File locking (via rename atomicity)
    - Processing metrics
    - Error handling and logging
    - Support for multiple file formats
    """

    SUPPORTED_FORMATS = [".pdf", ".xlsx", ".csv", ".png", ".jpg", ".jpeg"]

    def __init__(
        self,
        input_dir: str = "./queue/input",
        processing_dir: str = "./queue/processing",
        output_dir: str = "./queue/output",
        error_dir: str = "./queue/error",
    ):
        """
        Initialize file queue with directory paths.

        Args:
            input_dir: Directory for input files
            processing_dir: Directory for files being processed
            output_dir: Directory for successfully processed files
            error_dir: Directory for failed files
        """
        self.input_dir = Path(input_dir)
        self.processing_dir = Path(processing_dir)
        self.output_dir = Path(output_dir)
        self.error_dir = Path(error_dir)

        # Create directories
        for directory in [self.input_dir, self.processing_dir, self.output_dir, self.error_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Processing metrics
        self.metrics = {
            "total_processed": 0,
            "total_succeeded": 0,
            "total_failed": 0,
            "avg_processing_time_s": 0.0,
            "last_processed_at": None,
        }

        logger.info(f"SimpleFileQueue initialized with input_dir={input_dir}")

    def poll_for_jobs(self, timeout_s: Optional[int] = None) -> Optional[Path]:
        """
        Poll input directory for new files.

        This method blocks until a file is available or timeout is reached.

        Args:
            timeout_s: Maximum time to wait in seconds (None = wait forever)

        Returns:
            Path to first available file, or None if timeout reached

        Example:
            >>> queue = SimpleFileQueue()
            >>> file = queue.poll_for_jobs(timeout_s=60)
            >>> if file:
            ...     process(file)
        """
        start_time = time.time()

        while True:
            # Check for files
            files = self._get_pending_files()

            if files:
                logger.info(f"Found {len(files)} pending file(s)")
                return files[0]

            # Check timeout
            if timeout_s is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout_s:
                    logger.warning(f"Poll timeout after {elapsed:.1f}s")
                    return None

            # Sleep before next poll
            time.sleep(5)  # Poll every 5 seconds

    def _get_pending_files(self) -> List[Path]:
        """
        Get list of pending files from input directory.

        Returns:
            List of file paths sorted by creation time (oldest first)
        """
        files = []

        for ext in self.SUPPORTED_FORMATS:
            files.extend(self.input_dir.glob(f"*{ext}"))

        # Sort by creation time (oldest first)
        files.sort(key=lambda p: p.stat().st_mtime)

        return files

    def process_job(
        self,
        file_path: Path,
        pipeline_func: Callable[[str], Dict[str, Any]],
        save_outputs: bool = True
    ) -> Dict[str, Any]:
        """
        Process a single job through the pipeline.

        Workflow:
        1. Move file to processing directory (atomic operation)
        2. Execute pipeline function
        3. Save outputs to output directory
        4. Move original file to output directory
        5. Update metrics

        If any step fails, move file to error directory with error log.

        Args:
            file_path: Path to file to process
            pipeline_func: Pipeline function that takes file path and returns results
            save_outputs: Whether to save JSON/CSV outputs

        Returns:
            Processing result dictionary

        Example:
            >>> def my_pipeline(file_path):
            ...     return {"status": "success", "skus": [...]}
            >>> queue.process_job(file_path, my_pipeline)
        """
        start_time = time.time()
        processing_path = None

        try:
            # Step 1: Move to processing directory (atomic)
            processing_path = self.processing_dir / file_path.name
            logger.info(f"Processing: {file_path.name}")

            # Use shutil.move for cross-platform compatibility
            shutil.move(str(file_path), str(processing_path))

            # Step 2: Execute pipeline
            result = pipeline_func(str(processing_path))

            # Step 3: Save outputs
            if save_outputs:
                self._save_outputs(processing_path, result)

            # Step 4: Move to output directory
            output_path = self.output_dir / processing_path.name
            shutil.move(str(processing_path), str(output_path))

            # Step 5: Update metrics
            processing_time = time.time() - start_time
            self._update_metrics(success=True, processing_time=processing_time)

            logger.info(
                f"Success: {file_path.name} processed in {processing_time:.2f}s"
            )

            return {
                "status": "success",
                "file": file_path.name,
                "processing_time_s": processing_time,
                "result": result,
            }

        except Exception as e:
            # Handle errors
            processing_time = time.time() - start_time

            logger.error(f"Error processing {file_path.name}: {e}", exc_info=True)

            # Move to error directory with error log
            if processing_path and processing_path.exists():
                error_path = self.error_dir / processing_path.name
                shutil.move(str(processing_path), str(error_path))

                # Save error log
                error_log_path = self.error_dir / f"{processing_path.stem}_error.json"
                error_log = {
                    "file": processing_path.name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.utcnow().isoformat(),
                    "processing_time_s": processing_time,
                }
                with open(error_log_path, 'w') as f:
                    json.dump(error_log, f, indent=2)

            # Update metrics
            self._update_metrics(success=False, processing_time=processing_time)

            return {
                "status": "error",
                "file": file_path.name,
                "error": str(e),
                "processing_time_s": processing_time,
            }

    def _save_outputs(self, file_path: Path, result: Dict[str, Any]) -> None:
        """
        Save pipeline outputs to JSON and CSV files.

        Args:
            file_path: Source file path
            result: Pipeline result dictionary
        """
        stem = file_path.stem

        # Save JSON output (complete data)
        if "json_output" in result:
            json_path = self.output_dir / f"{stem}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result["json_output"], f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Saved JSON: {json_path.name}")

        # Save CSV output (tabular format)
        if "csv_output" in result:
            csv_path = self.output_dir / f"{stem}.csv"
            # CSV content should already be formatted
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write(result["csv_output"])
            logger.info(f"Saved CSV: {csv_path.name}")

        # Save summary report
        if "summary" in result:
            summary_path = self.output_dir / f"{stem}_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(result["summary"], f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Saved summary: {summary_path.name}")

    def _update_metrics(self, success: bool, processing_time: float) -> None:
        """
        Update processing metrics.

        Args:
            success: Whether processing succeeded
            processing_time: Processing time in seconds
        """
        self.metrics["total_processed"] += 1

        if success:
            self.metrics["total_succeeded"] += 1
        else:
            self.metrics["total_failed"] += 1

        # Update average processing time
        total = self.metrics["total_processed"]
        current_avg = self.metrics["avg_processing_time_s"]
        self.metrics["avg_processing_time_s"] = (
            (current_avg * (total - 1) + processing_time) / total
        )

        self.metrics["last_processed_at"] = datetime.utcnow().isoformat()

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current processing metrics.

        Returns:
            Metrics dictionary
        """
        return self.metrics.copy()

    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue status.

        Returns:
            Status dictionary with counts for each directory
        """
        pending_files = self._get_pending_files()

        return {
            "pending": len(pending_files),
            "processing": len(list(self.processing_dir.glob("*"))),
            "completed": len(list(self.output_dir.glob("*.pdf")))
                       + len(list(self.output_dir.glob("*.xlsx")))
                       + len(list(self.output_dir.glob("*.csv"))),
            "failed": len(list(self.error_dir.glob("*_error.json"))),
            "pending_files": [f.name for f in pending_files[:10]],  # First 10
        }

    def run_queue_processor(
        self,
        pipeline_func: Callable[[str], Dict[str, Any]],
        max_jobs: Optional[int] = None,
        poll_interval_s: int = 5
    ) -> None:
        """
        Run continuous queue processor.

        This method runs indefinitely, polling for new files and processing them.

        Args:
            pipeline_func: Pipeline function to execute for each file
            max_jobs: Maximum number of jobs to process (None = unlimited)
            poll_interval_s: Polling interval in seconds

        Example:
            >>> def my_pipeline(file_path):
            ...     return {"status": "success"}
            >>> queue.run_queue_processor(my_pipeline, max_jobs=100)
        """
        logger.info(f"Starting queue processor (max_jobs={max_jobs})")

        jobs_processed = 0

        try:
            while True:
                # Check max jobs limit
                if max_jobs is not None and jobs_processed >= max_jobs:
                    logger.info(f"Reached max jobs limit ({max_jobs})")
                    break

                # Poll for files
                file = self.poll_for_jobs(timeout_s=poll_interval_s)

                if file:
                    # Process file
                    self.process_job(file, pipeline_func)
                    jobs_processed += 1

                    # Log status
                    status = self.get_queue_status()
                    logger.info(
                        f"Queue status: {status['pending']} pending, "
                        f"{status['completed']} completed, "
                        f"{status['failed']} failed"
                    )
                else:
                    # No files available
                    logger.debug("No files in queue, waiting...")

        except KeyboardInterrupt:
            logger.info("Queue processor stopped by user")
        except Exception as e:
            logger.error(f"Queue processor error: {e}", exc_info=True)
            raise


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "SimpleFileQueue",
]
