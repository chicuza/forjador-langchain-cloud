# Git Workflow Guide - Forjador v5

## Repository Information

**Repository**: forjador-langchain-cloud
**Default Branch**: main
**Current State**: 10 commits, 63 tracked files, 8,935+ LOC
**Project**: SPEC-01 MVP - Industrial Fastener SKU Identification Pipeline

---

## Branch Strategy (Simple & Practical)

### Main Branch
- **Branch**: `main`
- **Purpose**: Production-ready code, deployable to LangGraph Platform Cloud
- **Protection**: Should be protected in production (no direct pushes)
- **Deployment**: Automatically deploys to LangGraph Cloud via GitHub Actions

### Feature Branches
- **Naming**: `feature/<short-description>` or `feat/<short-description>`
- **Examples**:
  - `feature/add-excel-parser`
  - `feature/improve-validation`
  - `feat/vector-search`
- **Purpose**: Develop new features, enhancements, or experiments
- **Lifecycle**: Create → Develop → Test → Merge → Delete

### Bug Fix Branches
- **Naming**: `fix/<issue-description>` or `bugfix/<issue-description>`
- **Examples**:
  - `fix/pdf-parsing-error`
  - `fix/validation-timeout`
- **Purpose**: Fix bugs and issues
- **Lifecycle**: Create → Fix → Test → Merge → Delete

### Hotfix Branches (Production Issues)
- **Naming**: `hotfix/<critical-issue>`
- **Examples**: `hotfix/api-timeout`
- **Purpose**: Emergency fixes for production
- **Lifecycle**: Create from main → Fix → Test → Merge → Deploy immediately

---

## Workflow Commands

### Starting New Work

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Work on your feature
# ... make changes ...

# Stage and commit changes
git add <files>
git commit -m "feat: Add your feature description"
```

### Committing Changes

Follow **Conventional Commits** format:

```bash
# Feature
git commit -m "feat: Add new SKU validation rule"

# Bug fix
git commit -m "fix: Resolve PDF parsing timeout"

# Documentation
git commit -m "docs: Update deployment instructions"

# Build/configuration
git commit -m "build: Update dependencies to LangGraph 0.7"

# Tests
git commit -m "test: Add integration tests for Excel parser"

# Refactoring
git commit -m "refactor: Simplify chunking logic"

# Performance
git commit -m "perf: Optimize DataFrame operations"

# CI/CD
git commit -m "ci: Add deployment workflow for staging"
```

### Merging Feature Branches

```bash
# Switch to main
git checkout main
git pull origin main

# Merge feature branch
git merge feature/your-feature-name

# Push to remote
git push origin main

# Delete feature branch
git branch -d feature/your-feature-name
```

### Pushing to Remote (First Time)

```bash
# Push feature branch to remote
git push -u origin feature/your-feature-name

# Create pull request on GitHub
# Review → Approve → Merge → Delete branch
```

---

## Commit Message Convention

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Code style (formatting, no logic change)
- **refactor**: Code refactoring
- **perf**: Performance improvement
- **test**: Add or update tests
- **build**: Build system or dependencies
- **ci**: CI/CD configuration
- **chore**: Maintenance tasks

### Examples
```bash
# Simple
git commit -m "feat: Add Gemini Vision parser"

# With body
git commit -m "fix: Resolve timeout in large PDF parsing

Increased timeout from 30s to 120s for documents >50 pages.
Added progress logging for better debugging."

# With breaking change
git commit -m "feat!: Change validation schema structure

BREAKING CHANGE: ValidationResult now returns structured errors
instead of simple strings. Update all validation consumers."
```

---

## LangGraph Cloud Deployment

### Automatic Deployment (via GitHub Actions)

When you push to `main`, the deployment workflow automatically:

1. Runs tests and quality checks
2. Validates `langgraph.json` configuration
3. Deploys to LangGraph Platform Cloud
4. Runs smoke tests

```bash
# Trigger deployment
git checkout main
git merge feature/your-feature
git push origin main

# GitHub Actions will:
# - Run pytest with coverage
# - Run ruff linting
# - Deploy to LangGraph Cloud
# - Verify deployment health
```

### Manual Deployment

```bash
# Using LangGraph CLI
langgraph deploy

# Or with explicit configuration
langgraph deploy --config langgraph.json
```

### Environment Variables

Required secrets in GitHub (`.github/workflows/deploy.yml`):
- `LANGGRAPH_API_KEY`: LangGraph Platform API key
- `GOOGLE_API_KEY`: Gemini API key
- `LANGSMITH_API_KEY`: LangSmith tracing key

See `GITHUB_SECRETS_SETUP.md` for detailed setup.

---

## Quality Checks Before Commit

### Run All Checks

```bash
# Linux/Mac
./scripts/check_quality.sh

# Windows PowerShell
.\scripts\check_quality.ps1
```

### Individual Checks

```bash
# Linting
ruff check src/ tests/

# Formatting
ruff format --check src/ tests/

# Type checking
mypy src/

# Tests
pytest tests/

# Coverage
pytest --cov=src --cov-report=term-missing
```

### Auto-fix Issues

```bash
# Linux/Mac
./scripts/fix_quality.sh

# Windows PowerShell
.\scripts\fix_quality.ps1

# Or manually
ruff check --fix src/ tests/
ruff format src/ tests/
```

---

## Pre-commit Hooks

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Configuration (`.pre-commit-config.yaml`)

Automatically runs on `git commit`:
- Trailing whitespace removal
- YAML/JSON validation
- Ruff linting and formatting
- Python syntax checks
- File size limits

---

## Common Workflows

### Working on a Feature

```bash
# 1. Create feature branch
git checkout -b feature/add-excel-parser

# 2. Make changes
# ... edit files ...

# 3. Stage and commit
git add src/parsers/excel_parser.py
git commit -m "feat: Add Excel parser with openpyxl"

# 4. Continue working
# ... more changes ...
git add tests/test_excel_parser.py
git commit -m "test: Add unit tests for Excel parser"

# 5. Push to remote
git push -u origin feature/add-excel-parser

# 6. Create pull request on GitHub
# 7. After approval, merge to main
git checkout main
git pull origin main
git branch -d feature/add-excel-parser
```

### Fixing a Bug

```bash
# 1. Create fix branch
git checkout -b fix/pdf-timeout

# 2. Fix the issue
# ... edit files ...

# 3. Test the fix
pytest tests/test_pdf_parser.py

# 4. Commit
git commit -m "fix: Increase PDF parsing timeout to 120s

Large documents (>50 pages) were timing out after 30s.
Increased timeout and added progress logging."

# 5. Push and create PR
git push -u origin fix/pdf-timeout
```

### Emergency Hotfix

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-validation-bug

# 2. Fix immediately
# ... fix critical issue ...

# 3. Test thoroughly
pytest tests/

# 4. Commit and push
git commit -m "fix!: Critical validation bug causing data loss"
git push -u origin hotfix/critical-validation-bug

# 5. Merge immediately after quick review
git checkout main
git merge hotfix/critical-validation-bug
git push origin main

# 6. Deploy immediately
# (GitHub Actions will auto-deploy)
```

### Updating Dependencies

```bash
# 1. Create branch
git checkout -b build/update-dependencies

# 2. Update pyproject.toml
# ... edit dependencies ...

# 3. Test thoroughly
pip install -e .[dev]
pytest tests/

# 4. Commit
git commit -m "build: Update LangGraph to 0.7.0 and dependencies"

# 5. Push and create PR
git push -u origin build/update-dependencies
```

---

## Git Configuration for LangGraph Cloud

### Required Files

1. **`langgraph.json`** - LangGraph Platform configuration
```json
{
  "python_version": "3.11",
  "dependencies": ["."],
  "graphs": {
    "forjador_v5_pipeline": "src.agent:graph"
  },
  "env": ".env"
}
```

2. **`pyproject.toml`** - Python dependencies
3. **`.env.example`** - Environment template
4. **`Dockerfile`** - Container configuration (optional)

### Deployment Checklist

Before deploying to LangGraph Cloud:

- [ ] All tests passing (`pytest`)
- [ ] Code quality checks passing (`ruff`)
- [ ] `langgraph.json` validated
- [ ] Environment variables configured
- [ ] API keys added to GitHub Secrets
- [ ] Documentation updated
- [ ] Commit history clean and meaningful

---

## Repository Statistics

```bash
# View commit history
git log --oneline --graph --all

# Count lines of code
git ls-files | grep '\.py$' | xargs wc -l

# View file tree
git ls-files --format='%(path)'

# Repository size
git count-objects -vH
```

### Current Stats
- **Total Commits**: 10
- **Tracked Files**: 63
- **Lines of Code**: 8,935+ (Python only)
- **Test Coverage**: Target 70%+
- **Documentation**: 6 major docs

---

## Troubleshooting

### Merge Conflicts

```bash
# Update your branch with main
git checkout feature/your-feature
git fetch origin
git merge origin/main

# If conflicts occur
# 1. Edit conflicting files
# 2. Stage resolved files
git add <resolved-files>

# 3. Complete merge
git commit -m "merge: Resolve conflicts with main"
```

### Undo Last Commit (Not Pushed)

```bash
# Keep changes, undo commit
git reset --soft HEAD~1

# Discard changes and commit
git reset --hard HEAD~1
```

### Undo Pushed Commit

```bash
# Create revert commit (safer)
git revert <commit-hash>
git push origin main
```

### View Changes

```bash
# Unstaged changes
git diff

# Staged changes
git diff --staged

# Changes between branches
git diff main feature/your-feature
```

---

## Best Practices

### Do's
- ✓ Write clear, descriptive commit messages
- ✓ Commit often (small, logical chunks)
- ✓ Test before committing
- ✓ Run quality checks before pushing
- ✓ Keep feature branches short-lived (1-3 days)
- ✓ Delete merged branches
- ✓ Use meaningful branch names
- ✓ Document breaking changes

### Don'ts
- ✗ Don't commit secrets or API keys
- ✗ Don't commit large binary files (PDFs, images)
- ✗ Don't force push to main
- ✗ Don't commit directly to main (use branches)
- ✗ Don't mix unrelated changes in one commit
- ✗ Don't leave branches unmerged for weeks

---

## References

- **LangGraph Cloud Docs**: https://langchain-ai.github.io/langgraph/cloud/
- **Conventional Commits**: https://www.conventionalcommits.org/
- **Git Documentation**: https://git-scm.com/doc
- **GitHub Flow**: https://guides.github.com/introduction/flow/

---

**Last Updated**: 2026-02-09
**Version**: 1.0
**Maintainer**: Forjador Development Team
