# CBC-India AGK Case Study Suite

An AI-powered Streamlit application built as a **functional prototype** for the CBC-India / AGK case-study ecosystem. The tool validates the end-to-end user workflows, prompt design, and AI feature set that are intended to be integrated into the AGK Platform. The front end is intentionally lightweight — the reusable value lies in the **prompts, user flows, and AI pipeline logic**.

## The Three Tools

| Tool | Purpose |
|---|---|
| **Case Study Analyser** | Evaluates uploaded case studies (PDF/DOCX) against the CBC-India AGK Case Study Review Rubric — weighted scoring across four assessment areas, detailed AI feedback, tiered grading, PDF report generation, and assessment history. |
| **CaseConnect** | AI-enabled case discovery: recommends AGK repository case studies to faculty based on course outlines and criteria (learners, objectives, competencies, duration, sector), with discussion points, key themes, and iGOT platform links. |
| **Case Study Generator** | Drafts new case studies from raw source material (transcripts, reports, URLs, notes) via an 8-step wizard. Supports Lesson-Drawing, Decision-Forcing, and Caselet formats, with section-by-section AI drafting, narrative continuity between sections, compliance review, teaching-note generation, and DOCX/PDF/TXT export. |

## Tech Stack at a Glance

- **Frontend + Backend**: Python / Streamlit (single-page app, session-state driven)
- **AI Engine**: OpenAI API (`gpt-4o`) — prompt-based, no fine-tuning. See [docs/DEVELOPER.md](docs/DEVELOPER.md#ai-engine--model-architecture) for full details on model usage, and notes on the Ollama-based local model switching and reasoning-model benchmarking work.
- **Database**: PostgreSQL via SQLAlchemy (SQLite fallback for local testing)
- **Exports**: `python-docx` (DOCX), `fpdf` (PDF)
- **Auth**: Username/password with bcrypt_sha256 hashing

## Quick Start

```bash
# 1. Install dependencies (Python 3.11+)
pip install -e .          # or: uv sync

# 2. Set required environment variables
export OPENAI_API_KEY=sk-...
export DATABASE_URL=postgresql://...   # omit to fall back to local SQLite

# 3. Run
streamlit run app.py --server.port 5000
```

## Repository Layout

```
app.py                    # Main Streamlit app — UI, wizard flows, auth, orchestration
case_generator.py         # Case Study Generator pipeline: prompts, section drafting, continuity, compliance
assessment_criteria.py    # CBC-India AGK Review Rubric definition + scoring logic
utils.py                  # OpenAI client, document extraction, CaseConnect analysis, helpers
db_models.py              # SQLAlchemy models: users, assessment_history, generated_cases
scripts/                  # Utility scripts
docs/DEVELOPER.md         # Full developer & architecture documentation (integration handover)
```

## Documentation

- **[docs/DEVELOPER.md](docs/DEVELOPER.md)** — developer documentation prepared for the AGK Platform integration review: AI engine & model architecture, prompt management, tech stack, async/job handling, infrastructure requirements, security & compliance, dependencies & licensing, and database schema.

## Status

This repository is a working prototype. For AGK Platform integration, the recommended approach is to port the prompt library, wizard flows, and AI pipeline logic into the platform's native stack rather than embedding the Streamlit UI as-is.
