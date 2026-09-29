# BizBook Progress Tracking

## Project Initialization
- Monorepo initialized under `scratch/bizbook`.
- Specification (`docs/SRS.md`) and architectural assumptions (`docs/ASSUMPTIONS.md`) documented.
- Development plan created in `docs/PLAN.md`.

## Phase 1: Foundation (COMPLETED)
- **Built**:
  - Monorepo structure with `/backend`, `/frontend`, `/docs`, `docker-compose.yml`, `.env.example`, `README.md`.
  - Full relational schema in SQLAlchemy 2.0 with Alembic migrations (`users`, `companies`, `memberships`, `company_profiles`, `company_brands`, `company_contacts`, `company_letterheads`, `company_signatures`, `company_seals`, `partner_logos`, `team_members`, `team_member_experiences`, `team_member_certifications`, `team_member_cvs`, `clients`, `client_contacts`, `projects`, `project_team_members`, `project_documents`, `services`, `audit_logs`).
  - Strict tenant scoping on every table and server-side RBAC dependency (`require_permission`, `require_roles`) across `OWNER`, `ADMIN`, `MANAGER`, `MEMBER`, `VIEWER`, `TENDER_MANAGER`.
  - Rate-limited auth endpoints (`/auth/register`, `/auth/login`, `/auth/me`, `/auth/reset-password`).
  - Company management, team management (with soft-delete), clients directory, services catalog, and projects portfolio with "create portfolio draft" generator.
  - Append-only audit logger capturing auth, creations, and portfolio events.
  - React + TypeScript + Vite + Tailwind CSS frontend desktop-first application with Dashboard shell, 9 core areas, global "Ask BizBook" modal, and actionable AI controls.
  - Full test suite passing 5/5 test modules (100% pass rate, 0 warnings).
- **Left**:
  - Phase 2: Document Engine & Vault (ClamAV virus scan, text extraction, OCR, versioning, S3 signed URLs, template engine).
  - Phase 3: AI Core & Grounded Company Memory (RAG, provider abstraction, token/cost logging).
  - Phase 4: Tender AI (Compliance matrix, requirement matching, proposal generation, ZIP export).
  - Phase 5: Business Operations & Final Acceptance Tests.
- **Assumed**:
  - Direct bcrypt hashing utilized for password security to guarantee compatibility across modern operating systems.
  - Single sliding-window in-memory rate limiting for local auth, designed to interface cleanly with Redis in multi-worker environments.
