# AGENTS.md
This file provides guidance to Verdent when working with code in this repository.

## Table of Contents
1. Commonly Used Commands
2. High-Level Architecture & Structure
3. Key Rules & Constraints
4. Development Hints

## Commands
- Build frontend: `cd frontend && npm run build`
- Dev frontend: `cd frontend && npm run dev`
- Lint backend: `cd backend && ruff check app tests` *[inferred]*
- Lint frontend: `cd frontend && npm run lint` *[inferred]*
- Test backend: `cd backend && pytest -q --cov=app --cov-report=term`
- Test frontend (unit): `cd frontend && npm test` *[inferred]*
- Run single test: `cd backend && pytest tests/unit/test_file.py -k test_name -v`
- Run E2E tests: `cd frontend && npx playwright test`
- Alembic migrate: `cd backend && alembic upgrade head`
- Alembic autogenerate: `cd backend && alembic revision --autogenerate -m "desc"`
- Run backend: `cd backend && uvicorn app.main:app --reload` *[inferred]*

## Architecture
- **Major subsystems & responsibilities**
  - `frontend/` — Next.js App Router (TypeScript), PWA with offline-first IndexedDB sync.
  - `backend/` — FastAPI (Python) with SQLAlchemy ORM, Alembic migrations, multi-tenant via `tenant_id` on every table.
  - `backend/app/services/` — AI abstraction (`ai_service.py`), rules engine (`rules_engine.py`), triage engine (`triage_engine.py`), sync engine (`sync_engine.py`).
  - `backend/app/core/security.py` — JWT OAuth2 + bcrypt + MFA TOTP.
  - Redis is used for caching, async task queues, and rate limiting.
- **Key data flows**
  - Patient intake (field visit or in-clinic) collects data → episode created with statuses `pending` → `consented` → `collecting` → `collected` → `processing` (if clinical completeness ≥ 70%).
  - AI pipeline: ingestion → OCR/NER → Rules Engine validation → LLM inference (agnostic provider + fallback) → confidence scoring → côté-à-côté validation UI → doctor signs.
  - Offline changes queue in IndexedDB; sync uses Conflict-Aware Engine (medical fields require manual arbitration; administrative fields use Last Write Wins).
- **External dependencies**
  - PostgreSQL + pgvector (production/tests security); SQLite (local dev only).
  - Redis (cache + queues).
  - LLM providers: OpenAI, Anthropic, Google Gemini, or self-hosted Mistral/LLaMA (fallback handled in `ai_service.py`).
- **Development entry points**
  - `backend/app/main.py` — FastAPI app factory.
  - `frontend/src/app/layout.tsx` — root layout.
  - `backend/app/api/routes.py` — all REST endpoints.
  - `frontend/src/utils/api.ts` — centralized HTTP client with JWT Bearer.
- **Mermaid diagram of subsystem relationships**
  ```mermaid
  graph LR
    subgraph Client
      NextJS[Next.js App Router]
      Sync[IndexedDB + sync.ts]
    end
    subgraph API
      FastAPI[FastAPI /api/routes]
      Security[JWT + OAuth2 + TOTP]
      RateLimit[Rate limiting / Redis]
    end
    subgraph Services
      AI[AIService / rules_engine / triage_engine]
      SyncEngine[Conflict-Aware Sync Engine]
      PDF[ReportLab PDF export]
    end
    subgraph Data
      SQL[(SQLAlchemy SQLite dev / PostgreSQL prod)]
      Redis[(Redis cache + queues)]
      pgvector[(pgvector RAG)]
    end
    Client -->|REST + WS /ws/triage| API
    API --> Services
    Services --> Data
    Sync -->|offline queue| SyncEngine
  ```

## Key Rules & Constraints
- **Role-based access control** applies at every layer; FastAPI dependency `require_role(...)` returns 403 for unauthorized roles.
- **Prescription signing** is `doctor`-only; creation/editing allowed for `doctor` and `ipa`.
- **Multi-tenancy** — all application queries must filter by `tenant_id`. RLS policies enforcement is planned for production PostgreSQL; do not rely on RLS in SQLite dev mode.
- **Environment-based database switch** controlled by `DATABASE_URL` only; no code changes between SQLite dev and PostgreSQL prod.
- **pgvector** is only available with PostgreSQL. In local SQLite dev, RAG features are mocked or disabled.
- **Medical fields must never be silently overwritten** during offline sync; always present both versions for manual arbitration (Conflict-Aware).
- **Audit trail** is INSERT-ONLY with immutable `audit_logs`; no updates or deletes permitted, even by admin.
- **Interop endpoints** for external systems (MSSanté, DMP, FHIR, Carte Vitale, DICOM) exist as stubs returning HTTP 501 in VI; production VC implements real adapters against `BaseConnector` interface.
- **WCAG 2.1 AA** — all new UI components require accessible labels, keyboard navigability, focus management, and `aria-live` regions for dynamic updates.

## Development Hints
- Adding a new API endpoint
  1. Add Pydantic schema in `backend/app/schemas/schemas.py` if request/response models are needed.
  2. Add route in `backend/app/api/routes.py` with `require_role(...)`.
  3. Add unit test in `backend/tests/unit/`. Security tests go in `backend/tests/security/` (requires PostgreSQL).
  4. Wire UI call in `frontend/src/utils/api.ts` and create/update page/component.
- Modifying CI/CD pipeline
  1. Edit `.github/workflows/ci.yml`; keep the 4 jobs: `backend-tests`, `frontend-build`, `alembic-check`, `e2e-tests`.
  2. Ensure E2E tests run with `npx playwright test` and backend tests run with `pytest`.
- Extending subsystems
  - AI provider support: implement new client in `backend/app/services/ai_service.py` respecting the provider-agnostic interface. Add tests around fallback/retry logic.
  - Offline sync: make changes in both `frontend/src/utils/sync.ts` and `backend/app/services/sync_engine.py`; Conflict-Aware logic must remain consistent across both.
  - New data entities: add SQLAlchemy model in `backend/app/models/models.py`, create Alembic migration, add RBAC checks in routes, and ensure `tenant_id` is populated.
