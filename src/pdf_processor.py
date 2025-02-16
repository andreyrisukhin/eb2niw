"""
Step 1: Extract text from a PDF file and create a well-formatted PDF document from input text.
Step Final: Create a well-formatted PDF document from input text.

This file contains the functions to extract text from a PDF file and create a well-formatted PDF document from input text.
"""

import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.units import inch

def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path (str): Path to the input PDF file
        
    Returns:
        str: Extracted text content
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from each page
            for page in pdf_reader.pages:
                text += page.extract_text()
                
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return None

def create_formatted_pdf(text, output_path):
    """
    Create a well-formatted PDF document from input text.
    
    Args:
        text (str): Text content to write to PDF
        output_path (str): Path where the output PDF should be saved
    """
    try:
        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Create styles
        styles = getSampleStyleSheet()
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            spaceBefore=6,
            spaceAfter=6
        )

        # Split text into paragraphs and create Paragraph objects
        content = []
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                p = Paragraph(para.replace('\n', ' '), normal_style)
                content.append(p)

        # Build the PDF
        doc.build(content)
        
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
