# BizBook Development Plan

## Phase 1: Foundation (COMPLETED)
- [x] Initialize monorepo structure (`/backend`, `/frontend`, `/docs`, `docker-compose.yml`)
- [x] Configure Python backend environment with `pyproject.toml` and dependencies
- [x] Database schema & SQLAlchemy models:
  - Users, Companies, Memberships, Roles, Permissions
  - CompanyProfile, CompanyBrand, CompanyContacts, Letterhead, Signature, Seal, PartnerLogos
  - TeamMember (experience, certifications, CV), Clients, ClientContacts
  - Projects, ProjectTeamMembers, ProjectDocuments, Services, AuditLogs
- [x] Database migrations with Alembic (`alembic upgrade head` verified)
- [x] Authentication system (Register, Login, Password Reset, JWT sessions, Sliding-window Rate limiting)
- [x] RBAC engine with roles: `OWNER`, `ADMIN`, `MANAGER`, `MEMBER`, `VIEWER`, `TENDER_MANAGER`
- [x] Service Layer & API routes:
  - Company, contacts, brand assets, signatures, seals
  - Team CRUD with experiences, certifications, soft-delete
  - Clients CRUD with contacts
  - Projects CRUD (with team/client linking and "create portfolio draft" action)
  - Services CRUD
  - Append-only Audit logging service
- [x] Frontend application setup (React + Vite + TypeScript + Tailwind CSS v4 + Lucide icons + Router)
- [x] Frontend core pages: Login, Register, Dashboard shell, Company, Team, Clients, Projects, Services, Vault, Tenders, Audit
- [x] Global "Ask BizBook" AI modal and Actionable AI controls
- [x] Automated tests (5/5 suites passing):
  - Healthcheck verification (`test_health.py`)
  - Authentication flow (`test_auth.py`)
  - Multi-tenant IDOR prevention tests (`test_tenant_isolation.py`)
  - RBAC permission enforcement (`test_rbac.py`)
  - Business entities & portfolio draft generation (`test_business_crud.py`)
- [x] Phase 1 Git Commit

## Phase 2: Document Engine & Vault (Next)
- [ ] Document Vault upload API (PDF, DOCX, XLSX, PPTX, JPG, PNG) with validation
- [ ] Processing states & versioning (Draft v1, v2, Approved/Final, Archived)
- [ ] Celery pipeline: ClamAV virus scanning, PyPDF/docx text extraction, OCR, metadata extraction
- [ ] Multi-tenant keyword and semantic search
- [ ] Expiry tracking for compliance documents
- [ ] Template engine with variable substitution
- [ ] Signed URL temporary private file delivery
- [ ] Document tests (immutable final documents, cross-tenant search isolation)

## Phase 3: AI Core & RAG (Pending)
## Phase 4: Tender AI (Pending)
## Phase 5: Business Operations & Final Delivery (Pending)
