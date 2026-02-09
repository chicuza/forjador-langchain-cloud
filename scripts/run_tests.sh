#!/bin/bash
# Forjador v5 - Test Runner Script
# Purpose: Run tests with various options
# Version: 1.0.0
# Date: 2026-02-09

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

# Parse arguments
TEST_TYPE=${1:-all}
EXTRA_ARGS="${@:2}"

echo -e "${BLUE}Forjador v5 - Test Runner${NC}"
echo ""

case $TEST_TYPE in
    all)
        echo "Running all tests..."
        python -m pytest tests/ -v $EXTRA_ARGS
        ;;

    unit)
        echo "Running unit tests..."
        python -m pytest tests/ -v -m "not integration" $EXTRA_ARGS
        ;;

    integration)
        echo "Running integration tests..."
        python -m pytest tests/ -v -m integration $EXTRA_ARGS
        ;;

    fast)
        echo "Running fast tests (no coverage)..."
        python -m pytest tests/ -v --no-cov -m "not slow" $EXTRA_ARGS
        ;;

    coverage)
        echo "Running tests with detailed coverage..."
        python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html $EXTRA_ARGS
        echo ""
        echo -e "${GREEN}Coverage report generated in: htmlcov/index.html${NC}"
        ;;

    parallel)
        echo "Running tests in parallel..."
        python -m pytest tests/ -v -n auto $EXTRA_ARGS
        ;;

    watch)
        echo "Running tests in watch mode..."
        python -m pytest tests/ -v --looponfail $EXTRA_ARGS
        ;;

    *)
        echo "Usage: $0 {all|unit|integration|fast|coverage|parallel|watch} [extra_args]"
        echo ""
        echo "Examples:"
        echo "  $0 all                    # Run all tests"
        echo "  $0 unit                   # Run only unit tests"
        echo "  $0 integration            # Run only integration tests"
        echo "  $0 fast                   # Run fast tests without coverage"
        echo "  $0 coverage               # Run with detailed coverage report"
        echo "  $0 parallel               # Run tests in parallel"
        echo "  $0 all -k test_pipeline   # Run specific test pattern"
        exit 1
        ;;
esac
