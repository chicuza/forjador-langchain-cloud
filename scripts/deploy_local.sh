#!/bin/bash
# ============================================================================
# Forjador v5 - Local Deployment Script
# ============================================================================
# Deploys to LangGraph Platform Cloud from local machine
# - Validates environment
# - Checks LangGraph CLI
# - Deploys to cloud
# - Tests deployment
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
echo -e "${BLUE}Forjador v5 - LangGraph Cloud Deployment${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# ----------------------------------------------------------------------------
# Step 1: Check Prerequisites
# ----------------------------------------------------------------------------
echo -e "${BLUE}[1/6] Checking prerequisites...${NC}"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Virtual environment not activated. Activating...${NC}"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
fi

# Check if langgraph CLI is installed
if ! command -v langgraph &> /dev/null; then
    echo -e "${YELLOW}LangGraph CLI not found. Installing...${NC}"
    pip install langgraph-cli
fi

# Verify langgraph CLI version
LANGGRAPH_VERSION=$(langgraph --version 2>&1 || echo "unknown")
echo -e "${GREEN}✓ LangGraph CLI: $LANGGRAPH_VERSION${NC}"

# Check if langgraph.json exists
if [ ! -f "langgraph.json" ]; then
    echo -e "${RED}ERROR: langgraph.json not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ langgraph.json found${NC}"

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}ERROR: pyproject.toml not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pyproject.toml found${NC}"

echo ""

# ----------------------------------------------------------------------------
# Step 2: Validate Environment
# ----------------------------------------------------------------------------
echo -e "${BLUE}[2/6] Validating environment configuration...${NC}"

# Source .env file if exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if API keys are set
if [ -z "$LANGCHAIN_API_KEY" ] || [ "$LANGCHAIN_API_KEY" = "your_langsmith_api_key_here" ]; then
    echo -e "${RED}ERROR: LANGCHAIN_API_KEY not set in .env${NC}"
    echo -e "${YELLOW}Get your API key from: https://smith.langchain.com/settings${NC}"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
    echo -e "${RED}ERROR: GOOGLE_API_KEY not set in .env${NC}"
    echo -e "${YELLOW}Get your API key from: https://aistudio.google.com/app/apikey${NC}"
    exit 1
fi

# Run environment validator
if python -m src.utils.env_validator; then
    echo -e "${GREEN}✓ Environment validation passed${NC}"
else
    echo -e "${RED}ERROR: Environment validation failed${NC}"
    exit 1
fi

echo ""

# ----------------------------------------------------------------------------
# Step 3: Validate Configuration Files
# ----------------------------------------------------------------------------
echo -e "${BLUE}[3/6] Validating configuration files...${NC}"

# Validate langgraph.json
if python -m json.tool langgraph.json > /dev/null 2>&1; then
    echo -e "${GREEN}✓ langgraph.json is valid JSON${NC}"
else
    echo -e "${RED}ERROR: langgraph.json is invalid JSON${NC}"
    exit 1
fi

# Check Python version in langgraph.json
PYTHON_VERSION=$(python -c "import json; print(json.load(open('langgraph.json'))['python_version'])")
echo -e "${GREEN}✓ Python version: $PYTHON_VERSION${NC}"

# Validate dependencies can be installed
echo -e "${YELLOW}Testing dependency installation (dry-run)...${NC}"
if pip install -e . --dry-run > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Dependencies are installable${NC}"
else
    echo -e "${RED}ERROR: Some dependencies cannot be installed${NC}"
    exit 1
fi

echo ""

# ----------------------------------------------------------------------------
# Step 4: Choose Deployment Name
# ----------------------------------------------------------------------------
echo -e "${BLUE}[4/6] Configure deployment...${NC}"

# Ask for deployment name
DEFAULT_NAME="forjador-v5-spec01-dev"
echo -e "${YELLOW}Enter deployment name (default: $DEFAULT_NAME):${NC}"
read -r DEPLOYMENT_NAME
DEPLOYMENT_NAME=${DEPLOYMENT_NAME:-$DEFAULT_NAME}

echo -e "${BLUE}Deployment name:${NC} $DEPLOYMENT_NAME"
echo ""

# Confirm deployment
echo -e "${YELLOW}This will deploy to LangGraph Platform Cloud.${NC}"
echo -e "${YELLOW}Deployment name: $DEPLOYMENT_NAME${NC}"
read -p "Continue? [Y/n] " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

echo ""

# ----------------------------------------------------------------------------
# Step 5: Deploy to LangGraph Cloud
# ----------------------------------------------------------------------------
echo -e "${BLUE}[5/6] Deploying to LangGraph Platform Cloud...${NC}"
echo -e "${YELLOW}This may take 2-5 minutes...${NC}"
echo ""

# Deploy using LangGraph CLI
if langgraph deploy --name "$DEPLOYMENT_NAME"; then
    echo ""
    echo -e "${GREEN}✓ Deployment successful!${NC}"
else
    echo ""
    echo -e "${RED}✗ Deployment failed${NC}"
    echo -e "${YELLOW}Check the error messages above for details${NC}"
    exit 1
fi

echo ""

# ----------------------------------------------------------------------------
# Step 6: Verify Deployment
# ----------------------------------------------------------------------------
echo -e "${BLUE}[6/6] Verifying deployment...${NC}"

# List deployments to confirm
echo -e "${YELLOW}Listing deployments...${NC}"
langgraph deployments list

echo ""
echo -e "${YELLOW}Getting deployment details...${NC}"
if langgraph deployments get "$DEPLOYMENT_NAME"; then
    echo -e "${GREEN}✓ Deployment verified${NC}"
else
    echo -e "${YELLOW}⚠ Could not get deployment details (may still be initializing)${NC}"
fi

echo ""

# ----------------------------------------------------------------------------
# Deployment Complete
# ----------------------------------------------------------------------------
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo -e "${BLUE}Deployment name:${NC} $DEPLOYMENT_NAME"
echo -e "${BLUE}Expected URL:${NC} https://$DEPLOYMENT_NAME.langchain.app"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Wait 1-2 minutes for deployment to fully initialize"
echo "  2. Check deployment status: langgraph deployments get $DEPLOYMENT_NAME"
echo "  3. View logs: langgraph deployments logs $DEPLOYMENT_NAME"
echo "  4. Monitor traces in LangSmith: https://smith.langchain.com/"
echo ""
echo -e "${BLUE}Testing deployment:${NC}"
echo "  - Health check: curl https://$DEPLOYMENT_NAME.langchain.app/health"
echo "  - Test API endpoint (see DEPLOYMENT.md for examples)"
echo ""
echo -e "${BLUE}Managing deployment:${NC}"
echo "  - Update: langgraph deploy --name $DEPLOYMENT_NAME"
echo "  - View logs: langgraph deployments logs $DEPLOYMENT_NAME"
echo "  - List all: langgraph deployments list"
echo ""
