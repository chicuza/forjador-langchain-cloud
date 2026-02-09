# Forjador v5 - SPEC-01 Deployment Guide

Complete deployment instructions for local development, Docker, and LangGraph Platform Cloud.

---

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [LangGraph Platform Cloud Deployment](#langgraph-platform-cloud-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Monitoring & Observability](#monitoring--observability)
6. [Troubleshooting](#troubleshooting)
7. [Performance Optimization](#performance-optimization)

---

## Local Development Setup

### Prerequisites

- **Python:** 3.11 or higher
- **pip:** Latest version
- **Git:** For version control
- **Google Gemini API Key:** Get from [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- **LangSmith Account:** Sign up at [https://smith.langchain.com/](https://smith.langchain.com/)

### Step 1: Clone and Navigate

```bash
cd C:\Users\chicu\forjador-langchain-cloud
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install project dependencies
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
```

### Step 4: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit with your API keys
notepad .env  # Windows
# nano .env   # Linux/Mac
```

**Required API Keys:**
- `LANGCHAIN_API_KEY`: Get from [LangSmith Settings](https://smith.langchain.com/settings)
- `GOOGLE_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Step 5: Validate Configuration

```bash
# Run environment validator
python -m src.utils.env_validator

# Expected output: "Environment validation successful! All 11 SPEC-01 variables configured."
```

### Step 6: Start Development Server

```bash
# Start LangGraph dev server
langgraph dev

# Server starts at http://localhost:8000
# GraphiQL interface at http://localhost:8000/
```

### Step 7: Test the Pipeline

```bash
# Place a test document in queue/input/
cp sample_document.pdf queue/input/

# Monitor LangSmith dashboard for traces
# Output appears in queue/output/
```

---

## Docker Deployment

### Prerequisites

- **Docker Desktop:** Version 20.10+ (Windows/Mac)
- **Docker Engine:** Version 20.10+ (Linux)
- **Docker Compose:** Version 2.0+

### Step 1: Build Docker Image

```bash
cd C:\Users\chicu\forjador-langchain-cloud

# Build image
docker build -t forjador-v5:spec01 .

# Verify build
docker images | grep forjador-v5
```

### Step 2: Configure Environment

```bash
# Ensure .env file exists with all variables
# Docker Compose will use it automatically
cp .env.example .env
# Edit .env with your API keys
```

### Step 3: Start with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f forjador-pipeline

# Check status
docker-compose ps
```

### Step 4: Health Check

```bash
# Check container health
docker-compose ps

# Test Python import
docker-compose exec forjador-pipeline python -c "import sys; print('OK')"

# View environment validation
docker-compose logs forjador-pipeline | grep "Environment validation"
```

### Step 5: Process Documents

```bash
# Copy document to input directory
cp sample_document.pdf queue/input/

# Monitor logs
docker-compose logs -f forjador-pipeline

# Check output
ls -la queue/output/
```

### Stop Services

```bash
docker-compose down

# Remove volumes (WARNING: deletes queue data)
docker-compose down -v
```

---

## LangGraph Platform Cloud Deployment

### Prerequisites

- **LangSmith Account:** With API access
- **LangGraph CLI:** Install with `pip install langgraph-cli`
- **API Keys:** Configured in `.env`

### Step 1: Install LangGraph CLI

```bash
# Install CLI globally
pip install langgraph-cli

# Verify installation
langgraph --version
```

### Step 2: Authenticate

```bash
# Login to LangGraph Cloud
langgraph login

# Follow prompts to authenticate with LangSmith
# Your API key will be stored in ~/.langchain/config.yml
```

### Step 3: Validate Configuration

```bash
# Ensure langgraph.json is present
cat langgraph.json

# Ensure all dependencies are listed in pyproject.toml
cat pyproject.toml
```

### Step 4: Deploy to Cloud

```bash
# Deploy to production
langgraph deploy --name forjador-v5-spec01-prod

# Expected output:
# Deploying forjador-v5-spec01-prod...
# Deployment successful!
# URL: https://forjador-v5-spec01-prod.langchain.app
```

### Step 5: Verify Deployment

```bash
# List deployments
langgraph deployments list

# Get deployment details
langgraph deployments get forjador-v5-spec01-prod

# Test health endpoint
curl https://forjador-v5-spec01-prod.langchain.app/health
```

### Step 6: Test API Endpoint

```bash
# Test with curl
curl -X POST https://forjador-v5-spec01-prod.langchain.app/runs \
  -H "Authorization: Bearer $LANGCHAIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "input_file_path": "sample.pdf"
    }
  }'

# Expected response: Run ID and status
```

### Step 7: Monitor Traces

1. Open [LangSmith Dashboard](https://smith.langchain.com/)
2. Navigate to your project: `forjador-v5-spec01`
3. View traces for each pipeline run
4. Analyze performance metrics

### Update Deployment

```bash
# Make code changes
# Commit changes to git (optional)

# Redeploy
langgraph deploy --name forjador-v5-spec01-prod

# Cloud deployment automatically pulls latest code
```

### Rollback Deployment

```bash
# List deployment history
langgraph deployments list --name forjador-v5-spec01-prod

# Rollback to previous version
langgraph deployments rollback forjador-v5-spec01-prod --version <version_id>
```

---

## Environment Configuration

### Environment Files

**Development:** `.env` (local)
**Production:** Set in LangGraph Cloud dashboard

### Configuration by Environment

| Variable | Development | Production | Notes |
|----------|-------------|------------|-------|
| `LANGCHAIN_TRACING_V2` | `true` | `true` | Always enable |
| `LANGCHAIN_PROJECT` | `forjador-v5-dev` | `forjador-v5-prod` | Separate projects |
| `QUALITY_GATE_THRESHOLD` | `0.80` | `0.85` | Higher in prod |
| `INPUT_DIR` | `./queue/input` | `/app/queue/input` | Absolute in Docker |
| `OUTPUT_DIR` | `./queue/output` | `/app/queue/output` | Absolute in Docker |

### Setting Cloud Environment Variables

**Option 1: LangSmith Dashboard**
1. Go to [LangSmith Settings](https://smith.langchain.com/settings)
2. Navigate to "Deployments"
3. Select your deployment
4. Add/edit environment variables
5. Restart deployment

**Option 2: CLI**
```bash
langgraph env set forjador-v5-spec01-prod QUALITY_GATE_THRESHOLD=0.85
langgraph deployments restart forjador-v5-spec01-prod
```

---

## Monitoring & Observability

### LangSmith Dashboard

**Access:** [https://smith.langchain.com/](https://smith.langchain.com/)

**Key Metrics:**
- **Execution Time:** < 25 seconds target
- **Quality Scores:** Average > 0.85
- **Error Rate:** < 5%
- **Parser Distribution:** SOL-04, SOL-05, SOL-08 usage

### Custom Metadata

Each trace includes:
```json
{
  "spec_version": "SPEC-01",
  "stage": "B.1-B.11",
  "timestamp": "2026-02-09T00:00:00Z",
  "project": "forjador-v5-spec01"
}
```

### Setting Up Alerts

1. Open LangSmith Dashboard
2. Go to "Monitoring" → "Alerts"
3. Create alert rules:
   - **Latency Alert:** Execution time > 30s
   - **Error Alert:** Error rate > 10%
   - **Quality Alert:** Quality score < 0.80

### Log Aggregation

**Local Development:**
```bash
# View logs
tail -f logs/forjador_v5.log

# Filter by stage
grep "B.6" logs/forjador_v5.log
```

**Docker:**
```bash
# View container logs
docker-compose logs -f forjador-pipeline

# Save logs to file
docker-compose logs forjador-pipeline > forjador.log
```

**Cloud:**
- View logs in LangSmith Dashboard
- Export traces to JSON for analysis

---

## Troubleshooting

### Common Issues

#### 1. Environment Validation Fails

**Symptom:**
```
ERROR: Missing required environment variables:
  - GOOGLE_API_KEY
```

**Solution:**
```bash
# Verify .env file exists
cat .env

# Ensure all 11 variables are set
python -m src.utils.env_validator
```

#### 2. Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'langgraph'
```

**Solution:**
```bash
# Reinstall dependencies
pip install -e .

# Verify installation
pip list | grep langgraph
```

#### 3. LangSmith Tracing Not Working

**Symptom:**
No traces appear in LangSmith dashboard

**Solution:**
```bash
# Check environment variables
echo $LANGCHAIN_API_KEY
echo $LANGCHAIN_TRACING_V2

# Test LangSmith connection
python -c "from src.utils import langsmith_config; print(langsmith_config.validate())"

# Verify network connectivity
curl https://api.smith.langchain.com/health
```

#### 4. Docker Build Fails

**Symptom:**
```
ERROR: failed to solve: process "/bin/sh -c pip install --no-cache-dir ." did not complete successfully
```

**Solution:**
```bash
# Check Dockerfile syntax
docker build --no-cache -t forjador-v5:spec01 .

# Verify pyproject.toml is valid
python -m pip install --dry-run .
```

#### 5. Deployment Timeout

**Symptom:**
```
langgraph deploy: Timeout waiting for deployment
```

**Solution:**
```bash
# Check langgraph.json is valid
cat langgraph.json | python -m json.tool

# Verify all dependencies are installable
pip install -e . --dry-run

# Try again with verbose output
langgraph deploy --name forjador-v5-spec01-prod --verbose
```

### Debug Mode

Enable debug logging:
```bash
# Local
export LOG_LEVEL=DEBUG
python -m src.agent

# Docker
docker-compose exec forjador-pipeline sh -c "export LOG_LEVEL=DEBUG && python -m src.agent"
```

### Getting Help

1. **Check Logs:** Review application and Docker logs
2. **LangSmith Traces:** Analyze traces for errors
3. **Documentation:** Review README.md and plan file
4. **Test Locally:** Reproduce issue in development environment

---

## Performance Optimization

### Target Metrics (SPEC-01)

- **End-to-End Latency:** < 25 seconds
- **Quality Score:** > 0.85 average
- **Success Rate:** > 95%
- **Deployment Time:** < 5 minutes

### Optimization Tips

#### 1. Chunk Size Tuning

```bash
# Smaller chunks (faster, lower accuracy)
CHUNK_SIZE=2000
CHUNK_OVERLAP=150

# Larger chunks (slower, higher accuracy)
CHUNK_SIZE=5000
CHUNK_OVERLAP=350
```

#### 2. Parser Selection

- **SOL-08 (Pandas):** Fastest for CSV/Excel
- **SOL-04 (Docling):** Best for structured PDFs
- **SOL-05 (Gemini Vision):** For images and complex layouts

#### 3. Caching (SPEC-02)

Not available in SPEC-01. Upgrade to SPEC-02 for Redis caching.

#### 4. Parallel Processing

LangGraph automatically parallelizes where possible using Send API.

### Monitoring Performance

```bash
# Check LangSmith dashboard for:
# - Average execution time per stage
# - Parser selection distribution
# - Quality score trends
# - Error patterns

# Export traces for analysis
# Use LangSmith API to download trace data
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All 11 environment variables configured
- [ ] API keys validated and working
- [ ] Dependencies installed and tested
- [ ] Queue directories created
- [ ] LangSmith project created
- [ ] Test documents prepared

### Development

- [ ] Local server starts without errors
- [ ] Environment validation passes
- [ ] Sample document processes successfully
- [ ] Outputs generated (JSON + CSV)
- [ ] LangSmith traces visible

### Docker

- [ ] Docker image builds successfully
- [ ] Container starts without errors
- [ ] Health check passes
- [ ] Volume mounts working
- [ ] Logs visible

### Cloud (LangGraph Platform)

- [ ] LangGraph CLI authenticated
- [ ] Deployment succeeds
- [ ] Health endpoint responds
- [ ] API endpoint tested
- [ ] Traces visible in LangSmith
- [ ] Performance meets targets (< 25s)

### Post-Deployment

- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] Team trained on deployment
- [ ] Rollback procedure tested
- [ ] Backup strategy in place

---

## Security Considerations

### API Keys

- **Never commit** `.env` to version control
- **Rotate keys** regularly (quarterly)
- **Use separate keys** for dev/prod
- **Restrict key permissions** to minimum required

### Docker Security

```bash
# Run as non-root user (add to Dockerfile)
USER 1000:1000

# Scan image for vulnerabilities
docker scan forjador-v5:spec01
```

### Network Security

- Use HTTPS for all API calls
- Restrict access to LangGraph Cloud endpoints
- Use VPN for production deployments (if applicable)

---

## Backup and Recovery

### File Queue Backup

```bash
# Backup queue directories
tar -czf queue_backup_$(date +%Y%m%d).tar.gz queue/

# Restore from backup
tar -xzf queue_backup_20260209.tar.gz
```

### Configuration Backup

```bash
# Backup configuration
cp .env .env.backup
cp langgraph.json langgraph.json.backup
```

### Recovery Procedure

1. Stop services
2. Restore configuration from backup
3. Restore queue data from backup
4. Restart services
5. Verify functionality

---

## Next Steps

### After Successful Deployment

1. **Implement Pipeline Nodes:** Complete B.1-B.11 stages
2. **Add Knowledge Assets:** Create validation_rules.yaml
3. **Test with Real Data:** Process actual purchase orders
4. **Monitor Performance:** Track metrics in LangSmith
5. **Iterate:** Optimize based on performance data

### Upgrading to SPEC-02

See plan file for SPEC-02 requirements:
- Add PostgreSQL database
- Implement HITL workflow
- Add 5 more parsers
- Enable Entity Resolution ensemble

---

**Deployment should complete in < 5 minutes on LangGraph Platform Cloud**

For issues, consult plan at: `C:\Users\chicu\.claude\plans\swift-petting-owl.md`
