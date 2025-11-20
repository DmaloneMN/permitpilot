"""
Reviewer Agent
- Validates tone, clarity, compliance flags, and risk of hallucination.
- Returns 'approve' or 'reject' with suggested edits.

Key Features:
- Tone and professionalism checks
- Clarity and completeness validation
- Hallucination risk detection
- Compliance flag identification
- Actionable feedback generation
"""
from typing import Dict, List


class ReviewError(Exception):
    """Custom exception for reviewer errors."""
    pass


# Problematic phrases that indicate issues
HEDGING_PHRASES = ["I think", "I believe", "maybe", "possibly", "might be"]
INFORMAL_PHRASES = ["gonna", "wanna", "kinda", "sorta", "yeah", "nope"]
UNCERTAIN_PHRASES = ["not sure", "unclear", "don't know", "can't say"]
HALLUCINATION_INDICATORS = [
    "according to my knowledge",
    "as far as I know",
    "I recall",
    "if I remember correctly"
]


def review(draft: str, strict_mode: bool = False) -> Dict:
    """
    Review a draft response for quality, tone, and compliance.
    
    Args:
        draft: Draft response text to review
        strict_mode: If True, applies stricter validation rules
    
    Returns:
        Dictionary with 'approved', 'reasons', 'suggestions', and 'score'
    
    Raises:
        ReviewError: If draft is invalid
    """
    # Validate input
    if not draft or not isinstance(draft, str):
        raise ReviewError("Draft must be a non-empty string")
    
    if len(draft.strip()) == 0:
        raise ReviewError("Draft cannot be empty or whitespace only")
    
    # Run all review checks
    issues = []
    suggestions = []
    
    # Check 1: Hedging language
    hedging_issues = _check_hedging(draft)
    if hedging_issues:
        issues.extend(hedging_issues)
        suggestions.append(
            "Remove hedging language and use definitive, sourced statements."
        )
    
    # Check 2: Informal language
    informal_issues = _check_informal_language(draft)
    if informal_issues:
        issues.extend(informal_issues)
        suggestions.append(
            "Replace informal language with professional terminology."
        )
    
    # Check 3: Uncertainty indicators
    uncertainty_issues = _check_uncertainty(draft)
    if uncertainty_issues:
        issues.extend(uncertainty_issues)
        suggestions.append(
            "Address uncertainties with qualified statements or request clarification."
        )
    
    # Check 4: Hallucination risk
    hallucination_issues = _check_hallucination_risk(draft)
    if hallucination_issues:
        issues.extend(hallucination_issues)
        suggestions.append(
            "Remove subjective phrases and cite specific sources or regulations."
        )
    
    # Check 5: Completeness and structure
    completeness_issues = _check_completeness(draft, strict_mode)
    if completeness_issues:
        issues.extend(completeness_issues)
        suggestions.extend(completeness_issues)
    
    # Calculate quality score (0-100)
    score = _calculate_quality_score(draft, len(issues))
    
    # Determine approval status
    # Approve if no critical issues or score is high enough
    approved = len(issues) == 0 or (not strict_mode and score >= 70)
    
    return {
        "approved": approved,
        "reasons": issues,
        "suggestions": suggestions,
        "score": score,
        "checks_performed": [
            "hedging_language",
            "informal_language",
            "uncertainty",
            "hallucination_risk",
            "completeness"
        ]
    }


def _check_hedging(draft: str) -> List[str]:
    """Check for hedging language that undermines authority."""
    issues = []
    draft_lower = draft.lower()
    
    for phrase in HEDGING_PHRASES:
        if phrase.lower() in draft_lower:
            issues.append(f"Hedging language detected: '{phrase}'")
    
    return issues


def _check_informal_language(draft: str) -> List[str]:
    """Check for informal or colloquial language."""
    issues = []
    draft_lower = draft.lower()
    
    for phrase in INFORMAL_PHRASES:
        if phrase.lower() in draft_lower:
            issues.append(f"Informal language detected: '{phrase}'")
    
    return issues


def _check_uncertainty(draft: str) -> List[str]:
    """Check for expressions of uncertainty."""
    issues = []
    draft_lower = draft.lower()
    
    for phrase in UNCERTAIN_PHRASES:
        if phrase.lower() in draft_lower:
            issues.append(f"Uncertainty expression detected: '{phrase}'")
    
    return issues


def _check_hallucination_risk(draft: str) -> List[str]:
    """Check for phrases that indicate potential hallucination."""
    issues = []
    draft_lower = draft.lower()
    
    for phrase in HALLUCINATION_INDICATORS:
        if phrase.lower() in draft_lower:
            issues.append(f"Potential hallucination indicator: '{phrase}'")
    
    return issues


def _check_completeness(draft: str, strict_mode: bool) -> List[str]:
    """Check if response appears complete and well-structured."""
    issues = []
    
    # Check minimum length (at least 50 characters for a meaningful response)
    if len(draft) < 50:
        issues.append("Response is too short to be comprehensive")
    
    # In strict mode, require more structure
    if strict_mode:
        # Check for paragraph structure (at least 2 newlines)
        if draft.count('\n') < 2:
            issues.append("Response lacks paragraph structure")
        
        # Check for substantive content (not just placeholder)
        if "stub" in draft.lower() or "placeholder" in draft.lower():
            issues.append("Response contains placeholder content")
    
    return issues


def _calculate_quality_score(draft: str, issue_count: int) -> int:
    """
    Calculate a quality score for the draft (0-100).
    
    Args:
        draft: Draft text
        issue_count: Number of issues found
    
    Returns:
        Quality score (0-100)
    """
    # Start with perfect score
    score = 100
    
    # Deduct points for each issue
    score -= (issue_count * 15)
    
    # Bonus for length (indicates thoroughness)
    if len(draft) > 200:
        score += 5
    if len(draft) > 500:
        score += 5
    
    # Ensure score is in valid range
    return max(0, min(100, score))

if __name__ == "__main__":
    print(review("This is my draft. I think this is acceptable."))
