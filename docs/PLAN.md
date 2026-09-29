# BizBook Development Plan

## Phase 1: Foundation (COMPLETED)
- [x] Monorepo structure, dependencies, docker-compose, configs, README
- [x] Database models with strict multi-tenancy & Alembic migrations
- [x] Authentication & RBAC engine (Owner, Admin, Manager, Member, Viewer, Tender Manager)
- [x] Service layer for company, team, clients, projects, services, and audit logs
- [x] Portfolio draft generation
- [x] React + Vite + Tailwind CSS frontend shell with 9 primary areas and "Ask BizBook" modal
- [x] Full automated test suite passing (5/5 modules) & Git commit

## Phase 2: Document Engine & Vault (COMPLETED)
- [x] Database models: Documents, DocumentVersions, Templates, SignatureApprovals
- [x] Document Vault upload API with validation (PDF, DOCX, XLSX, PPTX, JPG, PNG) and ClamAV scanning
- [x] Versioning states: UPLOADED, PROCESSING, PROCESSED, FAILED, ARCHIVED (Draft v1, v2, Approved/Final)
- [x] Asynchronous processing pipeline: PyPDF/docx text extraction, metadata classification
- [x] Multi-tenant search: keyword and category filtering scoped by company_id
- [x] Expiry tracking: automatically flags expired and expiring documents
- [x] Template engine with variable substitution ({{company.name}}, {{client.name}}, {{ceo.designation}}, etc.)
- [x] PDF/DOCX document generator with headers, footers, logos, signatures, seals
- [x] Signature and seal governance approval workflow with immutable final locks
- [x] Full automated test suite passing (6/6 modules)
- [x] Phase 2 Git Commit

## Phase 3: AI Core & RAG (Next)
- [ ] AI provider abstraction (OpenAI, Anthropic, MockAIAdapter)
- [ ] Usage tracking (Usage entity, tokens, estimated cost, prompt version logging)
- [ ] Plan quotas and rate limits enforced server-side
- [ ] Grounded Company Memory RAG pipeline (tenant-isolated retrieval, zero fabrication rule)
- [ ] AI document generation API (title, sections, sources, warnings, missing_information)
- [ ] In-app and email notifications (deadlines, expiries, reviews, missing requirements)
- [ ] Tests: AI reports missing certificates rather than inventing them; tenant memory isolation

## Phase 4: Tender AI (Pending)
## Phase 5: Business Operations & Final Delivery (Pending)
