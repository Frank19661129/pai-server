# Claudine Server v1

**Clean Architecture rebuild of Claudine backend with Identity-First design and Event-Driven architecture.**

## Overview

Claudine Server v1 is a production-ready rebuild of the Claudine voice assistant backend, implementing:

- **Clean Architecture** with clear separation of concerns
- **Identity-First Design** with multi-user JWT authentication
- **Event-Driven Architecture** for reliable command processing
- **FastAPI** for high-performance async API endpoints
- **PostgreSQL** with Alembic migrations
- **Dependency Injection** via FastAPI's Depends()

## Architecture

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (API Routes, Request/Response)         │
├─────────────────────────────────────────┤
│         Application Layer               │
│  (Use Cases, Business Orchestration)    │
├─────────────────────────────────────────┤
│         Domain Layer                    │
│  (Business Entities, Value Objects)     │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │
│  (Database, External Services)          │
└─────────────────────────────────────────┘
```

## Project Structure

```
claudine-server-v1/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── core/                   # Core configuration
│   │   ├── config.py           # Settings & environment
│   │   └── dependencies.py     # DI providers
│   ├── domain/                 # Business entities
│   │   ├── entities/
│   │   └── value_objects/
│   ├── application/            # Use cases
│   │   └── use_cases/
│   ├── infrastructure/         # External integrations
│   │   ├── database/
│   │   ├── repositories/
│   │   └── services/
│   └── presentation/           # API layer
│       └── routers/
├── alembic/                    # Database migrations
├── tests/                      # Test suite
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Prerequisites

- Docker & Docker Compose
- PostgreSQL 15 (running on port 5432)
- Python 3.11+ (for local development)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Frank19661129/Claudine-Server-v1.git
cd claudine-server-v1
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Server

```bash
docker-compose up -d
```

### 4. Verify Health

```bash
# Basic health check
curl http://localhost:8002/api/v1/health

# Database health check
curl http://localhost:8002/api/v1/health/db
```

### 5. Access API Documentation

- **Swagger UI:** http://localhost:8002/docs
- **ReDoc:** http://localhost:8002/redoc

## Development

### Local Development (without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Database Migrations

```bash
# Create new migration
alembic revision -m "description"

# Auto-generate from models
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Running Tests

```bash
pytest
pytest --cov=app  # With coverage
```

## API Endpoints

### Health

- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/db` - Database connectivity check

### (More endpoints to be added as features are implemented)

## Port Configuration

- **v1 Development:** Port 8002 (external) → 8000 (internal)
- **v0 Production:** Port 8001 (kept separate during transition)

After v1 is stable, v1 will move to port 8001 and v0 will be archived.

## Database

- **Database Name:** `claudine_v1`
- **PostgreSQL Version:** 15
- **Migrations:** Alembic
- **Connection:** PostgreSQL running on host (port 5432)

The database `claudine_v1` is automatically created by the `db-setup` service on first run.

## Technology Stack

- **Framework:** FastAPI 0.109+
- **Language:** Python 3.11+
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0+
- **Migrations:** Alembic
- **Testing:** pytest
- **Containerization:** Docker & Docker Compose

## Related Repositories

- **Documentation:** [Claudine](https://github.com/Frank19661129/Claudine)
- **Server v0 (Legacy):** [Claudine-Server](https://github.com/Frank19661129/Claudine-Server)
- **Client v0:** [Claudine-Voice](https://github.com/Frank19661129/Claudine-Voice)

## Contributing

This is a personal project rebuild. See [DECISIONS.md](../Claudine/DECISIONS.md) in the main documentation repository for architectural decisions.

## License

Private project - All rights reserved

## Status

🚧 **Active Development** - Week 1-2: Foundation Phase

- [x] Clean Architecture skeleton
- [x] FastAPI setup with health endpoints
- [x] Alembic migrations
- [x] Docker configuration
- [ ] Identity/Auth service
- [ ] Event Bus implementation
- [ ] Calendar integration
- [ ] Testing infrastructure

---

**Last Updated:** 2025-11-14
