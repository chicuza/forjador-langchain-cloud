"""
Forjador v5 - B.7: Hybrid Validation (YAML + Pydantic)
Purpose: Validate SKUs using both Pydantic schemas and YAML business rules
Version: 1.0.0
Date: 2026-02-09

This node performs:
- Pydantic structural validation
- YAML business rules validation
- Material-class compatibility checks
- Coating applicability validation

Performance Target: < 3 seconds for 4000 SKUs
"""

from typing import Any, Dict, List
import logging
from pathlib import Path
import yaml

from src.state.schemas import FastenerSKU, ValidationResult

logger = logging.getLogger(__name__)


# ============================================================================
# YAML RULES LOADING
# ============================================================================

def load_validation_rules(rules_path: str = None) -> Dict[str, Any]:
    """
    Load validation rules from YAML file.

    Default path: knowledge/validation_rules.yaml

    Args:
        rules_path: Optional custom path to rules file

    Returns:
        Dictionary of validation rules

    Example YAML structure:
        material_class_compatibility:
          "aço carbono":
            allowed_classes: ["4.6", "5.6", "8.8", "10.9", "12.9"]
          "aço inox 304":
            allowed_classes: ["A2-70", "A2-80"]

        coating_compatibility:
          "aço carbono":
            required_coatings: ["zincado", "galvanizado", "dacromet"]
          "aço inox":
            prohibited_coatings: ["zincado", "galvanizado"]
    """
    if rules_path is None:
        # Default to knowledge directory
        rules_path = Path(__file__).parent.parent.parent / "knowledge" / "validation_rules.yaml"

    try:
        if Path(rules_path).exists():
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            logger.info(f"Loaded validation rules from {rules_path}")
            return rules or {}
        else:
            logger.warning(f"Validation rules file not found: {rules_path}, using defaults")
            return get_default_validation_rules()
    except Exception as e:
        logger.error(f"Error loading validation rules: {e}", exc_info=True)
        return get_default_validation_rules()


def get_default_validation_rules() -> Dict[str, Any]:
    """
    Get default validation rules if YAML file not available.

    Returns:
        Dictionary of default rules
    """
    return {
        "material_class_compatibility": {
            "aço carbono": {
                "allowed_classes": ["4.6", "4.8", "5.6", "5.8", "6.8", "8.8", "10.9", "12.9"]
            },
            "aço inox 304": {
                "allowed_classes": ["A2-70", "A2-80", "8.8", "10.9"]
            },
            "aço inox 316": {
                "allowed_classes": ["A4-70", "A4-80", "8.8", "10.9"]
            },
            "latão": {
                "allowed_classes": []
            },
        },
        "coating_compatibility": {
            "aço carbono": {
                "recommended_coatings": ["zincado", "galvanizado", "dacromet", "geomet"],
                "prohibited_coatings": []
            },
            "aço inox": {
                "recommended_coatings": ["passivado", "eletropolido"],
                "prohibited_coatings": ["zincado", "galvanizado"]
            },
        },
        "tipo_dimension_patterns": {
            "parafuso": {
                "dimension_pattern": r"^M\d+(\.\d+)?(x\d+(\.\d+)?){0,2}$",
                "requires_classe": True
            },
            "porca": {
                "dimension_pattern": r"^M\d+(\.\d+)?$",
                "requires_classe": False
            },
            "arruela": {
                "dimension_pattern": r"^M\d+(\.\d+)?$",
                "requires_classe": False
            },
        }
    }


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_material_class_compatibility(
    sku: FastenerSKU,
    rules: Dict[str, Any]
) -> List[str]:
    """
    Validate material-class compatibility using YAML rules.

    Args:
        sku: FastenerSKU object
        rules: Validation rules dictionary

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if not sku.classe:
        return errors  # No class to validate

    material = sku.material.lower()
    classe = sku.classe

    # Get compatibility rules
    material_rules = rules.get("material_class_compatibility", {})

    # Find matching material rule (support partial matching)
    matching_rule = None
    for material_key, rule in material_rules.items():
        if material_key in material:
            matching_rule = rule
            break

    if matching_rule:
        allowed_classes = matching_rule.get("allowed_classes", [])
        if allowed_classes and classe not in allowed_classes:
            errors.append(
                f"Material '{material}' with class '{classe}' is not compatible. "
                f"Allowed classes: {', '.join(allowed_classes)}"
            )

    return errors


def validate_coating_compatibility(
    sku: FastenerSKU,
    rules: Dict[str, Any]
) -> List[str]:
    """
    Validate coating compatibility using YAML rules.

    Args:
        sku: FastenerSKU object
        rules: Validation rules dictionary

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    warnings = []

    if not sku.revestimento:
        return errors  # No coating to validate

    material = sku.material.lower()
    coating = sku.revestimento.lower()

    # Get compatibility rules
    coating_rules = rules.get("coating_compatibility", {})

    # Find matching material rule
    matching_rule = None
    for material_key, rule in coating_rules.items():
        if material_key in material:
            matching_rule = rule
            break

    if matching_rule:
        # Check prohibited coatings
        prohibited = matching_rule.get("prohibited_coatings", [])
        for prohibited_coating in prohibited:
            if prohibited_coating in coating:
                errors.append(
                    f"Material '{material}' cannot have coating '{coating}'. "
                    f"Prohibited coatings: {', '.join(prohibited)}"
                )

        # Check recommended coatings (warning only)
        recommended = matching_rule.get("recommended_coatings", [])
        if recommended:
            has_recommended = any(rec in coating for rec in recommended)
            if not has_recommended:
                warnings.append(
                    f"Material '{material}' should typically have coating from: "
                    f"{', '.join(recommended)}"
                )

    return errors


def validate_tipo_dimension_pattern(
    sku: FastenerSKU,
    rules: Dict[str, Any]
) -> List[str]:
    """
    Validate dimension pattern for fastener type.

    Args:
        sku: FastenerSKU object
        rules: Validation rules dictionary

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    tipo = sku.tipo.lower()
    dimension = sku.dimensao

    # Get tipo rules
    tipo_rules = rules.get("tipo_dimension_patterns", {})

    matching_rule = tipo_rules.get(tipo)

    if matching_rule:
        # Validate dimension pattern
        pattern = matching_rule.get("dimension_pattern")
        if pattern:
            import re
            if not re.match(pattern, dimension):
                errors.append(
                    f"Dimension '{dimension}' does not match expected pattern for "
                    f"tipo '{tipo}': {pattern}"
                )

        # Validate required classe
        requires_classe = matching_rule.get("requires_classe", False)
        if requires_classe and not sku.classe:
            errors.append(
                f"Tipo '{tipo}' requires strength class, but none provided"
            )

    return errors


# ============================================================================
# MAIN VALIDATION FUNCTION
# ============================================================================

def validate_sku_hybrid(
    sku: FastenerSKU,
    rules: Dict[str, Any] = None
) -> ValidationResult:
    """
    Validate SKU using hybrid Pydantic + YAML approach.

    Validation Layers:
    1. Pydantic field validators (already executed during object creation)
    2. Pydantic model validators (cross-field validation)
    3. YAML business rules (material-class, coating, etc.)

    Args:
        sku: FastenerSKU object (Pydantic validation already done)
        rules: Optional validation rules (loaded if not provided)

    Returns:
        ValidationResult object
    """
    if rules is None:
        rules = load_validation_rules()

    errors = []
    warnings = []

    # Pydantic validation is already done during object creation
    # Now apply YAML business rules

    # Rule 1: Material-class compatibility
    material_class_errors = validate_material_class_compatibility(sku, rules)
    errors.extend(material_class_errors)

    # Rule 2: Coating compatibility
    coating_errors = validate_coating_compatibility(sku, rules)
    errors.extend(coating_errors)

    # Rule 3: Tipo-dimension pattern
    tipo_dimension_errors = validate_tipo_dimension_pattern(sku, rules)
    errors.extend(tipo_dimension_errors)

    # Calculate validation score
    score = 1.0
    if errors:
        # Each error reduces score by 0.2
        score = max(0.0, 1.0 - (len(errors) * 0.2))

    # Determine if passed
    passed = len(errors) == 0

    return ValidationResult(
        passed=passed,
        errors=errors,
        warnings=warnings,
        score=score,
    )


def validate_skus_batch(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    B.7: Validate all extracted SKUs using hybrid validation.

    This function validates all SKUs extracted in B.6 and separates them
    into valid and invalid groups.

    Args:
        state: Pipeline state dict with 'extracted_skus' key

    Returns:
        Updated state dict with 'validation_results', 'valid_skus', 'invalid_skus' keys

    Performance: < 3 seconds for 4000 SKUs

    Example:
        >>> state = {"extracted_skus": [sku1, sku2, ...]}
        >>> result = validate_skus_batch(state)
        >>> len(result["valid_skus"])
        145
    """
    extracted_skus = state.get("extracted_skus", [])

    if not extracted_skus:
        logger.warning("B.7: No SKUs to validate")
        return {
            **state,
            "validation_results": [],
            "valid_skus": [],
            "invalid_skus": [],
        }

    logger.info(f"B.7: Validating {len(extracted_skus)} SKUs")

    # Load validation rules once
    rules = load_validation_rules()

    # Validate each SKU
    validation_results = []
    valid_skus = []
    invalid_skus = []

    for sku in extracted_skus:
        # Convert dict to FastenerSKU if needed
        if isinstance(sku, dict):
            try:
                sku = FastenerSKU(**sku)
            except Exception as e:
                logger.error(f"B.7: Error creating FastenerSKU from dict: {e}")
                # Create validation result for invalid SKU
                validation_result = ValidationResult(
                    passed=False,
                    errors=[f"Pydantic validation failed: {str(e)}"],
                    warnings=[],
                    score=0.0,
                )
                validation_results.append(validation_result)
                invalid_skus.append((sku, validation_result))
                continue

        # Validate SKU
        validation_result = validate_sku_hybrid(sku, rules)
        validation_results.append(validation_result)

        if validation_result.passed:
            valid_skus.append(sku)
        else:
            invalid_skus.append((sku, validation_result))

    # Log statistics
    valid_count = len(valid_skus)
    invalid_count = len(invalid_skus)
    validation_rate = valid_count / len(extracted_skus) if extracted_skus else 0.0

    logger.info(
        f"B.7: Validation complete - "
        f"{valid_count} valid ({validation_rate:.1%}), "
        f"{invalid_count} invalid"
    )

    # Log sample of errors
    if invalid_skus:
        sample_errors = []
        for sku, result in invalid_skus[:5]:  # First 5
            sample_errors.append(f"  - {sku.descricao_original[:50]}...: {result.errors}")
        logger.warning(f"B.7: Sample validation errors:\n" + "\n".join(sample_errors))

    return {
        **state,
        "validation_results": validation_results,
        "valid_skus": valid_skus,
        "invalid_skus": invalid_skus,
    }


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "validate_skus_batch",
    "validate_sku_hybrid",
    "load_validation_rules",
    "get_default_validation_rules",
    "validate_material_class_compatibility",
    "validate_coating_compatibility",
    "validate_tipo_dimension_pattern",
]
