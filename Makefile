.PHONY: install test lint format typecheck run build clean seed docker-up docker-down

install:
	pip install -e ".[dev]"
	cd frontend && npm install

test:
	pytest backend/tests/ -v

test-coverage:
	pytest backend/tests/ --cov --cov-report=html --cov-report=term

lint:
	ruff check backend/
	cd frontend && npm run lint

format:
	ruff format backend/
	cd frontend && npm run format

typecheck:
	mypy backend/app/
	cd frontend && npm run typecheck

run:
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

build:
	cd frontend && npm run build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf frontend/dist/
	rm -rf frontend/build/

seed:
	python scripts/seed_data.py

docker-up:
	docker compose -f infra/docker/docker-compose.yml up -d

docker-down:
	docker compose -f infra/docker/docker-compose.yml down

docker-logs:
	docker compose -f infra/docker/docker-compose.yml logs -f

migrate:
	cd backend && alembic upgrade head

migrate-create:
	cd backend && alembic revision --autogenerate -m "$(name)"

all: install lint typecheck test
