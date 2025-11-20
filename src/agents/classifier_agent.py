"""
Classifier Agent
- Accepts event with `text` and returns a domain tag and confidence score.
- Production: replace stubs with model calls, caching, and fallback logic.

Key Features:
- Domain classification (legal, environmental, procedural)
- Confidence scoring
- Error handling and validation
- Extensible rule-based fallback
"""
from typing import Dict, Optional


class ClassificationError(Exception):
    """Custom exception for classification errors."""
    pass


def classify(text: str, min_confidence: Optional[float] = None) -> Dict:
    """
    Classify input text into a regulatory domain.
    
    Args:
        text: Input text to classify
        min_confidence: Optional minimum confidence threshold
    
    Returns:
        Dictionary with 'domain' and 'confidence' keys
    
    Raises:
        ClassificationError: If text is invalid or classification fails
    """
    # Validate input
    if not text or not isinstance(text, str):
        raise ClassificationError("Text must be a non-empty string")
    
    if len(text.strip()) == 0:
        raise ClassificationError("Text cannot be empty or whitespace only")
    
    # Placeholder deterministic rules for prototyping
    # In production, this would call a fine-tuned model or LLM
    text_low = text.lower()
    
    # Environmental domain keywords
    if any(keyword in text_low for keyword in [
        "emission", "epa", "environment", "pollution", 
        "air quality", "water quality", "hazardous"
    ]):
        domain, confidence = "environmental", 0.92
    # Procedural domain keywords
    elif any(keyword in text_low for keyword in [
        "permit", "application", "process", "filing",
        "deadline", "submission", "procedure"
    ]):
        domain, confidence = "procedural", 0.87
    # Legal domain keywords
    elif any(keyword in text_low for keyword in [
        "liability", "law", "statute", "regulation",
        "compliance", "legal", "attorney"
    ]):
        domain, confidence = "legal", 0.90
    # Default: requires human triage
    else:
        domain, confidence = "triage-human", 0.45
    
    # Check minimum confidence threshold if provided
    if min_confidence is not None and confidence < min_confidence:
        domain = "triage-human"
    
    return {
        "domain": domain,
        "confidence": confidence,
        "text_length": len(text)
    }

if __name__ == "__main__":
    sample = "Is the new permit application conforming to EPA guidance?"
    print(classify(sample))
