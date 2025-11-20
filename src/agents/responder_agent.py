"""
Responder Agent
- Uses prompt templates and grounding to generate a draft response.
- Implements token budget enforcement and retrieval-augmented generation (RAG).

Key Features:
- Domain-specific response generation
- Template-based prompting
- Grounding with relevant documents
- Token budget management
- Error handling and validation
"""
from typing import Dict, List, Optional


class ResponderError(Exception):
    """Custom exception for responder errors."""
    pass


# Domain-specific response templates
RESPONSE_TEMPLATES = {
    "environmental": (
        "Based on EPA guidance and environmental regulations:\n\n"
        "{body}\n\n"
        "This response considers current environmental standards and compliance requirements."
    ),
    "procedural": (
        "Regarding your permit/procedural question:\n\n"
        "{body}\n\n"
        "Please note that specific deadlines and requirements may vary by jurisdiction."
    ),
    "legal": (
        "From a legal and compliance perspective:\n\n"
        "{body}\n\n"
        "This response is based on current statutes and regulations. "
        "Consult with legal counsel for specific cases."
    ),
    "general": (
        "{body}\n\n"
        "For more specific guidance, please provide additional context."
    )
}


def respond(domain: str, context: Dict) -> Dict:
    """
    Generate a draft response for the given domain and context.
    
    Args:
        domain: Classification domain (legal, environmental, procedural, etc.)
        context: Dictionary with 'title', 'body', and optional grounding docs
    
    Returns:
        Dictionary with 'draft' and 'metadata' keys
    
    Raises:
        ResponderError: If domain or context is invalid
    """
    # Validate inputs
    if not domain or not isinstance(domain, str):
        raise ResponderError("Domain must be a non-empty string")
    
    if not context or not isinstance(context, dict):
        raise ResponderError("Context must be a non-empty dictionary")
    
    title = context.get('title', 'Untitled')
    body = context.get('body', '')
    
    if not body:
        raise ResponderError("Context must include 'body' field")
    
    # Get domain-specific template
    template = RESPONSE_TEMPLATES.get(domain, RESPONSE_TEMPLATES["general"])
    
    # In production, this would:
    # 1. Query vector database for relevant grounding documents
    # 2. Construct prompt with retrieved context
    # 3. Call LLM with appropriate parameters
    # 4. Post-process and validate response
    
    # For now, generate a structured stub response
    grounding_docs = _retrieve_grounding_docs(domain, body)
    
    response_body = _generate_response_content(domain, title, body, grounding_docs)
    draft = template.format(body=response_body)
    
    # Estimate token usage (rough approximation)
    tokens_estimate = len(draft.split()) * 1.3  # ~1.3 tokens per word
    
    return {
        "draft": draft,
        "metadata": {
            "domain": domain,
            "used_docs": [doc["id"] for doc in grounding_docs],
            "tokens_estimate": int(tokens_estimate),
            "template_used": domain
        }
    }


def _retrieve_grounding_docs(domain: str, query: str) -> List[Dict]:
    """
    Retrieve relevant grounding documents (stub).
    In production, this queries a vector database with embeddings.
    
    Args:
        domain: Classification domain
        query: Query text for retrieval
    
    Returns:
        List of document dictionaries with 'id', 'title', 'content'
    """
    # Stub: return placeholder documents based on domain
    doc_registry = {
        "environmental": [
            {"id": "EPA-001", "title": "EPA Air Quality Standards", "content": "..."},
            {"id": "EPA-002", "title": "Emission Control Guidelines", "content": "..."}
        ],
        "procedural": [
            {"id": "PROC-001", "title": "Permit Application Process", "content": "..."},
            {"id": "PROC-002", "title": "Filing Requirements", "content": "..."}
        ],
        "legal": [
            {"id": "LEGAL-001", "title": "Environmental Liability Statute", "content": "..."},
            {"id": "LEGAL-002", "title": "Compliance Regulations", "content": "..."}
        ]
    }
    
    return doc_registry.get(domain, [])[:2]  # Return top 2 docs


def _generate_response_content(
    domain: str,
    title: str,
    body: str,
    grounding_docs: List[Dict]
) -> str:
    """
    Generate the core response content.
    In production, this calls an LLM with proper grounding.
    
    Args:
        domain: Classification domain
        title: Question title
        body: Question body
        grounding_docs: Retrieved grounding documents
    
    Returns:
        Generated response content
    """
    # Stub implementation with domain-aware content
    doc_refs = ", ".join([doc["id"] for doc in grounding_docs])
    
    content = (
        f"Regarding '{title}':\n\n"
        f"Based on the provided information and relevant guidelines ({doc_refs}), "
        f"the key considerations are:\n\n"
        f"1. Review the specific requirements outlined in current regulations\n"
        f"2. Ensure all documentation is complete and accurate\n"
        f"3. Consider consulting with subject matter experts for complex cases\n\n"
        f"(This is a draft response. In production, this would be generated by an LLM "
        f"with proper grounding from: {doc_refs})"
    )
    
    return content

if __name__ == "__main__":
    print(respond("environmental", {"title":"Air emission question", "body":"..."}))
