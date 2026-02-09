#!/bin/bash
# ============================================================================
# Forjador v5 - Local Test Script
# ============================================================================
# Runs all tests locally (matches CI/CD pipeline)
# - Unit tests with coverage
# - Integration tests (optional)
# - Generates coverage report
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
echo -e "${BLUE}Forjador v5 - Local Test Script${NC}"
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

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${RED}ERROR: pytest not found. Installing dev dependencies...${NC}"
    pip install -e ".[dev]"
fi

echo -e "${GREEN}✓ Prerequisites checked${NC}"
echo ""

# ----------------------------------------------------------------------------
# Step 2: Setup Test Environment
# ----------------------------------------------------------------------------
echo -e "${BLUE}[2/4] Setting up test environment...${NC}"

# Export mock environment variables for testing (matches CI pipeline)
export LANGCHAIN_TRACING_V2=false
export PRIMARY_LANGUAGE=pt-BR
export QUALITY_GATE_THRESHOLD=0.85
export CHUNK_SIZE=3500
export CHUNK_OVERLAP=250
export INPUT_DIR=./queue/input
export OUTPUT_DIR=./queue/output

# Use real API keys if available, otherwise use mock
if [ -f ".env" ]; then
    # Source real keys from .env if available
    source .env 2>/dev/null || true

    # Override tracing for tests
    export LANGCHAIN_TRACING_V2=false

    # Use mock key if not set
    if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
        export GOOGLE_API_KEY=mock_key_for_testing
    fi
fi

echo -e "${GREEN}✓ Test environment configured${NC}"
echo ""

# ----------------------------------------------------------------------------
# Step 3: Run Unit Tests
# ----------------------------------------------------------------------------
echo -e "${BLUE}[3/4] Running unit tests with coverage...${NC}"
echo ""

# Run pytest with coverage (matches CI pipeline)
if pytest tests/ -v --cov=src --cov-report=xml --cov-report=term-missing; then
    echo ""
    echo -e "${GREEN}✓ All unit tests passed${NC}"
else
    echo ""
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi

echo ""

# ----------------------------------------------------------------------------
# Step 4: Run Integration Tests (Optional)
# ----------------------------------------------------------------------------
echo -e "${BLUE}[4/4] Running integration tests (optional)...${NC}"

# Check if user has real API keys
if [ "$GOOGLE_API_KEY" = "mock_key_for_testing" ]; then
    echo -e "${YELLOW}Skipping integration tests (no real API keys configured)${NC}"
    echo -e "${YELLOW}To run integration tests, set GOOGLE_API_KEY in .env${NC}"
else
    read -p "Run integration tests? This will use real API calls. [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Running integration tests...${NC}"

        # Create queue directories if needed
        mkdir -p queue/input queue/output queue/processing queue/error queue/archive

        # Enable tracing for integration tests
        export LANGCHAIN_TRACING_V2=true

        if pytest tests/test_pipeline_integration.py -v -m integration; then
            echo -e "${GREEN}✓ Integration tests passed${NC}"
        else
            echo -e "${YELLOW}Some integration tests failed (this is expected if test data is not available)${NC}"
        fi
    else
        echo -e "${YELLOW}Skipping integration tests${NC}"
    fi
fi

echo ""

# ----------------------------------------------------------------------------
# Test Summary
# ----------------------------------------------------------------------------
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}Test Summary${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo -e "${GREEN}✓ Unit tests completed${NC}"
echo -e "  Coverage report: coverage.xml"
echo -e "  See terminal output above for coverage details"
echo ""

if [ -f "coverage.xml" ]; then
    echo -e "${BLUE}Coverage report generated:${NC} coverage.xml"
fi

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  - View coverage: open htmlcov/index.html (if generated)"
echo "  - Run quality checks: ./scripts/quality_check.sh"
echo "  - Deploy locally: ./scripts/deploy_local.sh"
echo ""
