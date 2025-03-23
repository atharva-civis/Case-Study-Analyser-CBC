import streamlit as st
import os
import pandas as pd
from io import BytesIO
import PyPDF2
import docx
from utils import extract_text_from_pdf, extract_text_from_docx, call_openai_api
from assessment_criteria import ASSESSMENT_AREAS, ASSESSMENT_CRITERIA

# Set page configuration
st.set_page_config(
    page_title="Policy Insight Generator",
    page_icon="📑",
    layout="wide"
)

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
        
        # Create tabs for each assessment area
        tabs = st.tabs([ASSESSMENT_AREAS[area_id]["name"] for area_id in ASSESSMENT_AREAS])
        
        for i, (area_id, area_info) in enumerate(ASSESSMENT_AREAS.items()):
            with tabs[i]:
                st.subheader(area_info["name"])
                st.write(area_info["description"])
                
                if area_id in st.session_state.assessment_results:
                    # Prepare data for table
                    table_data = []
                    area_criteria = ASSESSMENT_CRITERIA[area_id]
                    area_results = st.session_state.assessment_results[area_id]
                    
                    for criterion_id, result in area_results.items():
                        criterion_name = area_criteria[criterion_id]["name"]
                        table_data.append({
                            "Criteria": criterion_name,
                            "Score": result.get("score", "N/A"),
                            "Reasoning & Evidence": result.get("reasoning", "N/A"),
                            "Document Reference": result.get("document_reference", "N/A")
                        })
                    
                    # Display as a DataFrame
                    df = pd.DataFrame(table_data)
                    st.table(df)
                    
                    # Calculate and display average score for this area
                    avg_score = sum(result.get("score", 0) for result in area_results.values()) / len(area_results)
                    st.metric(f"Average Score for {area_info['name']}", f"{avg_score:.2f}/5")
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
