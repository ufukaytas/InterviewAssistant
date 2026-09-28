# Interview Service

The Interview Service is a standalone microservice of the **Interview Assistant** project. It owns interview sessions, the question pool, and feedback generation. It does **not** implement authentication, the API Gateway, the Profile Service, the React UI, or the root `docker-compose.yml` — those belong to other services/teammates.

- Language: Python 3.12+
- Framework: FastAPI
- Database: MongoDB (via Motor, async driver)
- Container port: `8080` (exposed externally as `3007` by the shared docker-compose)
- API prefix: `/api/v1`
- Auth: JWT issued by the Auth Service (HS256 / issuer `auth-servisi` / audience `mulakat-hazirlik` / subject = `user_id`)

## Architecture

Clean Architecture, with each layer depending only on the layer beneath it:

```
app/
├── main.py                      # FastAPI app, lifespan, exception handlers, router mounting
├── api/
│   ├── routes/                  # Thin HTTP controllers — no business logic
│   └── dependencies/            # DI wiring: auth, pagination, settings, repositories, services
├── application/
│   ├── services/                 # Business logic / use cases (InterviewService, QuestionService)
│   └── schemas/                  # Pydantic request/response models
├── domain/
│   ├── entities/                 # Framework-agnostic dataclasses (InterviewSession, Question, ...)
│   ├── enums/                    # InterviewStatus, QuestionAttemptStatus, QuestionSource, ...
│   └── repositories/             # Abstract repository interfaces (ports)
├── infrastructure/
│   ├── database/                 # MongoDB connection lifecycle (Motor client)
│   ├── repositories/             # Mongo implementations of the domain repository interfaces
│   └── external_clients/         # Isolated HTTP clients (Profile Service, LLM layer)
└── core/
    ├── config.py                 # Centralized settings (env-driven, pydantic-settings)
    ├── security.py                # JWT decode/verify against the Auth Service contract
    └── exceptions.py              # Domain/application exceptions + HTTP status mapping
```

Key decisions:

- **Route handlers never touch the database, HTTP clients, or business rules.** They validate input via Pydantic, call an application service, and return its response.
- **Domain entities are plain dataclasses** with no MongoDB or Pydantic coupling, so business rules (state transitions, ownership checks, timing) are testable without any infrastructure.
- **Repositories are interfaces in `domain/repositories`**, implemented in `infrastructure/repositories`. Services depend on the interface, not the Mongo implementation, via FastAPI dependency injection (`api/dependencies`).
- **All Profile Service HTTP calls live in `infrastructure/external_clients/profile_service_client.py`.** Nothing else makes outbound HTTP calls to the Profile Service.
- **A pluggable `LLMClient` interface** (`infrastructure/external_clients/llm_client.py`) backs question generation and feedback synthesis. No LLM provider or API key was specified in the requirements, so it ships with a deterministic `StubLLMClient` that keeps the service fully runnable and testable offline. Swap in a real provider behind the same interface without touching services or routes.
- **Centralized error handling**: all domain/application errors are `AppError` subclasses (`NotFoundError`, `ForbiddenError`, `InvalidStateTransitionError`, etc.) mapped to HTTP responses in `main.py`, so internal details (e.g. Mongo error text) never leak to clients.
- **Server-side timing only.** `question_started_at`, `answered_at`, `elapsed_seconds`, and `remaining_seconds` are all computed from server timestamps; the client-submitted payload never carries timing data.

## Environment Variables

Copy `.env.example` to `.env` and fill in real values. **Never commit `.env`.**

| Variable | Purpose |
|---|---|
| `APP_ENV` | `development` / `staging` / `production` / `test`. Disables `/dev/token` when `production`. |
| `MONGODB_URL` | Mongo connection string (shared infra provides this in docker-compose). |
| `MONGODB_DATABASE` | Database name. |
| `JWT_SECRET_KEY` | Must match the Auth Service's signing secret exactly. |
| `JWT_ISSUER` | Must be `auth-servisi` (shared contract). |
| `JWT_AUDIENCE` | Must be `mulakat-hazirlik` (shared contract). |
| `JWT_ALGORITHM` | `HS256`. |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Expiry used by the dev-token endpoint. |
| `ENABLE_DEV_TOKEN_ENDPOINT` | Set `false` (or `APP_ENV=production`) to disable `POST /dev/token`. |
| `LLM_API_KEY` | LLM provider API key (secret, `.env` only). Empty = offline stub. Use the same variable name in the Profile Service. |
| `LLM_PROVIDER`, `LLM_MODEL`, `LLM_BASE_URL`, `LLM_TIMEOUT_SECONDS`, `LLM_MAX_TOKENS` | LLM provider selection (`anthropic` or `openai`-compatible) and tuning. |
| `PROFILE_SERVICE_URL` | Base URL of the Profile Service (e.g. `http://profile-service:8080` inside compose). |
| `PROFILE_SERVICE_TIMEOUT_SECONDS` | HTTP timeout for Profile Service calls. |
| `DEFAULT_QUESTION_TIME_LIMIT_SECONDS`, `DEFAULT_INTERVIEW_QUESTION_COUNT`, `DEFAULT_PAGE_SIZE`, `MAX_PAGE_SIZE` | Tunable defaults. |

## API Endpoints

All endpoints below `/api/v1` require `Authorization: Bearer <jwt>` unless noted.

**Interview lifecycle**
```
POST   /api/v1/interviews                                          create a session
GET    /api/v1/interviews                                          list own sessions (paginated)
GET    /api/v1/interviews/{session_id}                             get one session
DELETE /api/v1/interviews/{session_id}                              delete (or abandon if in progress)
POST   /api/v1/interviews/{session_id}/start                        created -> in_progress
GET    /api/v1/interviews/{session_id}/current-question              current question + remaining time
POST   /api/v1/interviews/{session_id}/questions/{question_id}/start
POST   /api/v1/interviews/{session_id}/questions/{question_id}/answer
POST   /api/v1/interviews/{session_id}/questions/{question_id}/skip
POST   /api/v1/interviews/{session_id}/complete                     in_progress -> completed, generates feedback
GET    /api/v1/interviews/{session_id}/feedback
```

**Question pool** (any authenticated user; there is no role system in v1, admin checks will be added in v2)
```
GET    /api/v1/questions            filter by category, difficulty, status, tag
POST   /api/v1/questions
GET    /api/v1/questions/{id}
PATCH  /api/v1/questions/{id}
DELETE /api/v1/questions/{id}       archives (soft-deletes) rather than removing
```

**System** (no auth required)
```
GET  /health       liveness — always 200 while the process is alive
GET  /ready         readiness — verifies MongoDB connectivity
POST /dev/token      dev-only JWT issuer, disabled when APP_ENV=production or ENABLE_DEV_TOKEN_ENDPOINT=false
```

Interactive OpenAPI docs are available at `/docs` (Swagger UI) and `/redoc`.

## Running Locally

Requires a running MongoDB instance (local or containerized).

```bash
cd interview-service
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # then edit .env with real local values

uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Get a local JWT (dev only) and call a protected endpoint:

```bash
curl -X POST http://localhost:8080/dev/token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo-user"}'

curl http://localhost:8080/api/v1/interviews \
  -H "Authorization: Bearer <token from above>"
```

### Running with Docker (this service only)

```bash
docker build -t interview-service .
docker run -p 3007:8080 --env-file .env interview-service
```

### Running the tests

```bash
pip install -r requirements.txt   # includes pytest, pytest-asyncio, mongomock-motor
pytest -q
```

Tests do not require a real MongoDB or a real Profile Service — MongoDB is replaced with `mongomock_motor`'s in-memory async client, and the Profile Service HTTP client is replaced with an in-process fake, both wired in `tests/conftest.py`.

## Connecting via the Shared Docker Environment

This repository does **not** define the root `docker-compose.yml`; a teammate owns it. For this service to work in the shared compose, the following is expected:

- The shared compose builds this service from its `Dockerfile` and maps `3007:8080`.
- It injects environment variables matching `.env.example` (`MONGODB_URL`, `JWT_SECRET_KEY`, etc.) — typically pointing `MONGODB_URL` at the shared Mongo container's service name (e.g. `mongodb://mongo:27017`) and `PROFILE_SERVICE_URL` at the Profile Service's container name (e.g. `http://profile-service:8080`).
- `JWT_SECRET_KEY`, `JWT_ISSUER`, and `JWT_AUDIENCE` must be **identical** across the Auth Service and this service, or token validation will fail with 401.
- The API Gateway forwards the `Authorization` header through untouched; this service performs its own JWT validation rather than trusting gateway-level auth alone.

## Tests Implemented

`tests/` covers, per the project requirements:

- `test_system.py` — health/readiness probes, dev-token issuance and production lock-out
- `test_auth.py` — missing/invalid/forged tokens, wrong issuer/secret
- `test_questions.py` — question CRUD (authenticated users), category filtering, archive-not-delete
- `test_interviews.py` — interview creation (pool and generated), profile snapshotting, ownership enforcement, pagination, start/answer/skip/complete transitions, invalid state transitions, feedback retrieval, abandon-on-delete
- `test_llm_client.py` — LLM client selection (stub vs real), Anthropic/OpenAI response parsing, error handling, key masking
- `test_repositories.py` — Mongo repository behavior in isolation (create/get/list/update/delete/archive), independent of the HTTP layer

Run with `pytest -q` (46 tests, all passing against an in-memory Mongo double).

## Assumptions & Integration Points to Confirm with Teammates

1. **Profile Service contract.** `ProfileServiceClient` calls `GET /api/v1/job-postings/{id}`, `GET /api/v1/cvs/{id}` and `GET /api/v1/cvs/latest` (the latest CV is resolved from the forwarded `Authorization` token, so no `user_id` is in the path). It assumes the responses contain at least `title`/`description` (job posting) and `summary` (CV); confirm the exact field names with the Profile Service owner.
2. **No roles in v1.** The question-pool endpoints only require a valid JWT. Role/admin checks are planned for v2 once the Auth Service issues a role claim.
3. **LLM.** The key is read from `LLM_API_KEY` in the environment (never committed). Without a key the offline `StubLLMClient` is used. The provider (`anthropic` or an `openai`-compatible API) is selected with `LLM_PROVIDER`; confirm which one the team uses. The Profile Service should read the same variable names so one key is shared.
4. **Root `docker-compose.yml` and MongoDB provisioning** are owned by another teammate; this service only assumes `MONGODB_URL`/`MONGODB_DATABASE` (and `LLM_API_KEY`) are provided via environment variables.
5. **API Gateway** is assumed to forward the `Authorization` header unmodified; this service does not implement a second auth mechanism and does not trust any gateway-injected identity headers.
