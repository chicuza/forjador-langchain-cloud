#!/bin/bash
# Forjador v5 - Quality Check Script
# Purpose: Run all quality checks for CI/CD pipeline
# Version: 1.0.0
# Date: 2026-02-09

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}Forjador v5 - Quality Gate Check${NC}"
echo -e "${BLUE}==================================${NC}"
echo ""

# Track overall status
CHECKS_PASSED=0
CHECKS_FAILED=0

# Helper function to run checks
run_check() {
    local name=$1
    local command=$2

    echo -e "${YELLOW}Running: $name${NC}"
    echo "Command: $command"
    echo ""

    if eval "$command"; then
        echo -e "${GREEN}✓ $name passed${NC}"
        echo ""
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ $name failed${NC}"
        echo ""
        ((CHECKS_FAILED++))
        return 1
    fi
}

# 1. Code Formatting Check (Ruff)
echo -e "${BLUE}[1/4] Checking code formatting...${NC}"
run_check "Ruff Format Check" "python -m ruff format --check src/ tests/" || true

# 2. Linting (Ruff)
echo -e "${BLUE}[2/4] Running linter...${NC}"
run_check "Ruff Linting" "python -m ruff check src/ tests/" || true

# 3. Type Checking (MyPy)
echo -e "${BLUE}[3/4] Running type checker...${NC}"
run_check "MyPy Type Check" "python -m mypy src/" || true

# 4. Tests (Pytest)
echo -e "${BLUE}[4/4] Running tests...${NC}"
run_check "Pytest" "python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html" || true

# Summary
echo ""
echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}Quality Gate Summary${NC}"
echo -e "${BLUE}==================================${NC}"
echo -e "${GREEN}Passed: $CHECKS_PASSED${NC}"
echo -e "${RED}Failed: $CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All quality checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some quality checks failed. Please fix the issues above.${NC}"
    exit 1
fi
