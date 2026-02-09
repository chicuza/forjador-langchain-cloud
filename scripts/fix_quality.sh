#!/bin/bash
# Forjador v5 - Auto-fix Quality Issues
# Purpose: Automatically fix formatting and common issues
# Version: 1.0.0
# Date: 2026-02-09

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}Forjador v5 - Auto-fix Quality${NC}"
echo -e "${BLUE}==================================${NC}"
echo ""

# 1. Run Ruff formatter
echo -e "${YELLOW}[1/3] Running Ruff formatter...${NC}"
python -m ruff format src/ tests/
echo -e "${GREEN}✓ Code formatted${NC}"
echo ""

# 2. Run Ruff auto-fix
echo -e "${YELLOW}[2/3] Running Ruff auto-fix...${NC}"
python -m ruff check --fix src/ tests/
echo -e "${GREEN}✓ Auto-fixable issues resolved${NC}"
echo ""

# 3. Sort imports
echo -e "${YELLOW}[3/3] Sorting imports...${NC}"
python -m ruff check --select I --fix src/ tests/
echo -e "${GREEN}✓ Imports sorted${NC}"
echo ""

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}Quality fixes applied!${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo "Run './scripts/check_quality.sh' to verify all checks pass."
