import os
import json
import PyPDF2
import docx
import requests
import base64
import datetime
from io import BytesIO
from openai import OpenAI
from fpdf import FPDF
import plotly.graph_objects as go

# Initialize OpenAI client
# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(pdf_file):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_file: The uploaded PDF file object
        
    Returns:
        str: Extracted text from the PDF
    """
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    return text

def extract_text_from_docx(docx_file):
    """
    Extract text content from a DOCX file.
    
    Args:
        docx_file: The uploaded DOCX file object
        
    Returns:
        str: Extracted text from the DOCX
    """
    text = ""
    try:
        # Convert file to BytesIO object
        bytes_content = BytesIO(docx_file.getvalue())
        
        # Open using python-docx
        doc = docx.Document(bytes_content)
        
        # Extract text from paragraphs
        for para in doc.paragraphs:
            text += para.text + "\n"
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + " "
                text += "\n"
        
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    return text

def call_openai_api(prompt, model="gpt-4o", response_format=None):
    """
    Call the OpenAI API with the given prompt.
    
    Args:
        prompt (str): The prompt to send to the API
        model (str): The OpenAI model to use
        response_format (str, optional): Format for response (e.g., "json_object")
        
    Returns:
        The content of the API response
    """
    try:
        messages = [{"role": "user", "content": prompt}]
        
        # Set up response_format if specified
        kwargs = {}
        if response_format == "json_object":
            kwargs["response_format"] = {"type": "json_object"}
        
        # Make the API call
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,
            max_tokens=2000,
            **kwargs
        )
        
        # Process the response
        content = response.choices[0].message.content
        
        # If JSON format was requested, parse the result
        if response_format == "json_object":
            try:
                result = json.loads(content)
                
                # Ensure all expected fields exist and have the correct types
                if "score" not in result:
                    result["score"] = 3  # Default middle score
                elif not isinstance(result["score"], (int, float)):
                    # Convert to number if possible, otherwise use default
                    try:
                        result["score"] = float(result["score"])
                    except ValueError:
                        result["score"] = 3
                
                # Ensure reasoning is a string
                if "reasoning" not in result:
                    result["reasoning"] = "No reasoning provided"
                elif isinstance(result["reasoning"], list):
                    result["reasoning"] = ". ".join([str(item) for item in result["reasoning"]])
                
                # Ensure document_reference is a string
                if "document_reference" not in result:
                    result["document_reference"] = "No document reference provided"
                elif isinstance(result["document_reference"], list):
                    result["document_reference"] = ". ".join([str(item) for item in result["document_reference"]])
                
                return result
            except json.JSONDecodeError:
                return {
                    "score": 0,
                    "reasoning": "Failed to parse response from AI model",
                    "document_reference": "Error in analysis"
                }
        
        return content
    
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"
        
def create_gauge_chart(score, title):
    """
    Creates a gauge chart for a score from 1-5
    
    Args:
        score (float): Score value between 1 and 5
        title (str): Title for the gauge
        
    Returns:
        str: Base64 encoded image of the gauge chart
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 5], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "royalblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 2], 'color': 'lightcoral'},
                {'range': [2, 3.5], 'color': 'lightyellow'},
                {'range': [3.5, 5], 'color': 'lightgreen'}
            ]
        }
    ))
    
    fig.update_layout(
        height=300,
        width=400,
        margin=dict(l=30, r=30, b=20, t=40),
        paper_bgcolor="white",
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig
    
def generate_report_pdf(filename, policy_name, policy_summary, assessment_results, assessment_areas, assessment_criteria):
    """
    Generate a PDF report of the policy assessment
    
    Args:
        filename (str): Name to save the PDF as
        policy_name (str): Name of the policy document
        policy_summary (str): Summary of the policy
        assessment_results (dict): Results of the assessment
        assessment_areas (dict): Assessment areas information
        assessment_criteria (dict): Assessment criteria information
        
    Returns:
        BytesIO: PDF file as BytesIO object
    """
    class PDF(FPDF):
        def header(self):
            # Set up the header
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'Policy Assessment Report', 0, 1, 'C')
            self.ln(5)
        
        def footer(self):
            # Set up the footer
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            self.cell(0, 10, f'Generated on {date} - Page {self.page_no()}', 0, 0, 'C')
        
        def section_title(self, title):
            # Add a section title
            self.set_font('Arial', 'B', 14)
            self.set_fill_color(230, 230, 250)  # Light purple background
            self.cell(0, 10, title, 0, 1, 'L', True)
            self.ln(5)
        
        def sub_section_title(self, title):
            # Add a subsection title
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, title, 0, 1, 'L')
            self.ln(2)
        
        def add_score_box(self, label, score, max_score=5):
            # Create a visual score box
            self.set_fill_color(240, 240, 240)
            self.set_font('Arial', 'B', 10)
            self.cell(40, 10, label, 1, 0, 'L')
            
            # Choose color based on score
            if score >= 4:
                self.set_fill_color(144, 238, 144)  # Light green
            elif score >= 3:
                self.set_fill_color(255, 255, 153)  # Light yellow
            else:
                self.set_fill_color(255, 204, 203)  # Light red
                
            self.cell(20, 10, f"{score:.1f}/{max_score}", 1, 1, 'C', True)
            self.ln(1)
    
    # Create PDF object
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Cover page with title and document info
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 20, 'Policy Assessment Report', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"Document: {policy_name}", 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    
    # Executive summary page
    pdf.add_page()
    pdf.section_title("Executive Summary")
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, policy_summary)
    pdf.ln(5)
    
    # Calculate overall scores
    overall_scores = {}
    total_overall_score = 0
    total_criteria_count = 0
    
    for area_id, area_results in assessment_results.items():
        if area_results:
            area_total = sum(result.get("score", 0) for result in area_results.values())
            area_avg = area_total / len(area_results)
            overall_scores[area_id] = {
                "total": area_total,
                "average": area_avg,
                "count": len(area_results)
            }
            total_overall_score += area_total
            total_criteria_count += len(area_results)
    
    # Add overall score summary
    if total_criteria_count > 0:
        pdf.section_title("Assessment Summary")
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Overall Assessment Score: {total_overall_score / total_criteria_count:.2f}/5", 0, 1)
        pdf.ln(5)
        
        # Area scores
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, "Area Scores:", 0, 1)
        
        # Score boxes for each area
        for area_id, scores in overall_scores.items():
            area_name = assessment_areas[area_id]["name"]
            pdf.add_score_box(area_name, scores["average"])
        
        pdf.ln(10)
    
    # Detailed assessment by area
    for area_id, area_info in assessment_areas.items():
        pdf.add_page()
        pdf.section_title(f"Area Assessment: {area_info['name']}")
        
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, area_info["description"])
        pdf.ln(5)
        
        if area_id in assessment_results:
            area_results = assessment_results[area_id]
            
            # Calculate scores
            total_score = sum(result.get("score", 0) for result in area_results.values())
            avg_score = total_score / len(area_results) if area_results else 0
            
            # Display area scores
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(100, 10, f"Total Score: {total_score:.1f}", 0, 0)
            pdf.cell(0, 10, f"Average Score: {avg_score:.2f}/5", 0, 1)
            pdf.ln(5)
            
            # Process each criterion with detailed info
            area_criteria = assessment_criteria[area_id]
            
            pdf.sub_section_title("Detailed Criteria Assessment")
            
            for criterion_id, result in area_results.items():
                criterion_name = area_criteria[criterion_id]["name"]
                score = result.get("score", 0)
                reasoning = result.get("reasoning", "No reasoning provided")
                doc_ref = result.get("document_reference", "No references provided")
                
                # Criterion header with box
                pdf.set_draw_color(100, 100, 100)
                pdf.set_fill_color(240, 248, 255)  # Light blue background
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 8, f"{criterion_name}", 1, 1, 'L', True)
                
                # Score with colored box
                if score >= 4:
                    pdf.set_fill_color(144, 238, 144)  # Light green
                elif score >= 3:
                    pdf.set_fill_color(255, 255, 153)  # Light yellow
                else:
                    pdf.set_fill_color(255, 204, 203)  # Light red
                
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(30, 8, "Score:", 0, 0)
                pdf.cell(20, 8, f"{score}/5", 1, 1, 'C', True)
                
                # Reasoning
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 8, "Reasoning & Evidence:", 0, 1)
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 6, reasoning)
                
                # Document references
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 8, "Document References:", 0, 1)
                pdf.set_font('Arial', 'I', 9)
                pdf.multi_cell(0, 6, doc_ref)
                
                pdf.ln(5)
        else:
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 10, "No assessment data available for this area", 0, 1)
    
    # Save to BytesIO
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1')
    
    pdf_output = BytesIO(pdf_bytes)
    pdf_output.seek(0)
    
    return pdf_output

def get_download_link(pdf_bytes, filename, text):
    """
    Generate a download link for a PDF file
    
    Args:
        pdf_bytes (BytesIO): PDF file as BytesIO object
        filename (str): Filename for download
        text (str): Link text
        
    Returns:
        str: HTML for download link
    """
    b64 = base64.b64encode(pdf_bytes.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">{text}</a>'
    return href
