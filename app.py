import streamlit as st
from streamlit_option_menu import option_menu
import os
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import json
from io import BytesIO
import PyPDF2
import docx
from datetime import datetime, timedelta
from utils import extract_text_from_pdf, extract_text_from_docx, call_openai_api, generate_report_pdf, get_download_link, create_gauge_chart, analyze_writing_quality_chunked, load_case_database, run_caseconnect_analysis
from assessment_criteria import ASSESSMENT_AREAS, ASSESSMENT_CRITERIA, calculate_weighted_score, get_score_color, get_grade_label, SECTOR_MAPPING, PROMPT_EXCLUSION_INSTRUCTIONS, KCM_COMPETENCIES
from db_models import (
    initialize_session_state, 
    register_user, 
    authenticate_user, 
    login_user, 
    logout_user, 
    save_assessment,
    get_user_assessments,
    get_assessment
)

# Set page configuration
st.set_page_config(
    page_title="CBC-India AGK Case Study Suite",
    page_icon="📊",
    layout="wide"
)

# Load case database for CaseConnect
CASE_DB_PATH = "attached_assets/Case_details_-_Sheet1_1774840900142.csv"
@st.cache_data
def get_case_database():
    cases, structured_text, case_count = load_case_database(CASE_DB_PATH)
    link_lookup = {}
    for c in cases:
        if c.get("igot_link"):
            link_lookup[c["title"].strip().lower()] = c["igot_link"]
    return structured_text, case_count, link_lookup

CASE_DATABASE_TEXT, CASE_COUNT, CASE_LINK_LOOKUP = get_case_database()

def _resolve_igot_link(case_title):
    import unicodedata
    if not case_title:
        return ""
    def normalize(s):
        s = unicodedata.normalize('NFKD', s).strip().lower()
        s = re.sub(r'[\u2013\u2014\u2015\u2212]', '-', s)
        s = re.sub(r'[\u2018\u2019\u201c\u201d]', "'", s)
        s = re.sub(r'[^\w\s-]', '', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    norm_title = normalize(case_title)
    if case_title.strip().lower() in CASE_LINK_LOOKUP:
        return CASE_LINK_LOOKUP[case_title.strip().lower()]
    for db_title, link in CASE_LINK_LOOKUP.items():
        if normalize(db_title) == norm_title:
            return link
    for db_title, link in CASE_LINK_LOOKUP.items():
        if norm_title in normalize(db_title) or normalize(db_title) in norm_title:
            return link
    return ""

# Custom CSS to improve the appearance
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif !important;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Global button styling to standardize sizes */
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 50px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    
    /* Criteria Tab styling with wrapping and padding */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        padding: 10px 0px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto !important;
        min-height: 50px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        max-width: 200px !important;
        padding: 10px 15px !important;
        line-height: 1.2 !important;
        text-align: center !important;
        background-color: #f0f2f6 !important;
        border-radius: 8px 8px 0px 0px !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #074fa5 !important;
        color: white !important;
    }

    /* Result card header wrapping */
    .card-header, .criteria-heading, h4 {
        white-space: normal !important;
        word-wrap: break-word !important;
        line-height: 1.3 !important;
    }
    
    h1, h2, h3 {
        color: #1E3A8A;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stTextInput, .stButton, .stSelectbox {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Make sure all text elements use Poppins */
    p, span, div, label, button, select, input, textarea {
        font-family: 'Poppins', sans-serif !important;
    }
    .card {
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        background-color: #EFF6FF;
        box-shadow: 0 2px 4px rgba(0,0,0,0.12);
        color: #333333;
    }
    .criteria-heading {
        font-weight: bold;
        font-size: 1.1em;
        padding: 8px;
        margin-bottom: 12px;
        background-color: #DBEAFE;
        border-radius: 4px;
        color: #1E40AF;
    }
    .metrics-container {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    .metric-card {
        text-align: center;
        padding: 10px;
        border-radius: 5px;
        background-color: #F9FAFB;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    /* Auth form styling */
    .auth-form {
        max-width: 450px;
        margin: 0 auto;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: #F9FAFB;
    }
    .auth-form h3 {
        text-align: center;
        margin-bottom: 20px;
        color: #1E3A8A;
    }
    .auth-form .stButton>button {
        width: 100%;
        margin-top: 10px;
    }
    /* History card styling */
    .history-card {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: white;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .history-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .history-card h4 {
        margin-top: 0;
        color: #1E3A8A;
    }
    .history-card p {
        margin-bottom: 5px;
        color: #4B5563;
    }
    .history-card .date {
        color: #6B7280;
        font-size: 0.9em;
    }
    /* User profile section */
    .user-profile {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding: 10px;
        background-color: #F0F9FF;
        border-radius: 8px;
    }
    .user-profile .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #3B82F6;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
    }
    .user-profile .info {
        flex-grow: 1;
    }
    .user-profile .info p {
        margin: 0;
    }
    .user-profile .actions {
        margin-left: 10px;
    }
    /* Score badge styling */
    .score-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.9em;
    }
    .score-excellent {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .score-good {
        background-color: #DBEAFE;
        color: #1E40AF;
    }
    .score-satisfactory {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .score-needs-improvement {
        background-color: #FED7AA;
        color: #9A3412;
    }
    .score-poor {
        background-color: #FECACA;
        color: #991B1B;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for authentication
initialize_session_state()

# Authentication and user management
def show_login_page():
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    st.subheader("Login to Your Account")
    
    st.info("Please enter your credentials to access the Case Study Analyser")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login", use_container_width=True):
        if username and password:
            success, user = authenticate_user(username, password)
            if success:
                login_user(user)
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(user)  # Error message
        else:
            st.warning("Please enter both username and password")
    
    # Add note for authorized users
    st.markdown("""
    <div style="margin-top: 20px; padding: 10px; border-radius: 5px; background-color: #f8f9fa; font-size: 0.9em; color: #6c757d;">
    <strong>Note:</strong> This is a private application. Only authorized users can access this tool.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_register_page():
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    st.subheader("Create a New Account")
    
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Register"):
            if not username or not email or not password:
                st.warning("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = register_user(username, email, password)
                if success:
                    st.success(message)
                    st.session_state.show_register = False
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        if st.button("Back to Login"):
            st.session_state.show_register = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Function to display header with logos
def display_header_with_logos():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if os.path.exists("attached_assets/cbc_logo_1770210514857.png"):
            st.image("attached_assets/cbc_logo_1770210514857.png", width=100)
    with col2:
        active = st.session_state.get("active_tool", None)
        if active == "analyser":
            st.title("Case Study Analyser")
        elif active == "caseconnect":
            st.title("CaseConnect")
        else:
            st.title("CBC-India AGK Case Study Suite")
    with col3:
        if os.path.exists("attached_assets/agk_logo_1770210514857.png"):
            st.image("attached_assets/agk_logo_1770210514857.png", width=100)

# Show login page or main app
if not st.session_state.logged_in:
    display_header_with_logos()
    show_login_page()
        
else:
    display_header_with_logos()
    
    active = st.session_state.get("active_tool", None)
    col1, col2 = st.columns([3, 1])
    with col1:
        if active == "analyser":
            st.markdown("""
            This tool helps analyze case studies against the CBC-India AGK Case Study Review Rubric.
            Upload your case study document, and the AI will evaluate it based on four key assessment areas:
            1. Structure, Chronology & Logical Flow (30%)
            2. Language, Citations & Factual Accuracy (30%)
            3. Alignment with Teaching Note, Sector & Competencies (15%)
            4. Overall Effectiveness & Impact (25%)
            """)
        elif active == "caseconnect":
            st.markdown(f"""
            CaseConnect helps you discover relevant governance case studies from the AGK repository 
            for your teaching programme. Upload your course outline and answer a few questions — 
            the tool will recommend cases aligned with your course design, competencies, and sector.
            
            *Referring to {CASE_COUNT} case studies from the AGK repository.*
            """)
    
    with col2:
        st.markdown(f"""
        <div class="user-profile">
            <div class="avatar">{st.session_state.username[0].upper()}</div>
            <div class="info">
                <p class="text-[14px]"><strong>{st.session_state.username}</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Logout", key="logout_button"):
            logout_user()
            st.rerun()

# Initialize session state variables if they don't exist
if 'active_tool' not in st.session_state:
    st.session_state.active_tool = None
if 'case_study_text' not in st.session_state:
    st.session_state.case_study_text = ""
if 'teaching_note_text' not in st.session_state:
    st.session_state.teaching_note_text = ""
if 'case_study_analysis' not in st.session_state:
    st.session_state.case_study_analysis = None
if 'case_study_summary' not in st.session_state:
    st.session_state.case_study_summary = ""
if 'assessment_results' not in st.session_state:
    st.session_state.assessment_results = {}
if 'document_name' not in st.session_state:
    st.session_state.document_name = ""
if 'teaching_note_name' not in st.session_state:
    st.session_state.teaching_note_name = ""
if 'loaded_from_history' not in st.session_state:
    st.session_state.loaded_from_history = False
if 'weighted_scores' not in st.session_state:
    st.session_state.weighted_scores = None
if 'competency_mapping' not in st.session_state:
    st.session_state.competency_mapping = None
if 'sector_tags' not in st.session_state:
    st.session_state.sector_tags = []
if 'sector_subthemes' not in st.session_state:
    st.session_state.sector_subthemes = {}
if 'keywords' not in st.session_state:
    st.session_state.keywords = []
if 'sidebar_tab' not in st.session_state:
    st.session_state.sidebar_tab = "New Assessment"
if 'caseconnect_results' not in st.session_state:
    st.session_state.caseconnect_results = None
if 'caseconnect_curriculum_text' not in st.session_state:
    st.session_state.caseconnect_curriculum_text = ""

# Sidebar with simple navigation (only for logged-in users)
with st.sidebar:
    if st.session_state.logged_in and st.session_state.get("active_tool") is not None:
        if st.button("← Back to Home", key="back_home_btn", use_container_width=True):
            st.session_state.active_tool = None
            st.session_state.caseconnect_results = None
            st.session_state.caseconnect_curriculum_text = ""
            st.rerun()

        st.markdown("---")

        if st.session_state.active_tool == "analyser":
            selected = option_menu(
                menu_title=None,
                options=["New Assessment", "History"],
                icons=["file-earmark-text", "clock-history"],
                menu_icon="cast",
                default_index=0 if st.session_state.sidebar_tab == "New Assessment" else 1,
                orientation="vertical",
                styles={
                    "container": {"padding": "5px", "background-color": "#fafafa"},
                    "icon": {"color": "#1E3A8A", "font-size": "18px"},
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "left",
                        "margin": "5px",
                        "padding": "10px 15px",
                        "--hover-color": "#eee",
                        "border-radius": "8px"
                    },
                    "nav-link-selected": {
                        "background-color": "#074fa5",
                        "color": "white",
                        "font-weight": "600"
                    },
                }
            )

            st.markdown("""
            <style>
            div[data-testid="stVerticalBlock"] div.nav-link-selected i {
                color: white !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if selected != st.session_state.sidebar_tab:
                st.session_state.sidebar_tab = selected
                
                if selected == "New Assessment":
                    if not st.session_state.get('loaded_from_history', False):
                        st.session_state.case_study_text = ""
                        st.session_state.teaching_note_text = ""
                        st.session_state.case_study_analysis = None
                        st.session_state.case_study_summary = ""
                        st.session_state.assessment_results = {}
                        if 'recommendations' in st.session_state:
                            st.session_state.recommendations = ""
                        st.session_state.document_name = ""
                        st.session_state.teaching_note_name = ""
                        st.session_state.weighted_scores = None
                        st.session_state.competency_mapping = None
                        st.session_state.sector_tags = []
                        st.session_state.sector_subthemes = {}
                        st.session_state.keywords = []
                    else:
                        st.session_state.loaded_from_history = False
                elif selected == "History":
                    if 'selected_assessment' in st.session_state:
                        st.session_state.selected_assessment = None
                
                st.rerun()
            
            st.markdown("---")
        
        if st.session_state.sidebar_tab == "New Assessment" and st.session_state.get("active_tool") == "analyser":
            st.header("Upload Documents")
            
            st.subheader("1. Case Study Document")
            st.caption("Upload the case study document (PDF or DOCX)")
            case_study_file = st.file_uploader("Choose Case Study file", type=["pdf", "docx"], key="case_study_uploader")
            
            if case_study_file is not None:
                st.session_state.document_name = case_study_file.name
                
                # Process the uploaded file
                try:
                    if case_study_file.type == "application/pdf":
                        st.session_state.case_study_text = extract_text_from_pdf(case_study_file)
                    elif case_study_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        st.session_state.case_study_text = extract_text_from_docx(case_study_file)
                    
                    st.success(f"Case Study: {case_study_file.name}")
                    text_length = len(st.session_state.case_study_text)
                    st.info(f"Extracted {text_length} characters")
                    
                except Exception as e:
                    st.error(f"Error processing case study: {str(e)}")
            
            st.markdown("---")
            
            st.subheader("2. Teaching Note Document")
            st.caption("Upload the corresponding Teaching Note (PDF or DOCX)")
            teaching_note_file = st.file_uploader("Choose Teaching Note file", type=["pdf", "docx"], key="teaching_note_uploader")
            
            if teaching_note_file is not None:
                st.session_state.teaching_note_name = teaching_note_file.name
                
                # Process the uploaded file
                try:
                    if teaching_note_file.type == "application/pdf":
                        st.session_state.teaching_note_text = extract_text_from_pdf(teaching_note_file)
                    elif teaching_note_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        st.session_state.teaching_note_text = extract_text_from_docx(teaching_note_file)
                    
                    st.success(f"Teaching Note: {teaching_note_file.name}")
                    tn_length = len(st.session_state.teaching_note_text)
                    st.info(f"Extracted {tn_length} characters")
                    
                except Exception as e:
                    st.error(f"Error processing teaching note: {str(e)}")
            
            # Action buttons
            st.subheader("Analysis Actions")
            
            # Check if both documents are uploaded
            both_docs_uploaded = st.session_state.case_study_text and st.session_state.teaching_note_text
            
            if both_docs_uploaded:
                st.success("Both documents uploaded. Ready for assessment.")
                
                if st.button("Generate Summary"):
                    with st.spinner("Generating case study summary..."):
                        prompt = f"""
                        Please provide a concise summary of the following case study document. 
                        Focus on the main theme, key events, stakeholders involved, and outcomes:
                        
                        {st.session_state.case_study_text[:4000]}
                        
                        {PROMPT_EXCLUSION_INSTRUCTIONS}
                        """
                        
                        st.session_state.case_study_summary = call_openai_api(prompt)
                    
                    with st.spinner("Generating sector tags and keywords..."):
                        sector_prompt = f"""
                        You are an expert at classifying case studies by sector, sub-theme, and keywords.
                        
                        Based on the case study below, identify the applicable sectors, sub-themes, and keywords.
                        
                        === AVAILABLE SECTORS AND SUB-THEMES ===
                        {json.dumps(SECTOR_MAPPING, indent=2)}
                        
                        === CASE STUDY ===
                        {st.session_state.case_study_text[:5000]}
                        
                        {PROMPT_EXCLUSION_INSTRUCTIONS}
                        
                        Provide your analysis in the following JSON structure:
                        {{
                            "sectors": ["sector1", "sector2"],
                            "subthemes": {{"sector1": ["subtheme1", "subtheme2"], "sector2": ["subtheme1"]}},
                            "keywords": ["keyword1", "keyword2", "keyword3"]
                        }}
                        
                        Important:
                        - Select ONLY sectors from the provided SECTOR_MAPPING list
                        - For each selected sector, identify relevant sub-themes from that sector's sub-theme list
                        - Generate 5-10 keywords that a general public audience would use to search for this case study
                        - Keywords should be simple, commonly used terms
                        """
                        
                        tags_result = call_openai_api(sector_prompt, response_format="json_object")
                        if isinstance(tags_result, dict):
                            st.session_state.sector_tags = tags_result.get("sectors", [])
                            st.session_state.sector_subthemes = tags_result.get("subthemes", {})
                            st.session_state.keywords = tags_result.get("keywords", [])
                
                if st.button("Perform Full Assessment"):
                    progress_text = st.empty()
                    progress_bar = st.progress(0)
                    
                    st.session_state.assessment_results = {}
                    st.session_state.writing_findings = []
                    
                    # Count total criteria for progress tracking (add 1 for competency mapping)
                    total_criteria = sum(len(ASSESSMENT_CRITERIA[area_id]) for area_id in ASSESSMENT_AREAS) + 1
                    processed_criteria = 0
                    
                    # Process each assessment area
                    for area_id, area_info in ASSESSMENT_AREAS.items():
                        progress_text.text(f"Analyzing: {area_info['name']}")
                        criteria = ASSESSMENT_CRITERIA[area_id]
                        
                        st.session_state.assessment_results[area_id] = {}
                        
                        # Process each criterion in this area (one at a time)
                        for criterion_id, criterion_info in criteria.items():
                            criterion_progress = f"Evaluating: {criterion_info['name']} ({processed_criteria+1}/{total_criteria})"
                            progress_text.text(criterion_progress)
                            
                            is_informational = criterion_info.get('informational', False)
                            max_score = criterion_info.get('max_score', 3) if not is_informational else 0
                            scoring_logic = criterion_info.get('scoring_logic', '')
                            agent_prompt = criterion_info.get('prompt', criterion_info['description'])
                            requires_tn = criterion_info.get('requires_teaching_note', False)
                            
                            if is_informational:
                                prompt = f"""
                                You are a case study evaluation expert using the CBC-India AGK Case Study Review Rubric.
                                
                                Provide a detailed narrative analysis for the following criterion. Do NOT provide a score — this is an informational assessment only.
                                
                                **Criterion:** {criterion_info['name']}
                                **Description:** {criterion_info['description']}
                                **Analysis Task:** {agent_prompt}
                                
                                === CASE STUDY DOCUMENT ===
                                {st.session_state.case_study_text[:5000]}
                                
                                === TEACHING NOTE DOCUMENT ===
                                {st.session_state.teaching_note_text[:5000]}
                                
                                Provide your analysis in the following JSON structure:
                                {{
                                    "narrative": [a detailed narrative analysis addressing the criterion, as a single string],
                                    "document_reference": [specific sections or content from BOTH documents that supports this analysis as a single string]
                                }}
                                
                                {PROMPT_EXCLUSION_INSTRUCTIONS}
                                
                                Important:
                                - Do NOT include a score — this criterion is informational only
                                - Provide a thorough, well-structured narrative
                                - Ensure narrative and document_reference are STRINGS, not lists
                                """
                            elif requires_tn or area_id == "area3":
                                prompt = f"""
                                You are a case study evaluation expert using the CBC-India AGK Case Study Review Rubric.
                                
                                Evaluate the alignment between the case study and its teaching note against this specific criterion:
                                
                                **Criterion:** {criterion_info['name']}
                                **Description:** {criterion_info['description']}
                                **Evaluation Task:** {agent_prompt}
                                **Scoring Guide:** {scoring_logic}
                                **Maximum Score:** {max_score}
                                
                                === CASE STUDY DOCUMENT ===
                                {st.session_state.case_study_text[:5000]}
                                
                                === TEACHING NOTE DOCUMENT ===
                                {st.session_state.teaching_note_text[:5000]}
                                
                                Provide an analysis with the following JSON structure:
                                {{
                                    "score": [a number between 0 and {max_score}, following the scoring guide above],
                                    "reasoning": [detailed explanation of why this score was given, based on the scoring logic, as a single string],
                                    "document_reference": [specific sections or content from BOTH documents that supports this assessment as a single string]
                                }}
                                
                                {PROMPT_EXCLUSION_INSTRUCTIONS}
                                
                                Important:
                                - The score MUST be an integer between 0 and {max_score}
                                - Follow the scoring logic exactly: {scoring_logic}
                                - Apply the rubric strictly and consistently — use the scoring guide as the sole basis for the score
                                - Do NOT give benefit of the doubt — if evidence is absent or ambiguous, score lower
                                - Be deterministic: the same document should always receive the same score for this criterion
                                - Provide specific evidence from BOTH the case study AND teaching note
                                - Ensure reasoning and document_reference are STRINGS, not lists
                                """
                            else:
                                prompt = f"""
                                You are a case study evaluation expert using the CBC-India AGK Case Study Review Rubric.
                                
                                Evaluate the following case study document against this specific criterion:
                                
                                **Criterion:** {criterion_info['name']}
                                **Description:** {criterion_info['description']}
                                **Evaluation Task:** {agent_prompt}
                                **Scoring Guide:** {scoring_logic}
                                **Maximum Score:** {max_score}
                                
                                Case Study Document:
                                {st.session_state.case_study_text[:6000]}
                                
                                Provide an analysis with the following JSON structure:
                                {{
                                    "score": [a number between 0 and {max_score}, following the scoring guide above],
                                    "reasoning": [detailed explanation of why this score was given, based on the scoring logic, as a single string],
                                    "document_reference": [specific sections or content from the document that supports this assessment as a single string]
                                }}
                                
                                {PROMPT_EXCLUSION_INSTRUCTIONS}
                                
                                Important:
                                - The score MUST be an integer between 0 and {max_score}
                                - Follow the scoring logic exactly: {scoring_logic}
                                - Apply the rubric strictly and consistently — use the scoring guide as the sole basis for the score
                                - Do NOT give benefit of the doubt — if evidence is absent or ambiguous, score lower
                                - Be deterministic: the same document should always receive the same score for this criterion
                                - Provide specific evidence from the document
                                - Ensure reasoning and document_reference are STRINGS, not lists
                                """
                            
                            with st.spinner(f"Analyzing {criterion_info['name']}..."):
                                result = call_openai_api(prompt, response_format="json_object", temperature=0.1)
                                
                                if is_informational:
                                    if isinstance(result.get("narrative"), list):
                                        result["narrative"] = ". ".join(result["narrative"])
                                    if not result.get("narrative"):
                                        result["narrative"] = result.get("reasoning", "No analysis available.")
                                    if isinstance(result.get("document_reference"), list):
                                        result["document_reference"] = ". ".join(result["document_reference"])
                                    result["score"] = 0
                                    result["informational"] = True
                                else:
                                    if isinstance(result.get("reasoning"), list):
                                        result["reasoning"] = ". ".join(result["reasoning"])
                                    if isinstance(result.get("document_reference"), list):
                                        result["document_reference"] = ". ".join(result["document_reference"])
                                    
                                    score = result.get("score", 0)
                                    if isinstance(score, (int, float)):
                                        result["score"] = min(max(0, int(score)), max_score)
                                    else:
                                        result["score"] = 0
                                
                                st.session_state.assessment_results[area_id][criterion_id] = result
                            
                            # Update progress
                            processed_criteria += 1
                            progress_bar.progress(processed_criteria / total_criteria)
                    
                    progress_text.text("Running Writing Quality Analysis...")
                    with st.spinner("Analysing full document for writing issues..."):
                        writing_findings = analyze_writing_quality_chunked(
                            st.session_state.case_study_text,
                            exclusion_instructions=PROMPT_EXCLUSION_INSTRUCTIONS
                        )
                        st.session_state.writing_findings = writing_findings

                    # Generate KCM Competency Mapping
                    progress_text.text("Mapping Karmayogi Competencies...")
                    from assessment_criteria import KCM_COMPETENCIES
                    
                    kcm_prompt = f"""
                    You are an expert in the Karmayogi Competency Model (KCM) used by the Government of India for civil service capacity building.
                    
                    Based on the case study below, identify the TOP 3-4 SUB-COMPETENCIES (not just the broad competencies) that are most relevant to this case.
                    
                    === KARMAYOGI COMPETENCY MODEL (Competencies & their Sub-competencies) ===
                    
                    BEHAVIORAL:
                    - Integrity & Ethics: Honesty, Fairness, Moral Courage, Consistency, Transparency
                    - Adaptability: Flexibility, Openness to Change, Resilience, Versatility
                    - Compassion: Empathy, Sensitivity, Kindness, Supportive
                    - Perpetual Learning: Self-Development, Inquisitiveness, Knowledge Sharing, Reflective Practice
                    - Commitment & Purpose: Dedication, Goal Orientation, Public Service Value, Mission Focus
                    - Inner Calm & Balance: Emotional Intelligence, Stress Management, Equanimity, Self-Regulation
                    - Attention to Detail: Precision, Thoroughness, Meticulousness, Quality Consciousness
                    
                    FUNCTIONAL:
                    - Citizen Centricity: User-Centric Design, Responsive Service, Public Interest, Service Delivery Focus
                    - Accountability: Responsibility, Transparency, Results Orientation, Ethical Governance
                    - Innovation & Technology: Digital Literacy, Creative Problem Solving, Process Improvement, Tech Adoption
                    - Collaboration & Unity: Teamwork, Stakeholder Engagement, Partnership Building, Conflict Resolution
                    - Strategic Thinking: Visionary Planning, Systems Thinking, Policy Analysis, Risk Assessment
                    - Inclusive Development: Social Equity, Diversity & Inclusion, Sustainable Growth, Poverty Alleviation
                    - Cultural Awareness (Garva): Heritage Appreciation, Local Context Awareness, Indigenous Knowledge Support, National Identity
                    - Service Excellence: Standard Setting, Efficiency, Continuous Improvement, Benchmarking
                    
                    === CASE STUDY ===
                    {st.session_state.case_study_text[:5000]}
                    
                    {PROMPT_EXCLUSION_INSTRUCTIONS}
                    
                    Provide your analysis in the following JSON structure:
                    {{
                        "behavioral_competencies": [
                            {{
                                "name": "sub-competency name",
                                "parent_competency": "broad competency name",
                                "justification": "brief justification of why this sub-competency is relevant"
                            }}
                        ],
                        "functional_competencies": [
                            {{
                                "name": "sub-competency name", 
                                "parent_competency": "broad competency name",
                                "justification": "brief justification of why this sub-competency is relevant"
                            }}
                        ]
                    }}
                    
                    Important:
                    - Identify specific SUB-COMPETENCIES from the provided list.
                    - Select 2 behavioral and 2 functional sub-competencies (total 4).
                    - Ensure all values are strings.
                    """
                    
                    with st.spinner("Mapping Karmayogi Competencies..."):
                        competency_result = call_openai_api(kcm_prompt, response_format="json_object")
                        st.session_state.competency_mapping = competency_result
                    
                    processed_criteria += 1
                    progress_bar.progress(processed_criteria / total_criteria)
                    
                    progress_text.text("Generating sector tags and keywords...")
                    with st.spinner("Generating sector tags and keywords..."):
                        sector_prompt = f"""
                        You are an expert at classifying case studies by sector, sub-theme, and keywords.
                        
                        Based on the case study below, identify the applicable sectors, sub-themes, and keywords.
                        
                        === AVAILABLE SECTORS AND SUB-THEMES ===
                        {json.dumps(SECTOR_MAPPING, indent=2)}
                        
                        === CASE STUDY ===
                        {st.session_state.case_study_text[:5000]}
                        
                        {PROMPT_EXCLUSION_INSTRUCTIONS}
                        
                        Provide your analysis in the following JSON structure:
                        {{
                            "sectors": ["sector1", "sector2"],
                            "subthemes": {{"sector1": ["subtheme1", "subtheme2"], "sector2": ["subtheme1"]}},
                            "keywords": ["keyword1", "keyword2", "keyword3"]
                        }}
                        
                        Important:
                        - Select ONLY sectors from the provided SECTOR_MAPPING list
                        - For each selected sector, identify relevant sub-themes from that sector's sub-theme list
                        - Generate 5-10 keywords that a general public audience would use to search for this case study
                        - Keywords should be simple, commonly used terms
                        """
                        
                        tags_result = call_openai_api(sector_prompt, response_format="json_object")
                        if isinstance(tags_result, dict):
                            st.session_state.sector_tags = tags_result.get("sectors", [])
                            st.session_state.sector_subthemes = tags_result.get("subthemes", {})
                            st.session_state.keywords = tags_result.get("keywords", [])
                    
                    # Calculate weighted scores after assessment
                    st.session_state.weighted_scores = calculate_weighted_score(st.session_state.assessment_results)
                    
                    progress_text.text("Assessment complete!")
                    progress_bar.progress(100)
                    st.success("Case study assessment completed successfully!")
            else:
                # Show which documents are missing
                if not st.session_state.case_study_text and not st.session_state.teaching_note_text:
                    st.warning("Please upload both the Case Study and Teaching Note documents to begin assessment.")
                elif not st.session_state.case_study_text:
                    st.warning("Please upload the Case Study document.")
                else:
                    st.warning("Please upload the Teaching Note document.")
                
        elif st.session_state.sidebar_tab == "History" and st.session_state.get("active_tool") == "analyser":
            st.header("Assessment History")
            
            if st.session_state.user_id:
                try:
                    # Get user's assessment history with error handling
                    with st.spinner("Loading assessment history..."):
                        assessments = get_user_assessments(st.session_state.user_id)
                    
                    # Refresh button for history
                    if st.button("🔄 Refresh History"):
                        st.rerun()
                    
                    if assessments and len(assessments) > 0:
                        st.success(f"Found {len(assessments)} saved assessments.")
                        
                        for assessment in assessments:
                            with st.container():
                                # Simple list of assessments without custom CSS
                                st.subheader(assessment.document_name)
                                st.caption(f"Date: {assessment.created_at.strftime('%Y-%m-%d %H:%M')}")
                                
                                # Simple load button
                                if st.button("Load Assessment", key=f"load_{assessment.id}"):
                                    try:
                                        # Load assessment data into session state with history flag
                                        st.session_state.document_name = assessment.document_name
                                        st.session_state.case_study_summary = assessment.policy_summary
                                        st.session_state.assessment_results = assessment.get_results_dict()
                                        st.session_state.recommendations = assessment.recommendations
                                        st.session_state.case_study_text = "Loaded from history"  # Placeholder for text
                                        
                                        results_dict = st.session_state.assessment_results
                                        st.session_state.sector_tags = results_dict.get('_sector_tags', [])
                                        st.session_state.sector_subthemes = results_dict.get('_sector_subthemes', {})
                                        st.session_state.keywords = results_dict.get('_keywords', [])
                                        
                                        # Recalculate weighted scores
                                        st.session_state.weighted_scores = calculate_weighted_score(st.session_state.assessment_results)
                                        
                                        # Set a special flag to indicate this is from history
                                        st.session_state.loaded_from_history = True
                                        
                                        # Switch to New Assessment tab
                                        st.session_state.sidebar_tab = "New Assessment"
                                        
                                        # Show a success message
                                        st.success(f"Successfully loaded assessment: {assessment.document_name}")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error loading assessment: {str(e)}")
                                
                                st.markdown("---")
                    else:
                        st.info("No assessment history found. Complete an assessment and save it to see it here.")
                        st.write("After saving an assessment, click the 'Refresh History' button to see it listed here.")
                except Exception as e:
                    st.error(f"Error retrieving assessment history: {str(e)}")
                    st.info("Please try refreshing or check database connection.")
        if st.session_state.get("active_tool") == "caseconnect":
            st.header("Course Outline")
            st.caption("Upload your syllabus, session plan, or curriculum outline (optional but encouraged)")
            curriculum_file = st.file_uploader("Choose file", type=["pdf", "docx"], key="curriculum_uploader")
            
            if curriculum_file is not None:
                try:
                    if curriculum_file.type == "application/pdf":
                        st.session_state.caseconnect_curriculum_text = extract_text_from_pdf(curriculum_file)
                    elif curriculum_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        st.session_state.caseconnect_curriculum_text = extract_text_from_docx(curriculum_file)
                    st.success(f"Uploaded: {curriculum_file.name}")
                    st.info(f"Extracted {len(st.session_state.caseconnect_curriculum_text)} characters")
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
            
            st.markdown("---")
            st.info(f"Referencing {CASE_COUNT} case studies from the AGK repository")

    elif st.session_state.logged_in:
        st.info("Choose a tool from the home page to get started.")
    else:
        st.info("Please login to access the tools.")

# Main content area
if st.session_state.get("active_tool") is None and st.session_state.logged_in:
    st.header("Assessment Framework")
    st.write("The Case Study Analyser uses the CBC-India AGK Case Study Review Rubric with four weighted assessment areas:")
    
    for area_id, area_info in ASSESSMENT_AREAS.items():
        with st.expander(f"{area_info['name']} (Weight: {area_info['weight']*100:.0f}%, Total Points: {area_info['total_points']})"):
            st.write(area_info["description"])
            st.subheader("Criteria:")
            criteria = ASSESSMENT_CRITERIA[area_id]
            for criterion_id, criterion_info in criteria.items():
                if criterion_info.get("informational", False):
                    st.write(f"**{criterion_info['name']}** (Informational — no score)")
                    st.write(f"  - {criterion_info['description']}")
                else:
                    st.write(f"**{criterion_info['name']}** (Max: {criterion_info.get('max_score', 3)} points)")
                    st.write(f"  - {criterion_info['description']}")
                    st.write(f"  - *Scoring:* {criterion_info.get('scoring_logic', '')}")

    st.markdown("---")

    tool_col1, tool_col2 = st.columns(2)
    
    with tool_col1:
        st.markdown("""
        <div class="card" style="min-height: 280px;">
            <h3 style="color: #1E3A8A; margin-top: 0;">Case Study Analyser</h3>
            <p>Evaluate case studies against the CBC-India AGK Case Study Review Rubric. Upload your case study and teaching note documents, and the AI will assess them across four weighted areas — Structure, Language, Alignment, and Effectiveness — generating a detailed scoring report with recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Started — Case Study Analyser", key="start_analyser", use_container_width=True):
            st.session_state.active_tool = "analyser"
            st.session_state.sidebar_tab = "New Assessment"
            st.rerun()
    
    with tool_col2:
        st.markdown(f"""
        <div class="card" style="min-height: 280px;">
            <h3 style="color: #1E3A8A; margin-top: 0;">CaseConnect</h3>
            <p>Discover relevant governance case studies from the AGK repository for your teaching programme. Upload your course outline and answer a short questionnaire — the tool will recommend cases aligned with your course design, competencies, and sector. Currently referencing {CASE_COUNT} case studies.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Started — CaseConnect", key="start_caseconnect", use_container_width=True):
            st.session_state.active_tool = "caseconnect"
            st.rerun()

elif st.session_state.get("active_tool") == "caseconnect" and st.session_state.logged_in:
    st.header("Course Discovery Questionnaire")
    st.write("Answer the following questions to help us recommend the most relevant case studies for your teaching programme.")

    all_competency_names = []
    for category in ["behavioral", "functional"]:
        for comp_key, comp_data in KCM_COMPETENCIES.get(category, {}).items():
            all_competency_names.append(comp_data["name"])

    all_sectors = list(SECTOR_MAPPING.keys())

    with st.form("caseconnect_form"):
        q_learners = st.text_area(
            "1. Who are the learners?",
            placeholder="e.g., Mid-career IAS officers, State government training faculty, Fresh recruits to civil services...",
            height=80
        )
        
        q_objective = st.text_area(
            "2. What is the primary learning objective?",
            placeholder="e.g., Understanding stakeholder coordination in large infrastructure projects, Developing leadership in crisis situations...",
            height=80
        )
        
        q_competencies = st.multiselect(
            "3. Which competencies are you focusing on? (Karmayogi Competency Model)",
            options=all_competency_names,
            default=[]
        )
        
        q_duration = st.selectbox(
            "4. Duration of the session?",
            options=["30 minutes", "60 minutes", "90 minutes", "2 hours", "Half day (3-4 hours)", "Full day", "Multi-day programme"]
        )
        
        q_sector = st.multiselect(
            "5. What is the Sector/Theme?",
            options=all_sectors,
            default=[]
        )

        submitted = st.form_submit_button("Find Matching Cases", use_container_width=True)

    if submitted:
        if not q_learners and not q_objective and not q_competencies and not q_sector:
            st.warning("Please fill in at least one question to get recommendations.")
        else:
            questionnaire = {
                "learners": q_learners,
                "objective": q_objective,
                "competencies": q_competencies,
                "duration": q_duration,
                "sector": ", ".join(q_sector) if q_sector else ""
            }
            
            with st.spinner("Analysing your inputs and finding matching cases..."):
                st.session_state.caseconnect_results = run_caseconnect_analysis(
                    questionnaire,
                    st.session_state.caseconnect_curriculum_text,
                    CASE_DATABASE_TEXT,
                    CASE_COUNT
                )

    if st.session_state.caseconnect_results:
        results = st.session_state.caseconnect_results
        
        st.markdown("---")
        st.header("Recommended Cases for Your Course")
        
        case_recs = results.get("case_recommendations", [])
        if case_recs:
            import html as html_mod
            for i, rec in enumerate(case_recs, 1):
                with st.expander(f"**{i}. {rec.get('case_title', 'Untitled')}**", expanded=(i <= 3)):
                    st.write(f"**Why it fits:** {rec.get('why_it_fits', '')}")

                    themes = rec.get("key_themes", [])
                    if isinstance(themes, str):
                        themes = [themes]
                    if themes:
                        theme_badges = " ".join([f'<span class="score-badge" style="background-color:#EFF6FF;color:#1E3A8A;border:1px solid #BFDBFE;">{html_mod.escape(str(t))}</span>' for t in themes])
                        st.markdown(f"**Key Themes:** {theme_badges}", unsafe_allow_html=True)

                    comps = rec.get("relevant_competencies", [])
                    if isinstance(comps, str):
                        comps = [comps]
                    if comps:
                        comp_badges = " ".join([f'<span class="score-badge score-good">{html_mod.escape(str(c))}</span>' for c in comps])
                        st.markdown(f"**Relevant Competencies:** {comp_badges}", unsafe_allow_html=True)

                    discussion = rec.get("discussion_points", [])
                    if isinstance(discussion, str):
                        discussion = [discussion]
                    if discussion:
                        st.write("**Discussion Points for Classroom:**")
                        for dp_idx, dp in enumerate(discussion, 1):
                            st.write(f"{dp_idx}. {dp}")

                    dur = rec.get("suggested_duration", "")
                    if dur:
                        st.write(f"**Suggested Duration:** {dur}")

                    igot_link = _resolve_igot_link(rec.get("case_title", ""))
                    if igot_link:
                        safe_link = html_mod.escape(igot_link)
                        st.markdown(
                            f'<a href="{safe_link}" target="_blank" style="display:inline-block;background-color:#074fa5;color:white;padding:8px 20px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px;margin-top:8px;">Go to Case Study on iGOT ↗</a>',
                            unsafe_allow_html=True
                        )
        else:
            st.info("No specific case recommendations were generated. Try providing more details in the questionnaire.")

        module_suggestions = results.get("module_suggestions", [])
        if module_suggestions:
            st.markdown("---")
            st.header("Module-Level Suggestions")
            for mod in module_suggestions:
                st.subheader(mod.get("module_name", "Module"))
                mod_cases = mod.get("recommended_cases", [])
                if mod_cases:
                    for mc in mod_cases:
                        st.write(f"- **{mc.get('case_title', '')}** — {mc.get('relevance', '')}")

        teaching_strategy = results.get("teaching_strategy", "")
        if teaching_strategy:
            st.markdown("---")
            st.header("Teaching Strategy")
            st.write(teaching_strategy)

        additional = results.get("additional_notes", "")
        if additional:
            st.markdown("---")
            st.header("Additional Notes")
            st.write(additional)

elif st.session_state.get("active_tool") == "analyser" and st.session_state.case_study_text:
    # Document info section
    st.header("Document Information")
    st.write(f"**Filename:** {st.session_state.document_name}")
    
    # Summary section
    st.header("Case Study Summary")
    if st.session_state.case_study_summary:
        st.write(st.session_state.case_study_summary)
    else:
        st.info("Click 'Generate Summary' to create a summary of the case study document")
    
    if st.session_state.get('sector_tags'):
        st.header("Sector Tags & Keywords")
        
        sector_badges = " ".join([
            f'<span style="display: inline-block; padding: 5px 14px; margin: 4px; background-color: #DBEAFE; color: #1E40AF; border-radius: 20px; font-weight: 600; font-size: 0.9em;">{tag}</span>'
            for tag in st.session_state.sector_tags
        ])
        st.markdown(f"**Sector Tags:** {sector_badges}", unsafe_allow_html=True)
        
        subthemes = st.session_state.get('sector_subthemes', {})
        if subthemes:
            st.markdown("**Sub-themes:**")
            for sector, themes in subthemes.items():
                if themes:
                    theme_badges = " ".join([
                        f'<span style="display: inline-block; padding: 3px 10px; margin: 3px; background-color: #E0F2FE; color: #0369A1; border-radius: 15px; font-size: 0.85em;">{t}</span>'
                        for t in themes
                    ])
                    st.markdown(f"&nbsp;&nbsp;*{sector}:* {theme_badges}", unsafe_allow_html=True)
        
        keywords = st.session_state.get('keywords', [])
        if keywords:
            keyword_badges = " ".join([
                f'<span style="display: inline-block; padding: 4px 12px; margin: 3px; background-color: #F3F4F6; color: #374151; border-radius: 15px; font-size: 0.85em;">{kw}</span>'
                for kw in keywords
            ])
            st.markdown(f"**Keywords:** {keyword_badges}", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Assessment Results
    if st.session_state.assessment_results:
        st.header("Assessment Results")
        
        # Display Overall Composite Score prominently
        if st.session_state.weighted_scores:
            ws = st.session_state.weighted_scores
            final_score = ws["final_composite_score"]
            grade_label = get_grade_label(final_score)
            
            # Create a prominent score display
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            with col2:
                # Determine color based on grade
                if grade_label == "Excellent":
                    color = "#28a745"
                    badge_class = "score-excellent"
                elif grade_label == "Good":
                    color = "#3B82F6"
                    badge_class = "score-good"
                elif grade_label == "Satisfactory":
                    color = "#ffc107"
                    badge_class = "score-satisfactory"
                elif grade_label == "Needs Improvement":
                    color = "#fd7e14"
                    badge_class = "score-needs-improvement"
                else:
                    color = "#dc3545"
                    badge_class = "score-poor"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px; margin-bottom: 20px;">
                    <h2 style="margin: 0; color: #1E3A8A;">Final Composite Score</h2>
                    <h1 style="font-size: 3.5em; margin: 10px 0; color: {color};">{final_score:.1f}%</h1>
                    <span class="score-badge {badge_class}" style="font-size: 1.2em; padding: 8px 20px;">{grade_label}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Display weighted area breakdown
            st.subheader("Weighted Area Scores")
            
            # Create columns for area scores
            area_cols = st.columns(4)
            for i, (area_id, area_info) in enumerate(ASSESSMENT_AREAS.items()):
                with area_cols[i]:
                    area_score_data = ws["area_scores"].get(area_id, {})
                    weighted_data = ws["weighted_scores"].get(area_id, {})
                    
                    score = area_score_data.get("score", 0)
                    max_score = area_score_data.get("max_score", 1)
                    percentage = area_score_data.get("percentage", 0)
                    weight = weighted_data.get("weight", 0) * 100
                    contribution = weighted_data.get("weighted_contribution", 0) * 100
                    
                    st.markdown(f"""
                    <div style="text-align: center; padding: 15px; background-color: #F9FAFB; border-radius: 10px; border: 1px solid #E5E7EB; min-height: 250px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <p style="font-size: 0.85em; color: #6B7280; margin-bottom: 10px; line-height: 1.2; font-weight: 500;">{area_info['name']}</p>
                            <h3 style="margin: 10px 0; color: #1E3A8A; font-size: 1.6em;">{score}/{max_score}</h3>
                            <p style="font-size: 0.95em; color: #4B5563; margin: 0; font-weight: 500;">({percentage:.1f}%)</p>
                        </div>
                        <div style="border-top: 1px solid #E5E7EB; padding-top: 10px; margin-top: 10px;">
                            <p style="font-size: 0.8em; color: #9CA3AF; margin-bottom: 2px;">Weight: {weight:.0f}%</p>
                            <p style="font-size: 0.85em; color: #059669; margin: 0; font-weight: 600;">Contribution: {contribution:.1f}%</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Action buttons section
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate recommendations for case study improvement
            if 'recommendations' not in st.session_state or not st.session_state.recommendations:
                with st.spinner("Generating recommendations..."):
                    # Prepare data for recommendations generation
                    low_scores = []
                    for area_id, area_results in st.session_state.assessment_results.items():
                        area_name = ASSESSMENT_AREAS[area_id]["name"]
                        for criterion_id, result in area_results.items():
                            criterion_info = ASSESSMENT_CRITERIA[area_id][criterion_id]
                            if criterion_info.get("informational", False):
                                continue
                            criterion_name = criterion_info["name"]
                            max_score = criterion_info.get("max_score", 3)
                            score = result.get("score", 0)
                            
                            if score < max_score * 0.5:
                                low_scores.append({
                                    "area": area_name,
                                    "criterion": criterion_name,
                                    "score": score,
                                    "max_score": max_score,
                                    "reasoning": result.get("reasoning", "")
                                })
                    
                    # Generate recommendations based on low scores
                    if low_scores:
                        prompt = f"""
                        Based on the case study assessment using the CBC-India AGK Case Study Review Rubric, 
                        please generate 5-8 concrete, actionable recommendations to improve the case study.
                        
                        Focus on addressing the following areas with low scores:
                        
                        {json.dumps(low_scores, indent=2)}
                        
                        Format each recommendation as a numbered entry starting with "Recommendation 1:", 
                        "Recommendation 2:", etc. Each recommendation should be a complete, self-contained 
                        paragraph without line breaks or bullets in the middle of sentences.
                        
                        {PROMPT_EXCLUSION_INSTRUCTIONS}
                        
                        Your recommendations should be:
                        1. Specific and actionable for case study improvement
                        2. Practical to implement
                        3. Directly address deficiencies identified in the assessment
                        4. Aligned with the AGK case study writing standards
                        5. Written in complete sentences with proper punctuation
                        
                        Example format:
                        Recommendation 1: [Complete sentence describing specific action] to address [specific issue]. 
                        The recommendation should include enough detail to be actionable but be contained in a single complete paragraph.
                        """
                        
                        st.session_state.recommendations = call_openai_api(prompt)
                    else:
                        st.session_state.recommendations = "The case study generally scores well across all assessment areas. Consider maintaining the current approach while reviewing any minor areas for potential enhancement."
            
            # Save to history button (only shown to logged-in users)
            if st.session_state.logged_in:
                if st.button("💾 Save to History", use_container_width=True):
                    if st.session_state.user_id:
                        # Save assessment to database
                        try:
                            results_to_save = dict(st.session_state.assessment_results)
                            results_to_save['_sector_tags'] = st.session_state.get('sector_tags', [])
                            results_to_save['_sector_subthemes'] = st.session_state.get('sector_subthemes', {})
                            results_to_save['_keywords'] = st.session_state.get('keywords', [])
                            assessment_id = save_assessment(
                                user_id=st.session_state.user_id,
                                document_name=st.session_state.document_name,
                                policy_summary=st.session_state.case_study_summary,
                                assessment_results=results_to_save,
                                recommendations=st.session_state.get('recommendations', "No recommendations available.")
                            )
                            
                            if assessment_id:
                                # Make success message more prominent
                                st.success(f"Assessment successfully saved to your history!")
                            else:
                                st.error("Failed to save assessment. Database error occurred.")
                        except Exception as e:
                            st.error(f"Error saving assessment: {str(e)}")
                            st.info("Please try again or check database connection.")
                    else:
                        st.error("Error saving assessment. Please try again.")
        
        with col2:
            # Export as PDF button
            st.download_button(
                label="📄 Export Report as PDF",
                data=generate_report_pdf(
                    "case_study_assessment.pdf",
                    st.session_state.document_name,
                    st.session_state.case_study_summary,
                    st.session_state.assessment_results,
                    ASSESSMENT_AREAS,
                    ASSESSMENT_CRITERIA,
                    st.session_state.get('recommendations', "No recommendations available."),
                    st.session_state.weighted_scores,
                    st.session_state.get('competency_mapping', None),
                    tags_data={"sectors": st.session_state.get('sector_tags', []), "subthemes": st.session_state.get('sector_subthemes', {}), "keywords": st.session_state.get('keywords', [])},
                    writing_findings=st.session_state.get('writing_findings', [])
                ),
                file_name="case_study_assessment.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Create tabs for each assessment area
        tabs = st.tabs([ASSESSMENT_AREAS[area_id]["name"] for area_id in ASSESSMENT_AREAS])
        
        for i, (area_id, area_info) in enumerate(ASSESSMENT_AREAS.items()):
            with tabs[i]:
                st.subheader(area_info["name"])
                st.write(area_info["description"])
                st.write(f"**Weight:** {area_info['weight'] * 100:.0f}% | **Total Points:** {area_info['total_points']}")
                
                if area_id in st.session_state.assessment_results:
                    area_criteria = ASSESSMENT_CRITERIA[area_id]
                    area_results = st.session_state.assessment_results[area_id]
                    
                    total_score = sum(
                        result.get("score", 0) for crit_id, result in area_results.items()
                        if not ASSESSMENT_CRITERIA.get(area_id, {}).get(crit_id, {}).get("informational", False)
                    )
                    max_possible = area_info["total_points"]
                    percentage = (total_score / max_possible * 100) if max_possible > 0 else 0
                    
                    # Display scores in a metrics row
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Area Score", f"{total_score}/{max_possible}")
                    with col2:
                        st.metric("Percentage", f"{percentage:.1f}%")
                    with col3:
                        weighted_contribution = (area_info["weight"] * (total_score / max_possible) * 100) if max_possible > 0 else 0
                        st.metric("Weighted Contribution", f"{weighted_contribution:.1f}%")
                    
                    # Create visualizations for scores
                    st.subheader("Score Visualization")
                    
                    # Create gauge chart for area percentage
                    gauge_fig = create_gauge_chart(percentage, f"Score for {area_info['name']}", max_value=100)
                    st.plotly_chart(gauge_fig)
                    
                    criteria_names = []
                    criteria_scores = []
                    criteria_max_scores = []
                    
                    for crit_id, result in area_results.items():
                        if area_criteria[crit_id].get("informational", False):
                            continue
                        criteria_names.append(area_criteria[crit_id]["name"])
                        criteria_scores.append(result.get("score", 0))
                        criteria_max_scores.append(area_criteria[crit_id].get("max_score", 3))
                    
                    # Create DataFrame for the chart
                    df = pd.DataFrame({
                        'Criteria': criteria_names,
                        'Score': criteria_scores,
                        'Max Score': criteria_max_scores
                    })
                    
                    fig = go.Figure()
                    
                    # Add bars for actual scores
                    fig.add_trace(go.Bar(
                        x=df['Criteria'],
                        y=df['Score'],
                        name='Score',
                        marker_color=['#28a745' if s/m >= 0.75 else '#ffc107' if s/m >= 0.5 else '#dc3545' 
                                      for s, m in zip(df['Score'], df['Max Score'])],
                        text=[f"{s}/{m}" for s, m in zip(df['Score'], df['Max Score'])],
                        textposition='outside'
                    ))
                    
                    fig.update_layout(
                        title=f"Criteria Scores for {area_info['name']}",
                        xaxis_title="Criteria",
                        yaxis_title="Score",
                        height=400,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig)
                    
                    # Detailed criteria analysis
                    st.subheader("Detailed Assessment")
                    
                    for criterion_id, result in area_results.items():
                        criterion_info = area_criteria[criterion_id]
                        criterion_name = criterion_info["name"]
                        is_info = criterion_info.get("informational", False)
                        doc_ref = result.get("document_reference", "N/A")
                        
                        if is_info:
                            narrative = result.get("narrative", result.get("reasoning", "N/A"))
                            with st.container():
                                st.markdown(f"""
                                <div style="background-color: #EFF6FF; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #3B82F6;">
                                    <h4 style="margin: 0 0 10px 0; color: #1E3A8A;">{criterion_name}</h4>
                                    <div style="display: inline-block; padding: 5px 15px; background-color: #3B82F6; color: white; border-radius: 20px; font-weight: bold; font-size: 0.85em;">
                                        ℹ Informational
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.write(f"**Analysis:** {narrative}")
                                st.write(f"**Document Reference:** {doc_ref}")
                                st.markdown("---")
                        else:
                            max_score = criterion_info.get("max_score", 3)
                            scoring_logic = criterion_info.get("scoring_logic", "")
                            score = result.get("score", 0)
                            reasoning = result.get("reasoning", "N/A")
                            
                            score_pct = score / max_score if max_score > 0 else 0
                            if score_pct >= 0.75:
                                score_color = "#28a745"
                            elif score_pct >= 0.5:
                                score_color = "#ffc107"
                            else:
                                score_color = "#dc3545"
                            
                            with st.container():
                                st.markdown(f"""
                                <div style="background-color: #F9FAFB; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid {score_color};">
                                    <h4 style="margin: 0 0 10px 0; color: #1E3A8A;">{criterion_name}</h4>
                                    <p style="font-size: 0.9em; color: #6B7280; margin-bottom: 10px;"><strong>Scoring:</strong> {scoring_logic}</p>
                                    <div style="display: inline-block; padding: 5px 15px; background-color: {score_color}; color: white; border-radius: 20px; font-weight: bold;">
                                        Score: {score}/{max_score}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.write(f"**Reasoning & Evidence:** {reasoning}")
                                st.write(f"**Document Reference:** {doc_ref}")
                                st.markdown("---")

                    if area_id == "area2":
                        writing_findings = st.session_state.get('writing_findings', [])
                        if writing_findings:
                            st.subheader("Writing Assistant Findings")
                            st.write("Detailed analysis of grammar, spelling, tense consistency, redundancy, and sentence structure across the complete case study.")

                            type_counts = {}
                            severity_counts = {"High": 0, "Medium": 0, "Low": 0}
                            for f in writing_findings:
                                t = f.get("type", "Other")
                                s = f.get("severity", "Low")
                                type_counts[t] = type_counts.get(t, 0) + 1
                                severity_counts[s] = severity_counts.get(s, 0) + 1

                            summary_cols = st.columns(len(type_counts) + 1)
                            with summary_cols[0]:
                                st.metric("Total Issues", len(writing_findings))
                            for idx, (issue_type, count) in enumerate(type_counts.items()):
                                with summary_cols[idx + 1]:
                                    st.metric(issue_type, count)

                            sev_cols = st.columns(3)
                            sev_colors = {"High": "#dc3545", "Medium": "#ffc107", "Low": "#6c757d"}
                            for idx, (sev, count) in enumerate(severity_counts.items()):
                                with sev_cols[idx]:
                                    st.markdown(f"""
                                    <div style="text-align:center; padding:8px; background-color:{sev_colors[sev]}20; border-radius:8px; border:1px solid {sev_colors[sev]};">
                                        <span style="color:{sev_colors[sev]}; font-weight:bold;">{sev}: {count}</span>
                                    </div>
                                    """, unsafe_allow_html=True)

                            st.markdown("<br>", unsafe_allow_html=True)

                            table_data = []
                            for i, f in enumerate(writing_findings, 1):
                                table_data.append({
                                    "Issue #": i,
                                    "Type": f.get("type", "Other"),
                                    "Original Text": f.get("original_text", ""),
                                    "Suggested Fix": f.get("suggestion", ""),
                                    "Severity": f.get("severity", "Low"),
                                    "Explanation": f.get("context", "")
                                })

                            findings_df = pd.DataFrame(table_data)

                            def style_severity(val):
                                colors = {"High": "background-color: #f8d7da; color: #721c24;", "Medium": "background-color: #fff3cd; color: #856404;", "Low": "background-color: #e2e3e5; color: #383d41;"}
                                return colors.get(val, "")

                            styled_df = findings_df.style.applymap(style_severity, subset=["Severity"])
                            st.dataframe(styled_df, use_container_width=True, hide_index=True, height=min(400, 50 + len(table_data) * 35))

                            with st.expander("View All Findings in Detail", expanded=False):
                                for i, f in enumerate(writing_findings, 1):
                                    sev = f.get("severity", "Low")
                                    sev_color = sev_colors.get(sev, "#6c757d")
                                    type_badge_colors = {"Spelling": "#0d6efd", "Grammar": "#6610f2", "Tense": "#fd7e14", "Redundancy": "#20c997", "Structure": "#0dcaf0"}
                                    type_color = type_badge_colors.get(f.get("type", ""), "#6c757d")
                                    st.markdown(f"""
                                    <div style="padding:12px; margin-bottom:8px; background-color:#f8f9fa; border-radius:8px; border-left:4px solid {sev_color};">
                                        <div style="margin-bottom:6px;">
                                            <span style="display:inline-block; padding:2px 10px; background-color:{type_color}; color:white; border-radius:12px; font-size:0.8em; font-weight:bold;">{f.get("type", "Other")}</span>
                                            <span style="display:inline-block; padding:2px 10px; background-color:{sev_color}20; color:{sev_color}; border-radius:12px; font-size:0.8em; font-weight:bold; margin-left:5px;">{sev}</span>
                                        </div>
                                        <p style="margin:4px 0;"><strong>Original:</strong> <span style="color:#dc3545; text-decoration:line-through;">{f.get("original_text", "")}</span></p>
                                        <p style="margin:4px 0;"><strong>Suggested:</strong> <span style="color:#28a745;">{f.get("suggestion", "")}</span></p>
                                        <p style="margin:4px 0; font-size:0.9em; color:#6B7280;"><em>{f.get("context", "")}</em></p>
                                    </div>
                                    """, unsafe_allow_html=True)

                    # Display KCM Competency Mapping before recommendations
                    competency_data = st.session_state.get('competency_mapping')
                    if competency_data and isinstance(competency_data, dict):
                        st.subheader("Karmayogi Competency Mapping")
                        st.write("Based on the case study analysis, the following competencies from the Karmayogi Competency Model (KCM) are most relevant:")
                        
                        # Behavioral Competencies
                        behavioral_comps = competency_data.get('behavioral_competencies', [])
                        if behavioral_comps and isinstance(behavioral_comps, list):
                            st.markdown("#### Behavioral Sub-competencies")
                            for comp in behavioral_comps:
                                if isinstance(comp, dict):
                                    comp_name = comp.get('name', 'Unknown')
                                    parent = comp.get('parent_competency', '')
                                    display_name = f"{comp_name} ({parent})" if parent else comp_name
                                    justification = comp.get('justification', 'No justification provided')
                                    st.markdown(f"""
                                    <div style="background-color: #E0F2FE; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #0284C7;">
                                        <strong style="color: #0369A1;">{display_name}</strong>
                                        <p style="margin: 8px 0 0 0; color: #374151; font-size: 0.95em;">{justification}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # Functional Competencies
                        functional_comps = competency_data.get('functional_competencies', [])
                        if functional_comps and isinstance(functional_comps, list):
                            st.markdown("#### Functional Sub-competencies")
                            for comp in functional_comps:
                                if isinstance(comp, dict):
                                    comp_name = comp.get('name', 'Unknown')
                                    parent = comp.get('parent_competency', '')
                                    display_name = f"{comp_name} ({parent})" if parent else comp_name
                                    justification = comp.get('justification', 'No justification provided')
                                    st.markdown(f"""
                                    <div style="background-color: #ECFDF5; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #059669;">
                                        <strong style="color: #047857;">{display_name}</strong>
                                        <p style="margin: 8px 0 0 0; color: #374151; font-size: 0.95em;">{justification}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                    
                    # After all criteria are shown, add recommendations section
                    if 'recommendations' in st.session_state:
                        st.subheader("Recommendations for Improvement")
                        st.write("Based on the assessment, we recommend the following:")
                        
                        # Format recommendations as a simple list
                        recommendations = st.session_state.recommendations
                        
                        # Process the recommendations text
                        if "Recommendation" in recommendations:
                            # Split by "Recommendation" and process each item
                            if recommendations.strip().startswith("Recommendation"):
                                parts = recommendations.split("Recommendation")
                                for part in parts:
                                    if part.strip():
                                        # Clean up the format
                                        cleaned_part = part.strip().replace('\n', ' ')
                                        
                                        # Look for colons to preserve formatting
                                        if ':' in cleaned_part and cleaned_part.find(':') < 10:
                                            num, content = cleaned_part.split(':', 1)
                                            st.write(f"**Recommendation {num.strip()}:** {content.strip()}")
                                        else:
                                            st.write(f"**Recommendation {cleaned_part.strip()}**")
                        
                        # Fallback to regular dash-based splitting if no "Recommendation" keyword
                        elif "-" in recommendations:
                            rec_points = recommendations.split("-")
                            for point in rec_points:
                                if point.strip():
                                    st.write(f"- {point.strip()}")
                        else:
                            # Just show as regular text if no structured format detected
                            st.write(recommendations)
                else:
                    st.info("No assessment data available for this area")
    
    # Raw extracted text (collapsible)
    with st.expander("View Extracted Text"):
        st.subheader("Case Study Document")
        st.text_area("Case Study Text", st.session_state.case_study_text, height=250, key="view_case_study")
        if st.session_state.teaching_note_text:
            st.subheader("Teaching Note Document")
            st.text_area("Teaching Note Text", st.session_state.teaching_note_text, height=250, key="view_teaching_note")
elif st.session_state.get("active_tool") == "analyser" and not st.session_state.case_study_text:
    st.info("Please upload both Case Study and Teaching Note documents using the sidebar to begin analysis.")

elif not st.session_state.logged_in:
    st.info("Please login to access the tools.")
