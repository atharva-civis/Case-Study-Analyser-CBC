import os
import json
import PyPDF2
import docx
import requests
from io import BytesIO
from openai import OpenAI

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
                return json.loads(content)
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON response", "raw_content": content}
        
        return content
    
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"
