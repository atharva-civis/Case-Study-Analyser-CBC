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
import matplotlib.pyplot as plt
import numpy as np

# Initialize OpenAI client
# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(pdf_file):
    """
    Extract text content and metadata from a PDF file.
    
    Args:
        pdf_file: The uploaded PDF file object
        
    Returns:
        tuple: (extracted_text, metadata_dict)
    """
    text = ""
    metadata = {}
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        metadata = {
            'pages': len(pdf_reader.pages),
            'title': pdf_reader.metadata.get('/Title', 'Untitled'),
            'author': pdf_reader.metadata.get('/Author', 'Unknown'),
            'creation_date': pdf_reader.metadata.get('/CreationDate', 'Unknown')
        }
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_num} ---\n"
                text += page_text.strip() + "\n\n"
            else:
                print(f"Warning: No text extracted from page {page_num}")
                
    except Exception as e:
        if "File has not been decrypted" in str(e):
            raise Exception("PDF file is encrypted and cannot be processed")
        raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    return text, metadata

def extract_text_from_docx(docx_file):
    """
    Extract structured text content from a DOCX file.
    
    Args:
        docx_file: The uploaded DOCX file object
        
    Returns:
        dict: Structured content from the DOCX
    """
    content = {
        'headings': [],
        'paragraphs': [],
        'tables': [],
        'metadata': {}
    }
    
    try:
        bytes_content = BytesIO(docx_file.getvalue())
        doc = docx.Document(bytes_content)
        
        # Extract document properties
        content['metadata'] = {
            'title': doc.core_properties.title or 'Untitled',
            'author': doc.core_properties.author or 'Unknown',
            'created': str(doc.core_properties.created or 'Unknown'),
            'modified': str(doc.core_properties.modified or 'Unknown')
        }
        
        # Process paragraphs with style information
        for para in doc.paragraphs:
            if para.style.name.startswith('Heading'):
                content['headings'].append({
                    'level': int(para.style.name[-1]),
                    'text': para.text.strip()
                })
            elif para.text.strip():
                content['paragraphs'].append({
                    'text': para.text.strip(),
                    'style': para.style.name
                })
        
        # Process tables with headers
        for table in doc.tables:
            table_data = {'headers': [], 'rows': []}
            if table.rows:
                # Assume first row as headers
                table_data['headers'] = [cell.text.strip() for cell in table.rows[0].cells]
                # Rest as data
                for row in table.rows[1:]:
                    table_data['rows'].append([cell.text.strip() for cell in row.cells])
            content['tables'].append(table_data)
            
    except Exception as e:
        raise Exception(f"Error extracting content from DOCX: {str(e)}")
    
    return content

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
    
def generate_report_pdf(filename, policy_name, policy_summary, assessment_results, assessment_areas, assessment_criteria, recommendations="", document_metadata=None):
    """
    Generate an enhanced PDF report with better formatting and additional metadata
    """
    """
    Generate a PDF report of the policy assessment
    
    Args:
        filename (str): Name to save the PDF as
        policy_name (str): Name of the policy document
        policy_summary (str): Summary of the policy
        assessment_results (dict): Results of the assessment
        assessment_areas (dict): Assessment areas information
        assessment_criteria (dict): Assessment criteria information
        recommendations (str, optional): Recommendations for policy improvement
        
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
        
        # Overall scores - both total and average
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(100, 10, f"Overall Total Score: {total_overall_score:.1f}", 0, 0)
        pdf.cell(0, 10, f"Overall Average Score: {total_overall_score / total_criteria_count:.2f}/5", 0, 1)
        pdf.ln(5)
        
        # Area scores table header
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, "Area Scores:", 0, 1)
        
        # Create a table for area scores
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(100, 8, "Assessment Area", 1, 0, 'L', True)
        pdf.cell(30, 8, "Total", 1, 0, 'C', True)
        pdf.cell(30, 8, "Average", 1, 1, 'C', True)
        
        # Table rows
        pdf.set_font('Arial', '', 10)
        for area_id, scores in overall_scores.items():
            area_name = assessment_areas[area_id]["name"]
            total = scores["total"]
            avg = scores["average"]
            
            # Choose color based on average score
            if avg >= 4:
                pdf.set_fill_color(220, 255, 220)  # Very light green
            elif avg >= 3:
                pdf.set_fill_color(255, 255, 220)  # Very light yellow
            else:
                pdf.set_fill_color(255, 220, 220)  # Very light red
                
            # Long area names need to be wrapped
            if len(area_name) > 50:
                area_name = area_name[:47] + "..."
                
            pdf.cell(100, 8, area_name, 1, 0, 'L')
            pdf.cell(30, 8, f"{total:.1f}", 1, 0, 'C')
            pdf.cell(30, 8, f"{avg:.2f}/5", 1, 1, 'C', True)
        
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
            
            # Display area scores in a nice box with a colored background
            if avg_score >= 4:
                pdf.set_fill_color(200, 255, 200)  # Light green
            elif avg_score >= 3:
                pdf.set_fill_color(255, 255, 200)  # Light yellow
            else:
                pdf.set_fill_color(255, 220, 220)  # Light red
                
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(190, 12, f"Area Scores: Total {total_score:.1f} | Average {avg_score:.2f}/5", 1, 1, 'C', True)
            pdf.ln(5)
            
            # Create a bar chart visualization for the PDF
            pdf.sub_section_title("Criteria Score Visualization")
            
            try:
                # Create a simple visualization using the FPDF directly for reliability
                area_criteria_data = assessment_criteria[area_id]
                
                # Get criteria names and scores
                criteria_list = list(area_results.keys())
                criteria_list.sort()  # Sort for consistent order
                
                # Set up the chart dimensions
                chart_x = 40  # Starting X position
                chart_width = 160  # Width of chart area
                bar_height = 8  # Height of each bar
                max_bar_width = 100  # Maximum width of bars at score 5
                header_height = 20  # Height for headers
                space_between = 14  # Space between bars
                
                # Calculate total chart height
                chart_height = header_height + (len(criteria_list) * (bar_height + space_between))
                
                # Check if we need a new page
                if pdf.get_y() + chart_height > pdf.page_break_trigger:
                    pdf.add_page()
                
                # Draw chart header
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 10, f"Criteria Scores for {area_info['name']}", 0, 1)
                
                # Draw the scale as a color gradient
                pdf.set_font('Arial', 'B', 8)
                scale_y = pdf.get_y()
                
                # Create a label for the scale
                pdf.text(chart_x - 35, scale_y + 3, "Score Scale:")
                
                # Draw colored segments for the scale
                segment_width = max_bar_width / 5
                
                # First segment (1) - Red
                pdf.set_fill_color(255, 204, 203)  # Light red
                pdf.rect(chart_x, scale_y, segment_width, 6, 'F')
                
                # Second segment (2) - Light red-orange
                pdf.set_fill_color(255, 229, 204)
                pdf.rect(chart_x + segment_width, scale_y, segment_width, 6, 'F')
                
                # Third segment (3) - Yellow
                pdf.set_fill_color(255, 255, 153)  # Light yellow
                pdf.rect(chart_x + 2*segment_width, scale_y, segment_width, 6, 'F')
                
                # Fourth segment (4) - Light yellow-green
                pdf.set_fill_color(229, 255, 204)
                pdf.rect(chart_x + 3*segment_width, scale_y, segment_width, 6, 'F')
                
                # Fifth segment (5) - Green
                pdf.set_fill_color(144, 238, 144)  # Light green
                pdf.rect(chart_x + 4*segment_width, scale_y, segment_width, 6, 'F')
                
                # Add a border around the scale
                pdf.set_draw_color(0, 0, 0)  # Black
                pdf.rect(chart_x, scale_y, max_bar_width, 6, 'D')
                
                # Draw scale markers
                pdf.set_font('Arial', '', 7)
                for i in range(6):
                    mark_x = chart_x + (i * segment_width)
                    if i > 0:  # Skip the first vertical line (position 0)
                        pdf.line(mark_x, scale_y, mark_x, scale_y + 6)
                    # Place numbers below the scale
                    pdf.text(mark_x - 1 if i > 0 else mark_x, scale_y + 10, str(i))
                
                # Move below the scale
                pdf.ln(15)
                
                # Draw each criterion score as a bar
                for crit_id in criteria_list:
                    criterion_name = area_criteria_data[crit_id]["name"]
                    score = area_results[crit_id].get("score", 0)
                    
                    # Draw criterion name - aligned to the right of the chart
                    bar_y = pdf.get_y()
                    
                    # Draw a text to the left of the bars
                    pdf.set_font('Arial', '', 9)
                    # Shorten long names and ensure they fit
                    name_width = 35  # Maximum width for names in characters
                    if len(criterion_name) > name_width:
                        criterion_name = criterion_name[:name_width-3] + "..."
                    
                    # Position the text before the chart
                    name_x = chart_x - 5
                    pdf.set_xy(name_x - 30, bar_y)  # Position 30 units to the left of chart start
                    pdf.cell(30, bar_height, criterion_name, 0, 0, 'R')  # Right-aligned
                    
                    # Draw bar background (gray)
                    pdf.set_fill_color(240, 240, 240)  # Light gray
                    pdf.rect(chart_x, bar_y, max_bar_width, bar_height, 'F')
                    
                    # Choose bar color based on score
                    if score >= 4:
                        pdf.set_fill_color(144, 238, 144)  # Light green
                    elif score >= 3:
                        pdf.set_fill_color(255, 255, 153)  # Light yellow
                    else:
                        pdf.set_fill_color(255, 204, 203)  # Light red
                    
                    # Draw the score bar
                    bar_width = (score / 5) * max_bar_width
                    if bar_width > 0:  # Only draw if score is greater than 0
                        pdf.rect(chart_x, bar_y, bar_width, bar_height, 'F')
                    
                    # Add a black border around the bar
                    pdf.set_draw_color(0, 0, 0)  # Black outline
                    pdf.rect(chart_x, bar_y, max_bar_width, bar_height, 'D')  # Draw outline
                    
                    # Add score text
                    pdf.set_font('Arial', 'B', 8)
                    pdf.text(chart_x + max_bar_width + 5, bar_y + (bar_height/2), f"{score}/5")
                    
                    # Space for next bar
                    pdf.ln(space_between)
                
                pdf.ln(5)
                
            except Exception as e:
                # If visualization fails, just continue without the chart
                pdf.set_font('Arial', 'I', 10)
                pdf.cell(0, 10, f"Chart visualization not available: {str(e)}", 0, 1)
            
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
    
    # Add recommendations section
    if recommendations:
        pdf.add_page()
        pdf.section_title("Recommendations for Improvement")
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 6, "Based on the assessment results, the following recommendations are provided to improve the policy:")
        pdf.ln(5)
        
        # Format the recommendations text
        pdf.set_font('Arial', '', 11)
        
        # Split recommendations by dash list items or bullet points
        if "-" in recommendations:
            rec_points = recommendations.split("-")
            for point in rec_points:
                if point.strip():
                    pdf.set_font('Arial', '', 11)
                    pdf.multi_cell(0, 6, "- " + point.strip())
                    pdf.ln(2)
        # Fallback in case bullet points are still used
        elif "•" in recommendations:
            rec_points = recommendations.split("•")
            for point in rec_points:
                if point.strip():
                    pdf.set_font('Arial', '', 11)
                    pdf.multi_cell(0, 6, "- " + point.strip())
                    pdf.ln(2)
        else:
            pdf.multi_cell(0, 6, recommendations)
    
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
