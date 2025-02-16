"""
Step 3: Gather evidence for each claim.
"""

import requests
from typing import List, Tuple, Dict
import os
from serpapi import GoogleSearch
from semanticscholar import SemanticScholar
import anthropic
from perplexity import Perplexity

def gather_evidence_for_claim(claim: Tuple[str, str, str]) -> Dict:
    """
    Gather supporting evidence for a given claim from multiple sources.
    
    Args:
        claim: Tuple containing (claim_text, claim_type, initial_evidence)
        
    Returns:
        Dict containing gathered evidence and metadata
    """
    claim_text, claim_type, initial_evidence = claim
    evidence = {
        'claim_text': claim_text,
        'claim_type': claim_type,
        'initial_evidence': initial_evidence,
        'web_evidence': [],
        'academic_evidence': None,
        'expert_validation': None
    }
    
    # Search web sources
    evidence['web_evidence'].extend(search_perplexity(claim_text))
    evidence['web_evidence'].extend(search_you_dot_com(claim_text))
    evidence['web_evidence'].extend(search_serp(claim_text))
    
    # For academic claims, validate using Semantic Scholar
    if contains_academic_reference(claim_text):
        evidence['academic_evidence'] = validate_academic_claim(claim_text)
    
    # Get expert validation using Claude
    evidence['expert_validation'] = get_expert_validation(claim_text, evidence['web_evidence'])
    
    return evidence

def search_perplexity(query: str) -> List[Dict]:
    """Search Perplexity API for evidence."""
    client = Perplexity(api_key=os.getenv('PERPLEXITY_API_KEY'))
    results = []
    
    try:
        response = client.search(query)
        for result in response['results']:
            results.append({
                'source': 'perplexity',
                'title': result.get('title'),
                'snippet': result.get('snippet'),
                'url': result.get('url')
            })
    except Exception as e:
        print(f"Perplexity search error: {str(e)}")
        
    return results

def search_you_dot_com(query: str) -> List[Dict]:
    """Search You.com API for evidence."""
    api_key = os.getenv('YOU_API_KEY')
    url = f"https://api.you.com/search"
    
    try:
        response = requests.get(url, 
            params={'q': query, 'key': api_key},
            headers={'Accept': 'application/json'}
        )
        results = []
        for item in response.json().get('hits', []):
            results.append({
                'source': 'you.com',
                'title': item.get('title'),
                'snippet': item.get('snippet'),
                'url': item.get('url')
            })
        return results
    except Exception as e:
        print(f"You.com search error: {str(e)}")
        return []

def search_serp(query: str) -> List[Dict]:
    """Search using SerpAPI."""
    try:
        search = GoogleSearch({
            "q": query,
            "api_key": os.getenv('SERP_API_KEY')
        })
        results = []
        for item in search.get_dict().get('organic_results', []):
            results.append({
                'source': 'serp',
                'title': item.get('title'),
                'snippet': item.get('snippet'),
                'url': item.get('link')
            })
        return results
    except Exception as e:
        print(f"SERP API error: {str(e)}")
        return []

def contains_academic_reference(text: str) -> bool:
    """Check if claim contains academic references."""
    academic_indicators = [
        'paper', 'research', 'study', 'journal', 'publication',
        'published', 'doi', 'arxiv', 'conference'
    ]
    return any(indicator in text.lower() for indicator in academic_indicators)

def validate_academic_claim(text: str) -> Dict:
    """Validate academic claims using Semantic Scholar."""
    sch = SemanticScholar()
    results = {}
    
    try:
        # Extract paper title or DOI if present
        # This is a simplified extraction - could be more sophisticated
        search_results = sch.search_paper(text, limit=5)
        
        if search_results:
            paper = search_results[0]
            results = {
                'title': paper.title,
                'authors': [author.name for author in paper.authors],
                'year': paper.year,
                'citation_count': paper.citationCount,
                'influential_citation_count': paper.influentialCitationCount,
                'url': paper.url
            }
    except Exception as e:
        print(f"Semantic Scholar API error: {str(e)}")
        
    return results

def get_expert_validation(claim: str, evidence: List[Dict]) -> str:
    """Use Claude to validate claim against gathered evidence."""
    client = anthropic.Anthropic()
    
    evidence_text = "\n".join([
        f"Source: {e['source']}\n{e['snippet']}"
        for e in evidence
    ])
    
    prompt = f"""Please analyze this claim and the supporting evidence to validate its accuracy:
    
    CLAIM: {claim}
    
    EVIDENCE:
    {evidence_text}
    
    Please provide:
    1. An assessment of whether the evidence supports the claim
    2. Any potential gaps or limitations in the evidence
    3. Overall confidence level in the claim (High/Medium/Low)
    """
    
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=500,
            temperature=0,
            system="You are an expert validator analyzing claims and evidence.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Claude API error: {str(e)}")
        return None

def gather_evidence(claims: List[Tuple[str, str, str]]) -> List[Dict]:
    """
    Gather evidence for a list of claims.
    
    Args:
        claims: List of claim tuples (claim_text, claim_type, initial_evidence)
        
    Returns:
        List of evidence dictionaries for each claim
    """
    evidence_collection = []
    
    for claim in claims:
        evidence = gather_evidence_for_claim(claim)
        evidence_collection.append(evidence)
        
    return evidence_collection
