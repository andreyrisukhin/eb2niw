"""
Step 2: Extract claims from the text.
"""

import spacy
from typing import List, Dict, Tuple

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
    client = anthropic.Anthropic()
    
    # Define specific prompts to assess different types of claims
    merit_prompts = [
        "Does the text describe specific technical achievements or innovations?",
        "Are there measurable impacts or improvements described?",
        "Does it demonstrate advancement in a particular field or industry?",
        "Are there quantifiable metrics showing value or merit?",
        "Does it describe novel solutions to existing problems?"
    ]

    importance_prompts = [
        "Does it address a national need or challenge?",
        "Are there broad societal or economic implications?",
        "Does it benefit multiple sectors or regions of the country?",
        "Is there evidence of widespread adoption or interest?",
        "Does it contribute to national priorities (e.g. healthcare, security, economy)?",
        "Does it have implications beyond a single company or organization?"
    ]

    evidence_prompts = [
        "Are there specific examples or case studies provided?",
        "Is there data or statistics supporting the claims?",
        "Are there expert opinions or testimonials cited?",
        "Is there documentation of real-world implementation?",
        "Are there references to peer-reviewed research or publications?"
    ]

    # Combine all prompts into a comprehensive analysis framework
    prompt_framework = """Please analyze the following text using these specific criteria:

    Merit Assessment:
    - {merit_prompts_str}

    National Importance Assessment:
    - {importance_prompts_str}

    Evidence Validation:
    - {evidence_prompts_str}

    For each claim identified, provide:
    1. Whether it demonstrates merit or national importance based on the above criteria
    2. The specific claim text
    3. Supporting evidence that addresses the evidence criteria above

    Please be thorough but only extract claims that explicitly relate to merit or national importance."""

    # Format the prompt lists into strings
    merit_prompts_str = "\n- ".join(merit_prompts)
    importance_prompts_str = "\n- ".join(importance_prompts)
    evidence_prompts_str = "\n- ".join(evidence_prompts)

    # Create the final formatted prompt
    analysis_prompt = prompt_framework.format(
        merit_prompts_str=merit_prompts_str,
        importance_prompts_str=importance_prompts_str,
        evidence_prompts_str=evidence_prompts_str
    )

    
    # Craft specific prompt for claim extraction
    prompt = f"""Please analyze the following text and extract claims about national importance 
    and substantial merit. For each claim:
    1. Identify if it relates to 'merit' or 'national importance'
    2. Extract the specific claim text
    3. Find any supporting evidence
    
    Format each as: CLAIM TYPE: <merit/importance>
    CLAIM TEXT: <exact quote>
    EVIDENCE: <supporting text>
    
    Only extract claims that are explicitly about merit or national importance.
    Text to analyze: {text}"""

    # Get response from Claude
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0,
        system="You are a specialized claim extractor focused on identifying claims about national importance and substantial merit in immigration contexts.",
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse response into claims
    claims = []
    current_claim = {}
    
    for line in response.content[0].text.split('\n'):
        line = line.strip()
        if line.startswith('CLAIM TYPE:'):
            if current_claim:
                claims.append((
                    current_claim['text'],
                    current_claim['type'],
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
            current_claim['text'],
            current_claim['type'],
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
    spacy_claims = extract_claims_spacy(text)
    # anthropic_claims = extract_claims_anthropic(text) # TODO Optimize token cost by not passing text already marked as a claim
    
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
    return spacy_claims


