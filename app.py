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
from utils import extract_text_from_pdf, extract_text_from_docx, call_openai_api, generate_report_pdf, get_download_link, create_gauge_chart
from assessment_criteria import ASSESSMENT_AREAS, ASSESSMENT_CRITERIA

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
    /* Criteria heading styling defined above */
</style>
""", unsafe_allow_html=True)

# Application title and description
st.title("Policy Insight Generator")
st.markdown("""
This tool helps analyze policy documents against structured assessment criteria.
Upload your policy document, and the AI will evaluate it based on three key assessment areas:
1. Does the Draft Clearly Explain Why and What?
2. Does the Draft Thoroughly Assess the Impact?
3. Does the Draft Enable Meaningful Public Participation?
""")

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

# Sidebar for file upload and actions
with st.sidebar:
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
                    
                    # Display each criterion in a card-like format
                    for criterion_id, result in area_results.items():
                        criterion_name = area_criteria[criterion_id]["name"]
                        score = result.get("score", "N/A")
                        reasoning = result.get("reasoning", "N/A")
                        doc_ref = result.get("document_reference", "N/A")
                        
                        with st.container():
                            st.markdown(f"""
                            <div class="card">
                                <div class="criteria-heading">{criterion_name} - Score: {score}/5</div>
                                <p><strong>Reasoning & Evidence:</strong> {reasoning}</p>
                                <p><strong>Document Reference:</strong> {doc_ref}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    # After all criteria are shown, add recommendations section
                    if 'recommendations' in st.session_state:
                        st.subheader("Recommendations for Improvement")
                        st.markdown("""
                        <div class="card" style="background-color: #EEFCF4; padding: 20px; border-radius: 8px; border-left: 5px solid #34D399;">
                            <h4 style="color: #047857; margin-top: 0;">Based on the assessment, we recommend the following:</h4>
                            <div style="padding-left: 15px;">
                        """, unsafe_allow_html=True)
                        
                        # Format recommendations as a well-structured list
                        recommendations = st.session_state.recommendations
                        
                        # Process the recommendations text
                        if "Recommendation" in recommendations:
                            # Split by "Recommendation" and process each item
                            cleaned_lines = []
                            
                            # If it starts with "Recommendation", remove any leading characters
                            if recommendations.strip().startswith("Recommendation"):
                                parts = recommendations.split("Recommendation")
                                for part in parts:
                                    if part.strip():
                                        # Clean up the format, preserving sentence integrity
                                        cleaned_part = part.strip().replace('\n', ' ')
                                        # Remove any stray bullets that might be causing breaks
                                        cleaned_part = cleaned_part.replace('•', '')
                                        # Remove any stray hyphens that might be causing breaks
                                        cleaned_part = cleaned_part.replace('- ', '')
                                        
                                        # Look for colons to preserve formatting
                                        if ':' in cleaned_part and cleaned_part.find(':') < 10:
                                            num, content = cleaned_part.split(':', 1)
                                            cleaned_lines.append(f"<strong>Recommendation {num.strip()}:</strong>{content}")
                                        else:
                                            cleaned_lines.append(f"<strong>Recommendation {cleaned_part}</strong>")
                            
                            # Display each recommendation as a complete paragraph with proper formatting
                            for i, line in enumerate(cleaned_lines):
                                st.markdown(f"""
                                <div style="display: flex; margin-bottom: 12px;">
                                    <div style="min-width: 24px; margin-right: 8px;">•</div>
                                    <div>{line}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Fallback to regular dash-based splitting if no "Recommendation" keyword
                        elif "-" in recommendations:
                            rec_points = recommendations.split("-")
                            for point in rec_points:
                                if point.strip():
                                    # Clean up the recommendation text
                                    clean_point = point.strip().replace('\n', ' ')
                                    st.markdown(f"""
                                    <div style="display: flex; margin-bottom: 12px;">
                                        <div style="min-width: 24px; margin-right: 8px;">•</div>
                                        <div>{clean_point}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            # Just show as regular text if no structured format detected
                            st.markdown(f"<p>{recommendations}</p>", unsafe_allow_html=True)
                        
                        st.markdown("</div></div>", unsafe_allow_html=True)
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
