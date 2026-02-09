# GitHub Actions CI/CD Pipeline

This directory contains GitHub Actions workflows for the Forjador v5 LangGraph Platform Cloud deployment.

## Workflows

### 1. Test Workflow (`test.yml`)
**Trigger:** Push/PR to `main` or `develop` branches

**Purpose:** Run all tests to ensure code quality and functionality

**Steps:**
- Checkout code
- Set up Python 3.11
- Install dependencies
- Create queue directories
- Run pytest with coverage
- Upload coverage report (on push)

**Duration:** ~2-3 minutes

---

### 2. Quality Workflow (`quality.yml`)
**Trigger:** Push/PR to `main` or `develop` branches

**Purpose:** Enforce code quality standards

**Steps:**
- Checkout code
- Set up Python 3.11
- Install quality tools (ruff, black, mypy)
- Run linter (Ruff)
- Check formatting (Black)
- Type check (MyPy)
- Security scan (Bandit)

**Duration:** ~1-2 minutes

---

### 3. Deploy Workflow (`deploy.yml`)
**Trigger:** Push to `main` branch OR manual workflow dispatch

**Purpose:** Deploy to LangGraph Platform Cloud

**Steps:**
- Checkout code
- Set up Python 3.11
- Install LangGraph CLI
- Validate langgraph.json
- Install project dependencies
- Deploy using `langgraph deploy --wait`
- Report deployment status

**Duration:** ~3-5 minutes

---

## Required GitHub Secrets

Configure these secrets in your GitHub repository settings:

### Navigate to: Repository Settings > Secrets and variables > Actions > New repository secret

#### 1. `LANGCHAIN_API_KEY`
- **Purpose:** Authenticate with LangGraph Platform Cloud
- **How to get:**
  1. Visit https://smith.langchain.com/
  2. Sign in to your LangChain account
  3. Navigate to Settings > API Keys
  4. Create a new API key
  5. Copy the key (starts with `lsv2_pt_...`)

#### 2. `GOOGLE_API_KEY`
- **Purpose:** Authenticate with Google Gemini API for document parsing
- **How to get:**
  1. Visit https://aistudio.google.com/apikey
  2. Sign in to your Google account
  3. Create a new API key
  4. Copy the key

#### 3. `CODECOV_TOKEN` (Optional)
- **Purpose:** Upload test coverage reports to Codecov
- **How to get:**
  1. Visit https://codecov.io/
  2. Sign in with GitHub
  3. Add your repository
  4. Copy the upload token

---

## Setting Up Secrets

### Via GitHub UI:
1. Go to your repository on GitHub
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name listed above

### Via GitHub CLI:
```bash
gh secret set LANGCHAIN_API_KEY
gh secret set GOOGLE_API_KEY
gh secret set CODECOV_TOKEN
```

---

## Testing the Pipeline

### Test on Pull Request:
```bash
git checkout -b test-ci
git commit --allow-empty -m "Test CI pipeline"
git push origin test-ci
# Create PR on GitHub
```

### Test Deployment:
```bash
# Automatic deployment on main branch push
git checkout main
git merge develop
git push origin main

# OR manual deployment
# Go to Actions tab > Deploy workflow > Run workflow
```

---

## Pipeline Status Badges

Add these to your README.md:

```markdown
![Test](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/test.yml/badge.svg)
![Quality](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/quality.yml/badge.svg)
![Deploy](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/deploy.yml/badge.svg)
```

---

## Workflow Dependencies

```
┌─────────────┐
│   Quality   │
└─────────────┘
       │
       ├─ Ruff Linting
       ├─ Black Formatting
       ├─ MyPy Type Checking
       └─ Bandit Security Scan

┌─────────────┐
│    Test     │
└─────────────┘
       │
       ├─ Unit Tests
       ├─ Integration Tests
       └─ Coverage Report

┌─────────────┐
│   Deploy    │ (runs after push to main)
└─────────────┘
       │
       ├─ Validate Configuration
       ├─ Install Dependencies
       └─ LangGraph Deploy
```

---

## Environment Configuration

The deploy workflow uses the following environment variables (set via secrets):

| Variable | Source | Purpose |
|----------|--------|---------|
| `LANGCHAIN_API_KEY` | GitHub Secret | LangGraph Platform authentication |
| `GOOGLE_API_KEY` | GitHub Secret | Google Gemini API authentication |

---

## Troubleshooting

### Deployment fails with authentication error:
- Verify `LANGCHAIN_API_KEY` is set correctly in GitHub Secrets
- Ensure the API key has not expired
- Check the key has deployment permissions

### Tests fail with Google API error:
- Verify `GOOGLE_API_KEY` is set correctly
- Check API quota limits
- Ensure the Gemini API is enabled in your Google Cloud project

### LangGraph CLI not found:
- Ensure `langgraph-cli` is being installed in the workflow
- Check PyPI availability
- Verify Python version compatibility

### Deployment takes too long:
- Check the `--wait` flag in deploy command
- Monitor LangGraph Platform Cloud status
- Review deployment logs in Actions tab

---

## Best Practices

1. **Always run tests before deployment** - The pipeline enforces this by running tests on PR
2. **Use pull requests** - Merge to `main` only through reviewed PRs
3. **Monitor deployments** - Check Actions tab after each deployment
4. **Keep secrets secure** - Never commit secrets to version control
5. **Use semantic commits** - Follow conventional commit format for clear history

---

## Next Steps

Once the basic pipeline is working, consider adding:

- **Staging environment:** Add a `develop` branch deployment to staging
- **Rollback capability:** Implement deployment version tagging
- **Slack notifications:** Add deployment status notifications
- **Performance tests:** Add load testing before production deployment
- **Dependency caching:** Optimize build times with pip caching

---

## Support

- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/
- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **LangGraph Platform Cloud:** https://docs.smith.langchain.com/
