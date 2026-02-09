"""
LangSmith Tracing Configuration
Provides observability and monitoring for the Forjador v5 pipeline
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime


class LangSmithConfig:
    """LangSmith tracing configuration for observability."""

    def __init__(self):
        self.tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        self.endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
        self.api_key = os.getenv("LANGCHAIN_API_KEY")
        self.project = os.getenv("LANGCHAIN_PROJECT", "forjador-v5-spec01")

    def validate(self) -> bool:
        """Validate LangSmith configuration."""
        if not self.tracing_enabled:
            logging.warning("LangSmith tracing is disabled")
            return False

        if not self.api_key:
            logging.error("LANGCHAIN_API_KEY not set - tracing will not work")
            return False

        logging.info(f"LangSmith tracing enabled for project: {self.project}")
        return True

    def get_run_metadata(self, stage: str, **kwargs) -> Dict[str, Any]:
        """Generate metadata for LangSmith trace runs."""
        return {
            "spec_version": "SPEC-01",
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat(),
            "project": self.project,
            **kwargs,
        }


def setup_logging(level: str = "INFO") -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


# Initialize LangSmith configuration
langsmith_config = LangSmithConfig()
