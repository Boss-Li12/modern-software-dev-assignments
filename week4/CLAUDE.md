# CLAUDE.md - Week 4 Project Guide

> This file provides repository-specific instructions and context for AI assistants working on this project.

## 🏗️ Project Overview

This is a **"Developer's Command Center"** - a minimal full-stack starter application.

| Component | Technology | Location |
|-----------|------------|----------|
| Backend | FastAPI + SQLAlchemy | `backend/app/` |
| Frontend | Static HTML/JS/CSS | `frontend/` |
| Database | SQLite | `data/` |
| Tests | pytest | `backend/tests/` |

---

## 🚀 Quick Start Commands

### Running the Application
```bash
cd week4
PYTHONPATH=. /Users/boss_li12/miniforge3/bin/python -m uvicorn backend.app.main:app --reload
```
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

### Testing
```bash
make test                    # Run all tests
make test ARGS="-k notes"    # Run specific tests
```

### Code Quality
```bash
make format    # Auto-fix with black + ruff
make lint      # Check with ruff
```

---

## 📁 Code Navigation

### Entry Points
| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI application entry point |
| `frontend/index.html` | Frontend entry point |
| `data/seed.sql` | Database schema + seed data |

### API Routers
| Router | Location | Endpoints |
|--------|----------|-----------|
| Notes | `backend/app/routers/notes.py` | `GET/POST/DELETE /notes/{id}`, `GET /notes/search/` |
| Action Items | `backend/app/routers/action_items.py` | `GET/POST /action-items/`, `PUT /action-items/{id}/complete` |

### Data Layer
| File | Purpose |
|------|---------|
| `backend/app/models.py` | SQLAlchemy ORM models (Note, ActionItem) |
| `backend/app/schemas.py` | Pydantic validation schemas |
| `backend/app/db.py` | Database connection and session management |

### Services
| File | Purpose |
|------|---------|
| `backend/app/services/extract.py` | Action item extraction logic |

---

## 🎨 Style & Safety Guardrails

### Tooling Requirements
- **Formatter**: black (line length default)
- **Linter**: ruff
- **Pre-commit**: Install with `pre-commit install`

### Code Style Rules
1. Use Python 3.10+ type hints (e.g., `str | None` not `Optional[str]`)
2. Use Pydantic v2 `ConfigDict` instead of class-based `Config`
3. Use FastAPI lifespan handlers instead of `@app.on_event()`

### Safe Commands ✅
- `make run` - Start dev server
- `make test` - Run tests
- `make format` - Auto-fix formatting
- `make lint` - Check linting
- `make seed` - Re-seed database

### Unsafe Commands ⚠️
- Direct SQL operations on production database
- `rm -rf data/` - Would delete database
- Any command modifying `seed.sql` without backup

---

## 🔄 Standard Workflows

### Adding a New API Endpoint
1. **Write a failing test first** in `backend/tests/test_*.py`
2. **Add Pydantic schema** in `backend/app/schemas.py` (if needed)
3. **Implement the endpoint** in appropriate router
4. **Run tests**: `make test`
5. **Run pre-commit**: `pre-commit run --all-files`
6. **Update docs** if API changed

### Modifying Database Schema
1. Update `backend/app/models.py`
2. Update `data/seed.sql`
3. Delete `data/*.db` to reset
4. Run `make seed` or restart app
5. Update related schemas and routers

### Debugging Tips
- API errors: Check http://localhost:8000/docs for request/response schemas
- Database issues: Check `data/` directory for SQLite file
- Test failures: Run with `-v --tb=long` for detailed output

---

## 📋 Pending Tasks (from docs/TASKS.md)

| # | Task | Status |
|---|------|--------|
| 1 | Enable pre-commit and fix repo | ⬜ |
| 2 | Add search endpoint for notes | ✅ Already exists |
| 3 | Complete action item flow | ⬜ |
| 4 | Improve extraction logic (parse #tags) | ⬜ |
| 5 | Notes CRUD (PUT/DELETE) | 🔶 DELETE done, PUT pending |
| 6 | Request validation & error handling | ⬜ |
| 7 | Docs drift check (API.md) | ⬜ |

---

## 🤖 AI Assistant Guidelines

### When asked to implement a feature:
1. First check if similar code exists in the codebase
2. Follow existing patterns (routers, schemas, tests)
3. Always write tests before or with implementation
4. Run `make lint` before finishing

### When asked to debug:
1. Reproduce the issue first
2. Check test coverage for the affected code
3. Add a regression test for the fix

### When asked about the project:
1. Reference this CLAUDE.md for structure
2. Check `docs/TASKS.md` for pending work
3. Use `/run-tests` workflow to verify changes
