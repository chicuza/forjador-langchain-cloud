"""
Pytest Configuration and Fixtures for SPEC-01
"""

import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables."""
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_API_KEY"] = "test_key"
    os.environ["LANGCHAIN_PROJECT"] = "forjador-v5-test"
    os.environ["GOOGLE_API_KEY"] = "test_google_key"
    os.environ["PRIMARY_LANGUAGE"] = "pt-BR"
    os.environ["QUALITY_GATE_THRESHOLD"] = "0.85"
    os.environ["CHUNK_SIZE"] = "3500"
    os.environ["CHUNK_OVERLAP"] = "250"
    os.environ["INPUT_DIR"] = "./queue/input"
    os.environ["OUTPUT_DIR"] = "./queue/output"
    yield


@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a sample PDF file for testing."""
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_text("Sample PDF content")
    return str(pdf_file)


@pytest.fixture
def sample_excel_path(tmp_path):
    """Create a sample Excel file for testing."""
    excel_file = tmp_path / "sample.xlsx"
    excel_file.write_text("Sample Excel content")
    return str(excel_file)


@pytest.fixture
def sample_csv_path(tmp_path):
    """Create a sample CSV file for testing."""
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text("header1,header2\nvalue1,value2")
    return str(csv_file)


@pytest.fixture
def queue_directories(tmp_path):
    """Create temporary queue directories."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    processing_dir = tmp_path / "processing"
    error_dir = tmp_path / "error"

    input_dir.mkdir()
    output_dir.mkdir()
    processing_dir.mkdir()
    error_dir.mkdir()

    return {
        "input": str(input_dir),
        "output": str(output_dir),
        "processing": str(processing_dir),
        "error": str(error_dir),
    }
