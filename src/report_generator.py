"""
Step 5: Generate a well-formatted PDF document listing all supporting evidence and arguments for eligibility criterion #1.
"""

from typing import Dict, List
from pdf_processor import create_formatted_pdf
import anthropic
import os

def generate_evidence_report(applicant_info: Dict, validated_evidence: List[Dict], output_path: str, use_anthropic: bool = False):
    """
    Generate a well-formatted PDF report documenting evidence for NIW eligibility criterion #1.
    
    Args:
        applicant_info: Dictionary containing applicant details (name, field, etc.)
        validated_evidence: List of validated and categorized evidence 
        output_path: Path to save the output PDF report
        use_anthropic: Whether to use Anthropic's API for report generation
    """
    if use_anthropic:
        report_content = _generate_report_with_anthropic(applicant_info, validated_evidence)
    else:
        report_content = _generate_report_template(applicant_info, validated_evidence)
        
    # Generate PDF
    create_formatted_pdf(report_content, output_path)

def _generate_report_template(applicant_info: Dict, validated_evidence: List[Dict]) -> str:
    """Generate report content using template approach"""
    report_sections = []
    
    # Section 2 header
    report_sections.append(f"Section.2 Dr. {applicant_info['name']}'s proposed endeavor has both substantial merit and national importance for the United States")
    
    # Overview paragraph
    report_sections.append(
        f"Dr. {applicant_info['name']}'s proposed endeavor is to develop state-of-the-art {applicant_info['field']} "
        f"for {applicant_info['endeavor_description']}. Among other applications, Dr. {applicant_info['name']}'s work "
        f"is relevant to {', '.join(applicant_info['applications'])}, which is of substantial merit and great importance "
        f"to the United States."
    )
    
    # Section 2.1 - Merit
    report_sections.append(f"2.1 {applicant_info['field']} is an area of substantial merit")
    
    # Field description and impact
    for evidence in validated_evidence:
        if evidence['category'] == 'field_impact':
            report_sections.append(evidence['content'])
            if evidence.get('source'):
                report_sections.append(f"({evidence['source']})")
    
    # Market data and government recognition
    for evidence in validated_evidence:
        if evidence['category'] in ['market_data', 'government_recognition']:
            report_sections.append(evidence['content'])
            if evidence.get('source'):
                report_sections.append(f"({evidence['source']})")
    
    # Merit summary
    report_sections.append(
        f"In summary, {applicant_info['field']} is an important technology and has broad impact in many industries. "
        "It is of substantial merit to the United States."
    )
    
    # Section 2.2 - Benefits
    report_sections.append(f"2.2 Dr. {applicant_info['name']}'s work will be beneficial to the United States")
    
    # Specific benefits and applications
    for evidence in validated_evidence:
        if evidence['category'] == 'specific_benefits':
            report_sections.append(evidence['content'])
    
    # Expert testimonials
    report_sections.append(
        "Fellow experts in the field have provided further detail on the importance of this endeavor:"
    )
    for evidence in validated_evidence:
        if evidence['category'] == 'expert_testimony':
            report_sections.append(
                f"• \"{evidence['content']}\" ({evidence['source']})"
            )
    
    return '\n\n'.join(report_sections)

def _generate_report_with_anthropic(applicant_info: Dict, validated_evidence: List[Dict]) -> str:
    """Generate report content using Anthropic's API"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Prepare evidence summary for prompt
    evidence_summary = []
    for evidence in validated_evidence:
        evidence_summary.append(f"Category: {evidence['category']}")
        evidence_summary.append(f"Content: {evidence['content']}")
        if evidence.get('source'):
            evidence_summary.append(f"Source: {evidence['source']}")
        evidence_summary.append("---")
    
    prompt = f"""
    Generate a formal report section demonstrating that Dr. {applicant_info['name']}'s work in {applicant_info['field']} 
    has substantial merit and national importance for the United States. Use the following evidence and maintain a formal,
    academic tone:

    Applicant Details:
    Name: {applicant_info['name']}
    Field: {applicant_info['field']}
    Endeavor: {applicant_info['endeavor_description']}
    Applications: {', '.join(applicant_info['applications'])}

    Evidence:
    {'\n'.join(evidence_summary)}

    The report should follow this structure:
    1. Overview of the endeavor
    2. Discussion of field's substantial merit
    3. Market and government recognition
    4. Specific benefits to the United States
    5. Expert testimonials
    """

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2000,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

