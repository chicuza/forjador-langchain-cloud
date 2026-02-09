#!/bin/bash
# ============================================================================
# Forjador v5 - Setup Script
# ============================================================================
# Initial setup for local development
# - Creates virtual environment
# - Installs dependencies
# - Creates .env from template
# - Creates queue directories
# - Validates environment
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
echo -e "${BLUE}Forjador v5 - Setup Script${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Change to project root
cd "$PROJECT_ROOT"
echo -e "${BLUE}Project root:${NC} $PROJECT_ROOT"
echo ""

# ----------------------------------------------------------------------------
# Step 1: Check Prerequisites
# ----------------------------------------------------------------------------
echo -e "${BLUE}[1/7] Checking prerequisites...${NC}"

# Check Python version
if ! command -v python &> /dev/null; then
    echo -e "${RED}ERROR: Python not found. Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}ERROR: Python $REQUIRED_VERSION+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check pip
if ! command -v pip &> /dev/null; then
    echo -e "${RED}ERROR: pip not found. Please install pip${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip found${NC}"

# Check git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}WARNING: git not found (optional for development)${NC}"
else
    echo -e "${GREEN}✓ git found${NC}"
fi

echo ""

# ----------------------------------------------------------------------------
# Step 2: Create Virtual Environment
# ----------------------------------------------------------------------------
echo -e "${BLUE}[2/7] Creating virtual environment...${NC}"

if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping...${NC}"
else
    python -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash)
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# ----------------------------------------------------------------------------
# Step 3: Upgrade pip
# ----------------------------------------------------------------------------
echo -e "${BLUE}[3/7] Upgrading pip, setuptools, wheel...${NC}"
python -m pip install --quiet --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# ----------------------------------------------------------------------------
# Step 4: Install Dependencies
# ----------------------------------------------------------------------------
echo -e "${BLUE}[4/7] Installing project dependencies...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}"

pip install --quiet -e .
echo -e "${GREEN}✓ Core dependencies installed${NC}"

# Ask if user wants dev dependencies
echo ""
read -p "Install development dependencies (pytest, ruff, black, mypy)? [Y/n] " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    pip install --quiet -e ".[dev]"
    echo -e "${GREEN}✓ Development dependencies installed${NC}"
fi

echo ""

# ----------------------------------------------------------------------------
# Step 5: Create Environment File
# ----------------------------------------------------------------------------
echo -e "${BLUE}[5/7] Creating .env file...${NC}"

if [ -f ".env" ]; then
    echo -e "${YELLOW}.env file already exists. Skipping...${NC}"
    read -p "Overwrite existing .env? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created from template${NC}"
        echo -e "${YELLOW}IMPORTANT: Edit .env and add your API keys:${NC}"
        echo -e "  - LANGCHAIN_API_KEY (get from https://smith.langchain.com/settings)"
        echo -e "  - GOOGLE_API_KEY (get from https://aistudio.google.com/app/apikey)"
    fi
else
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created from template${NC}"
    echo -e "${YELLOW}IMPORTANT: Edit .env and add your API keys:${NC}"
    echo -e "  - LANGCHAIN_API_KEY (get from https://smith.langchain.com/settings)"
    echo -e "  - GOOGLE_API_KEY (get from https://aistudio.google.com/app/apikey)"
fi

echo ""

# ----------------------------------------------------------------------------
# Step 6: Create Queue Directories
# ----------------------------------------------------------------------------
echo -e "${BLUE}[6/7] Creating queue directories...${NC}"

mkdir -p queue/input
mkdir -p queue/output
mkdir -p queue/processing
mkdir -p queue/error
mkdir -p queue/archive

echo -e "${GREEN}✓ Queue directories created:${NC}"
echo "  - queue/input      (place documents here)"
echo "  - queue/output     (processed results)"
echo "  - queue/processing (files being processed)"
echo "  - queue/error      (failed files)"
echo "  - queue/archive    (successfully processed)"
echo ""

# ----------------------------------------------------------------------------
# Step 7: Validate Environment (if API keys are set)
# ----------------------------------------------------------------------------
echo -e "${BLUE}[7/7] Validating environment...${NC}"

# Source .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if API keys are set
if [ -z "$LANGCHAIN_API_KEY" ] || [ "$LANGCHAIN_API_KEY" = "your_langsmith_api_key_here" ]; then
    echo -e "${YELLOW}WARNING: LANGCHAIN_API_KEY not set in .env${NC}"
    echo -e "${YELLOW}Skipping environment validation...${NC}"
elif [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
    echo -e "${YELLOW}WARNING: GOOGLE_API_KEY not set in .env${NC}"
    echo -e "${YELLOW}Skipping environment validation...${NC}"
else
    if python -m src.utils.env_validator; then
        echo -e "${GREEN}✓ Environment validation successful${NC}"
    else
        echo -e "${RED}ERROR: Environment validation failed${NC}"
        echo -e "${YELLOW}Please check your .env file and API keys${NC}"
    fi
fi

echo ""

# ----------------------------------------------------------------------------
# Setup Complete
# ----------------------------------------------------------------------------
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Edit .env and add your API keys"
echo "  2. Run validation: python -m src.utils.env_validator"
echo "  3. Run tests: ./scripts/test_local.sh"
echo "  4. Start dev server: langgraph dev"
echo ""
echo -e "${BLUE}Quick commands:${NC}"
echo "  - Activate venv: source venv/bin/activate (Linux/Mac)"
echo "  - Activate venv: source venv/Scripts/activate (Git Bash)"
echo "  - Run tests: ./scripts/test_local.sh"
echo "  - Quality check: ./scripts/quality_check.sh"
echo "  - Deploy local: ./scripts/deploy_local.sh"
echo ""
