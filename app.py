import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import json
from io import BytesIO
import PyPDF2
import docx
from datetime import datetime, timedelta
from utils import extract_text_from_pdf, extract_text_from_docx, call_openai_api, generate_report_pdf, get_download_link, create_gauge_chart
from assessment_criteria import ASSESSMENT_AREAS, ASSESSMENT_CRITERIA
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
    page_title="Policy Insight Generator",
    page_icon="📑",
    layout="wide"
)

# Custom CSS to improve the appearance
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #E5E7EB;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #1F2937;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3B82F6;
        color: white;
        font-weight: bold;
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
</style>
""", unsafe_allow_html=True)

# Initialize session state for authentication
initialize_session_state()

# Authentication and user management
def show_login_page():
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    st.subheader("Login to Your Account")
    
    st.info("Please enter your credentials to access the Policy Analysis Tool")
    
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

# Show login page or main app
if not st.session_state.logged_in:
    # Application title
    st.title("Policy Insight Generator")
    
    # Show login page
    show_login_page()
        
else:
    # Application title and description for logged-in users
    st.title("Policy Insight Generator")
    
    # User profile section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        This tool helps analyze policy documents against structured assessment criteria.
        Upload your policy document, and the AI will evaluate it based on three key assessment areas:
        1. Does the Draft Clearly Explain Why and What?
        2. Does the Draft Thoroughly Assess the Impact?
        3. Does the Draft Enable Meaningful Public Participation?
        """)
    
    with col2:
        # User profile with logout button
        st.markdown(f"""
        <div class="user-profile">
            <div class="avatar">{st.session_state.username[0].upper()}</div>
            <div class="info">
                <p><strong>{st.session_state.username}</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple logout button instead of JavaScript approach
        if st.button("Logout", key="logout_button"):
            logout_user()
            st.rerun()

# Initialize session state variables if they don't exist
if 'policy_text' not in st.session_state:
    st.session_state.policy_text = ""
if 'policy_analysis' not in st.session_state:
    st.session_state.policy_analysis = None
if 'policy_summary' not in st.session_state:
    st.session_state.policy_summary = ""
if 'assessment_results' not in st.session_state:
    st.session_state.assessment_results = {}
if 'document_name' not in st.session_state:
    st.session_state.document_name = ""
if 'loaded_from_history' not in st.session_state:
    st.session_state.loaded_from_history = False

# Sidebar with simple navigation (only for logged-in users)
with st.sidebar:
    if st.session_state.logged_in:
        # Simple sidebar navigation with radio buttons in a row
        st.header("Navigation")
        
        # Initialize sidebar tab state if not present
        if 'sidebar_tab' not in st.session_state:
            st.session_state.sidebar_tab = "New Assessment"
        
        # Simple radio selection
        sidebar_tab = st.radio("", ["New Assessment", "History"])
        
        # Set session state and rerun if changed
        if sidebar_tab != st.session_state.sidebar_tab:
            st.session_state.sidebar_tab = sidebar_tab
            
            # Clear main section content when switching tabs
            if sidebar_tab == "New Assessment":
                # Check if we're already loading from history - don't clear if so
                if not st.session_state.get('loaded_from_history', False):
                    # Completely reset all assessment-related data
                    if 'policy_text' in st.session_state:
                        st.session_state.policy_text = ""
                    if 'policy_analysis' in st.session_state:
                        st.session_state.policy_analysis = None
                    if 'policy_summary' in st.session_state:
                        st.session_state.policy_summary = ""
                    if 'assessment_results' in st.session_state:
                        st.session_state.assessment_results = {}
                    if 'recommendations' in st.session_state:
                        st.session_state.recommendations = ""
                    if 'document_name' in st.session_state:
                        st.session_state.document_name = ""
                else:
                    # If switching back to New Assessment with loaded content,
                    # just reset the flag for next time
                    st.session_state.loaded_from_history = False
            elif sidebar_tab == "History":
                # Reset history view data if needed
                if 'selected_assessment' in st.session_state:
                    st.session_state.selected_assessment = None
            
            st.rerun()
        
        st.markdown("---")
        
        if st.session_state.sidebar_tab == "New Assessment":
            st.header("Upload Policy Document")
            uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
            
            if uploaded_file is not None:
                st.session_state.document_name = uploaded_file.name
                
                # Process the uploaded file
                try:
                    if uploaded_file.type == "application/pdf":
                        st.session_state.policy_text = extract_text_from_pdf(uploaded_file)
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        st.session_state.policy_text = extract_text_from_docx(uploaded_file)
                    
                    st.success(f"Successfully processed {uploaded_file.name}")
                    
                    # Display text length information
                    text_length = len(st.session_state.policy_text)
                    st.info(f"Extracted {text_length} characters from document")
                    
                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
            
            # Action buttons
            st.subheader("Analysis Actions")
            
            if st.session_state.policy_text:
                if st.button("Generate Summary"):
                    with st.spinner("Generating policy summary..."):
                        prompt = f"""
                        Please provide a concise summary of the following policy document. 
                        Focus on the main objectives, key provisions, and policy intent:
                        
                        {st.session_state.policy_text[:4000]}  # Limit text length to avoid token limits
                        """
                        
                        st.session_state.policy_summary = call_openai_api(prompt)
                
                if st.button("Perform Full Assessment"):
                    progress_text = st.empty()
                    progress_bar = st.progress(0)
                    
                    st.session_state.assessment_results = {}
                    
                    # Count total criteria for progress tracking
                    total_criteria = sum(len(ASSESSMENT_CRITERIA[area_id]) for area_id in ASSESSMENT_AREAS)
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
                            
                            prompt = f"""
                            You are a policy analysis expert. Please evaluate the following policy document 
                            against this specific criterion: "{criterion_info['description']}"
                            
                            Policy Document:
                            {st.session_state.policy_text[:4000]}  # Limit text length
                            
                            Provide an analysis with the following JSON structure:
                            {{
                                "score": [a number between 1 and 5, where 1 is poor and 5 is excellent],
                                "reasoning": [detailed explanation of why this score was given as a single string, not a list],
                                "document_reference": [specific sections or content from the document that supports this assessment as a single string, not a list]
                            }}
                            
                            Ensure that ALL fields (score, reasoning, document_reference) are provided and that reasoning and document_reference are STRINGS, not lists or arrays.
                            
                            Base your evaluation on how well the document addresses this criterion.
                            """
                            
                            with st.spinner(f"Analyzing {criterion_info['name']}..."):
                                result = call_openai_api(prompt, response_format="json_object")
                                
                                # Ensure consistent data types - convert any lists to strings
                                if isinstance(result.get("reasoning"), list):
                                    result["reasoning"] = ". ".join(result["reasoning"])
                                if isinstance(result.get("document_reference"), list):
                                    result["document_reference"] = ". ".join(result["document_reference"])
                                
                                st.session_state.assessment_results[area_id][criterion_id] = result
                            
                            # Update progress
                            processed_criteria += 1
                            progress_bar.progress(processed_criteria / total_criteria)
                    
                    progress_text.text("Assessment complete!")
                    progress_bar.progress(100)
                    st.success("Policy assessment completed successfully!")
            else:
                st.info("Please upload a document first")
                
        elif st.session_state.sidebar_tab == "History":
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
                                        st.session_state.policy_summary = assessment.policy_summary
                                        st.session_state.assessment_results = assessment.get_results_dict()
                                        st.session_state.recommendations = assessment.recommendations
                                        st.session_state.policy_text = "Loaded from history"  # Placeholder for text
                                        
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
    else:
        # For non-logged in users, show basic upload
        st.header("Upload Policy Document")
        st.info("Please login to use the policy assessment tool.")

# Main content area
if st.session_state.policy_text:
    # Document info section
    st.header("Document Information")
    st.write(f"**Filename:** {st.session_state.document_name}")
    
    # Summary section
    st.header("Policy Summary")
    if st.session_state.policy_summary:
        st.write(st.session_state.policy_summary)
    else:
        st.info("Click 'Generate Summary' to create a summary of the policy document")
    
    # Assessment Results
    if st.session_state.assessment_results:
        st.header("Assessment Results")
        
        # Add export report button
        col1, col2 = st.columns([4, 1])
        with col2:
            # Generate recommendations for policy improvement
            if 'recommendations' not in st.session_state:
                with st.spinner("Generating recommendations..."):
                    # Prepare data for recommendations generation
                    low_scores = []
                    for area_id, area_results in st.session_state.assessment_results.items():
                        area_name = ASSESSMENT_AREAS[area_id]["name"]
                        for criterion_id, result in area_results.items():
                            criterion_name = ASSESSMENT_CRITERIA[area_id][criterion_id]["name"]
                            score = result.get("score", 0)
                            if score < 3.5:  # Focus on areas that need improvement
                                low_scores.append({
                                    "area": area_name,
                                    "criterion": criterion_name,
                                    "score": score,
                                    "reasoning": result.get("reasoning", "")
                                })
                    
                    # Generate recommendations based on low scores
                    if low_scores:
                        prompt = f"""
                        Based on the policy assessment, please generate 5-8 concrete, actionable recommendations 
                        to improve the policy draft. Focus on addressing the following areas with low scores:
                        
                        {json.dumps(low_scores, indent=2)}
                        
                        Format each recommendation as a numbered entry starting with "Recommendation 1:", 
                        "Recommendation 2:", etc. Each recommendation should be a complete, self-contained 
                        paragraph without line breaks or bullets in the middle of sentences.
                        
                        Your recommendations should be:
                        1. Specific and actionable
                        2. Practical to implement
                        3. Directly address deficiencies identified in the assessment
                        4. Written in complete sentences with proper punctuation
                        5. Free of any hyphens, bullets, or line breaks within each recommendation
                        
                        Example format:
                        Recommendation 1: [Complete sentence describing specific action] to address [specific issue]. The recommendation should include enough detail to be actionable but be contained in a single complete paragraph.
                        
                        Recommendation 2: [Complete sentence describing another specific action] to address [another specific issue]. Keep this as a single continuous paragraph without any internal formatting or line breaks.
                        """
                        
                        st.session_state.recommendations = call_openai_api(prompt)
                    else:
                        st.session_state.recommendations = "- The policy generally scores well across all assessment areas. Consider maintaining the current approach while monitoring implementation effectiveness."
            
            # Save to history button (only shown to logged-in users)
            if st.session_state.logged_in:
                if st.button("Save to History"):
                    if st.session_state.user_id:
                        # Save assessment to database
                        try:
                            assessment_id = save_assessment(
                                user_id=st.session_state.user_id,
                                document_name=st.session_state.document_name,
                                policy_summary=st.session_state.policy_summary,
                                assessment_results=st.session_state.assessment_results,
                                recommendations=st.session_state.get('recommendations', "No recommendations available.")
                            )
                            
                            if assessment_id:
                                # Make success message more prominent
                                st.success(f"Assessment successfully saved to your history!")
                                st.info("You can view it in the History tab.")
                            else:
                                st.error("Failed to save assessment. Database error occurred.")
                        except Exception as e:
                            st.error(f"Error saving assessment: {str(e)}")
                            st.info("Please try again or check database connection.")
                    else:
                        st.error("Error saving assessment. Please try again.")
            
            # Export as PDF button
            st.download_button(
                label="Export Report as PDF",
                data=generate_report_pdf(
                    "policy_assessment.pdf",
                    st.session_state.document_name,
                    st.session_state.policy_summary,
                    st.session_state.assessment_results,
                    ASSESSMENT_AREAS,
                    ASSESSMENT_CRITERIA,
                    st.session_state.get('recommendations', "No recommendations available.")
                ),
                file_name="policy_assessment.pdf",
                mime="application/pdf"
            )
        
        # Create tabs for each assessment area
        tabs = st.tabs([ASSESSMENT_AREAS[area_id]["name"] for area_id in ASSESSMENT_AREAS])
        
        for i, (area_id, area_info) in enumerate(ASSESSMENT_AREAS.items()):
            with tabs[i]:
                st.subheader(area_info["name"])
                st.write(area_info["description"])
                
                if area_id in st.session_state.assessment_results:
                    area_criteria = ASSESSMENT_CRITERIA[area_id]
                    area_results = st.session_state.assessment_results[area_id]
                    
                    # Calculate scores
                    total_score = sum(result.get("score", 0) for result in area_results.values())
                    avg_score = total_score / len(area_results) if area_results else 0
                    
                    # Display scores in a metrics row
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Score", f"{total_score:.1f}")
                    with col2:
                        st.metric("Average Score", f"{avg_score:.2f}/5")
                    
                    # Create visualizations for scores
                    st.subheader("Score Visualization")
                    
                    # Create gauge chart for average score
                    gauge_fig = create_gauge_chart(avg_score, f"Average Score for {area_info['name']}")
                    st.plotly_chart(gauge_fig)
                    
                    # Create a bar chart for all criteria scores
                    score_data = {area_criteria[crit_id]["name"]: result.get("score", 0) 
                                  for crit_id, result in area_results.items()}
                    
                    fig = px.bar(
                        x=list(score_data.keys()),
                        y=list(score_data.values()),
                        labels={"x": "Criteria", "y": "Score"},
                        title=f"Scores by Criteria for {area_info['name']}",
                        color=list(score_data.values()),
                        color_continuous_scale=["red", "yellow", "green"],
                        range_color=[1, 5]
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig)
                    
                    # Detailed criteria analysis
                    st.subheader("Detailed Assessment")
                    
                    # Display each criterion with simple formatting
                    for criterion_id, result in area_results.items():
                        criterion_name = area_criteria[criterion_id]["name"]
                        score = result.get("score", "N/A")
                        reasoning = result.get("reasoning", "N/A")
                        doc_ref = result.get("document_reference", "N/A")
                        
                        with st.container():
                            st.write(f"**{criterion_name} - Score: {score}/5**")
                            st.write(f"**Reasoning & Evidence:** {reasoning}")
                            st.write(f"**Document Reference:** {doc_ref}")
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
        st.text_area("Document Text", st.session_state.policy_text, height=300)
else:
    # Placeholder content when no document is loaded
    st.info("Please upload a policy document to begin analysis")
    
    # Display info about the assessment framework
    st.header("Assessment Framework")
    for area_id, area_info in ASSESSMENT_AREAS.items():
        with st.expander(area_info["name"]):
            st.write(area_info["description"])
            
            # List the criteria for this area
            st.subheader("Criteria:")
            criteria = ASSESSMENT_CRITERIA[area_id]
            for criterion_id, criterion_info in criteria.items():
                st.write(f"**{criterion_info['name']}**: {criterion_info['description']}")
