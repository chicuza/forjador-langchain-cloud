# Forjador v5 - CLI Scripts

Practical CLI scripts for local development, testing, and deployment.

---

## Overview

These scripts provide a simple, efficient way to work with Forjador v5 locally and deploy to LangGraph Platform Cloud. They match the commands used in the CI/CD pipeline.

### Available Scripts

| Script | Purpose | Matches CI/CD |
|--------|---------|---------------|
| `setup.sh` | Initial setup (venv, deps, .env) | - |
| `test_local.sh` | Run tests with coverage | Unit Tests job |
| `quality_check.sh` | Code quality checks | Code Quality job |
| `deploy_local.sh` | Deploy to LangGraph Cloud | Deployment workflow |

---

## Quick Start

### 1. Initial Setup

```bash
# Run once to set up your environment
./scripts/setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Create .env from template
- Create queue directories
- Validate environment

### 2. Run Tests

```bash
# Run all tests with coverage (matches CI)
./scripts/test_local.sh
```

This will:
- Run unit tests
- Generate coverage report
- Optionally run integration tests

### 3. Quality Checks

```bash
# Run code quality checks (matches CI)
./scripts/quality_check.sh
```

This will:
- Run Ruff linting
- Check Black formatting
- Run MyPy type checking

### 4. Deploy to Cloud

```bash
# Deploy to LangGraph Platform Cloud
./scripts/deploy_local.sh
```

This will:
- Validate environment
- Check configuration files
- Deploy to LangGraph Cloud
- Verify deployment

---

## Script Details

### setup.sh

**Purpose:** Initial project setup

**Prerequisites:**
- Python 3.11+
- pip

**What it does:**
1. Checks Python version (3.11+)
2. Creates virtual environment
3. Upgrades pip, setuptools, wheel
4. Installs project dependencies
5. Optionally installs dev dependencies
6. Creates .env from template
7. Creates queue directories
8. Validates environment (if API keys are set)

**Usage:**
```bash
./scripts/setup.sh
```

**After running:**
1. Edit `.env` and add your API keys:
   - `LANGCHAIN_API_KEY` (from https://smith.langchain.com/settings)
   - `GOOGLE_API_KEY` (from https://aistudio.google.com/app/apikey)
2. Run validation: `python -m src.utils.env_validator`

---

### test_local.sh

**Purpose:** Run tests locally (matches CI pipeline)

**Prerequisites:**
- Virtual environment created
- Dev dependencies installed (`pip install -e ".[dev]"`)

**What it does:**
1. Activates virtual environment
2. Sets up test environment variables
3. Runs unit tests with coverage
4. Optionally runs integration tests
5. Generates coverage.xml report

**Usage:**
```bash
./scripts/test_local.sh
```

**Options:**
- Tests run with mock API keys by default
- If real API keys are in `.env`, you'll be prompted to run integration tests
- Coverage report saved to `coverage.xml`

**Matches CI:**
```yaml
# .github/workflows/test.yml - Unit Tests job
pytest tests/ -v --cov=src --cov-report=xml --cov-report=term
```

---

### quality_check.sh

**Purpose:** Code quality checks (matches CI pipeline)

**Prerequisites:**
- Virtual environment created
- Quality tools installed (ruff, black, mypy)

**What it does:**
1. Runs Ruff linting on `src/` and `tests/`
2. Checks Black formatting
3. Runs MyPy type checking
4. Reports pass/fail for each check

**Usage:**
```bash
./scripts/quality_check.sh
```

**Auto-fix issues:**
```bash
# Fix linting issues
ruff check src/ tests/ --fix

# Format code
black src/ tests/
```

**Matches CI:**
```yaml
# .github/workflows/test.yml - Code Quality job
ruff check src/ tests/
black --check src/ tests/
mypy src/ --ignore-missing-imports
```

---

### deploy_local.sh

**Purpose:** Deploy to LangGraph Platform Cloud

**Prerequisites:**
- LangGraph CLI installed (`pip install langgraph-cli`)
- API keys configured in `.env`
- Environment validated

**What it does:**
1. Checks LangGraph CLI is installed
2. Validates environment configuration
3. Validates `langgraph.json` and `pyproject.toml`
4. Prompts for deployment name
5. Deploys to LangGraph Cloud
6. Verifies deployment

**Usage:**
```bash
./scripts/deploy_local.sh
```

**Interactive prompts:**
1. Deployment name (default: `forjador-v5-spec01-dev`)
2. Confirmation before deploying

**After deployment:**
- Wait 1-2 minutes for initialization
- Check status: `langgraph deployments get <name>`
- View logs: `langgraph deployments logs <name>`
- Test health: `curl https://<name>.langchain.app/health`

**Matches:**
```bash
# Manual deployment command
langgraph deploy --name forjador-v5-spec01-prod
```

---

## Environment Variables

All scripts use environment variables from `.env` file.

### Required for Testing

```bash
# Mock values (for unit tests)
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
# Real API keys required
LANGCHAIN_API_KEY=ls__your_real_key
GOOGLE_API_KEY=AIza_your_real_key
LANGCHAIN_PROJECT=forjador-v5-dev
```

See `.env.example` for complete list of all 11 required variables.

---

## Common Workflows

### First Time Setup

```bash
# 1. Initial setup
./scripts/setup.sh

# 2. Edit .env with your API keys
nano .env  # or notepad .env on Windows

# 3. Validate environment
python -m src.utils.env_validator

# 4. Run tests
./scripts/test_local.sh

# 5. Run quality checks
./scripts/quality_check.sh
```

### Development Workflow

```bash
# 1. Make code changes
# 2. Run tests
./scripts/test_local.sh

# 3. Run quality checks
./scripts/quality_check.sh

# 4. Fix any issues
ruff check src/ tests/ --fix
black src/ tests/

# 5. Test locally with LangGraph dev server
langgraph dev
```

### Deployment Workflow

```bash
# 1. Run quality checks
./scripts/quality_check.sh

# 2. Run tests
./scripts/test_local.sh

# 3. Deploy to cloud
./scripts/deploy_local.sh

# 4. Monitor deployment
langgraph deployments get forjador-v5-spec01-dev
langgraph deployments logs forjador-v5-spec01-dev

# 5. Check LangSmith traces
# https://smith.langchain.com/
```

### Pre-Commit Workflow

```bash
# Before committing code
./scripts/quality_check.sh && ./scripts/test_local.sh
```

---

## Windows (Git Bash) Compatibility

All scripts work on Windows with Git Bash.

### Git Bash Setup

1. Install Git for Windows: https://git-scm.com/download/win
2. Open Git Bash terminal
3. Navigate to project: `cd /c/Users/chicu/forjador-langchain-cloud`
4. Run scripts: `./scripts/setup.sh`

### Path Handling

Scripts automatically detect Windows (Git Bash) and use correct paths:
- Virtual environment: `venv/Scripts/activate` (Windows)
- Virtual environment: `venv/bin/activate` (Linux/Mac)

---

## Troubleshooting

### Script won't run (Permission denied)

```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Virtual environment not found

```bash
# Run setup script first
./scripts/setup.sh
```

### Import errors in tests

```bash
# Reinstall dependencies
pip install -e ".[dev]"
```

### LangGraph CLI not found

```bash
# Install LangGraph CLI
pip install langgraph-cli

# Verify installation
langgraph --version
```

### Deployment fails

```bash
# 1. Check API keys in .env
python -m src.utils.env_validator

# 2. Validate langgraph.json
cat langgraph.json | python -m json.tool

# 3. Test dependency installation
pip install -e . --dry-run

# 4. Check LangGraph CLI authentication
langgraph login
```

---

## CI/CD Integration

These scripts match the GitHub Actions CI/CD pipeline in `.github/workflows/test.yml`.

### Local vs CI Comparison

| Check | Local Script | CI Job |
|-------|-------------|--------|
| Linting | `quality_check.sh` | `code-quality` job |
| Formatting | `quality_check.sh` | `code-quality` job |
| Type checking | `quality_check.sh` | `code-quality` job |
| Unit tests | `test_local.sh` | `unit-tests` job |
| Integration tests | `test_local.sh` | `integration-tests` job |
| Coverage | `test_local.sh` | `unit-tests` job |

### Testing Before Push

```bash
# Run same checks as CI pipeline
./scripts/quality_check.sh && ./scripts/test_local.sh
```

If both pass locally, CI should pass too.

---

## Performance

### Script Execution Times

| Script | Typical Time | Notes |
|--------|-------------|-------|
| `setup.sh` | 2-5 minutes | Depends on internet speed |
| `test_local.sh` | 10-30 seconds | Unit tests only |
| `quality_check.sh` | 5-10 seconds | Fast static checks |
| `deploy_local.sh` | 2-5 minutes | Cloud deployment |

### Optimization Tips

**Faster testing:**
```bash
# Run specific test file
pytest tests/test_file_validation.py -v

# Skip coverage for faster runs
pytest tests/ -v
```

**Faster quality checks:**
```bash
# Run only one check
ruff check src/ tests/
```

---

## Additional Commands

### LangGraph CLI Commands

```bash
# List all deployments
langgraph deployments list

# Get deployment details
langgraph deployments get <name>

# View deployment logs
langgraph deployments logs <name>

# Update deployment
langgraph deploy --name <name>

# Start local dev server
langgraph dev
```

### Python Commands

```bash
# Validate environment
python -m src.utils.env_validator

# Run agent directly
python -m src.agent

# Interactive Python shell
python
>>> from src.agent import graph
>>> graph.get_graph().draw_ascii()
```

### Testing Commands

```bash
# Run specific test
pytest tests/test_file_validation.py -v

# Run with markers
pytest -m integration

# Generate HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Best Practices

### Development

1. Always run `setup.sh` first on new machine
2. Run `quality_check.sh` before committing
3. Run `test_local.sh` before pushing
4. Keep `.env` file secure (never commit)
5. Use separate API keys for dev/prod

### Testing

1. Write tests for new features
2. Maintain > 80% code coverage
3. Run integration tests before deployment
4. Use mock API keys for unit tests
5. Monitor LangSmith traces for issues

### Deployment

1. Test locally with `langgraph dev` first
2. Run quality checks before deploying
3. Use descriptive deployment names
4. Monitor deployment logs after deploying
5. Test health endpoint after deployment
6. Check LangSmith traces for production

---

## Support

For issues with scripts:

1. Check this README for troubleshooting steps
2. Review `.env.example` for required variables
3. See `DEPLOYMENT.md` for deployment help
4. Check `README.md` for project overview
5. Review plan at: `C:\Users\chicu\.claude\plans\swift-petting-owl.md`

---

**Scripts created for Forjador v5 SPEC-01 MVP**

All scripts are production-ready and match CI/CD pipeline commands.
