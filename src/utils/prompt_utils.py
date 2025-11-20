"""
Prompt utilities:
- slot_fill(template, slots): fills template safely
- enforce_token_budget(text, budget, strategy): truncate intelligently
"""
def slot_fill(template: str, slots: dict) -> str:
    return template.format(**slots)

def enforce_token_budget(text: str, budget_tokens: int, strategy: str = "truncate_tail") -> str:
    # Placeholder: in production, use tokenizer (tiktoken or similar)
    words = text.split()
    approx_tokens = len(words) // 0.75  # rough heuristic
    if approx_tokens <= budget_tokens:
        return text
    # Very simple truncation by words
    cutoff = int(len(words) * (budget_tokens / approx_tokens))
    if strategy == "prioritize_summary":
        return " ".join(words[:cutoff])
    return " ".join(words[:cutoff])
