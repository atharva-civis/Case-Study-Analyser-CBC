# Developer Documentation — CBC-India AGK Case Study Suite

Prepared for the AGK Platform engineering team's technical review and integration handover.

> **Positioning note.** This application is a functional prototype. The Streamlit front end is a simple wrapper meant to validate workflows quickly; the durable assets for integration are the **prompt library, user flows, assessment rubric logic, and AI pipeline design**, which can be ported into the AGK Platform's native stack.

---

## 1. AI Engine & Model Architecture

### 1.1 LLMs & Hosting

- **Current production model**: OpenAI **`gpt-4o`**, called via the external OpenAI cloud API (`openai` Python SDK, chat-completions). No models are hosted inside the application.
- **How it is used**:
  - All AI calls go through a single wrapper, `call_openai_api()` in `utils.py`, so the model/provider can be swapped in one place.
  - Calls are **non-streaming** completions.
  - Temperature is tuned per task: `0.1` for structured/JSON outputs (rubric scoring, source analysis), `0.2` for mapping/classification tasks, `0.5` for narrative drafting.
  - A fixed **seed (42)** is passed on most calls for reproducibility of assessments.
  - Structured tasks request **JSON responses** which are parsed and validated before use.
- **Model portability**: During development the same pipeline was also run against **locally hosted models via Ollama**, using the single-wrapper design to switch providers (Ollama exposes an OpenAI-compatible API, so switching is a base-URL + model-name change). This confirmed the architecture is not locked to OpenAI.
- **Benchmarking**: A benchmarking study was conducted comparing top reasoning models available on rubric-scoring accuracy and drafting quality. Google **Gemini** models performed at higher accuracy in that study (report shared separately). Given the KB team's partnership with the Google Gemini team, migrating the provider to Gemini is a straightforward change at the wrapper level.

### 1.2 API Management

- **API keys**: Read from the environment (`OPENAI_API_KEY`); never hardcoded or persisted. In the Replit environment the key is stored as a managed secret.
- **Rate limits / retries**: The application relies on the OpenAI SDK's built-in retry behaviour; there is no custom rate-limit queue in the prototype. Database connections have a custom 3-attempt retry with backoff.
- **Failover**: No automatic model failover is implemented in the prototype. Because all calls route through one wrapper, adding failover (e.g., OpenAI → Gemini/Ollama) is a contained change.

### 1.3 RAG & Vector Search

- **No vector database or embedding models are used.**
- The **CaseConnect** feature performs context injection rather than RAG: the AGK case repository (a 62-case CSV, `attached_assets/Case_details_-_Sheet1_*.csv`) is loaded into memory, serialised to structured text, and injected directly into the prompt for matching/recommendation (`utils.run_caseconnect_analysis`).
- This works well at the current corpus size. If the repository grows substantially, a pgvector/Qdrant-backed RAG layer with an embedding model would be the natural upgrade path.

### 1.4 Prompt Management

- Prompts are **hardcoded Python string templates**, dynamically rendered with user/wizard inputs at call time. They live in:
  - `case_generator.py` — section-by-section drafting prompts (hook, executive summary, introduction, body, teaching notes), narrative-continuity instructions, and compliance-review prompts.
  - `assessment_criteria.py` — the CBC-India AGK Review Rubric, criterion definitions, and scoring prompts.
  - `utils.py` — CaseConnect matching and document-analysis prompts.
- **No prompt framework** (LangChain, LlamaIndex, LangSmith) is used — just raw templates + the OpenAI SDK. This keeps the prompts fully portable to any stack.

### 1.5 Model Customization

- **No fine-tuning** has been performed. All behaviour is **strictly prompt-based** (prompt engineering + structured JSON outputs), which means the logic transfers directly to any capable model, including Gemini.

---

## 2. Tech Stack & Asynchronous Tasks

### 2.1 Core Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit (Python) — single-page app, custom CSS, Plotly charts |
| Backend | Python 3.11 — same Streamlit process; logic in `app.py`, `utils.py`, `case_generator.py`, `assessment_criteria.py` |
| Database | PostgreSQL via SQLAlchemy ORM (`db_models.py`); SQLite fallback for local dev |
| Document I/O | `PyPDF2` (PDF extraction), `python-docx` (DOCX read/write), `fpdf` (PDF reports) |
| Auth | Username/password, `passlib` bcrypt_sha256 hashing |

### 2.2 Job Execution

- Long-running AI generation is handled **synchronously within the request**, wrapped in Streamlit `st.spinner` blocks.
- Multi-section drafting and compliance checks use **`concurrent.futures.ThreadPoolExecutor`** to parallelise independent LLM calls.
- There is **no Redis/Celery/BullMQ queue and no WebSocket streaming** in the prototype. For AGK Platform integration, the generation pipeline is a good candidate for the platform's existing background-job infrastructure; the pipeline functions are already pure Python functions with clear inputs/outputs.

### 2.3 Database Schema

Three SQLAlchemy models (`db_models.py`):

- **`users`** — id, username (unique), email (unique), bcrypt password hash, timestamps.
- **`assessment_history`** — per-user rubric assessment results (scores, feedback JSON, document metadata).
- **`generated_cases`** — auto-persisted Case Study Generator drafts (wizard state, section drafts, exports metadata).

Tables are created via SQLAlchemy `create_all` on startup; there is no separate migration tool (Alembic recommended for production).

---

## 3. Infrastructure & Hosting Requirements

- **Compute**: The app is I/O-bound (waiting on LLM APIs), not compute-bound.
  - Staging: 1 vCPU / 2 GB RAM is sufficient.
  - Production: 2 vCPU / 4 GB RAM recommended headroom for concurrent users + document parsing.
- **Storage**: Application footprint is small (<1 GB including dependencies). Database growth is driven by assessment history and drafts (text) — modest.
- **GPU**: **None required.** All inference is via external API. GPUs would be needed only if the team chooses to self-host models via Ollama/vLLM (in that case: sizing depends on the model; ~16 GB+ VRAM for mid-size open models).
- **Ports**: Serves HTTP on a single port (currently 5000 via `streamlit run app.py --server.port 5000`).

---

## 4. Security, Compliance & Dependencies

- **Data privacy**: User inputs, prompt context, and generated content are sent to OpenAI via API. Under OpenAI's API terms, **API data is not used for model training** by default. No other third-party AI vendors receive data. All data-at-rest lives in the team's own PostgreSQL database.
- **Encryption**:
  - **In transit**: All external calls (OpenAI API, database when configured with SSL) use TLS. The hosted app is served over HTTPS.
  - **At rest**: Handled by the hosting/database provider (managed Postgres encrypts at rest). The application itself does not add a separate encryption layer.
- **Secrets**: Managed via environment variables (`OPENAI_API_KEY`, `DATABASE_URL`, `SESSION_SECRET`); nothing is committed to the repository.
- **Third-party services & licensing**:
  - Paid SaaS: **OpenAI API** (usage-billed) is the only paid external service.
  - All Python dependencies are permissively licensed (MIT / BSD / Apache-2.0): `streamlit`, `openai`, `sqlalchemy`, `psycopg2-binary`, `python-docx`, `fpdf`, `PyPDF2`, `pandas`, `plotly`, `matplotlib`, `passlib`/`bcrypt`, `pyspellchecker`. No GPL/restrictive-license dependencies and no proprietary libraries.
- **Security audits**: No formal penetration test has been conducted on this prototype. Passwords are hashed with bcrypt_sha256; SQL access goes through the ORM (parameterised). A dependency/SAST scan is recommended as part of the platform-integration hardening pass.

---

## 5. Local Setup Guide

```bash
# Prerequisites: Python 3.11+, (optionally) PostgreSQL

# 1. Install
pip install -e .        # or: uv sync

# 2. Environment
export OPENAI_API_KEY=sk-...
export DATABASE_URL=postgresql://user:pass@host:5432/db   # optional; SQLite fallback otherwise
export SESSION_SECRET=<random string>

# 3. Run
streamlit run app.py --server.port 5000
# App available at http://localhost:5000
```

Tests: `python test_spelling_validation.py` (spelling/validation checks used by the compliance step).

---

## 6. Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                 │
│  Auth · Analyser wizard · CaseConnect · Generator wizard │
└───────┬───────────────────┬──────────────────┬───────────┘
        │                   │                  │
        ▼                   ▼                  ▼
 assessment_criteria.py  utils.py       case_generator.py
 (rubric + scoring       (OpenAI wrapper,  (section drafting,
  prompts)                doc extraction,   continuity, compliance,
                          CaseConnect)      teaching notes)
        │                   │                  │
        └────────┬──────────┴─────────┬────────┘
                 ▼                    ▼
        OpenAI API (gpt-4o)    PostgreSQL (SQLAlchemy)
        [swappable: Ollama /   users · assessment_history ·
         Gemini via wrapper]   generated_cases
```

**Integration guidance**: treat `case_generator.py`, `assessment_criteria.py`, and the prompt templates as the portable core. The Streamlit layer (`app.py`) documents the intended user flows (step order, mandatory fields, validation rules) and should be re-implemented in the AGK Platform's native front end.
