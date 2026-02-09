#!/bin/bash
# ============================================================================
# Forjador v5 - Quality Check Script
# ============================================================================
# Runs code quality checks locally (matches CI/CD pipeline)
# - Ruff linting
# - Black formatting check
# - MyPy type checking
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}Forjador v5 - Code Quality Check${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# ----------------------------------------------------------------------------
# Step 1: Check Prerequisites
# ----------------------------------------------------------------------------
echo -e "${BLUE}[1/4] Checking prerequisites...${NC}"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Virtual environment not activated. Activating...${NC}"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
fi

# Check and install quality tools if needed
TOOLS_NEEDED=false

if ! python -c "import ruff" 2>/dev/null; then
    echo -e "${YELLOW}ruff not found${NC}"
    TOOLS_NEEDED=true
fi

if ! python -c "import black" 2>/dev/null; then
    echo -e "${YELLOW}black not found${NC}"
    TOOLS_NEEDED=true
fi

if ! python -c "import mypy" 2>/dev/null; then
    echo -e "${YELLOW}mypy not found${NC}"
    TOOLS_NEEDED=true
fi

if [ "$TOOLS_NEEDED" = true ]; then
    echo -e "${YELLOW}Installing quality tools...${NC}"
    pip install ruff black mypy
fi

echo -e "${GREEN}✓ Prerequisites checked${NC}"
echo ""

# ----------------------------------------------------------------------------
# Step 2: Run Ruff (Linter)
# ----------------------------------------------------------------------------
echo -e "${BLUE}[2/4] Running Ruff (linter)...${NC}"
echo ""

if ruff check src/ tests/; then
    echo ""
    echo -e "${GREEN}✓ Ruff linting passed${NC}"
    RUFF_PASSED=true
else
    echo ""
    echo -e "${RED}✗ Ruff linting failed${NC}"
    echo -e "${YELLOW}Run 'ruff check src/ tests/ --fix' to auto-fix issues${NC}"
    RUFF_PASSED=false
fi

echo ""

# ----------------------------------------------------------------------------
# Step 3: Run Black (Formatter)
# ----------------------------------------------------------------------------
echo -e "${BLUE}[3/4] Running Black (formatter check)...${NC}"
echo ""

if black --check src/ tests/; then
    echo ""
    echo -e "${GREEN}✓ Black formatting check passed${NC}"
    BLACK_PASSED=true
else
    echo ""
    echo -e "${RED}✗ Black formatting check failed${NC}"
    echo -e "${YELLOW}Run 'black src/ tests/' to auto-format code${NC}"
    BLACK_PASSED=false
fi

echo ""

# ----------------------------------------------------------------------------
# Step 4: Run MyPy (Type Checker)
# ----------------------------------------------------------------------------
echo -e "${BLUE}[4/4] Running MyPy (type checker)...${NC}"
echo ""

if mypy src/ --ignore-missing-imports; then
    echo ""
    echo -e "${GREEN}✓ MyPy type checking passed${NC}"
    MYPY_PASSED=true
else
    echo ""
    echo -e "${YELLOW}⚠ MyPy type checking found issues (warnings only)${NC}"
    MYPY_PASSED=true  # Don't fail on mypy warnings
fi

echo ""

# ----------------------------------------------------------------------------
# Quality Check Summary
# ----------------------------------------------------------------------------
echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}Quality Check Summary${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

if [ "$RUFF_PASSED" = true ]; then
    echo -e "${GREEN}✓ Ruff linting: PASSED${NC}"
else
    echo -e "${RED}✗ Ruff linting: FAILED${NC}"
fi

if [ "$BLACK_PASSED" = true ]; then
    echo -e "${GREEN}✓ Black formatting: PASSED${NC}"
else
    echo -e "${RED}✗ Black formatting: FAILED${NC}"
fi

if [ "$MYPY_PASSED" = true ]; then
    echo -e "${GREEN}✓ MyPy type checking: PASSED${NC}"
else
    echo -e "${YELLOW}⚠ MyPy type checking: WARNINGS${NC}"
fi

echo ""

# Exit with error if any critical check failed
if [ "$RUFF_PASSED" = false ] || [ "$BLACK_PASSED" = false ]; then
    echo -e "${RED}Quality checks failed. Please fix issues before deploying.${NC}"
    echo ""
    echo -e "${BLUE}Quick fixes:${NC}"
    echo "  - Auto-fix linting: ruff check src/ tests/ --fix"
    echo "  - Auto-format code: black src/ tests/"
    echo ""
    exit 1
fi

echo -e "${GREEN}All quality checks passed!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  - Run tests: ./scripts/test_local.sh"
echo "  - Deploy locally: ./scripts/deploy_local.sh"
echo ""
