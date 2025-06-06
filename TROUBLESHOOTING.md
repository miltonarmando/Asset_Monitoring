# Troubleshooting & Best Practices

This guide summarizes the most common issues, their root causes, and proven solutions for the Asset Monitoring project. Use this as a reference during setup, rebuilds, or debugging.

## 1. Environment & Configuration

- **Always use the `.env` file** for all sensitive and environment-specific config (DB URI, Redis, SNMP, etc.).
- **Consistency is critical:** Ensure the same env vars are loaded by Docker Compose, the FastAPI app, and Alembic migrations.
- **Verify DB URI:** The app and Alembic must use the same `SQLALCHEMY_DATABASE_URI` (from Pydantic `Settings`).
- **Check your Docker Compose file:**
  - `POSTGRES_SERVER` should be `db` (the service name), not `localhost`.
  - Ports must not conflict with other local services.

## 2. Database Migrations & Initialization

- **Apply Alembic migrations** before starting the app:
  ```bash
  docker-compose exec app alembic upgrade head
  ```
- If you see `relation "devices" does not exist`, it means migrations were not applied or the DB URI is wrong.
- **If migrations fail:**
  - Check logs for DB connection errors (wrong host, port, or credentials).
  - Ensure the DB container is healthy and accepting connections.
- **To reset from scratch:**
  ```bash
  docker-compose down -v
  docker-compose up --build
  docker-compose exec app alembic upgrade head
  ```

## 3. API Usage & Testing

- **Trailing slashes matter:** Always use `/api/v1/devices/` (not `/api/v1/devices`) to avoid 307 redirects.
- **Common API errors:**
  - `400`: Duplicate device (IP or hostname exists)
  - `404`: Not found (wrong ID)
  - `422`: Missing required fields in request JSON
  - `500`: Usually DB/config issues
- **Clean up test data:** Delete test devices before re-running scripts to avoid conflicts.

## 4. Docker & Service Health

- **All services must be running:**
  - `app` (FastAPI)
  - `db` (Postgres)
  - `redis` (for caching and Celery)
- **Check logs:**
  ```bash
  docker-compose logs app
  docker-compose logs db
  ```
- **If DB connection refused:**
  - Verify `POSTGRES_SERVER` is `db` in `.env` and Compose.
  - Make sure the DB container is healthy.

## 5. Alembic & Environment Variables

- **Alembic must read the same `.env` as the app.**
- If you change `.env`, rebuild the containers or restart Alembic/app.

## 6. Project Structure & Documentation

- **README.md**: Entry point, quick start, and references to all docs.
- **docs/context.md**: Project background, objectives, and tech stack.
- **docs/execution_plan.md**: Development phases, deliverables, and roadmap.
- **docs/requirements.md**: All system and dependency requirements.
- **alembic/README**: Alembic migration usage and troubleshooting.

## 7. FAQ

- **Q: Why do I get `relation does not exist`?**
  - A: Migrations not applied or DB URI mismatch. Check `.env`, run Alembic.
- **Q: Why does the app connect to `localhost` instead of `db`?**
  - A: `.env` or Compose misconfigured. Fix `POSTGRES_SERVER`.
- **Q: Why do I get a 307 redirect?**
  - A: Missing trailing slash in API URL.

---

For more details, see the inline comments in `src/app/core/config.py`, `src/app/database.py`, and `docker-compose.yml`.
