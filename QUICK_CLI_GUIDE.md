# Forjador v5 - Quick CLI Guide

One-page guide to get started quickly with CLI scripts.

---

## 1. First Time Setup (2-5 minutes)

```bash
# Navigate to project
cd C:\Users\chicu\forjador-langchain-cloud

# Run setup script (creates venv, installs deps, creates .env)
./scripts/setup.sh

# Edit .env with your API keys
notepad .env  # Windows
# nano .env   # Linux/Mac

# Add these keys:
# LANGCHAIN_API_KEY=ls__your_key_here
# GOOGLE_API_KEY=AIza_your_key_here

# Validate environment
python -m src.utils.env_validator
```

**Expected output:**
```
Environment validation successful! All 11 SPEC-01 variables configured.
```

---

## 2. Development Workflow

### Run Quality Checks (5-10 seconds)

```bash
./scripts/quality_check.sh
```

**Checks:**
- Ruff linting
- Black formatting
- MyPy type checking

**If issues found:**
```bash
# Auto-fix linting
ruff check src/ tests/ --fix

# Auto-format code
black src/ tests/
```

### Run Tests (10-30 seconds)

```bash
./scripts/test_local.sh
```

**Runs:**
- Unit tests with coverage
- Optional integration tests

**Expected output:**
```
✓ All unit tests passed
Coverage: 85%+
```

### Start Dev Server

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
# source venv/Scripts/activate  # Git Bash (Windows)

# Start LangGraph dev server
langgraph dev
```

**Access:**
- Server: http://localhost:8000
- GraphiQL: http://localhost:8000/

---

## 3. Deploy to Cloud (2-5 minutes)

```bash
./scripts/deploy_local.sh
```

**Interactive prompts:**
1. Deployment name (default: `forjador-v5-spec01-dev`)
2. Confirm deployment

**After deployment:**
```bash
# Check status
langgraph deployments get forjador-v5-spec01-dev

# View logs
langgraph deployments logs forjador-v5-spec01-dev

# Test health
curl https://forjador-v5-spec01-dev.langchain.app/health
```

---

## 4. Quick Commands Reference

### Setup

```bash
./scripts/setup.sh              # Initial setup
python -m src.utils.env_validator  # Validate environment
```

### Quality & Testing

```bash
./scripts/quality_check.sh      # Code quality checks
./scripts/test_local.sh         # Run tests
```

### Development

```bash
source venv/bin/activate        # Activate venv (Linux/Mac)
source venv/Scripts/activate    # Activate venv (Git Bash)
langgraph dev                   # Start dev server
```

### Deployment

```bash
./scripts/deploy_local.sh       # Deploy to cloud
langgraph deployments list      # List deployments
langgraph deployments get <name>  # Get details
langgraph deployments logs <name> # View logs
```

---

## 5. Pre-Commit Checklist

```bash
# 1. Quality checks
./scripts/quality_check.sh

# 2. Run tests
./scripts/test_local.sh

# 3. If both pass, commit
git add .
git commit -m "Your message"
git push
```

---

## 6. Troubleshooting

### Permission denied

```bash
chmod +x scripts/*.sh
```

### Import errors

```bash
pip install -e ".[dev]"
```

### Environment validation fails

```bash
# Check .env file exists
cat .env

# Verify API keys are set
grep LANGCHAIN_API_KEY .env
grep GOOGLE_API_KEY .env
```

### LangGraph CLI not found

```bash
pip install langgraph-cli
langgraph --version
```

---

## 7. File Locations

| What | Where |
|------|-------|
| Scripts | `C:\Users\chicu\forjador-langchain-cloud\scripts\` |
| Environment | `C:\Users\chicu\forjador-langchain-cloud\.env` |
| Config | `C:\Users\chicu\forjador-langchain-cloud\langgraph.json` |
| Source | `C:\Users\chicu\forjador-langchain-cloud\src\` |
| Tests | `C:\Users\chicu\forjador-langchain-cloud\tests\` |

---

## 8. API Keys

### Get API Keys

1. **LangSmith API Key**
   - Go to: https://smith.langchain.com/settings
   - Copy API key (starts with `ls__`)
   - Add to `.env`: `LANGCHAIN_API_KEY=ls__your_key`

2. **Google Gemini API Key**
   - Go to: https://aistudio.google.com/app/apikey
   - Create API key
   - Add to `.env`: `GOOGLE_API_KEY=AIza_your_key`

---

## 9. Documentation

| Document | Purpose |
|----------|---------|
| `scripts/README.md` | Detailed scripts documentation |
| `scripts/QUICK_REFERENCE.md` | One-page command reference |
| `DEPLOYMENT.md` | Complete deployment guide |
| `README.md` | Project overview |

---

## 10. Common Workflows

### New Developer

```bash
./scripts/setup.sh
notepad .env  # Add API keys
python -m src.utils.env_validator
./scripts/test_local.sh
```

### Daily Development

```bash
source venv/bin/activate
# Make code changes
./scripts/quality_check.sh
./scripts/test_local.sh
# Commit if passing
```

### Before Deploying

```bash
./scripts/quality_check.sh
./scripts/test_local.sh
./scripts/deploy_local.sh
```

---

## Need Help?

1. Check `scripts/README.md` for detailed documentation
2. See `DEPLOYMENT.md` for deployment help
3. Review `README.md` for project overview
4. Check plan file: `C:\Users\chicu\.claude\plans\swift-petting-owl.md`

---

**Print this page for quick reference at your desk**

All scripts work on Windows (Git Bash), Linux, and Mac.
