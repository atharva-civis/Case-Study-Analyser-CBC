# CBC-India AGK Case Study Suite - Replit Documentation

## Overview

The CBC-India AGK Case Study Suite is a Streamlit-based web application providing two AI-powered tools:

1. **Case Study Analyser**: Evaluates case studies against the CBC-India AGK Case Study Review Rubric across four weighted assessment areas (Structure/Chronology, Language/Citations, Alignment with Teaching Notes, Overall Effectiveness). Uses OpenAI's API to analyze uploaded documents (PDF/DOCX), generates detailed scoring reports with recommendations, and maintains assessment history through a PostgreSQL database.

2. **CaseConnect**: An AI-enabled case discovery tool that recommends AGK repository case studies to faculty based on course outlines and a questionnaire about learners, objectives, competencies (KCM), duration, and sector. References the AGK case database CSV file (62 cases with title, description, full case text, and iGOT platform links) for matching. Each recommendation includes discussion points, key themes, and a "Go to Case Study on iGOT" button linking directly to the iGOT Karmayogi platform.

### App Structure
- **Landing Page** (`active_tool = None`): Shows Assessment Framework overview + two tool cards with "Get Started" buttons
- **Case Study Analyser** (`active_tool = "analyser"`): Sidebar with New Assessment / History tabs + document upload; main area shows assessment results
- **CaseConnect** (`active_tool = "caseconnect"`): Sidebar with optional curriculum upload; main area shows 5-question form and AI-generated case recommendations

### Recent Updates (March 2026)
- **CaseConnect Tool**: New AI case discovery feature — 5-question questionnaire (learners, objective, KCM competencies, duration, sector), optional curriculum upload, AGK case database matching, results with case recommendations, module suggestions, and teaching strategy. Case database switched from PDF (regex parsing) to XLSX (pandas/openpyxl structured read) to CSV (with full case text + iGOT links) for reliable title/description extraction. Upgraded to rich CSV with 62 cases including full case text and iGOT platform links; AI prompt redesigned for specific, grounded recommendations referencing actual case protagonists, challenges, and outcomes; each recommendation now includes key themes badges, classroom discussion points, and "Go to Case Study on iGOT" button.
- **Suite Architecture**: App restructured from single-tool to multi-tool suite with landing page, active_tool routing, conditional sidebar
- **Writing Assistant (Area 2)**: Full-document writing quality analysis using chunked processing — checks grammar, spelling (British English), tense consistency (past tense), redundancy, and sentence structure. Results shown as a findings table with severity badges in the Area 2 tab and in the PDF report. Processes the entire case study regardless of length. Uses temperature=0.1 and seed=42 for deterministic/consistent results across runs.
- **PDF Word Repair**: Post-extraction `repair_broken_words()` function fixes mid-word spaces introduced by PyPDF2 (e.g., "gover nance" → "governance"). Uses a curated domain word set + self-referencing heuristic + suffix-based word recognition. Also handles Unicode ligature artifacts (fi, fl, ff).
- **Parallel Assessment Pipeline**: Rubric criteria within each area are evaluated concurrently via ThreadPoolExecutor. Writing quality analysis, KCM mapping, and sector tagging also run in parallel. Progress bar tracks per-area batch completion.
- **Sector Tags & Keywords**: Auto-generates sector classifications (from SECTOR_MAPPING reference), sub-themes, and public search keywords alongside summaries; displayed in UI as badges and in PDF below Executive Summary
- **Prompt Exclusion Rules**: All AI prompts now exclude "Note from the Author" sections and Creative Commons cover page content (license URLs, citation markers) from evaluation
- **Informational Criteria in Area 3**: Competency Alignment and Sector/Theme Classification & SDG Mapping are now AI-generated narrative sections (not scored). Area 3 total points recalibrated from 10 to 6.
- **Dual Document Upload**: Now requires both Case Study and Teaching Note documents before assessment can proceed
- **Updated Assessment Criteria**: Expanded parameters across all 4 assessment areas based on the updated Case Review Matrix
- **Area 3 TN Integration**: Alignment with Teaching Note evaluations now analyze both Case Study and Teaching Note documents together
- **KCM Competency Mapping**: Added Karmayogi Competency Model (KCM) mapping that identifies top 3-4 behavioral and functional competencies per case with justifications, displayed before recommendations

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework**: Streamlit web framework with wide layout configuration

**UI Components**:
- Custom CSS styling using Poppins font family and tailored color schemes (primarily blue palette #1E3A8A)
- Interactive data visualizations using Plotly (gauge charts, bar charts, radar charts)
- PDF and DOCX document upload capabilities
- Session-based user authentication flow
- Multi-tab interface for assessment results, history, and downloads

**Design Pattern**: Single-page application with session state management for user authentication and assessment data persistence

### Backend Architecture

**Application Structure**:
- `app.py`: Main Streamlit application entry point orchestrating UI and business logic
- `utils.py`: Utility functions for document processing, OpenAI API integration, and report generation
- `assessment_criteria.py`: Configuration module defining rubric areas, criteria, weights, and scoring logic
- `db_models.py`: Data access layer handling database operations and user management

**Assessment Engine**:
- Rubric-based evaluation system with 4 weighted assessment areas
- Each area contains multiple criteria with specific scoring ranges (0-3 points typically)
- Weighted score calculation: Area 1 (30%), Area 2 (30%), Area 3 (15%), Area 4 (25%)
- Area 3 contains informational (non-scored) criteria marked with `"informational": True` flag
- Informational criteria generate AI narrative analysis but do not contribute to scoring
- AI-powered text analysis using structured prompts sent to OpenAI API

**Document Processing Pipeline**:
1. File upload (PDF/DOCX supported)
2. Text extraction using PyPDF2 or python-docx
3. AI-driven evaluation against predefined criteria
4. Score aggregation and weighted calculation
5. PDF report generation with visualizations

### Data Storage Solutions

**Database**: PostgreSQL (with SQLite fallback for testing)

**ORM**: SQLAlchemy with declarative base pattern

**Schema Design**:
- `users` table: User authentication and profile data
  - Fields: id, username, email, hashed_password, is_active, created_at
  - Password hashing: bcrypt_sha256
  - One-to-many relationship with assessment history

- `assessment_history` table: Stores assessment results
  - Fields: id, user_id, assessment_name, document_name, case_text, teaching_note_text, scores (JSON), recommendations (JSON), created_at
  - Foreign key relationship to users table

**Connection Management**:
- Connection pooling with pre-ping validation
- Connection recycling after 1 hour
- 15-second connection timeout for PostgreSQL
- Error handling for SSL connection issues

### Authentication and Authorization

**Authentication Method**: Username/password-based authentication

**Security Features**:
- Password hashing using bcrypt_sha256 (passlib library)
- Session state management for logged-in users
- User registration with unique username and email constraints
- Active user status flag for account management

**Session Management**:
- Streamlit session state stores: user_id, username, logged_in status
- Initialize session state function ensures consistency
- Login/logout functions manage session lifecycle

### AI Integration

**Provider**: OpenAI API (GPT models)

**Integration Pattern**:
- OpenAI client initialization with API key from environment variables
- Structured prompt engineering for each assessment criterion
- JSON response parsing for scores and feedback
- Error handling and retry logic for API failures

**Prompt Architecture**:
- Each criterion has a specific evaluation prompt
- Prompts request structured JSON responses with scores and justifications
- Context includes extracted document text and rubric definitions

### Reporting and Visualization

**Report Generation**: FPDF library for PDF creation with embedded visualizations

**Visualization Libraries**:
- Plotly for interactive charts (gauge, bar, radar charts)
- Matplotlib for static chart generation in reports
- Score color coding based on performance tiers (red/yellow/green)

**Grade Labeling System**:
- Tiered grading: Excellent (>90%), Good (70-90%), Satisfactory (50-70%), Needs Improvement (<50%)

## External Dependencies

### Third-Party Services

**OpenAI API**: 
- Purpose: AI-powered text analysis and assessment
- Configuration: API key via OPENAI_API_KEY environment variable
- Models: GPT series (specific model not hardcoded)

**Database Service**:
- PostgreSQL database (production)
- Connection via DATABASE_URL environment variable
- SQLite fallback for local development

### Key Python Libraries

**Web Framework**:
- `streamlit`: Main application framework for UI and interactivity

**Database & ORM**:
- `sqlalchemy`: ORM and database connection management
- `psycopg2`: PostgreSQL adapter (implied by error logs)

**Document Processing**:
- `PyPDF2`: PDF text extraction
- `python-docx`: DOCX file processing

**Data Analysis & Visualization**:
- `pandas`: Data manipulation and tabular display
- `plotly`: Interactive charts and visualizations
- `matplotlib`: Static chart generation
- `numpy`: Numerical operations

**AI Integration**:
- `openai`: Official OpenAI Python client

**Security**:
- `passlib`: Password hashing (bcrypt_sha256)

**Report Generation**:
- `fpdf`: PDF report creation

**Utilities**:
- `base64`: File encoding for downloads
- `json`: Data serialization
- `datetime`: Timestamp management

### Environment Configuration

**Required Environment Variables**:
- `OPENAI_API_KEY`: OpenAI API authentication
- `DATABASE_URL`: PostgreSQL connection string (optional, falls back to SQLite)

**Optional Variables** (from attached files suggesting Azure deployment):
- `AZURE_INFERENCE_SDK_ENDPOINT`: Azure AI endpoint
- `DEPLOYMENT_NAME`: Model deployment name