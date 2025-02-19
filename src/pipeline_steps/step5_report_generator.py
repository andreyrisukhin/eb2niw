"""
Step 5: Generate a well-formatted PDF document listing all supporting evidence and arguments for eligibility criterion #1.
"""

from typing import Dict, List, Tuple
from pipeline_steps.step1_pdf_processor import create_formatted_pdf
import anthropic
import os

def generate_evidence_report(claims: List, validated_evidence: List):
    """
    Generate a well-formatted PDF report documenting evidence for NIW eligibility criterion #1.
    
    Args:
        validated_evidence: List of validated and categorized evidence 
        # TODO: applicant_info: Dictionary containing applicant details (name, field, etc.)
    """
    use_anthropic = True
    if use_anthropic:
        report_content = _generate_report_with_anthropic(claims, validated_evidence)
    else:
        report_content = _generate_report_template(applicant_info, validated_evidence)
        
    return report_content

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


# TODO update this to support the profile of the applicant (first name, last name, Dr. or Prof. if relevant, ...)
def _generate_report_with_anthropic(claims: List[Tuple[str, str, str]], evidence_list: List[str]) -> str:
    """
    Generate report content using Anthropic's API by synthesizing claims and evidence.
    
    Args:
        claims: List of (claim_type, claim_text, claim_explanation) tuples from step 2
        evidence_list: List of evidence strings from step 3
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Group claims by type
    claims_by_type = {}
    for claim_type, claim_text, explanation in claims:
        if claim_type not in claims_by_type:
            claims_by_type[claim_type] = []
        claims_by_type[claim_type].append((claim_text, explanation))

    # Match evidence to claims where possible
    evidence_summary = []
    for i, (claim_type, claim_group) in enumerate(claims_by_type.items()):
        evidence_summary.append(f"\nClaim Type: {claim_type}")
        for claim_text, explanation in claim_group:
            evidence_summary.append(f"\nClaim: {claim_text}")
            evidence_summary.append(f"Context: {explanation}")
            if i < len(evidence_list):
                evidence_summary.append(f"Supporting Evidence: {evidence_list[i]}")
    
    prompt = f"""
    Generate a formal 2-3 paragraph report synthesizing the following claims and evidence. 
    Each paragraph should address a key claim and its supporting evidence.
    Maintain a formal, academic tone and focus on demonstrating substantial merit and national importance.

    Claims and Evidence:
    {chr(10).join(evidence_summary)}

    Focus on synthesizing the strongest evidence that validates the original claims made.
    Avoid speculating beyond what is directly supported by the evidence provided.
    """ # char 10 is newline

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

