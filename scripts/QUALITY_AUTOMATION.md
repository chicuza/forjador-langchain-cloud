# Forjador v5 - Quality Automation Guide

Complete guide for automated quality checks, testing, and CI/CD integration.

## Quick Reference

```bash
# Fix code quality issues automatically
./scripts/fix_quality.sh

# Run all quality checks
./scripts/check_quality.sh

# Run tests with coverage
./scripts/run_tests.sh coverage

# Install pre-commit hooks
pre-commit install
```

---

## Quality Tools Overview

### 1. Ruff (Linting & Formatting)
**Purpose:** Fast Python linter and formatter (replaces flake8, black, isort)

**Configuration:** `pyproject.toml` → `[tool.ruff]`

**Usage:**
```bash
# Check for issues
python -m ruff check src/ tests/

# Auto-fix issues
python -m ruff check --fix src/ tests/

# Format code
python -m ruff format src/ tests/

# Check formatting
python -m ruff format --check src/ tests/
```

### 2. MyPy (Type Checking)
**Purpose:** Static type checker for Python

**Configuration:** `pyproject.toml` → `[tool.mypy]`

**Usage:**
```bash
# Type check source code
python -m mypy src/

# Type check specific module
python -m mypy src/agent.py

# Show detailed error codes
python -m mypy src/ --show-error-codes
```

### 3. Pytest (Testing)
**Purpose:** Test framework with coverage reporting

**Configuration:** `pyproject.toml` → `[tool.pytest.ini_options]`

**Usage:**
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test
python -m pytest tests/test_pipeline_integration.py -v

# Run tests in parallel
python -m pytest tests/ -n auto
```

### 4. Pre-commit (Git Hooks)
**Purpose:** Automated quality checks before commits

**Configuration:** `.pre-commit-config.yaml`

**Usage:**
```bash
# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Skip hooks for one commit
git commit --no-verify -m "message"
```

---

## Script Details

### check_quality.sh / check_quality.ps1

**Purpose:** Run all quality gates in sequence

**Checks performed:**
1. Ruff format check (code formatting)
2. Ruff linting (code quality)
3. MyPy type checking (type safety)
4. Pytest (tests with coverage)

**Exit codes:**
- `0`: All checks passed
- `1`: One or more checks failed

**Usage:**
```bash
# Linux/Mac/Git Bash
./scripts/check_quality.sh

# Windows PowerShell
.\scripts\check_quality.ps1
```

**CI/CD Integration:**
This script matches exactly what runs in CI, so if it passes locally, CI should pass.

---

### fix_quality.sh / fix_quality.ps1

**Purpose:** Automatically fix common quality issues

**Actions performed:**
1. Format code with Ruff
2. Auto-fix linting issues
3. Sort imports

**Usage:**
```bash
# Linux/Mac/Git Bash
./scripts/fix_quality.sh

# Windows PowerShell
.\scripts\fix_quality.ps1
```

**Recommended workflow:**
```bash
# 1. Make code changes
# 2. Auto-fix issues
./scripts/fix_quality.sh

# 3. Verify all checks pass
./scripts/check_quality.sh

# 4. Commit
git add .
git commit -m "your message"
```

---

### run_tests.sh / run_tests.ps1

**Purpose:** Run tests with various configurations

**Test modes:**
- `all` - Run all tests (default)
- `unit` - Unit tests only (fast)
- `integration` - Integration tests only
- `fast` - No coverage (very fast)
- `coverage` - Detailed coverage report
- `parallel` - Run in parallel (requires pytest-xdist)

**Usage:**
```bash
# Linux/Mac/Git Bash
./scripts/run_tests.sh [mode] [extra_args]

# Windows PowerShell
.\scripts\run_tests.ps1 [mode] [extra_args]
```

**Examples:**
```bash
# All tests with coverage
./scripts/run_tests.sh coverage

# Fast iteration during development
./scripts/run_tests.sh fast

# Run specific test pattern
./scripts/run_tests.sh all -k test_pipeline

# Run tests in parallel
./scripts/run_tests.sh parallel
```

---

## Quality Standards

### Code Coverage
- **Minimum:** 70% (enforced)
- **Target:** 80%+
- **Critical paths:** 90%+

Coverage is tracked in:
- Terminal output
- HTML report: `htmlcov/index.html`
- XML report: `coverage.xml` (for CI)

### Linting Rules
**Tool:** Ruff

**Selected rule sets:**
- `E` - pycodestyle errors
- `W` - pycodestyle warnings
- `F` - pyflakes
- `I` - isort (import sorting)
- `B` - flake8-bugbear
- `C4` - flake8-comprehensions
- `UP` - pyupgrade
- `N` - pep8-naming
- `SIM` - flake8-simplify
- `RET` - flake8-return
- `ARG` - flake8-unused-arguments

**Ignored rules:**
- `E501` - Line too long (handled by formatter)
- `B008` - Function calls in argument defaults
- `ARG001/002` - Unused arguments (common in handlers)

### Type Checking
**Tool:** MyPy

**Configuration:**
- Gradual typing enabled
- Strict mode for `src/state/*`
- Ignore missing imports
- Show error codes

**Coverage:**
- State schemas: 100% typed
- Nodes: Gradually improving
- Utils: Optional typing

### Testing Standards
**Framework:** Pytest

**Test organization:**
- Unit tests: Fast, isolated, no external dependencies
- Integration tests: Test complete workflows
- Markers: `unit`, `integration`, `slow`

**Test timeout:** 5 minutes per test

**Async support:** pytest-asyncio with auto mode

---

## Pre-commit Hooks

### Installation

```bash
# Install pre-commit package
pip install pre-commit

# Install git hooks
pre-commit install

# Verify installation
pre-commit --version
```

### Configured Hooks

1. **Ruff Linter** - Auto-fix linting issues
2. **Ruff Format** - Format code
3. **MyPy** - Type checking (src/ only)
4. **File checks** - Large files, trailing whitespace, EOF
5. **Syntax checks** - YAML, JSON validation
6. **Merge conflict check** - Prevent incomplete merges
7. **Branch protection** - Prevent direct commits to main
8. **Secret detection** - Detect accidentally committed secrets

### Usage

**Automatic (on commit):**
```bash
git add .
git commit -m "message"
# Hooks run automatically
```

**Manual run:**
```bash
# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files src/agent.py

# Run specific hook
pre-commit run ruff --all-files
```

**Skip hooks:**
```bash
# Skip all hooks
git commit --no-verify -m "message"

# Skip specific hook
SKIP=mypy git commit -m "message"
```

### Troubleshooting

**Hooks too slow?**
```bash
# Skip slow hooks during rapid iteration
SKIP=mypy git commit -m "WIP: quick change"
```

**Hook failing?**
```bash
# Run manually to see details
pre-commit run ruff --all-files

# Fix issues
./scripts/fix_quality.sh

# Try commit again
git commit -m "message"
```

**Update hooks:**
```bash
# Update to latest versions
pre-commit autoupdate

# Reinstall hooks
pre-commit clean
pre-commit install
```

---

## CI/CD Integration

### GitHub Actions Workflow

**File:** `.github/workflows/quality.yml`

**Triggers:**
- Push to `main`
- Pull requests
- Manual workflow dispatch

**Jobs:**

1. **Lint**
   - Ruff format check
   - Ruff linting

2. **Type Check**
   - MyPy on src/

3. **Test**
   - Pytest with coverage
   - Upload coverage to Codecov

4. **Quality Gate**
   - Require 70% coverage
   - All checks must pass

### Local CI Simulation

**Exact match with CI:**
```bash
./scripts/check_quality.sh
```

This runs the same commands as CI, so if it passes locally, CI should pass.

### CI Configuration

**Coverage threshold:** 70% (matches pytest config)

**Python version:** 3.11 (matches project requirement)

**Dependencies:** Installed from `pyproject.toml`

---

## Development Workflows

### Daily Development

```bash
# 1. Start work
git pull

# 2. Make changes
# ... edit code ...

# 3. Fast tests during development
./scripts/run_tests.sh fast

# 4. Auto-fix quality issues
./scripts/fix_quality.sh

# 5. Full quality check
./scripts/check_quality.sh

# 6. Commit (hooks run automatically)
git add .
git commit -m "descriptive message"

# 7. Push
git push
```

### Before Pull Request

```bash
# 1. Ensure on feature branch
git checkout -b feature/my-feature

# 2. Run full quality suite
./scripts/check_quality.sh

# 3. Review coverage report
./scripts/run_tests.sh coverage
open htmlcov/index.html

# 4. Fix any issues
./scripts/fix_quality.sh

# 5. Commit all changes
git add .
git commit -m "feat: implement my feature"

# 6. Push and create PR
git push -u origin feature/my-feature
```

### Fixing Failing CI

```bash
# 1. Pull latest
git pull origin main

# 2. Run same checks as CI
./scripts/check_quality.sh

# 3. Review failures
# Look at terminal output for details

# 4. Fix automatically if possible
./scripts/fix_quality.sh

# 5. Fix remaining issues manually
# Edit code based on error messages

# 6. Verify fixes
./scripts/check_quality.sh

# 7. Commit fixes
git add .
git commit -m "fix: resolve quality issues"
git push
```

### Adding New Tests

```bash
# 1. Create test file
# tests/test_new_feature.py

# 2. Run single test file
pytest tests/test_new_feature.py -v

# 3. Check coverage impact
pytest tests/test_new_feature.py --cov=src --cov-report=term-missing

# 4. Run full suite
./scripts/run_tests.sh coverage

# 5. Commit tests
git add tests/test_new_feature.py
git commit -m "test: add tests for new feature"
```

---

## Troubleshooting

### Tests Failing

**ImportError: No module named 'src'**
```bash
# Install package in editable mode
pip install -e .
```

**Coverage below 70%**
```bash
# View detailed report
./scripts/run_tests.sh coverage
open htmlcov/index.html

# Add tests for uncovered code
```

**Async test warnings**
```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Check asyncio_mode in pyproject.toml
# Should be: asyncio_mode = "auto"
```

### Linting Failures

**Ruff errors**
```bash
# See all errors
python -m ruff check src/ tests/

# Auto-fix what can be fixed
python -m ruff check --fix src/ tests/

# Format code
python -m ruff format src/ tests/
```

**Import order issues**
```bash
# Auto-fix imports
python -m ruff check --select I --fix src/ tests/
```

### Type Checking Failures

**MyPy errors**
```bash
# See detailed errors
python -m mypy src/ --show-error-codes

# Check specific file
python -m mypy src/agent.py

# Common fixes:
# 1. Add type hints
# 2. Add # type: ignore comment
# 3. Update mypy config to ignore
```

### Pre-commit Issues

**Hooks not running**
```bash
# Reinstall hooks
pre-commit clean
pre-commit install
```

**Hook failing**
```bash
# Run manually to debug
pre-commit run ruff --all-files

# Skip problematic hook temporarily
SKIP=mypy git commit -m "message"
```

**Hooks too slow**
```bash
# Skip all hooks temporarily
git commit --no-verify -m "message"
```

### Windows-Specific Issues

**Scripts not executable**
```bash
# Use PowerShell versions
.\scripts\check_quality.ps1
.\scripts\run_tests.ps1
.\scripts\fix_quality.ps1
```

**Path issues**
```bash
# Use backslashes in PowerShell
python -m pytest tests\ -v

# Or use forward slashes (works in PS)
python -m pytest tests/ -v
```

---

## Configuration Files Reference

### pyproject.toml

All tool configurations are centralized in `pyproject.toml`:

```toml
[tool.ruff]              # Linter & formatter config
[tool.ruff.lint]         # Linting rules
[tool.ruff.format]       # Formatting rules
[tool.mypy]              # Type checker config
[tool.pytest.ini_options] # Test framework config
```

### .pre-commit-config.yaml

Pre-commit hook definitions and versions.

### .secrets.baseline

Baseline for secret detection (generated on first run).

---

## Best Practices

### Code Quality

1. **Format before committing**
   ```bash
   ./scripts/fix_quality.sh
   ```

2. **Check locally before pushing**
   ```bash
   ./scripts/check_quality.sh
   ```

3. **Use pre-commit hooks**
   ```bash
   pre-commit install
   ```

### Testing

1. **Write tests for new features**
   - Aim for 80%+ coverage
   - Include edge cases

2. **Run fast tests during development**
   ```bash
   ./scripts/run_tests.sh fast
   ```

3. **Full suite before PR**
   ```bash
   ./scripts/run_tests.sh coverage
   ```

### Type Safety

1. **Add type hints to new code**
   ```python
   def process_file(path: str) -> dict:
       ...
   ```

2. **Use Pydantic for data validation**
   ```python
   from pydantic import BaseModel

   class FileMetadata(BaseModel):
       path: str
       size: int
   ```

3. **Check types periodically**
   ```bash
   python -m mypy src/
   ```

---

## Performance Optimization

### Faster Testing

```bash
# Skip coverage (faster)
pytest tests/ -v

# Run only changed tests
pytest tests/ --lf  # last failed
pytest tests/ --ff  # failed first

# Parallel execution
pytest tests/ -n auto

# Stop on first failure
pytest tests/ -x
```

### Faster Quality Checks

```bash
# Run only linting
python -m ruff check src/ tests/

# Run only formatting
python -m ruff format --check src/ tests/

# Run only type checking
python -m mypy src/
```

### CI Optimization

**Cache dependencies:**
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
```

**Parallel jobs:**
- Lint and type check run in parallel
- Tests run separately

---

## Resources

### Tool Documentation

- **Ruff:** https://docs.astral.sh/ruff/
- **MyPy:** https://mypy.readthedocs.io/
- **Pytest:** https://docs.pytest.org/
- **Pre-commit:** https://pre-commit.com/

### Project Documentation

- **Main README:** `README.md`
- **Scripts Guide:** `scripts/README.md`
- **Deployment:** `DEPLOYMENT.md`
- **Implementation:** `IMPLEMENTATION_SUMMARY.md`

### Support

For quality automation issues:
1. Check this guide
2. Review tool documentation
3. Check CI logs for details
4. Run checks locally with `-v` flag

---

**Quality automation setup for Forjador v5 SPEC-01 MVP**

All tools configured and integrated with CI/CD pipeline.
