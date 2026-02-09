"""
Forjador v5 - SPEC-01 MVP Pydantic Schemas
Purpose: Data validation schemas for industrial fastener SKU extraction pipeline
Version: 1.0.0
Date: 2026-02-09

This module defines all Pydantic models for the LCEL pipeline including:
- FastenerSKU: Core model for extracted fastener data (10 required fields)
- ValidationResult: Result of hybrid validation (YAML + Pydantic)
- ForjadorPipelineState: LCEL pipeline state management
- Supporting models for parsing, quality gates, and chunking
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional

import re
from pydantic import BaseModel, Field, field_validator, model_validator


# ============================================================================
# ENUMERATIONS - Type Safety for Known Values
# ============================================================================

class FastenerType(str, Enum):
    """11 fastener types supported in SPEC-01"""
    PARAFUSO = "parafuso"  # Bolt/Screw
    PORCA = "porca"  # Nut
    ARRUELA = "arruela"  # Washer
    BUCHA = "bucha"  # Anchor
    CHUMBADOR = "chumbador"  # Chemical anchor
    PRISIONEIRO = "prisioneiro"  # Stud
    REBITE = "rebite"  # Rivet
    PINO = "pino"  # Pin
    GRAMPO = "grampo"  # Clamp
    INSERTO = "inserto"  # Insert
    ANEL_DE_TRAVA = "anel_de_trava"  # Retaining ring


class UnitType(str, Enum):
    """Units of measurement for fasteners"""
    UN = "UN"  # Unit
    CX = "CX"  # Box
    PCT = "PCT"  # Package
    KG = "KG"  # Kilogram
    JOGO = "JOGO"  # Set
    PAR = "PAR"  # Pair


class FileFormat(str, Enum):
    """Supported file formats for B.1 validation"""
    PDF = "pdf"
    XLSX = "xlsx"
    CSV = "csv"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"


class ParserType(str, Enum):
    """3 parser solutions for SPEC-01 (B.3)"""
    DOCLING = "docling"  # Docling 2.0 for standard PDFs
    GEMINI_VISION = "gemini_vision"  # Gemini 2.5 Flash for scanned/images
    PANDAS = "pandas"  # Pandas/Polars for CSV/Excel


class ComplexityTier(str, Enum):
    """11 complexity tiers for document classification (B.2)"""
    TIER_1 = "tier_1"  # Simple structured CSV
    TIER_2 = "tier_2"  # Simple Excel spreadsheet
    TIER_3 = "tier_3"  # Standard PDF with text
    TIER_4 = "tier_4"  # PDF with embedded tables
    TIER_5 = "tier_5"  # PDF with images/charts
    TIER_6 = "tier_6"  # Multi-page complex PDF
    TIER_7 = "tier_7"  # Scanned PDF (OCR needed)
    TIER_8 = "tier_8"  # Poor quality scanned PDF
    TIER_9 = "tier_9"  # Handwritten documents
    TIER_10 = "tier_10"  # Mixed format documents
    TIER_11 = "tier_11"  # Corrupted or damaged files


# ============================================================================
# CORE MODELS - FastenerSKU (10 Required Fields)
# ============================================================================

class FastenerSKU(BaseModel):
    """
    Core model for extracted fastener SKU data (SPEC-01 M6 requirement).

    This model enforces both structural validation (Pydantic) and business
    validation (YAML rules). It represents a single fastener item extracted
    from purchase orders.

    Validation Strategy:
    - Field validators: Basic format and allowed values
    - Model validators: Cross-field business rules (material-class compatibility)
    - YAML validation: External business rules loaded from knowledge/validation_rules.yaml

    Performance: Validation must complete in < 3 seconds for 4000 SKUs
    """

    # Required Fields (10 minimum for SPEC-01)
    tipo: str = Field(
        description="Fastener type (parafuso, porca, arruela, etc.)",
        examples=["parafuso", "porca", "arruela"]
    )

    dimensao: str = Field(
        description="Main dimension (e.g., M8, M8x30, M8x1.25x30)",
        examples=["M8", "M8x30", "M8x1.25x30", "M10x50"]
    )

    material: str = Field(
        description="Material (aço carbono, aço inox 304, etc.)",
        examples=["aço carbono", "aço inox 304", "aço inox 316", "latão"]
    )

    classe: Optional[str] = Field(
        None,
        description="Strength class (4.6, 8.8, 10.9, etc.) - Optional for some types",
        examples=["4.6", "5.6", "8.8", "10.9", "12.9"]
    )

    quantidade: int = Field(
        gt=0,
        description="Quantity (must be positive)",
        examples=[100, 500, 1000]
    )

    unidade: str = Field(
        default="UN",
        description="Unit of measurement (UN, CX, PCT, KG)",
        examples=["UN", "CX", "PCT", "KG"]
    )

    descricao_original: str = Field(
        description="Original description from purchase order (for traceability)",
        examples=["PARAFUSO SEXTAVADO M8X30 AC ZINC CL 8.8", "PORCA SEXT M10 INOX 304"]
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Extraction confidence score (0.0-1.0)",
        examples=[0.95, 0.87, 0.92]
    )

    revestimento: Optional[str] = Field(
        None,
        description="Coating/finish (zincado, galvanizado, etc.) - Optional",
        examples=["zincado", "galvanizado", "niquelado", "cromado", "dacromet"]
    )

    norma: Optional[str] = Field(
        None,
        description="Standard (ABNT, DIN, ISO, etc.) - Optional",
        examples=["ABNT NBR ISO 4014", "DIN 933", "ISO 4017"]
    )

    # Metadata Fields (automatically populated)
    extracted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of extraction"
    )

    chunk_id: Optional[str] = Field(
        None,
        description="Source chunk ID for traceability"
    )

    # ========================================================================
    # FIELD VALIDATORS - Basic Format Validation
    # ========================================================================

    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v: str) -> str:
        """Validate fastener type against known types"""
        valid_tipos = [
            "parafuso", "porca", "arruela", "bucha", "chumbador",
            "prisioneiro", "rebite", "pino", "grampo", "inserto", "anel_de_trava"
        ]

        v_normalized = v.lower().strip().replace(" ", "_")

        if v_normalized not in valid_tipos:
            raise ValueError(
                f"Invalid fastener type '{v}'. "
                f"Must be one of: {', '.join(valid_tipos)}"
            )

        return v_normalized

    @field_validator('dimensao')
    @classmethod
    def validate_dimensao(cls, v: str) -> str:
        """Validate dimension format (metric or imperial)"""
        # Metric patterns: M8, M8x30, M8x1.25x30
        metric_patterns = [
            r'^M\d+(\.\d+)?$',  # M8, M10.5
            r'^M\d+(\.\d+)?x\d+(\.\d+)?$',  # M8x30, M10x50
            r'^M\d+(\.\d+)?x\d+(\.\d+)?x\d+(\.\d+)?$'  # M8x1.25x30
        ]

        # Imperial patterns: #8-32, 1/4"-20
        imperial_patterns = [
            r'^#\d+-\d+$',  # #8-32
            r'^\d+/\d+"-\d+$'  # 1/4"-20
        ]

        all_patterns = metric_patterns + imperial_patterns

        if not any(re.match(pattern, v) for pattern in all_patterns):
            raise ValueError(
                f"Invalid dimension format '{v}'. "
                f"Expected metric (M8, M8x30) or imperial (#8-32, 1/4\"-20)"
            )

        return v

    @field_validator('material')
    @classmethod
    def validate_material(cls, v: str) -> str:
        """Validate material against known materials (basic check)"""
        # Full validation happens in YAML rules
        # This is a sanity check for common materials
        common_materials = [
            "aço carbono", "aço inox", "aço inox 304", "aço inox 316", "aço inox 430",
            "latão", "bronze", "alumínio", "plástico", "nylon",
            "borracha", "cobre", "titânio"
        ]

        v_normalized = v.lower().strip()

        # Check if material starts with any known material
        if not any(v_normalized.startswith(mat) for mat in common_materials):
            # Warning but not error - allow unknown materials for flexibility
            # Full validation happens in YAML rules
            pass

        return v_normalized

    @field_validator('classe')
    @classmethod
    def validate_classe(cls, v: Optional[str]) -> Optional[str]:
        """Validate strength class format"""
        if v is None:
            return None

        # Common strength classes for fasteners
        # Full validation happens in YAML rules (material-class compatibility)
        # This checks format only
        valid_classes = [
            "4.6", "4.8", "5.6", "5.8", "6.8", "8.8", "10.9", "12.9",
            "4", "5", "8", "10", "12",  # For nuts
            "A2-70", "A2-80", "A4-70", "A4-80"  # Stainless steel classes
        ]

        if v not in valid_classes:
            raise ValueError(
                f"Invalid strength class '{v}'. "
                f"Common classes: 4.6, 5.6, 8.8, 10.9, 12.9"
            )

        return v

    @field_validator('unidade')
    @classmethod
    def validate_unidade(cls, v: str) -> str:
        """Validate unit of measurement"""
        valid_units = ["UN", "CX", "PCT", "KG", "JOGO", "PAR"]

        v_upper = v.upper().strip()

        if v_upper not in valid_units:
            raise ValueError(
                f"Invalid unit '{v}'. "
                f"Must be one of: {', '.join(valid_units)}"
            )

        return v_upper

    # ========================================================================
    # MODEL VALIDATORS - Cross-Field Business Rules
    # ========================================================================

    @model_validator(mode='after')
    def validate_material_class_compatibility(self) -> 'FastenerSKU':
        """
        Validate material-class compatibility.

        Business Rules:
        - Plastic/rubber cannot have strength class
        - Stainless steel uses different class system (A2-70, A4-70)
        - Carbon steel can have any standard class
        """
        material = self.material.lower()
        classe = self.classe

        # Rule 1: Plastic/rubber cannot have strength class
        if any(x in material for x in ["plástico", "nylon", "borracha"]) and classe:
            raise ValueError(
                f"Material '{material}' cannot have strength class. "
                f"Plastic/rubber/nylon do not have mechanical strength classes."
            )

        # Rule 2: Stainless steel compatibility
        if "inox" in material and classe:
            # Stainless should use A2-70, A4-70 format
            # But also allow standard classes for compatibility
            if classe not in ["8.8", "10.9", "A2-70", "A2-80", "A4-70", "A4-80"]:
                # Warning but allow - full validation in YAML
                pass

        return self

    @model_validator(mode='after')
    def validate_coating_compatibility(self) -> 'FastenerSKU':
        """
        Validate coating compatibility with material.

        Business Rules:
        - Stainless steel should not have metallic coating
        - Carbon steel typically requires coating
        - Plastic cannot have metallic coating
        """
        material = self.material.lower()
        revestimento = self.revestimento

        if not revestimento:
            return self

        revestimento_lower = revestimento.lower()

        # Rule 1: Stainless steel should not have coating
        if "inox" in material and revestimento_lower not in ["natural", "passivado"]:
            raise ValueError(
                f"Material '{material}' should not have coating '{revestimento}'. "
                f"Stainless steel has natural corrosion resistance."
            )

        # Rule 2: Plastic cannot have metallic coating
        if "plástico" in material or "nylon" in material:
            metallic_coatings = ["zincado", "galvanizado", "niquelado", "cromado"]
            if any(coat in revestimento_lower for coat in metallic_coatings):
                raise ValueError(
                    f"Material '{material}' cannot have metallic coating '{revestimento}'"
                )

        return self

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "tipo": "parafuso",
                "dimensao": "M8x1.25x30",
                "material": "aço carbono",
                "classe": "8.8",
                "quantidade": 1000,
                "unidade": "UN",
                "descricao_original": "PARAFUSO SEXTAVADO M8X30 AC ZINC CL 8.8",
                "confidence": 0.95,
                "revestimento": "zincado",
                "norma": "ABNT NBR ISO 4014"
            }
        }


# ============================================================================
# VALIDATION MODELS - Hybrid Validation Results
# ============================================================================

class ValidationResult(BaseModel):
    """
    Result of hybrid validation (Pydantic + YAML rules).

    This model captures the outcome of validating a FastenerSKU against
    business rules defined in knowledge/validation_rules.yaml.
    """

    passed: bool = Field(
        description="Whether validation passed (no errors)"
    )

    errors: list[str] = Field(
        default_factory=list,
        description="List of validation errors (blocking issues)"
    )

    warnings: list[str] = Field(
        default_factory=list,
        description="List of validation warnings (non-blocking issues)"
    )

    score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Validation quality score (0.0-1.0)"
    )

    validation_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When validation was performed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "passed": True,
                "errors": [],
                "warnings": ["Material 'aço carbono' should have coating"],
                "score": 0.95,
            }
        }


# ============================================================================
# DOCUMENT PROCESSING MODELS - B.1 through B.6
# ============================================================================

class FileMetadata(BaseModel):
    """File validation metadata (B.1)"""

    file_path: str = Field(description="Absolute path to file")
    file_format: FileFormat = Field(description="File format")
    file_size_mb: float = Field(description="File size in MB")
    line_count: Optional[int] = Field(None, description="Number of lines (for text files)")
    page_count: Optional[int] = Field(None, description="Number of pages (for PDFs)")
    encoding: Optional[str] = Field(None, description="Text encoding")
    created_at: Optional[datetime] = Field(None, description="File creation timestamp")

    # Validation results
    is_valid: bool = Field(default=True, description="Whether file passed validation")
    validation_errors: list[str] = Field(default_factory=list)

    @field_validator('file_size_mb')
    @classmethod
    def validate_file_size(cls, v: float) -> float:
        """Validate file size is within limits (max 100 MB)"""
        if v > 100:
            raise ValueError(f"File size {v} MB exceeds maximum 100 MB")
        return v

    @field_validator('line_count')
    @classmethod
    def validate_line_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate line count is within limits (max 5000 lines)"""
        if v is not None and v > 5000:
            raise ValueError(f"Line count {v} exceeds maximum 5000 lines")
        return v


class ComplexityClassification(BaseModel):
    """Document complexity classification (B.2)"""

    tier: ComplexityTier = Field(description="Complexity tier (1-11)")
    tier_name: str = Field(description="Human-readable tier name")
    features: dict[str, Any] = Field(description="Extracted features for classification")

    # Parser routing decision
    primary_parser: ParserType = Field(description="Primary parser to use")
    fallback_parsers: list[ParserType] = Field(
        default_factory=list,
        description="Fallback parser chain"
    )

    avg_processing_time_s: float = Field(
        description="Estimated processing time in seconds"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Classification confidence"
    )


class ParsedContent(BaseModel):
    """Parsed document content (B.3)"""

    parser_used: ParserType = Field(description="Parser that successfully extracted content")
    raw_content: str = Field(description="Raw extracted text/markdown")

    # Quality metrics
    quality_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Content quality score"
    )

    completeness: float = Field(
        ge=0.0,
        le=1.0,
        description="Estimated completeness (0.0-1.0)"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Parser confidence"
    )

    # Metadata
    parsing_time_s: float = Field(description="Parsing time in seconds")
    retry_count: int = Field(default=0, description="Number of retries")
    fallback_used: bool = Field(default=False, description="Whether fallback parser was used")


class QualityGateResult(BaseModel):
    """Quality gate validation result (B.4)"""

    passed: bool = Field(description="Whether quality gate passed (≥0.85 threshold)")
    score: float = Field(ge=0.0, le=1.0, description="Overall quality score")

    # Component scores
    content_completeness: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    structure_validity: float = Field(ge=0.0, le=1.0)

    # Actions
    should_retry: bool = Field(description="Whether to retry with fallback parser")
    retry_count: int = Field(default=0, description="Current retry count")
    max_retries_reached: bool = Field(default=False, description="Whether max retries (2) reached")


class DocumentChunk(BaseModel):
    """Intelligent document chunk (B.5)"""

    chunk_id: str = Field(description="Unique chunk identifier")
    index: int = Field(ge=0, description="Chunk index in document")
    content: str = Field(description="Chunk text content")

    # Metadata
    source_file: str = Field(description="Source file path")
    chunk_size: int = Field(description="Chunk size in characters")
    overlap_size: int = Field(description="Overlap with previous chunk")

    # Semantic boundaries
    starts_with_separator: bool = Field(
        default=False,
        description="Whether chunk starts with semantic separator"
    )

    separators_used: list[str] = Field(
        default_factory=list,
        description="Separators used for splitting"
    )


# ============================================================================
# PIPELINE STATE - LCEL State Management
# ============================================================================

class ForjadorPipelineState(BaseModel):
    """
    Complete LCEL pipeline state for Forjador v5 SPEC-01.

    This model tracks the state of the document processing pipeline from
    file validation (B.1) through validation (B.6). It enables state
    persistence and recovery for long-running pipelines.

    Pipeline Stages (SPEC-01):
    - B.1: File Validation
    - B.2: Complexity Classification
    - B.3: Document Parsing
    - B.4: Quality Gate
    - B.5: Intelligent Chunking
    - B.6: Structured Extraction
    - B.7: Hybrid Validation (added in this state)

    Performance Target: Complete pipeline in < 25 seconds for typical document
    """

    # ========================================================================
    # INPUT
    # ========================================================================

    input_file_path: str = Field(description="Input file path")

    # ========================================================================
    # B.1: FILE VALIDATION
    # ========================================================================

    file_metadata: Optional[FileMetadata] = Field(
        None,
        description="File validation metadata"
    )

    # ========================================================================
    # B.2: COMPLEXITY CLASSIFICATION
    # ========================================================================

    complexity_classification: Optional[ComplexityClassification] = Field(
        None,
        description="Document complexity classification"
    )

    # ========================================================================
    # B.3: DOCUMENT PARSING
    # ========================================================================

    parsed_content: Optional[ParsedContent] = Field(
        None,
        description="Parsed document content"
    )

    # ========================================================================
    # B.4: QUALITY GATE
    # ========================================================================

    quality_gate: Optional[QualityGateResult] = Field(
        None,
        description="Quality gate validation result"
    )

    # ========================================================================
    # B.5: INTELLIGENT CHUNKING
    # ========================================================================

    chunks: list[DocumentChunk] = Field(
        default_factory=list,
        description="Document chunks"
    )

    # ========================================================================
    # B.6: STRUCTURED EXTRACTION
    # ========================================================================

    extracted_skus: list[FastenerSKU] = Field(
        default_factory=list,
        description="Extracted fastener SKUs"
    )

    # ========================================================================
    # B.7: HYBRID VALIDATION (SPEC-01 Final Stage)
    # ========================================================================

    validation_results: list[ValidationResult] = Field(
        default_factory=list,
        description="Validation results for each SKU"
    )

    valid_skus: list[FastenerSKU] = Field(
        default_factory=list,
        description="SKUs that passed validation"
    )

    invalid_skus: list[tuple[FastenerSKU, ValidationResult]] = Field(
        default_factory=list,
        description="SKUs that failed validation with errors"
    )

    # ========================================================================
    # PIPELINE METADATA
    # ========================================================================

    pipeline_started_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Pipeline start timestamp"
    )

    pipeline_completed_at: Optional[datetime] = Field(
        None,
        description="Pipeline completion timestamp"
    )

    total_processing_time_s: Optional[float] = Field(
        None,
        description="Total processing time in seconds"
    )

    current_stage: str = Field(
        default="B.1",
        description="Current pipeline stage"
    )

    errors: list[str] = Field(
        default_factory=list,
        description="Pipeline errors"
    )

    warnings: list[str] = Field(
        default_factory=list,
        description="Pipeline warnings"
    )

    # ========================================================================
    # OUTPUT METADATA
    # ========================================================================

    total_skus_extracted: int = Field(
        default=0,
        description="Total SKUs extracted"
    )

    total_skus_valid: int = Field(
        default=0,
        description="Total SKUs that passed validation"
    )

    total_skus_invalid: int = Field(
        default=0,
        description="Total SKUs that failed validation"
    )

    avg_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average extraction confidence"
    )

    class Config:
        """Pydantic configuration"""
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "input_file_path": "/data/purchase_order_001.pdf",
                "current_stage": "B.6",
                "total_skus_extracted": 42,
                "total_skus_valid": 40,
                "total_skus_invalid": 2,
                "avg_confidence": 0.92
            }
        }


# ============================================================================
# HELPER MODELS - Supporting Data Structures
# ============================================================================

class SKUStatistics(BaseModel):
    """Statistics for extracted SKUs (for output reports)"""

    total_skus: int = Field(description="Total SKUs extracted")
    valid_skus: int = Field(description="Valid SKUs")
    invalid_skus: int = Field(description="Invalid SKUs")

    # Breakdown by type
    skus_by_type: dict[str, int] = Field(
        default_factory=dict,
        description="SKU count by fastener type"
    )

    # Breakdown by material
    skus_by_material: dict[str, int] = Field(
        default_factory=dict,
        description="SKU count by material"
    )

    # Quality metrics
    avg_confidence: float = Field(ge=0.0, le=1.0)
    min_confidence: float = Field(ge=0.0, le=1.0)
    max_confidence: float = Field(ge=0.0, le=1.0)

    # Validation metrics
    validation_pass_rate: float = Field(
        ge=0.0,
        le=1.0,
        description="Percentage of SKUs that passed validation"
    )


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    # Enums
    "FastenerType",
    "UnitType",
    "FileFormat",
    "ParserType",
    "ComplexityTier",

    # Core Models
    "FastenerSKU",
    "ValidationResult",

    # Document Processing Models
    "FileMetadata",
    "ComplexityClassification",
    "ParsedContent",
    "QualityGateResult",
    "DocumentChunk",

    # Pipeline State
    "ForjadorPipelineState",

    # Helper Models
    "SKUStatistics",
]
