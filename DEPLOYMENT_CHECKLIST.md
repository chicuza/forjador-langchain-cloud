# LangGraph Platform Cloud Deployment Checklist

Complete this checklist before your first deployment.

## Pre-Deployment Checklist

### 1. GitHub Secrets Configuration
- [ ] `LANGCHAIN_API_KEY` set in GitHub Secrets
- [ ] `GOOGLE_API_KEY` set in GitHub Secrets
- [ ] `CODECOV_TOKEN` set in GitHub Secrets (optional)
- [ ] Verified secrets are accessible: `gh secret list`

### 2. Repository Setup
- [ ] Code pushed to GitHub repository
- [ ] Repository has `main` and `develop` branches
- [ ] Workflows directory exists: `.github/workflows/`
- [ ] Three workflow files present:
  - [ ] `test.yml`
  - [ ] `quality.yml`
  - [ ] `deploy.yml`

### 3. LangGraph Configuration
- [ ] `langgraph.json` exists in project root
- [ ] Entry point defined: `src.agent:graph`
- [ ] Python version set to `3.11`
- [ ] Dependencies specified in `pyproject.toml`

### 4. Project Structure
- [ ] `src/` directory contains agent code
- [ ] `tests/` directory contains test files
- [ ] `pyproject.toml` has all dependencies listed
- [ ] `.env.example` exists (if applicable)

### 5. Local Testing
- [ ] Tests pass locally: `pytest tests/ -v`
- [ ] Code quality checks pass: `ruff check src/ tests/`
- [ ] Formatting is correct: `black --check src/ tests/`
- [ ] Type checking passes: `mypy src/`

---

## Deployment Process

### Step 1: Test the Quality Workflow
```bash
# Create a test branch
git checkout -b test-quality-workflow
git commit --allow-empty -m "test: quality workflow"
git push origin test-quality-workflow

# Create pull request
gh pr create --title "Test Quality Workflow" --body "Testing linting and formatting"
```

**Expected Result:**
- ✅ Quality workflow runs successfully
- ✅ Ruff, Black, and MyPy checks pass
- ✅ PR shows green checkmark

**If it fails:**
- Fix linting errors: `ruff check src/ tests/ --fix`
- Fix formatting: `black src/ tests/`
- Fix type errors: `mypy src/`
- Push fixes and verify

---

### Step 2: Test the Test Workflow
```bash
# Use the same test branch or create new one
git commit --allow-empty -m "test: test workflow"
git push origin test-quality-workflow
```

**Expected Result:**
- ✅ Test workflow runs successfully
- ✅ All tests pass
- ✅ Coverage report generated

**If it fails:**
- Check test logs in GitHub Actions
- Verify secrets are set correctly
- Run tests locally: `pytest tests/ -v`
- Fix failing tests and push

---

### Step 3: Test the Deploy Workflow (Manual)
```bash
# Go to GitHub Actions tab
# Click "Deploy" workflow
# Click "Run workflow"
# Select "main" branch
# Click "Run workflow" button
```

**Expected Result:**
- ✅ Deploy workflow runs successfully
- ✅ LangGraph CLI installs correctly
- ✅ Deployment completes without errors
- ✅ Graph is accessible in LangGraph Platform Cloud

**If it fails:**
- Check deployment logs in GitHub Actions
- Verify `LANGCHAIN_API_KEY` is correct
- Verify `langgraph.json` is valid
- Check LangGraph Platform Cloud status

---

### Step 4: Test Automatic Deployment
```bash
# Merge test branch to main
git checkout main
git merge test-quality-workflow
git push origin main
```

**Expected Result:**
- ✅ Deploy workflow triggers automatically
- ✅ Deployment completes successfully
- ✅ New version is live on LangGraph Platform Cloud

---

## Post-Deployment Verification

### 1. Verify Deployment in LangGraph Cloud
- [ ] Log in to https://smith.langchain.com/
- [ ] Navigate to "Deployments" section
- [ ] Verify `forjador_v5_pipeline` is deployed
- [ ] Check deployment status is "Running"
- [ ] Note the deployment URL

### 2. Test the Deployed Graph
```bash
# Using LangGraph SDK (Python)
from langchain_smith import LangChainClient

client = LangChainClient(api_key="your_langchain_api_key")

# Test the deployment
result = client.invoke_graph(
    graph_name="forjador_v5_pipeline",
    input={"input_file_path": "test.pdf"}
)
print(result)
```

### 3. Monitor Deployment
- [ ] Check LangSmith traces for invocations
- [ ] Monitor error rates
- [ ] Verify response times are acceptable
- [ ] Check API usage and quotas

---

## Workflow Triggers Reference

| Workflow | Triggers | Purpose |
|----------|----------|---------|
| **Quality** | Push/PR to `main` or `develop` | Code quality checks |
| **Test** | Push/PR to `main` or `develop` | Run all tests |
| **Deploy** | Push to `main` OR manual trigger | Deploy to production |

---

## Common Issues & Solutions

### Issue: "Secret not found" error
**Solution:**
```bash
# Verify secrets are set
gh secret list

# Re-set the secret if missing
gh secret set LANGCHAIN_API_KEY
gh secret set GOOGLE_API_KEY
```

### Issue: Tests fail with authentication error
**Solution:**
- Verify `GOOGLE_API_KEY` is valid
- Check API quota limits
- Ensure Gemini API is enabled

### Issue: Deployment fails with "Graph not found"
**Solution:**
- Verify `langgraph.json` is correct
- Check entry point: `src.agent:graph`
- Ensure `src/agent.py` exports `graph` variable

### Issue: Deployment succeeds but graph doesn't work
**Solution:**
- Check environment variables in LangGraph Cloud console
- Verify all dependencies are listed in `pyproject.toml`
- Review deployment logs for warnings

### Issue: Workflow stuck on "Waiting for deployment"
**Solution:**
- Check LangGraph Platform Cloud status
- Verify API key permissions
- Cancel and re-run workflow

---

## Deployment Best Practices

1. **Always deploy from `main` branch**
   - Use `develop` for testing
   - Merge to `main` only after review

2. **Test locally before pushing**
   ```bash
   pytest tests/ -v
   ruff check src/ tests/
   black --check src/ tests/
   ```

3. **Use pull requests**
   - Quality and Test workflows run automatically
   - Require passing checks before merge

4. **Monitor deployments**
   - Check Actions tab after each deployment
   - Review LangSmith traces
   - Monitor error rates

5. **Version your deployments**
   - Use semantic versioning
   - Tag releases: `git tag v1.0.0`
   - Document changes in CHANGELOG.md

---

## Rollback Procedure

If a deployment causes issues:

### Method 1: Revert and Redeploy
```bash
# Revert the problematic commit
git revert HEAD
git push origin main

# Deploy workflow will automatically redeploy previous version
```

### Method 2: Manual Rollback
```bash
# Find the last working commit
git log --oneline

# Reset to that commit
git reset --hard <commit-hash>
git push origin main --force

# Note: Force push should be used with caution
```

### Method 3: LangGraph Cloud Console
1. Log in to LangGraph Platform Cloud
2. Navigate to Deployments
3. Select previous deployment version
4. Click "Rollback" or "Deploy This Version"

---

## Monitoring & Observability

### Key Metrics to Monitor

1. **Deployment Success Rate**
   - Target: >95% successful deployments
   - Check: GitHub Actions history

2. **Test Pass Rate**
   - Target: 100% passing tests
   - Check: GitHub Actions test results

3. **Code Quality Score**
   - Target: 0 linting errors
   - Check: Ruff reports in Actions

4. **Deployment Time**
   - Target: <5 minutes
   - Check: Deploy workflow duration

5. **API Response Time**
   - Target: <2 seconds (depends on document size)
   - Check: LangSmith traces

### Setting Up Alerts

Add to `.github/workflows/deploy.yml` for notifications:
```yaml
- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Deployment failed for forjador-v5"
      }
```

---

## Next Steps After First Deployment

1. [ ] Add deployment status badge to README
2. [ ] Set up staging environment (deploy from `develop`)
3. [ ] Configure environment protection rules
4. [ ] Add deployment notifications (Slack/Discord)
5. [ ] Set up automated rollback on failure
6. [ ] Create deployment dashboard
7. [ ] Document API endpoints
8. [ ] Set up performance monitoring

---

## Support Resources

- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/cloud/
- **LangSmith Console:** https://smith.langchain.com/
- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Project Repository:** Check README.md for project-specific docs

---

## Deployment Timeline

**Estimated time for first deployment:** 30-45 minutes

- Configure secrets: 10 minutes
- Test quality workflow: 5 minutes
- Test test workflow: 5 minutes
- Test deploy workflow: 10 minutes
- Verify deployment: 5 minutes
- Post-deployment testing: 10 minutes

---

**Checklist Version:** 1.0.0
**Last Updated:** 2026-02-09
**Next Review:** After first production deployment
