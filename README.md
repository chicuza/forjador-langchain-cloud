# Forjador v5 - Industrial Fastener SKU Identification Pipeline

## SPEC-01 MVP - File-Based Extraction with LangGraph

**Version:** 0.1.0
**Status:** Alpha
**Target:** Production-ready MVP
**Performance:** < 25 seconds end-to-end

---

## Overview

Forjador v5 is an AI-powered pipeline for extracting structured SKU data from industrial fastener purchase order documents (PDF, Excel, CSV, images). Built with LangGraph and optimized for Brazilian Portuguese (pt-BR) content.

### Key Features (SPEC-01)

- **7-Stage Pipeline** (B.1-B.7, B.11) with LangGraph StateGraph
- **3 Document Parsers** (Docling 2.0, Gemini 2.5 Flash Vision, Pandas/CSV)
- **Hybrid Validation** (YAML business rules + Pydantic schemas)
- **Quality Gate** (0.85 threshold by default)
- **File-Based** (No database required)
- **LangSmith Observability** (Full tracing and monitoring)
- **Cloud-Ready** (LangGraph Platform Cloud v0.2+ compatible)

### What's Not Included (SPEC-02/03)

- Database persistence
- HITL (Human-in-the-Loop) workflow
- Entity Resolution (ER) ensemble
- GraphQL API layer
- Advanced parsing solutions (5 additional parsers)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Google Gemini API key
- LangSmith account (for tracing)

### Installation

```bash
# 1. Clone repository
cd C:\Users\chicu\forjador-langchain-cloud

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -e .

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Verify setup
python -m src.utils.env_validator
```

### Running Locally

```bash
# Start LangGraph dev server
langgraph dev

# Server runs at http://localhost:8000
# GraphiQL interface at http://localhost:8000/
```

---

## Project Structure

```
forjador-langchain-cloud/
├── src/
│   ├── agent.py                    # Main LangGraph StateGraph
│   ├── state/                      # State definitions
│   ├── nodes/                      # Pipeline nodes (B.1-B.11)
│   ├── parsers/                    # Document parsers (SOL-04, 05, 08)
│   ├── chains/                     # LCEL chains
│   ├── knowledge/                  # Domain knowledge assets
│   └── utils/                      # Utilities (logging, validation)
├── tests/                          # Pytest test suite
├── knowledge/                      # YAML validation rules
├── queue/                          # File queue directories
│   ├── input/                      # Documents to process
│   ├── output/                     # Generated outputs
│   ├── processing/                 # Files being processed
│   ├── error/                      # Failed files
│   └── archive/                    # Successfully processed
├── pyproject.toml                  # Python dependencies
├── langgraph.json                  # LangGraph Platform config
├── .env.example                    # Environment template
├── Dockerfile                      # Container image
├── docker-compose.yml              # Local deployment
└── README.md                       # This file
```

---

## Environment Variables

SPEC-01 requires **11 environment variables**. See [.env.example](.env.example) for details.

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing | `true` |
| `LANGCHAIN_ENDPOINT` | LangSmith API endpoint | `https://api.smith.langchain.com` |
| `LANGCHAIN_API_KEY` | LangSmith API key | `ls__1234...` |
| `LANGCHAIN_PROJECT` | LangSmith project name | `forjador-v5-spec01` |
| `GOOGLE_API_KEY` | Gemini API key | `AIza...` |
| `PRIMARY_LANGUAGE` | Primary language | `pt-BR` |
| `QUALITY_GATE_THRESHOLD` | Quality threshold (0.0-1.0) | `0.85` |
| `CHUNK_SIZE` | Chunk size (characters) | `3500` |
| `CHUNK_OVERLAP` | Chunk overlap (characters) | `250` |
| `INPUT_DIR` | Input directory | `./queue/input` |
| `OUTPUT_DIR` | Output directory | `./queue/output` |

---

## Pipeline Stages

### B.1: File Validation & Metadata Enrichment
- Validates file format (PDF, Excel, CSV, images)
- Extracts metadata (size, encoding, line count)
- Status: `valid`, `invalid`, `pending`

### B.2: Complexity Classification
- Classifies document into 11 complexity tiers
- Routes to appropriate parser (SOL-04, SOL-05, SOL-08)

### B.3: Document Parsing
- **SOL-04:** Docling 2.0 (structured documents)
- **SOL-05:** Gemini 2.5 Flash Vision (images, complex PDFs)
- **SOL-08:** Pandas/CSV (tabular data)

### B.4: Quality Gate
- Calculates quality score (0.0-1.0)
- Flags documents below threshold for review

### B.5: Intelligent Chunking
- Chunks large documents (3500 chars, 250 overlap)
- Preserves semantic boundaries

### B.6: Structured Extraction
- Extracts SKU data using Pydantic schemas
- 11 fastener types, 57 subtypes supported
- Self-correction enabled

### B.7: Hybrid Validation
- YAML business rules (material compatibility, coating rules)
- Pydantic schema validation

### B.11: Output Generation
- JSON output (structured data)
- CSV output (tabular format)
- Audit trail with timestamps

---

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide covering:
- Local development setup
- Docker containerization
- LangGraph Platform Cloud deployment
- Environment configuration
- Monitoring and troubleshooting

---

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_file_validation.py -v

# Run integration tests (requires API keys)
pytest tests/test_integration_spec01.py -v -m integration
```

---

## Supported Document Types

| Format | Extension | Parser | Notes |
|--------|-----------|--------|-------|
| PDF | `.pdf` | Docling, Gemini Vision | Text and image-based |
| Excel | `.xlsx` | Pandas | Multi-sheet support |
| CSV | `.csv` | Pandas | UTF-8 encoding |
| Images | `.png`, `.jpg` | Gemini Vision | OCR-based extraction |

---

## Performance Targets

- **End-to-End:** < 25 seconds (typical document)
- **Quality Gate:** 85% threshold (configurable)
- **Success Rate:** > 95% (valid documents)
- **Deployment Time:** < 5 minutes (LangGraph Cloud)

---

## Monitoring

### LangSmith Dashboard

Access at [https://smith.langchain.com/](https://smith.langchain.com/)

**Key Metrics:**
- Pipeline execution time
- Quality scores
- Parser selection distribution
- Error rates
- Validation failures

### Custom Metadata

Each run includes:
- `spec_version`: SPEC-01
- `stage`: Current pipeline stage
- `timestamp`: ISO 8601 format
- `project`: Project name

---

## Troubleshooting

### Common Issues

**Environment validation fails:**
```bash
# Verify all variables are set
python -m src.utils.env_validator
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -e .
```

**LangSmith tracing not working:**
- Check `LANGCHAIN_API_KEY` is valid
- Verify `LANGCHAIN_TRACING_V2=true`
- Check network connectivity to api.smith.langchain.com

**File parsing fails:**
- Check file format is supported
- Verify file is not corrupted
- Review logs in `./logs/`

---

## Development Workflow

1. **Create branch** for new feature
2. **Implement node** in `src/nodes/`
3. **Add tests** in `tests/`
4. **Run tests** with `pytest`
5. **Test locally** with `langgraph dev`
6. **Submit PR** with test coverage

---

## License

Proprietary - Internal Use Only

---

## Support

For issues and questions:
- Review [DEPLOYMENT.md](DEPLOYMENT.md)
- Check LangSmith traces for errors
- Review plan at `C:\Users\chicu\.claude\plans\swift-petting-owl.md`

---

## Roadmap

### SPEC-02 (Advanced Features) - +16 days
- Database persistence (PostgreSQL)
- HITL workflow
- Entity Resolution ensemble
- 3-layer cascading validation
- +5 parsing solutions

### SPEC-03 (GraphQL API) - +16 days
- GraphQL API layer
- WebSocket subscriptions
- Redis caching
- Type-safe client generation

---

**Built with LangGraph Platform Cloud v0.2+**
