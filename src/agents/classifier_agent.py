"""
Classifier Agent (stub)
- Accepts event with `text` and returns a domain tag and confidence score.
- Production: replace stubs with model calls, caching, and fallback logic.
"""
from typing import Dict

def classify(text: str) -> Dict:
    # Placeholder deterministic rules for prototyping
    text_low = text.lower()
    if "permit" in text_low or "application" in text_low:
        return {"domain": "procedural", "confidence": 0.87}
    if "emission" in text_low or "epa" in text_low or "environment" in text_low:
        return {"domain": "environmental", "confidence": 0.92}
    if "liability" in text_low or "law" in text_low or "statute" in text_low:
        return {"domain": "legal", "confidence": 0.9}
    return {"domain": "triage-human", "confidence": 0.45}

if __name__ == "__main__":
    sample = "Is the new permit application conforming to EPA guidance?"
    print(classify(sample))
