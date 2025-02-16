"""
Step 4: Validate and rank evidence. (Precision-like, keep only the strongest evidence)
"""

from typing import List, Dict, Tuple
import re
from collections import defaultdict

# Scoring thresholds and weights
MINIMUM_EVIDENCE_SCORE = 3
CITATION_THRESHOLD = 50
INFLUENTIAL_CITATION_THRESHOLD = 10
RECENT_YEAR_THRESHOLD = 2020

SCORE_WEIGHTS = {
    'academic': {
        'citations': 2,
        'influential_citations': 2, 
        'recent_publication': 1
    },
    'web_source': {
        'government': 3,
        'academic': 2,
        'organization': 1,
        'research_indicators': 1,
        'recognition_indicators': 2
    },
    'expert_validation': {
        'high_confidence': 3,
        'medium_confidence': 2,
        'low_confidence': 1,
        'strongly_supports': 2,
        'supports': 1
    }
}

# Source patterns
SOURCE_PATTERNS = {
    'government': r'\.gov$|\.gov/',
    'academic': r'\.edu$|\.edu/',
    'organization': r'\.org$|\.org/'
}

# Content indicators
RESEARCH_INDICATORS = ['study shows', 'research demonstrates', 'according to']
RECOGNITION_INDICATORS = ['patent', 'award', 'recognition']

def validate_and_rank_evidence(evidence_collection: List[Dict]) -> List[Dict]:
    """
    Validate and rank evidence, keeping only the strongest supporting evidence.
    
    Args:
        evidence_collection: List of evidence dictionaries from evidence gathering step
        
    Returns:
        List of validated and ranked evidence dictionaries
    """
    validated_evidence = []
    
    for evidence in evidence_collection:
        scored_evidence = score_evidence(evidence)
        if scored_evidence['strength_score'] >= MINIMUM_EVIDENCE_SCORE:
            validated_evidence.append(scored_evidence)
            
    # Sort by strength score
    validated_evidence.sort(key=lambda x: x['strength_score'], reverse=True)
    
    return validated_evidence

def score_evidence(evidence: Dict) -> Dict:
    """Score a single piece of evidence based on all available data."""
    evidence['strength_score'] = 0
    evidence['categories'] = []
    
    if evidence.get('academic_evidence'):
        academic_score = score_academic_evidence(evidence['academic_evidence'])
        evidence['strength_score'] += academic_score
        evidence['categories'].append('academic')
        
    if evidence.get('web_evidence'):
        web_scores = score_web_evidence(evidence['web_evidence'])
        evidence['strength_score'] += web_scores['score']
        evidence['categories'].extend(web_scores['categories'])
        
    if evidence.get('expert_validation'):
        expert_score = score_expert_validation(evidence['expert_validation'])
        evidence['strength_score'] += expert_score
        if expert_score > 0:
            evidence['categories'].append('expert_validated')
            
    return evidence

def score_academic_evidence(academic_evidence: Dict) -> int:
    """Score academic evidence based on citations and influence."""
    score = 0
    weights = SCORE_WEIGHTS['academic']
    
    if academic_evidence.get('citation_count', 0) > CITATION_THRESHOLD:
        score += weights['citations']
    if academic_evidence.get('influential_citation_count', 0) > INFLUENTIAL_CITATION_THRESHOLD:
        score += weights['influential_citations']
    if academic_evidence.get('year', 0) >= RECENT_YEAR_THRESHOLD:
        score += weights['recent_publication']
    return score

def score_web_evidence(web_evidence: List[Dict]) -> Dict:
    """Score web evidence based on source reputation and content."""
    score = 0
    categories = []
    weights = SCORE_WEIGHTS['web_source']
    
    for evidence in web_evidence:
        source = evidence.get('source', '').lower()
        snippet = evidence.get('snippet', '').lower()
        
        # Score based on domain
        for category, pattern in SOURCE_PATTERNS.items():
            if re.search(pattern, source):
                score += weights[category]
                categories.append(category)
            
        # Score based on content indicators
        if any(term in snippet for term in RESEARCH_INDICATORS):
            score += weights['research_indicators']
            categories.append('research_based')
        if any(term in snippet for term in RECOGNITION_INDICATORS):
            score += weights['recognition_indicators']
            categories.append('recognition')
            
    return {
        'score': score,
        'categories': list(set(categories))
    }

def score_expert_validation(validation: str) -> int:
    """Score evidence based on expert validation response."""
    if not validation:
        return 0
        
    score = 0
    validation = validation.lower()
    weights = SCORE_WEIGHTS['expert_validation']
    
    # Check confidence level
    if 'high confidence' in validation:
        score += weights['high_confidence']
    elif 'medium confidence' in validation:
        score += weights['medium_confidence']
    elif 'low confidence' in validation:
        score += weights['low_confidence']
        
    # Check evidence assessment
    if 'strongly supports' in validation:
        score += weights['strongly_supports']
    elif 'supports' in validation:
        score += weights['supports']
        
    return score

def categorize_evidence(validated_evidence: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Categorize validated evidence by type to support merit and importance claims.
    
    Args:
        validated_evidence: List of validated and ranked evidence
        
    Returns:
        Dictionary mapping categories to relevant evidence
    """
    categories = defaultdict(list)
    
    for evidence in validated_evidence:
        for category in evidence['categories']:
            categories[category].append(evidence)
            
    return dict(categories)
