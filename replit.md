# Case Study Analyser - Replit Documentation

## Overview

The Case Study Analyser is a Streamlit-based web application designed to evaluate case studies against the CBC-India AGK Case Study Review Rubric. The application provides automated assessment across four key areas: Structure/Chronology, Language/Citations, Alignment with Teaching Notes, and Overall Effectiveness. It uses OpenAI's API to analyze uploaded documents (PDF/DOCX), generates detailed scoring reports, and maintains user assessment history through a PostgreSQL database.

### Recent Updates (January 2026)
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
- Weighted score calculation: Area 1 (25%), Area 2 (20%), Area 3 (25%), Area 4 (30%)
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