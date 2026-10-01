# Movie Mood Finder

Anonymous movie discovery & logging platform (FastAPI + PostgreSQL + Jinja2).
The full README (features, deployment, TMDB import) is completed in the final phase.

## Quick start (Phases 1-2)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # edit DATABASE_URL
alembic upgrade head
uvicorn app.main:app --reload   # http://localhost:8000  /health  /docs
pytest
```

PostgreSQL via Docker:

```bash
docker run -d --name pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=moviefinder -p 5432:5432 postgres:16
```
