# GitHub Secrets Setup Guide

This guide will help you configure the required secrets for the CI/CD pipeline.

## Required Secrets

You need to configure **2 mandatory secrets** and **1 optional secret**:

### 1. LANGCHAIN_API_KEY (Mandatory)
**Purpose:** Deploy to LangGraph Platform Cloud

**Steps to obtain:**
1. Visit https://smith.langchain.com/
2. Sign in or create an account
3. Navigate to **Settings** → **API Keys**
4. Click **Create API Key**
5. Give it a name (e.g., "GitHub Actions Deploy")
6. Copy the key (format: `lsv2_pt_xxxxxxxxxxxxx`)

### 2. GOOGLE_API_KEY (Mandatory)
**Purpose:** Google Gemini API for document parsing (Docling + Gemini 2.5 Flash Vision)

**Steps to obtain:**
1. Visit https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click **Create API Key**
4. Select a Google Cloud project (or create new)
5. Copy the API key

### 3. CODECOV_TOKEN (Optional)
**Purpose:** Upload test coverage reports

**Steps to obtain:**
1. Visit https://codecov.io/
2. Sign in with GitHub
3. Add your repository
4. Copy the upload token from repository settings

---

## Setting Up Secrets in GitHub

### Method 1: GitHub Web UI (Recommended)

1. Go to your GitHub repository
2. Click **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret:
   - **Name:** `LANGCHAIN_API_KEY`
   - **Value:** Paste your LangChain API key
   - Click **Add secret**
6. Repeat for `GOOGLE_API_KEY` and optionally `CODECOV_TOKEN`

### Method 2: GitHub CLI

```bash
# Install GitHub CLI if needed
# https://cli.github.com/

# Set secrets interactively
gh secret set LANGCHAIN_API_KEY
# Paste your key when prompted

gh secret set GOOGLE_API_KEY
# Paste your key when prompted

gh secret set CODECOV_TOKEN  # Optional
# Paste your token when prompted
```

### Method 3: GitHub CLI (One-liner)

```bash
# Set secrets directly (be careful with shell history)
echo "your_langchain_api_key" | gh secret set LANGCHAIN_API_KEY
echo "your_google_api_key" | gh secret set GOOGLE_API_KEY
echo "your_codecov_token" | gh secret set CODECOV_TOKEN
```

---

## Verifying Secrets

After setting up secrets, verify they're configured:

### Via GitHub UI:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. You should see:
   - ✅ `LANGCHAIN_API_KEY`
   - ✅ `GOOGLE_API_KEY`
   - ✅ `CODECOV_TOKEN` (if added)

### Via GitHub CLI:
```bash
gh secret list
```

Expected output:
```
LANGCHAIN_API_KEY    Updated 2024-XX-XX
GOOGLE_API_KEY       Updated 2024-XX-XX
CODECOV_TOKEN        Updated 2024-XX-XX
```

---

## Testing the Setup

### Test the Quality & Test workflows:
```bash
# Create a test branch
git checkout -b test-ci-setup
git commit --allow-empty -m "test: verify CI/CD pipeline setup"
git push origin test-ci-setup

# Create a pull request
gh pr create --title "Test CI/CD Setup" --body "Testing pipeline configuration"
```

This will trigger:
- ✅ **Quality workflow** (linting, formatting, type checking)
- ✅ **Test workflow** (unit + integration tests)

### Test the Deploy workflow:
```bash
# Merge to main (or push directly to main)
git checkout main
git merge test-ci-setup
git push origin main
```

This will trigger:
- ✅ **Deploy workflow** (deployment to LangGraph Platform Cloud)

---

## Security Best Practices

1. **Never commit secrets to version control**
   ```bash
   # Add to .gitignore if not already present
   echo ".env" >> .gitignore
   echo "*.key" >> .gitignore
   ```

2. **Rotate secrets regularly**
   - Change API keys every 90 days
   - Immediately rotate if compromised

3. **Use environment protection rules**
   - Go to **Settings** → **Environments**
   - Create "production" environment
   - Add required reviewers for deployments

4. **Monitor secret usage**
   - Check Actions logs for unauthorized access
   - Review API usage in LangChain and Google Cloud consoles

5. **Limit secret scope**
   - Create deployment-only API keys (no admin access)
   - Use principle of least privilege

---

## Troubleshooting

### "Secret not found" error:
- Verify secret name exactly matches (case-sensitive)
- Ensure secret is set at repository level (not organization)
- Check repository permissions for Actions

### Deployment authentication fails:
- Verify `LANGCHAIN_API_KEY` is valid
- Check key hasn't expired
- Ensure key has deployment permissions in LangChain console

### Google API errors in tests:
- Verify `GOOGLE_API_KEY` is valid
- Check API quota limits in Google Cloud Console
- Ensure Gemini API is enabled

### Secrets not updating in workflows:
- Re-run workflow after updating secrets
- Wait ~5 minutes for GitHub to propagate changes
- Clear Actions cache if issue persists

---

## Environment Variables vs Secrets

**Secrets** (sensitive data):
- `LANGCHAIN_API_KEY` ← Secret
- `GOOGLE_API_KEY` ← Secret
- `CODECOV_TOKEN` ← Secret

**Environment Variables** (non-sensitive config):
- `PYTHON_VERSION=3.11` ← Defined in workflow
- `QUALITY_GATE_THRESHOLD=0.85` ← Defined in workflow
- `CHUNK_SIZE=3500` ← Defined in workflow

---

## Next Steps

After setting up secrets:

1. ✅ Verify secrets are configured
2. ✅ Test Quality + Test workflows with a PR
3. ✅ Test Deploy workflow with a push to main
4. ✅ Monitor first deployment in Actions tab
5. ✅ Verify deployment in LangGraph Platform Cloud console

---

## Quick Reference

| Secret Name | Required | Purpose | Where to Get |
|-------------|----------|---------|--------------|
| `LANGCHAIN_API_KEY` | ✅ Yes | LangGraph deployment | https://smith.langchain.com/ |
| `GOOGLE_API_KEY` | ✅ Yes | Gemini API | https://aistudio.google.com/apikey |
| `CODECOV_TOKEN` | ⚠️ Optional | Coverage reports | https://codecov.io/ |

---

## Support Links

- **LangChain API Keys:** https://docs.smith.langchain.com/administration/how_to_guides/organization_management/api_keys
- **Google AI Studio:** https://ai.google.dev/tutorials/setup
- **GitHub Secrets Docs:** https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **GitHub CLI:** https://cli.github.com/manual/gh_secret

---

**Last Updated:** 2026-02-09
**Pipeline Version:** 1.0.0
