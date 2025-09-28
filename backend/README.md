# AutoForgeNexus Backend

Python 3.13 + FastAPI backend for AI prompt optimization platform.

## Quick Start

```bash
# Local development
python3.13 -m venv venv
source venv/bin/activate
pip install -e .[dev]
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Docker development
docker compose -f ../docker-compose.dev.yml up backend
```

## Architecture

- **Framework**: FastAPI 0.116.1
- **Python**: 3.13
- **Database**: Turso (libSQL) / SQLite (dev)
- **Cache**: Redis 7.4.1
- **Architecture**: Clean Architecture with DDD

## API Documentation

- Development: http://localhost:8000/docs
- API Base: http://localhost:8000/api/v1

## Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=html
```