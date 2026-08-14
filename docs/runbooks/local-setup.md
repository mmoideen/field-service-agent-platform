# Local Development Setup

This runbook guides you through setting up the Field Service Agent Platform for local development.

## Prerequisites

Install the following on your development machine:

- **Python 3.12 or higher**: `python --version`
- **Node.js 20 or higher**: `node --version`
- **Docker Desktop** (recommended) or PostgreSQL 16 and Redis 7
- **Git**: `git --version`

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd field-service-agent-platform
```

## Step 2: Start Databases

### Option A: Using Docker (Recommended)

```bash
make docker-up
```

This starts PostgreSQL on port 5432 and Redis on port 6379.

To stop databases:
```bash
make docker-down
```

To view logs:
```bash
make docker-logs
```

### Option B: Native Installation

**PostgreSQL:**
```bash
# macOS with Homebrew
brew install postgresql@16
brew services start postgresql@16

# Create database
createdb fieldservice
```

**Redis:**
```bash
# macOS with Homebrew
brew install redis
brew services start redis
```

## Step 3: Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` if using custom database credentials or ports:

```bash
DATABASE_URL=postgresql://fieldservice:fieldservice@localhost:5432/fieldservice
REDIS_URL=redis://localhost:6379/0
```

## Step 4: Install Backend Dependencies

```bash
pip install -e ".[dev]"
```

This installs FastAPI, SQLAlchemy, pytest, and all development tools.

Verify installation:
```bash
python -c "import fastapi; print(fastapi.__version__)"
```

## Step 5: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

Verify installation:
```bash
cd frontend && npm run typecheck && cd ..
```

## Step 6: Initialize Database Schema

The seed script creates tables automatically, but you can create them manually:

```bash
python -c "
import asyncio
from backend.app.core.database import engine, Base
asyncio.run(engine.begin().run_sync(Base.metadata.create_all))
"
```

## Step 7: Seed Demo Data

```bash
make seed
```

This creates:
- 3 technicians with different skills
- Sample service tickets
- Warranty claims
- Parts inventory

## Step 8: Start Backend Server

In terminal 1:

```bash
make run
```

The API server starts on http://localhost:8000

Verify health:
```bash
curl http://localhost:8000/health
```

Access API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Step 9: Start Frontend Development Server

In terminal 2:

```bash
make run-frontend
```

The dashboard starts on http://localhost:5173

Open http://localhost:5173 in your browser.

## Step 10: Verify Setup

Run the test suite:

```bash
make test
```

All tests should pass.

Run linting:

```bash
make lint
```

No errors should appear.

## Common Issues

### Port Already in Use

**Problem:** Backend fails to start with "Address already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Database Connection Error

**Problem:** Backend logs "could not connect to server"

**Solution:**
1. Verify PostgreSQL is running: `docker ps` or `brew services list`
2. Check DATABASE_URL in `.env` matches your setup
3. Test connection: `psql postgresql://fieldservice:fieldservice@localhost:5432/fieldservice`

### Redis Connection Error

**Problem:** Backend logs "Error connecting to Redis"

**Solution:**
1. Verify Redis is running: `docker ps` or `brew services list`
2. Test connection: `redis-cli ping` (should return "PONG")

### Frontend Build Errors

**Problem:** `npm install` fails with dependency errors

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Python Import Errors

**Problem:** `ImportError: cannot import name 'X'`

**Solution:**
1. Ensure you installed with editable mode: `pip install -e ".[dev]"`
2. Verify PYTHONPATH includes project root
3. Restart Python interpreter

## Development Workflow

### Making Changes

1. **Backend changes**: Edit files in `backend/`. Uvicorn auto-reloads on save.
2. **Frontend changes**: Edit files in `frontend/src/`. Vite hot-reloads instantly.
3. **Database schema changes**: Modify models in `backend/app/models/`, then run migrations.

### Running Tests

```bash
# Backend tests with coverage
make test-coverage

# Single test file
pytest backend/tests/unit/test_dispatch_optimizer.py -v

# Frontend tests
cd frontend && npm test
```

### Code Quality

Before committing:

```bash
# Format code
make format

# Check linting
make lint

# Type checking
make typecheck

# Run all quality gates
make all
```

### Resetting Demo Data

To start fresh:

```bash
# Drop and recreate database
make docker-down
make docker-up

# Reseed data
make seed
```

## IDE Setup

### VS Code

Install recommended extensions:
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense

Add to `.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true
}
```

### PyCharm

1. Mark `backend` as Sources Root
2. Enable mypy integration in Preferences > Tools > Python Integrated Tools
3. Set code style to match ruff configuration

## Next Steps

- Read [Architecture Decision Records](../adr/) to understand design decisions
- Explore API at http://localhost:8000/docs
- Review agent implementations in `backend/app/agents/`
- Check frontend components in `frontend/src/components/`

## Getting Help

If you encounter issues not covered here:
1. Check GitHub Issues for similar problems
2. Review application logs in terminal output
3. Open a new issue with error details and steps to reproduce
