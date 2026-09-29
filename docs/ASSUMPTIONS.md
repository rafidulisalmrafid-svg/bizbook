# BizBook System Assumptions & Architectural Decisions

## 1. Multi-Tenancy Architecture
- Shared database, shared schema pattern with `company_id` on every company-scoped table.
- All database queries filter explicitly by `company_id`.
- Tenant context is extracted server-side from JWT claims verified against active database memberships.

## 2. Authentication & Sessions
- Access tokens are signed JWTs with expiration (e.g. 60 minutes).
- Refresh tokens with secure rotation.
- Password hashing with `bcrypt` (or Argon2).
- Rate limiting implemented per IP/email on authentication routes (`/auth/login`, `/auth/register`).

## 3. Storage Layer
- S3-compatible private object storage protocol (MinIO used for local dev/testing).
- File keys follow the structure: `{company_id}/{category}/{document_id}/{version}_{filename}`.
- Signed URLs expire after 15 minutes by default.
- In test environments, a local filesystem storage mock/adapter implements the S3 signed URL protocol.

## 4. Background Job Processing
- Celery worker with Redis broker and result backend.
- Task tracking entity in database or Redis storing status (`PENDING`, `STARTED`, `PROCESSING`, `SUCCESS`, `FAILURE`), progress percentage, retry count, start/end timestamps, and error messages.
- Local testing uses an eager execution mode (`CELERY_TASK_ALWAYS_EAGER=True`) to run tests synchronously without requiring a live Redis daemon.

## 5. AI Engine & Provider Abstraction
- Unified interface `AIProvider` with methods:
  - `generate_text(prompt, system_message, ...)`
  - `analyze_document(text_content, schema, ...)`
  - `extract_structured_data(text_content, pydantic_model, ...)`
  - `generate_embeddings(text)`
  - `summarize(text, max_length, ...)`
- Providers: `OpenAIAdapter`, `AnthropicAdapter`, and `MockAIAdapter`.
- `MockAIAdapter` deterministically evaluates tests, flags missing documents, and simulates token usage and costs.
