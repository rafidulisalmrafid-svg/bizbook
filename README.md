# BizBook - Multi-Tenant AI-Enabled Enterprise SaaS

BizBook centralizes institutional knowledge, compliance documents, digital assets, team skills, project evidence, and powers tender/proposal generation with zero hallucination.

## Tech Stack
- **Backend**: FastAPI (Python 3.11+), Pydantic v2, SQLAlchemy 2.0, Alembic, Celery, Redis
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React
- **Storage**: S3-compatible private object storage (MinIO) with signed URLs
- **Database**: PostgreSQL 16
- **AI Adapters**: OpenAI, Anthropic, and Mock AI Provider

## Quick Start

### 1. Prerequisites
- Node.js 18+
- Python 3.11+ (or `uv`)
- Docker & Docker Compose (optional for standalone dependencies)

### 2. Infrastructure Services (Docker)
```bash
docker-compose up -d
```

### 3. Backend Setup
```bash
cd backend
uv venv
uv pip install -e .
# Run migrations
alembic upgrade head
# Run dev server
uv run uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 5. Running Tests
```bash
cd backend
uv run pytest -v
```
