# Forjador v5 - Quick Start Guide

Get up and running with SPEC-01 MVP in 5 minutes.

---

## Prerequisites

- Python 3.11+
- Google Gemini API key
- LangSmith account

---

## Setup (5 Steps)

### 1. Install Dependencies

```bash
cd C:\Users\chicu\forjador-langchain-cloud

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit with your API keys
notepad .env
```

**Required Keys:**
- Get `LANGCHAIN_API_KEY` from [https://smith.langchain.com/settings](https://smith.langchain.com/settings)
- Get `GOOGLE_API_KEY` from [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 3. Validate Configuration

```bash
python -m src.utils.env_validator
```

Expected output: "Environment validation successful!"

### 4. Start Development Server

```bash
langgraph dev
```

Server runs at [http://localhost:8000](http://localhost:8000)

### 5. Test Pipeline

```bash
# Place test document in input queue
cp sample.pdf queue/input/

# Check output directory
ls queue/output/
```

---

## Quick Commands

### Development
```bash
# Activate environment
.\venv\Scripts\activate

# Start dev server
langgraph dev

# Run tests
pytest

# Check code quality
ruff check src/
black --check src/
```

### Docker
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Deployment
```bash
# Login to LangGraph Cloud
langgraph login

# Deploy to production
langgraph deploy --name forjador-v5-spec01-prod

# Check status
langgraph deployments list
```

---

## File Locations

| What | Where |
|------|-------|
| **Input documents** | `queue/input/` |
| **Output results** | `queue/output/` |
| **Configuration** | `.env` |
| **Main agent** | `src/agent.py` |
| **Utilities** | `src/utils/` |
| **Tests** | `tests/` |

---

## Environment Variables

All 11 variables must be set in `.env`:

```bash
# LangSmith (4 variables)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_PROJECT=forjador-v5-spec01

# Gemini (1 variable)
GOOGLE_API_KEY=your_key_here

# Language (1 variable)
PRIMARY_LANGUAGE=pt-BR

# Pipeline (3 variables)
QUALITY_GATE_THRESHOLD=0.85
CHUNK_SIZE=3500
CHUNK_OVERLAP=250

# Directories (2 variables)
INPUT_DIR=./queue/input
OUTPUT_DIR=./queue/output
```

---

## Troubleshooting

### Environment validation fails
```bash
python -m src.utils.env_validator
```

### Module not found
```bash
pip install -e .
```

### LangSmith not working
- Check `LANGCHAIN_API_KEY` is valid
- Verify `LANGCHAIN_TRACING_V2=true`

### Docker issues
```bash
docker-compose down -v
docker-compose up --build -d
```

---

## Common Tasks

### Process a document
1. Copy file to `queue/input/`
2. Check `queue/output/` for results

### View traces
1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Select project: `forjador-v5-spec01`
3. View pipeline traces

### Run tests
```bash
pytest tests/ -v
```

### Check code quality
```bash
ruff check src/
black src/
mypy src/
```

---

## Next Steps

1. **Implement Nodes** - Complete B.1-B.11 stages
2. **Add Parsers** - SOL-04, SOL-05, SOL-08
3. **Create Knowledge** - validation_rules.yaml
4. **Write Tests** - Unit and integration
5. **Deploy** - LangGraph Platform Cloud

---

## Documentation

- **README.md** - Full project overview
- **DEPLOYMENT.md** - Complete deployment guide
- **INFRASTRUCTURE_SUMMARY.md** - Infrastructure details

---

## Support

- Review traces in LangSmith dashboard
- Check logs in `queue/` directories
- See plan: `C:\Users\chicu\.claude\plans\swift-petting-owl.md`

---

**Performance Target:** < 25 seconds end-to-end
**Quality Target:** > 0.85 average score
**Deployment Target:** < 5 minutes on cloud
