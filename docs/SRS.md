# BizBook System Requirements Specification (SRS)

## 1. Overview & Vision
BizBook is an enterprise-grade, multi-tenant, API-first, AI-enabled SaaS platform designed for modern businesses. It centralizes institutional memory, company credentials, digital assets, team skills, project portfolio, official vaults, and leverages structured AI pipelines for automated tender parsing, requirement matching, and proposal generation with zero hallucination and strict human-in-the-loop workflows.

## 2. Technology Stack
- **Frontend**: React 18+ + TypeScript + Vite + Tailwind CSS (desktop-first, responsive, accessible, dark/light theme support, rich micro-interactions).
- **Backend**: FastAPI (Python 3.11+) with typed Pydantic v2 schemas, OpenAPI documentation, versioned under `/api/v1`. Layered architecture with controllers, service layer, repository/data access layer.
- **Database & Migrations**: PostgreSQL with SQLAlchemy 2.0 (async/sync) and Alembic migrations. Every tenant table contains `company_id`.
- **Private Storage**: S3-compatible private object storage (MinIO for local dev), served exclusively via signed, temporary URLs.
- **Background Jobs**: Celery + Redis (single queue system), idempotent jobs tracking start/end time, retry count, failure reasons.
- **AI Engine**: Provider abstraction (`generate_text`, `analyze_document`, `extract_structured_data`, `generate_embeddings`, `summarize`) with OpenAI, Anthropic, and Mock adapters. Model, prompt version, operation, token usage, and cost logged for every call.
- **Document Processing**: PyPDF/pdfplumber/python-docx/openpyxl/python-pptx text extraction, Tesseract/OCR engine, ClamAV virus scanning.
- **DevOps**: Docker Compose for PostgreSQL, Redis, MinIO, and ClamAV.

## 3. Non-Negotiable Architecture & Security Rules
1. **Tenant Isolation**: Every company-owned table has `company_id`. Every DB query is scoped by `company_id`. Cross-tenant data access is strictly forbidden at API, DB, and AI retrieval levels.
2. **Server-Side Authorization**: Role-Based Access Control (RBAC) enforced on every protected endpoint via reusable FastAPI dependencies. Frontend state is never trusted.
3. **Document Immutability & Versioning**: Never silently overwrite documents. Any update spawns a new version (`Draft v1`, `v2`, `Approved/Final`). Final documents are locked and immutable.
4. **Temporary Signed URLs**: Private files are never directly public. Served only via time-limited signed URLs.
5. **Append-Only Audit Logs**: Mandatory tamper-evident audit trails for login, upload, download, deletion, generation, tender creation, export, signature use, seal use, and permission changes.
6. **Zero AI Fabrication**: AI must never invent credentials, projects, certificates, or turnover. Missing details must be flagged under `missing_information` or status `MISSING`.
7. **Human-in-the-Loop for Financials & Legal**: AI-generated financial/legal content is flagged "needs human review". Monetary values require explicit human approval.
8. **Signature & Seal Governance**: Dedicated permissions with 6-stage workflow: Generate -> Review -> Request Authorization -> Authorized User Approves -> Apply -> Lock Final Version -> Audit Event.
9. **Idempotent Background Pipelines**: Long-running OCR, extraction, generation, and exports must run asynchronously with comprehensive status and retry semantics.
10. **Customer Privacy**: Customer documents are never used for external model training.

## 38. Frontend Route Structure
- `/auth/login` - User login
- `/auth/register` - User registration & company onboarding
- `/auth/reset-password` - Password recovery
- `/app/dashboard` - Executive dashboard with live metrics
- `/app/company` - Company profile, brand assets, letterhead, signatures & seals
- `/app/team` - Team members, qualifications, certifications, CVs
- `/app/clients` - Client directory, contacts, project associations
- `/app/projects` - Project portfolio, deliverables, evidence documents
- `/app/services` - Company services and capabilities catalog
- `/app/vault` - Document Vault (search, upload, metadata, versions, expiry)
- `/app/templates` - Dynamic document templates & variable placeholders
- `/app/tenders` - Tender management & compliance matrix
- `/app/tenders/:id` - Tender detail, requirements, matching, generation & export
- `/app/proposals` - Proposals & Quotations
- `/app/invoices` - Invoice tracking & payment status
- `/app/ask` - "Ask BizBook" AI Assistant & Company Memory Search
- `/app/audit` - Audit logs & compliance trail

## 44. Critical Acceptance Tests
1. **Multi-Tenant Isolation**: Tenant A cannot read, edit, or delete Tenant B's records via IDOR on any endpoint.
2. **RBAC Enforcement**: VIEWER role cannot edit or delete documents, team members, or clients. MEMBER cannot use signature/seal.
3. **Document Immutability**: Editing an approved/final document fails or creates a new version draft; original remains unchanged.
4. **Signature/Seal Workflow**: Unapproved signature/seal application is rejected; approved use creates an immutable final version and audit log.
5. **Zero AI Fabrication**: Generating tender proposals with missing certifications produces explicit `missing_information` alerts rather than fabricated records.
6. **Signed URLs**: Document access requires valid, non-expired signed URL tokens.
7. **Background Job Resilience**: Celery pipelines gracefully handle corrupted documents with failed status and retry limits without crashing.
