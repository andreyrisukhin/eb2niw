"""
Step 3: Gather evidence for each claim.
"""

import requests
from typing import List, Tuple, Dict
import os
from serpapi import GoogleSearch

from semanticscholar import SemanticScholar
from scholarly import scholarly # Google Scholar API

import anthropic
# from perplexity import Perplexity # TODO add perplexity API key

# Plan for gathering evidence:
"""
* Here are a few tips for where evidence of national importance can be sourced from:
    
When a scientific artifact of work is mentioned, such as a publication, search Semantic Scholar and Google Scholar for the paper. Record its impact metrics, and interpret them.
    TODO implement once deanonymized data

If specific commercial work or its award is mentioned, look for articles:
    1.	Media articles and reports from reputable outlets that highlight the broader impact of your work or its alignment with national interests
    6.	Evidence of media coverage in national or reputable regional outlets, indicating broader interest in your work
    TODO implement once deanonymized data

If a claim mentions a specific topic, compare its alignment with government priorities:
    2.	Evidence showing your work aligns with U.S. government priorities, such as federal climate action initiatives or energy independence goals - Executive orders or government press releases
    3.	Documentation demonstrating your work's potential to employ U.S. workers or have significant economic impact, particularly in economically depressed areas
    4.	Evidence of your work's potential to produce significant economic impact or other substantial positive economic effects
    Compare against govt priorities text (in context; docs added/removed as priorities change especially with current administration)

When a claim mentions advancements in a field or claims to be on the cutting edge, search for:
    5.	Documentation showing your endeavor has national or global implications within a particular field, such as improved manufacturing processes or medical advances
    7.	Comparative analysis demonstrating how your work stands out in your field, emphasizing its unique national importance
    8.	Documentation showing the scalability of your work, indicating its potential for broader impact beyond its current scope
    Search for evidence from Harvard Business Review, MIT Technology Review, and other reputable sources.
    Use Perplexity, Google Search to find evidence.
"""


# From https://www.state.gov/priorities-and-mission-of-the-second-trump-administrations-department-of-state/
usa_administration_priorities = """
Every dollar we spend, every program we fund, and every policy we pursue must be justified with the answer to three simple questions:
(1) Does it make America safer?  
(2) Does it make America stronger?  
(3) Does it make America more prosperous?  

First, we must curb mass migration and secure our borders. The State Department will no longer undertake any activities that facilitate or encourage mass migration.  Our diplomatic relations with other countries, particularly in the Western Hemisphere, will prioritize securing America’s borders, stopping illegal and destabilizing migration, and negotiating the repatriation of illegal immigrants.

Next, we must reward performance and merit, including within the State Department ranks. President Trump issued an executive order eliminating “DEIA” requirements, programs, and offices throughout the government. This order will be faithfully executed and observed in both letter and spirit.

Relatedly, we must return to the basics of diplomacy by eliminating our focus on political and cultural causes that are divisive at home and deeply unpopular abroad. This will allow us to conduct a pragmatic foreign policy in cooperation with other nations to advance our core national interests.

We must stop censorship and suppression of information. The State Department’s efforts to combat malign propaganda have expanded and fundamentally changed since the Cold War era and we must reprioritize truth. The State Department I lead will support and defend Americans’ rights to free speech, terminating any programs that in any way lead to censoring the American people.  While we will combat genuine enemy propaganda, we will do so only with the fundamental truth that America is a great and just country whose people are generous and whose leaders now prioritize Americans’ core interests while respecting the rights and interests of other nations.

Finally, we must leverage our strengths and do away with climate policies that weaken America. While we will not ignore threats to our natural environment and will support sensible environmental protections, the State Department will use diplomacy to help President Trump fulfill his promise for a return to American energy dominance.

In short, President Trump’s forward-looking agenda for our country and foreign relations will guide the State Department’s refocus on American national interests. Amid today’s reemerging great power rivalry, I will empower our talented diplomatic corps to advance our mission to make America safer, stronger, and more prosperous.
"""
# TODO also include current executive orders, their influence.
# TODO generate explanation of how this applicant for immigration is aligned with these priorities and extraordinarily talented, emphasizing the benefit to the US of admitting them.

def process_claim_by_type(claim: Tuple[str, str, str]) -> List[Dict]:
    """
    Process a claim based on its type (background or importance).
    For background claims, return a placeholder for applicant evidence.
    For importance claims, gather supporting evidence from various sources.
    
    Args:
        claim_text: The text of the claim
        claim_type: Type of claim ('background' or 'importance')
        
    Returns:
        List of evidence dictionaries
    """
    claim_type, claim_text, initial_evidence = claim
    if claim_type == 'background':
        return [{
            'source': 'PLACEHOLDER',
            'snippet': '[Applicant to provide supporting documentation such as: '
                      'degrees, certifications, employment records, awards, '
                      'or other relevant evidence of expertise and experience.]',
            'relevance': 'Direct background evidence required'
        }]
        
    elif claim_type == 'importance':
        evidence = []
        
        # TODO implement search over tech articles, industry sources (Pitchbook to show rising industries?)
        # # Check for field/technology mentions to find industry impact
        # tech_sources = ['Harvard Business Review', 'MIT Technology Review', 
        #                'Nature', 'Science', 'Forbes']
        # for source in tech_sources:
        #     results = search_serp(f'site:{source} {claim_text}')
        #     evidence.extend(results)

        # TODO eventually implement search, executive order search as they come out, for now just use the statement of priorities.
        # # Check alignment with government priorities
        # gov_priorities = [
        #     'artificial intelligence leadership',
        #     'healthcare innovation',
        #     'energy independence', 
        #     'economic growth',
        #     'national security',
        #     'renewable energy'
        # ]
        
        # for priority in gov_priorities:
        #     if priority.lower() in claim_text.lower():
        #         results = search_serp(
        #             f'site:whitehouse.gov OR site:energy.gov OR site:defense.gov '
        #             f'{priority} {claim_text}'
        #         )
        #         evidence.extend(results)
                
        # # Look for economic impact evidence
        # if any(term in claim_text.lower() for term in ['economic', 'jobs', 'growth']):
        #     results = search_serp(
        #         f'site:bls.gov OR site:commerce.gov {claim_text}'
        #     )
        #     evidence.extend(results)

        # Get concise analysis of how claim aligns with priorities
        prompt = f"""Analyze how this claim aligns with U.S. administration priorities. Be extremely concise, 1-2 sentences per relevant priority:
        Claim: {claim_text}
        Priorities to check alignment with:
        {usa_administration_priorities}"""

        # Initialize Anthropic client
        anthropic.api_key = os.getenv("ANTHROPIC_API_KEY")
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0,
            system="You are an expert policy analyst. Be extremely concise.",
            messages=[{"role": "user", "content": prompt}]
        )

        evidence.append({
            'source': 'U.S. Administration Priorities Analysis',
            'snippet': response.content,
            'relevance': 'Direct alignment with administration priorities'
        })

        return evidence
            
    return []

def gather_evidence_all_claims(claims: List[Tuple[str, str, str]]) -> List[Dict]:
    """
    Gather evidence for a list of claims.
    
    Args:
        claims: List of claim tuples (claim_text, claim_type, initial_evidence)
        
    Returns:
        List of evidence dictionaries for each claim
    """
    evidence_collection = []
    for claim in claims:
        evidence = process_claim_by_type(claim)
        evidence_collection.append(evidence)
        
    return evidence_collection


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# TODO Below are methods for gathering evidence from various sources. These are not used in the current implementation.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def gather_evidence_for_claim(claim: Tuple[str, str, str]) -> Dict:
    """
    Gather supporting evidence for a given claim from multiple sources.
    
    Args:
        claim: Tuple containing (claim_text, claim_type, initial_evidence)
        
    Returns:
        Dict containing gathered evidence and metadata
    """
    claim_type, claim_text, initial_evidence = claim
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
