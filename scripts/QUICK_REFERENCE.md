# CLI Scripts - Quick Reference

One-page reference for all Forjador v5 CLI scripts.

---

## Quick Start

```bash
# First time setup
./scripts/setup.sh                 # Setup everything
nano .env                          # Add API keys
python -m src.utils.env_validator  # Validate

# Development workflow
./scripts/quality_check.sh         # Check code quality
./scripts/test_local.sh            # Run tests
langgraph dev                      # Start local server

# Deploy to cloud
./scripts/deploy_local.sh          # Deploy to LangGraph Cloud
```

---

## Scripts Reference

### 1. setup.sh - Initial Setup

**When:** First time setup or new machine

**What:**
- Creates virtual environment
- Installs dependencies
- Creates .env file
- Creates queue directories

**Usage:**
```bash
./scripts/setup.sh
```

**After:**
- Edit .env with API keys
- Run: `python -m src.utils.env_validator`

---

### 2. test_local.sh - Run Tests

**When:** Before committing/deploying

**What:**
- Runs unit tests
- Generates coverage report
- Optionally runs integration tests

**Usage:**
```bash
./scripts/test_local.sh
```

**Matches CI:**
```yaml
pytest tests/ -v --cov=src --cov-report=xml
```

---

### 3. quality_check.sh - Code Quality

**When:** Before committing

**What:**
- Ruff linting
- Black formatting check
- MyPy type checking

**Usage:**
```bash
./scripts/quality_check.sh
```

**Auto-fix:**
```bash
ruff check src/ tests/ --fix
black src/ tests/
```

**Matches CI:**
```yaml
ruff check src/ tests/
black --check src/ tests/
mypy src/ --ignore-missing-imports
```

---

### 4. deploy_local.sh - Deploy to Cloud

**When:** Deploying to LangGraph Platform

**What:**
- Validates environment
- Deploys to LangGraph Cloud
- Verifies deployment

**Usage:**
```bash
./scripts/deploy_local.sh
```

**Interactive:**
- Prompts for deployment name
- Confirms before deploying

**After:**
```bash
langgraph deployments get <name>
langgraph deployments logs <name>
```

---

## Common Workflows

### New Developer Setup

```bash
./scripts/setup.sh
nano .env  # Add API keys
python -m src.utils.env_validator
./scripts/test_local.sh
```

### Pre-Commit Checks

```bash
./scripts/quality_check.sh && ./scripts/test_local.sh
```

### Pre-Deploy Checks

```bash
./scripts/quality_check.sh
./scripts/test_local.sh
./scripts/deploy_local.sh
```

### Fix Quality Issues

```bash
# Check issues
./scripts/quality_check.sh

# Auto-fix
ruff check src/ tests/ --fix
black src/ tests/

# Verify
./scripts/quality_check.sh
```

---

## LangGraph CLI Commands

### Development

```bash
# Start local dev server
langgraph dev

# Server: http://localhost:8000
```

### Deployment

```bash
# Deploy
langgraph deploy --name <deployment-name>

# List deployments
langgraph deployments list

# Get details
langgraph deployments get <name>

# View logs
langgraph deployments logs <name>

# Update deployment
langgraph deploy --name <name>
```

---

## Environment Variables

### Required for Tests

```bash
LANGCHAIN_TRACING_V2=false
GOOGLE_API_KEY=mock_key_for_testing
PRIMARY_LANGUAGE=pt-BR
QUALITY_GATE_THRESHOLD=0.85
CHUNK_SIZE=3500
CHUNK_OVERLAP=250
INPUT_DIR=./queue/input
OUTPUT_DIR=./queue/output
```

### Required for Deployment

```bash
LANGCHAIN_API_KEY=ls__your_real_key
GOOGLE_API_KEY=AIza_your_real_key
LANGCHAIN_PROJECT=forjador-v5-dev
```

See `.env.example` for all 11 required variables.

---

## Troubleshooting

### Permission denied

```bash
chmod +x scripts/*.sh
```

### Import errors

```bash
pip install -e ".[dev]"
```

### Virtual environment not found

```bash
./scripts/setup.sh
```

### Deployment fails

```bash
python -m src.utils.env_validator
cat langgraph.json | python -m json.tool
pip install -e . --dry-run
```

---

## File Locations

| File | Path |
|------|------|
| Scripts | `C:\Users\chicu\forjador-langchain-cloud\scripts\` |
| .env | `C:\Users\chicu\forjador-langchain-cloud\.env` |
| langgraph.json | `C:\Users\chicu\forjador-langchain-cloud\langgraph.json` |
| Tests | `C:\Users\chicu\forjador-langchain-cloud\tests\` |
| Source | `C:\Users\chicu\forjador-langchain-cloud\src\` |
| Queue | `C:\Users\chicu\forjador-langchain-cloud\queue\` |

---

## Performance

| Script | Typical Time |
|--------|-------------|
| setup.sh | 2-5 minutes |
| test_local.sh | 10-30 seconds |
| quality_check.sh | 5-10 seconds |
| deploy_local.sh | 2-5 minutes |

---

## Support

1. Scripts README: [`scripts/README.md`](README.md)
2. Deployment guide: [`DEPLOYMENT.md`](../DEPLOYMENT.md)
3. Main README: [`README.md`](../README.md)
4. Plan file: `C:\Users\chicu\.claude\plans\swift-petting-owl.md`

---

**All scripts match CI/CD pipeline commands**

Print this page for quick reference during development.
