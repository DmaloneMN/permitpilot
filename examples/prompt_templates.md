# Prompt Templates and Fallback Logic

This document provides concrete prompt templates and strategies for the PermitPilot multi-agent system.

## Overview

Effective prompts are crucial for:
- **Accuracy**: Ensuring domain-specific responses
- **Consistency**: Maintaining professional tone across agents
- **Performance**: Optimizing token usage and response time
- **Safety**: Reducing hallucination and ensuring compliance

## Classifier Agent Prompt Template

The classifier determines which domain (legal, environmental, procedural) a query belongs to.

### Template Structure
```
You are a regulatory domain classifier. Analyze the following text and determine which domain it belongs to.

INPUT TEXT:
{text}

CONTEXT (if available):
Title: {title}
Source: {source}

DOMAINS:
- environmental: EPA regulations, emissions, pollution, environmental compliance
- legal: Statutes, liability, legal compliance, regulatory law
- procedural: Permit applications, filing processes, deadlines, submissions
- triage-human: Unclear or requires human expertise

OUTPUT FORMAT:
Return a JSON object with:
{
  "domain": "<domain_name>",
  "confidence": <float between 0 and 1>,
  "reasoning": "<brief explanation>"
}

Consider keywords, context, and regulatory terminology in your classification.
```

### Example Usage
```python
from utils.prompt_utils import slot_fill

template = """You are a regulatory domain classifier..."""
prompt = slot_fill(template, {
    "text": "Does our facility need EPA approval for air emissions?",
    "title": "EPA Approval Question",
    "source": "public_comment"
})
```

## Responder Agent Prompt Templates

Domain-specific templates for generating responses.

### Environmental Domain Template
```
You are an environmental regulatory expert. Provide a response to the following query based on EPA guidelines and environmental regulations.

QUERY:
Title: {title}
Body: {body}

GROUNDING DOCUMENTS:
{grounding_docs}

GUIDELINES:
1. Reference specific EPA regulations or guidelines when applicable
2. Use precise, technical language appropriate for regulatory context
3. Cite document sources (e.g., "According to EPA CFR 40...")
4. If uncertain, explicitly state limitations
5. Keep response under {token_budget} tokens

OUTPUT FORMAT:
Provide a clear, well-structured response that:
- Directly addresses the query
- Cites relevant regulations
- Provides actionable guidance
- Maintains professional tone

RESPONSE:
```

### Legal Domain Template
```
You are a legal compliance expert. Provide a response to the following regulatory legal query.

QUERY:
Title: {title}
Body: {body}

GROUNDING DOCUMENTS:
{grounding_docs}

GUIDELINES:
1. Reference specific statutes, CFR sections, or case law
2. Distinguish between legal requirements and recommendations
3. Note jurisdiction-specific considerations
4. Include appropriate legal disclaimers
5. Keep response under {token_budget} tokens

LEGAL DISCLAIMER:
"This response provides general guidance based on federal regulations. 
Consult with qualified legal counsel for specific cases."

OUTPUT FORMAT:
Provide a response that:
- Cites relevant legal authorities
- Clarifies legal obligations vs. best practices
- Notes any jurisdictional variations
- Includes appropriate disclaimers

RESPONSE:
```

### Procedural Domain Template
```
You are a regulatory process expert. Provide guidance on the following procedural question.

QUERY:
Title: {title}
Body: {body}

GROUNDING DOCUMENTS:
{grounding_docs}

GUIDELINES:
1. Provide step-by-step guidance when applicable
2. Note relevant deadlines and timelines
3. Reference official forms or submission requirements
4. Clarify jurisdiction-specific procedures
5. Keep response under {token_budget} tokens

OUTPUT FORMAT:
Provide a response that:
- Outlines clear procedural steps
- Identifies key deadlines
- References required forms or documentation
- Notes jurisdiction-specific variations

RESPONSE:
```

## Reviewer Agent Prompt Template

For validating generated responses before posting.

### Template Structure
```
You are a compliance reviewer. Evaluate the following draft response for quality, accuracy, and appropriateness.

ORIGINAL QUERY:
{original_query}

DRAFT RESPONSE:
{draft}

EVALUATION CRITERIA:
1. **Accuracy**: Does it correctly address the query?
2. **Tone**: Professional, authoritative, appropriate?
3. **Citations**: Are sources properly referenced?
4. **Completeness**: Does it fully answer the question?
5. **Safety**: Free from hallucinations or unsupported claims?
6. **Compliance**: Appropriate disclaimers and legal language?

PROBLEMATIC PATTERNS:
- Hedging language: "I think", "maybe", "possibly"
- Informal language: "gonna", "kinda"
- Uncertain phrases: "not sure", "unclear"
- Unsourced claims: "according to my knowledge"

OUTPUT FORMAT:
Return a JSON object:
{
  "approved": <boolean>,
  "score": <int 0-100>,
  "issues": [<list of specific issues>],
  "suggestions": [<list of improvements>]
}

If approved=false, the response will be flagged for human review.
```

## Fallback Strategies

### Low Confidence Handling
```python
if classification.confidence < 0.7:
    return {
        "action": "route_to_human",
        "reason": f"Low confidence ({classification.confidence})",
        "suggested_domain": classification.domain
    }
```

### Error Recovery
```python
try:
    response = generate_response(prompt)
except APIError as e:
    if attempt < max_retries:
        # Exponential backoff with jitter
        time.sleep(base_delay * (2 ** attempt) + random.uniform(0, 1))
        retry()
    else:
        # Fallback to simpler prompt or human routing
        return fallback_response()
```

### Token Budget Enforcement
```python
from utils.prompt_utils import enforce_token_budget

# Truncate input intelligently
truncated = enforce_token_budget(
    text=input_text,
    budget_tokens=1200,
    strategy="prioritize_summary"  # or "truncate_tail"
)
```

## Performance Best Practices

### 1. Slot Filling (Safe Template Substitution)
```python
from utils.prompt_utils import slot_fill

# Safe - escapes user input
prompt = slot_fill(template, {
    "user_input": untrusted_text,
    "domain": domain
})

# Unsafe - direct string formatting
prompt = template.format(user_input=untrusted_text)  # ❌ Don't do this
```

### 2. Token Budgeting
```python
# Set per-agent token budgets
BUDGETS = {
    "classifier": 256,    # Fast classification
    "responder": 1200,    # Detailed responses
    "reviewer": 400       # Quick validation
}

# Enforce before API call
input_text = enforce_token_budget(text, BUDGETS["responder"])
```

### 3. Streaming vs. Non-Streaming
```python
# Streaming: Use for long responses where partial results are useful
# - Reviewer agent (can start checking while generating)
# - Interactive UIs

# Non-streaming: Use for atomic operations
# - Classifier (need complete result)
# - Responder (ensure complete, valid JSON/structured output)
```

### 4. Caching and Deduplication
```python
# Cache classifier results for identical queries
from functools import lru_cache

@lru_cache(maxsize=1000)
def classify_cached(text: str) -> Dict:
    return classify(text)
```

## Testing and Validation

### Example Test Cases
```python
test_cases = [
    {
        "input": "What are EPA emission limits for industrial facilities?",
        "expected_domain": "environmental",
        "min_confidence": 0.8
    },
    {
        "input": "What is the statute of limitations for environmental liability?",
        "expected_domain": "legal",
        "min_confidence": 0.8
    },
    {
        "input": "How do I submit a permit application?",
        "expected_domain": "procedural",
        "min_confidence": 0.8
    }
]
```

## References

- EPA Regulations: https://www.epa.gov/regulations
- CFR Title 40: https://www.ecfr.gov/current/title-40
- Federal Register: https://www.federalregister.gov
