"""
Forjador v5 - Pipeline Integration Tests
Purpose: Test complete SPEC-01 pipeline
Version: 1.0.0
Date: 2026-02-09
"""

import pytest
from pathlib import Path
from src.agent import create_forjador_pipeline, run_pipeline
from src.state.schemas import FileFormat, ComplexityTier, ParserType


class TestPipelineIntegration:
    """Integration tests for complete SPEC-01 pipeline"""

    def test_create_pipeline(self):
        """Test that pipeline can be created"""
        pipeline = create_forjador_pipeline()
        assert pipeline is not None

    def test_pipeline_initialization(self):
        """Test pipeline state initialization"""
        from src.agent import initialize_pipeline_state

        state = initialize_pipeline_state({"input_file_path": "test.pdf"})

        assert state["input_file_path"] == "test.pdf"
        assert "pipeline_started_at" in state
        assert state["current_stage"] == "B.1"
        assert isinstance(state["errors"], list)
        assert isinstance(state["warnings"], list)

    @pytest.mark.skipif(
        not Path("./test_data/sample_purchase_order.pdf").exists(),
        reason="Test data not available"
    )
    def test_pipeline_with_sample_pdf(self):
        """Test pipeline with sample PDF file (if available)"""
        test_file = "./test_data/sample_purchase_order.pdf"

        result = run_pipeline(test_file)

        # Verify basic structure
        assert "input_file_path" in result
        assert "file_metadata" in result
        assert "complexity_classification" in result
        assert "parsed_content" in result
        assert "quality_gate" in result
        assert "chunks" in result
        assert "extracted_skus" in result
        assert "valid_skus" in result
        assert "json_output" in result
        assert "csv_output" in result
        assert "summary" in result

        # Verify outputs
        assert isinstance(result["json_output"], dict)
        assert isinstance(result["csv_output"], str)
        assert isinstance(result["summary"], dict)


class TestFileValidation:
    """Tests for B.1: File Validation"""

    def test_file_validation_nonexistent_file(self):
        """Test validation with nonexistent file"""
        from src.nodes.b01_file_validation import validate_file_and_extract_metadata

        state = {"input_file_path": "/nonexistent/file.pdf"}
        result = validate_file_and_extract_metadata(state)

        assert "file_metadata" in result
        assert not result["file_metadata"].is_valid
        assert len(result["file_metadata"].validation_errors) > 0


class TestComplexityClassification:
    """Tests for B.2: Complexity Classification"""

    def test_classify_csv(self):
        """Test classification for CSV files"""
        from src.nodes.b02_complexity_routing import classify_complexity_tier

        features = {
            "file_format": "csv",
            "file_size_mb": 1.5,
            "line_count": 100,
            "page_count": 0,
            "is_large": False,
            "is_multipage": False,
            "is_image_format": False,
        }

        tier = classify_complexity_tier(features)
        assert tier == ComplexityTier.TIER_1

    def test_classify_simple_excel(self):
        """Test classification for simple Excel files"""
        from src.nodes.b02_complexity_routing import classify_complexity_tier

        features = {
            "file_format": "xlsx",
            "file_size_mb": 2.0,
            "line_count": 0,
            "page_count": 0,
            "is_large": False,
            "is_multipage": False,
            "is_image_format": False,
        }

        tier = classify_complexity_tier(features)
        assert tier == ComplexityTier.TIER_2

    def test_classify_standard_pdf(self):
        """Test classification for standard PDF"""
        from src.nodes.b02_complexity_routing import classify_complexity_tier

        features = {
            "file_format": "pdf",
            "file_size_mb": 1.5,
            "line_count": 0,
            "page_count": 3,
            "is_large": False,
            "is_multipage": False,
            "is_image_format": False,
        }

        tier = classify_complexity_tier(features)
        assert tier == ComplexityTier.TIER_3


class TestQualityGate:
    """Tests for B.4: Quality Gate"""

    def test_calculate_completeness_good_content(self):
        """Test completeness calculation for good content"""
        from src.nodes.b04_quality_gate import calculate_content_completeness

        content = """
        Item 1: PARAFUSO SEXTAVADO M8x30 ACO CARBONO ZINC CL 8.8 - QTD: 1000 UN
        Item 2: PORCA SEXTAVADA M10 ACO INOX 304 - QTD: 500 UN
        Item 3: ARRUELA LISA M8 ACO CARBONO ZINC - QTD: 2000 UN
        """

        score = calculate_content_completeness(content)
        assert score > 0.7  # Should score well

    def test_calculate_completeness_empty_content(self):
        """Test completeness calculation for empty content"""
        from src.nodes.b04_quality_gate import calculate_content_completeness

        score = calculate_content_completeness("")
        assert score == 0.0

    def test_quality_gate_pass(self):
        """Test quality gate with passing content"""
        from src.nodes.b04_quality_gate import evaluate_quality_gate
        from src.state.schemas import ParsedContent, ParserType

        content = """
        Item 1: PARAFUSO SEXTAVADO M8x30 ACO CARBONO ZINC CL 8.8 - QTD: 1000 UN
        Item 2: PORCA SEXTAVADA M10 ACO INOX 304 - QTD: 500 UN
        Item 3: ARRUELA LISA M8 ACO CARBONO ZINC - QTD: 2000 UN
        """

        parsed_content = ParsedContent(
            parser_used=ParserType.DOCLING,
            raw_content=content,
            quality_score=0.9,
            completeness=0.95,
            confidence=0.95,
            parsing_time_s=1.0,
            retry_count=0,
            fallback_used=False,
        )

        state = {"parsed_content": parsed_content}
        result = evaluate_quality_gate(state)

        assert "quality_gate" in result
        assert result["quality_gate"].passed


class TestChunking:
    """Tests for B.5: Chunking"""

    def test_chunk_short_text(self):
        """Test chunking with short text"""
        from src.utils.chunking_utils import chunk_document

        text = "Item 1: PARAFUSO M8x30 - 100 UN"
        chunks = chunk_document(text, preserve_line_items=True)

        assert len(chunks) == 1
        assert chunks[0].content == text

    def test_chunk_long_text(self):
        """Test chunking with long text"""
        from src.utils.chunking_utils import chunk_document

        # Create text longer than chunk size
        text = "\n".join([f"Item {i}: PARAFUSO M8x30 - 100 UN" for i in range(200)])
        chunks = chunk_document(text, chunk_size=1000, chunk_overlap=100)

        assert len(chunks) > 1
        # Verify all chunks have content
        assert all(chunk.content for chunk in chunks)


class TestDataframeUtils:
    """Tests for dataframe utilities"""

    def test_merge_and_dedup_skus(self):
        """Test SKU merging and deduplication"""
        from src.utils.dataframe_utils import merge_and_dedup_skus_polars

        skus = [
            {
                "tipo": "parafuso",
                "dimensao": "M8x30",
                "material": "aço carbono",
                "classe": "8.8",
                "quantidade": 100,
                "unidade": "UN",
                "descricao_original": "PARAFUSO M8x30 CL 8.8",
                "confidence": 0.95,
                "revestimento": "zincado",
                "norma": None,
                "extracted_at": "2024-01-01T00:00:00",
            },
            {
                "tipo": "parafuso",
                "dimensao": "M8x30",
                "material": "aço carbono",
                "classe": "8.8",
                "quantidade": 50,
                "unidade": "UN",
                "descricao_original": "PARAFUSO M8x30 CL 8.8",
                "confidence": 0.92,
                "revestimento": "zincado",
                "norma": None,
                "extracted_at": "2024-01-01T00:00:00",
            },
        ]

        df = merge_and_dedup_skus_polars(skus)

        # Should merge into single row
        assert len(df) == 1
        # Quantity should be summed
        assert df["quantidade"][0] == 150
        # Confidence should be max
        assert df["confidence"][0] == 0.95

    def test_calculate_statistics(self):
        """Test statistics calculation"""
        from src.utils.dataframe_utils import calculate_sku_statistics
        import polars as pl

        skus = [
            {"tipo": "parafuso", "material": "aço carbono", "quantidade": 100, "confidence": 0.95},
            {"tipo": "parafuso", "material": "aço inox 304", "quantidade": 50, "confidence": 0.92},
            {"tipo": "porca", "material": "aço carbono", "quantidade": 200, "confidence": 0.90},
        ]

        df = pl.DataFrame(skus)
        stats = calculate_sku_statistics(df)

        assert stats["total_skus"] == 3
        assert stats["total_quantity"] == 350
        assert "parafuso" in stats["skus_by_type"]
        assert "porca" in stats["skus_by_type"]
        assert stats["skus_by_type"]["parafuso"] == 2
        assert stats["skus_by_type"]["porca"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
