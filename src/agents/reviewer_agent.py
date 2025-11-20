"""
Reviewer Agent (stub)
- Validates tone, clarity, compliance flags, and risk of hallucination.
- Returns 'approve' or 'reject' with suggested edits.
"""
from typing import Dict

def review(draft: str) -> Dict:
    # Simple heuristic checks
    if "I think" in draft:
        return {"approved": False, "reasons":["hedging language"], "suggestion":"Use definitive, sourced statements."}
    return {"approved": True, "reasons": [], "suggestion": ""}

if __name__ == "__main__":
    print(review("This is my draft. I think this is acceptable."))
