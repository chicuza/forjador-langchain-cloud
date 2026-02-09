"""
Environment Variable Validation
Ensures all required SPEC-01 environment variables are set
"""

import os
import sys
from typing import List, Tuple
from pathlib import Path


class EnvValidator:
    """Validates SPEC-01 environment variables."""

    REQUIRED_VARS = [
        # LangSmith (4 variables)
        "LANGCHAIN_TRACING_V2",
        "LANGCHAIN_ENDPOINT",
        "LANGCHAIN_API_KEY",
        "LANGCHAIN_PROJECT",
        # Gemini API (1 variable)
        "GOOGLE_API_KEY",
        # Language Settings (1 variable)
        "PRIMARY_LANGUAGE",
        # Pipeline Settings (3 variables)
        "QUALITY_GATE_THRESHOLD",
        "CHUNK_SIZE",
        "CHUNK_OVERLAP",
        # File Queue (2 variables)
        "INPUT_DIR",
        "OUTPUT_DIR",
    ]

    @classmethod
    def validate_all(cls) -> Tuple[bool, List[str]]:
        """
        Validate all required environment variables.

        Returns:
            Tuple[bool, List[str]]: (is_valid, missing_vars)
        """
        missing_vars = []

        for var in cls.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)

        return len(missing_vars) == 0, missing_vars

    @classmethod
    def validate_directories(cls) -> Tuple[bool, List[str]]:
        """
        Validate and create queue directories if needed.

        Returns:
            Tuple[bool, List[str]]: (is_valid, errors)
        """
        errors = []
        directories = [
            os.getenv("INPUT_DIR", "./queue/input"),
            os.getenv("OUTPUT_DIR", "./queue/output"),
        ]

        for dir_path in directories:
            path = Path(dir_path)
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create directory {dir_path}: {e}")

        return len(errors) == 0, errors

    @classmethod
    def validate_numeric_vars(cls) -> Tuple[bool, List[str]]:
        """
        Validate numeric environment variables.

        Returns:
            Tuple[bool, List[str]]: (is_valid, errors)
        """
        errors = []

        # Validate QUALITY_GATE_THRESHOLD (0.0-1.0)
        try:
            threshold = float(os.getenv("QUALITY_GATE_THRESHOLD", "0.85"))
            if not 0.0 <= threshold <= 1.0:
                errors.append("QUALITY_GATE_THRESHOLD must be between 0.0 and 1.0")
        except ValueError:
            errors.append("QUALITY_GATE_THRESHOLD must be a valid float")

        # Validate CHUNK_SIZE (positive integer)
        try:
            chunk_size = int(os.getenv("CHUNK_SIZE", "3500"))
            if chunk_size <= 0:
                errors.append("CHUNK_SIZE must be a positive integer")
        except ValueError:
            errors.append("CHUNK_SIZE must be a valid integer")

        # Validate CHUNK_OVERLAP (positive integer)
        try:
            chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "250"))
            if chunk_overlap < 0:
                errors.append("CHUNK_OVERLAP must be a non-negative integer")
        except ValueError:
            errors.append("CHUNK_OVERLAP must be a valid integer")

        return len(errors) == 0, errors

    @classmethod
    def validate_and_exit_on_error(cls) -> None:
        """
        Validate all environment variables and exit if invalid.
        Call this at application startup.
        """
        print("Validating SPEC-01 environment variables...")

        # Check required variables
        is_valid, missing_vars = cls.validate_all()
        if not is_valid:
            print("\nERROR: Missing required environment variables:")
            for var in missing_vars:
                print(f"  - {var}")
            print("\nPlease copy .env.example to .env and fill in all values.")
            sys.exit(1)

        # Validate directories
        is_valid, errors = cls.validate_directories()
        if not is_valid:
            print("\nERROR: Directory validation failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

        # Validate numeric variables
        is_valid, errors = cls.validate_numeric_vars()
        if not is_valid:
            print("\nERROR: Numeric variable validation failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

        print("Environment validation successful! All 11 SPEC-01 variables configured.\n")
