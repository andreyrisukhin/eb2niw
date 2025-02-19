"""
Step 2: Extract claims from the text.
"""
# import spacy
from typing import List, Dict, Tuple
import os

# TODO: Improve spacy extraction to be more accurate before using it again.
def extract_claims_spacy(text: str) -> List[Tuple[str, str, str]]:
    """
    Extract claims about national importance and substantial merit from the text.
    
    Args:
        text (str): Input text from which to extract claims
        
    Returns:
        List[Tuple[str, str, str]]: List of extracted claims, where each tuple contains:
            - claim: The actual claim text in original case
            - type: Either 'merit' or 'importance'
            - evidence: Supporting text/evidence for the claim in original case
    """
    # Load English language model
    nlp = spacy.load("en_core_web_sm")
    
    # Process the text
    doc = nlp(text)
    
    claims = []
    
    # Keywords indicating claims about merit/importance (case insensitive matching)
    merit_keywords = ["merit", "valuable", "significant", "achievement", "impact", "advance", "improve"]
    importance_keywords = ["national", "importance", "benefit", "united states", "country", "public", "society"]
    
    # Analyze each sentence
    for sent in doc.sents:
        sent_text_lower = sent.text.lower()
        
        # Check if sentence contains claim indicators
        is_merit = any(keyword in sent_text_lower for keyword in merit_keywords)
        is_importance = any(keyword in sent_text_lower for keyword in importance_keywords)
        
        if is_merit or is_importance:
            claim_type = "merit" if is_merit else "importance"
            
            # Look for supporting evidence in next sentence
            next_sent = next(doc.sents, None)
            evidence = next_sent.text if next_sent else ""
            
            # Store original text with original capitalization
            claims.append((
                sent.text.strip(),
                claim_type,
                evidence.strip()
            ))
    
    return claims

def extract_claims_anthropic(text: str) -> List[Tuple[str, str, str]]:
    """
    Extract claims about national importance and substantial merit using Anthropic's Claude API.
    
    Args:
        text (str): Input text from which to extract claims
        
    Returns:
        List[Tuple[str, str, str]]: List of extracted claims, where each tuple contains:
            - claim: The actual claim text
            - type: Either 'merit' or 'importance' 
            - evidence: Supporting text/evidence for the claim
    """
    try:
        import anthropic
    except ImportError:
        print("anthropic package not installed. Please install with: pip install anthropic")
        return []

    # Initialize Anthropic client
    anthropic.api_key = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic()

    prompt_2 = f"""You are an expert at extracting claims from an immigration petition for an EB-2 NIW (National Interest Waiver) visa.

    You will be given a text and you will need to extract every claim that is either a:
        (1) Claim about the subject's background and previous experiences
        (2) Claim about the national importance of the subject's work
    
    When deciding whether a sentence is a claim about the subject's background, consider the following:
        - Does the sentence mention the subject's education, work experience, publications, patents, awards, or other background experiences 
        or accomplishments that are relevant to their eligibility for an EB-2 NIW visa?

    When deciding whether a sentence is a claim about the national importance of the subject's work, consider the following:
        - Does the sentence describe the impact of the work on the U.S. or its citizens?
        - Does the sentence describe the potential for the work to have a significant economic, scientific, or technological impact?
        - Does the sentence describe the potential for the work to have a significant impact on national security?
        - Does the sentence compare the subject's work to other works or achievements in the same field?
        - Does the sentence mention media articles or reports from reputable outlets that highlight the broader impact of the work or alignment with U.S. government priorities?

    Format each claim as: CLAIM TYPE: <background/importance>
    CLAIM TEXT: <exact quote>
    EVIDENCE: <supporting text>

    Only extract claims that are explicitly about the subject's background or their work's national importance.
    Text to analyze: {text}"""

    # Get response from Claude
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0,
        system="You are a specialized claim extractor focused on identifying claims about national importance and substantial merit in immigration contexts.",
        messages=[{"role": "user", "content": prompt_2}]
    )

    # Parse response into claims
    claims = []
    current_claim = {}
    
    for line in response.content[0].text.split('\n'):
        line = line.strip()
        if line.startswith('CLAIM TYPE:'):
            if current_claim:
                claims.append((
                    current_claim['type'],
                    current_claim['text'],
                    current_claim['evidence']
                ))
            current_claim = {'type': line.split(':')[1].strip().lower()}
        elif line.startswith('CLAIM TEXT:'):
            current_claim['text'] = line.split(':')[1].strip()
        elif line.startswith('EVIDENCE:'):
            current_claim['evidence'] = line.split(':')[1].strip()

    # Add final claim if exists
    if current_claim:
        claims.append((
            current_claim['type'],
            current_claim['text'],
            current_claim['evidence']
        ))

    return claims

def extract_claims_combined(text: str) -> List[Tuple[str, str, str]]:
    """
    Combine claims extracted from multiple methods for more comprehensive results.
    
    Args:
        text (str): Input text from which to extract claims
        
    Returns:
        List[Tuple[str, str, str]]: Combined and deduplicated list of claims
    """
    # Get claims from both methods
    # spacy_claims = extract_claims_spacy(text)
    anthropic_claims = extract_claims_anthropic(text) # If another method is added, optimize token cost by not passing text already marked as a claim
    
    # # Combine claims, removing duplicates
    # all_claims = spacy_claims + anthropic_claims
    
    # # Remove duplicates while preserving order
    # seen = set()
    # unique_claims = []
    
    # for claim in all_claims:
    #     # Create normalized version for comparison
    #     normalized = (
    #         claim[0].lower().strip(),
    #         claim[1].lower().strip(),
    #         claim[2].lower().strip()
    #     )
        
    #     if normalized not in seen:
    #         seen.add(normalized)
    #         unique_claims.append(claim)
    
    # return unique_claims
    return anthropic_claims


