# Quality Automation - Quick Setup Guide

**5 minutes to get quality automation running**

---

## Step 1: Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- pytest (testing framework)
- pytest-asyncio (async test support)
- pytest-cov (coverage reporting)
- pytest-xdist (parallel testing)
- pytest-timeout (test timeouts)
- ruff (linter and formatter)
- mypy (type checker)
- pre-commit (git hooks)
- Type stubs for common packages

**Verify installation:**
```bash
python -m pytest --version
python -m ruff --version
python -m mypy --version
pre-commit --version
```

---

## Step 2: Install Pre-commit Hooks (Optional but Recommended)

```bash
pre-commit install
```

This enables automatic quality checks before every commit.

**Verify installation:**
```bash
pre-commit --version
```

---

## Step 3: Run Quality Checks

**Windows (PowerShell):**
```powershell
.\scripts\check_quality.ps1
```

**Linux/Mac/Git Bash:**
```bash
./scripts/check_quality.sh
```

**First run might show issues.** That's normal - continue to Step 4.

---

## Step 4: Auto-fix Issues

**Windows (PowerShell):**
```powershell
.\scripts\fix_quality.ps1
```

**Linux/Mac/Git Bash:**
```bash
./scripts/fix_quality.sh
```

This automatically fixes:
- Code formatting
- Import order
- Simple linting issues

---

## Step 5: Verify Everything Works

Run quality checks again:

**Windows:**
```powershell
.\scripts\check_quality.ps1
```

**Linux/Mac/Git Bash:**
```bash
./scripts/check_quality.sh
```

**Expected output:**
```
==================================
Forjador v5 - Quality Gate Check
==================================

[1/4] Checking code formatting...
✓ Ruff Format Check passed

[2/4] Running linter...
✓ Ruff Linting passed

[3/4] Running type checker...
✓ MyPy Type Check passed

[4/4] Running tests...
✓ Pytest passed

==================================
Quality Gate Summary
==================================
Passed: 4
Failed: 0

✓ All quality checks passed!
```

---

## Daily Usage

### Before Starting Work

```bash
git pull
pip install -e ".[dev]"  # Update dependencies
```

### During Development

```bash
# Fast tests (no coverage)
./scripts/run_tests.sh fast           # Linux/Mac/Git Bash
.\scripts\run_tests.ps1 fast         # Windows PowerShell
```

### Before Committing

```bash
# Auto-fix issues
./scripts/fix_quality.sh              # Linux/Mac/Git Bash
.\scripts\fix_quality.ps1            # Windows PowerShell

# Verify all checks pass
./scripts/check_quality.sh            # Linux/Mac/Git Bash
.\scripts\check_quality.ps1          # Windows PowerShell

# Commit (pre-commit hooks run automatically)
git add .
git commit -m "your message"
```

---

## Troubleshooting

### "Module not found" errors

```bash
# Reinstall dependencies
pip install -e ".[dev]"
```

### "Permission denied" on Linux/Mac

```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Scripts won't run on Windows

Use PowerShell (`.ps1`) versions:
```powershell
.\scripts\check_quality.ps1
.\scripts\fix_quality.ps1
.\scripts\run_tests.ps1
```

### Pre-commit hooks not running

```bash
# Reinstall hooks
pre-commit clean
pre-commit install
```

### Tests failing

```bash
# Run with verbose output
pytest tests/ -v

# Run specific test
pytest tests/test_pipeline_integration.py -v
```

---

## What's Next?

1. **Read the full guide:** `scripts/QUALITY_AUTOMATION.md`
2. **Check project summary:** `QUALITY_SETUP_SUMMARY.md`
3. **Review scripts:** `scripts/README.md`
4. **Start developing** with confidence!

---

## Quick Reference

```bash
# Install everything
pip install -e ".[dev]"
pre-commit install

# Check quality
./scripts/check_quality.sh          # Linux/Mac/Git Bash
.\scripts\check_quality.ps1        # Windows PowerShell

# Fix issues
./scripts/fix_quality.sh            # Linux/Mac/Git Bash
.\scripts\fix_quality.ps1          # Windows PowerShell

# Run tests
./scripts/run_tests.sh coverage     # Linux/Mac/Git Bash
.\scripts\run_tests.ps1 coverage   # Windows PowerShell

# Run hooks manually
pre-commit run --all-files
```

---

**Setup takes 5 minutes. Quality lasts forever.**
