# Copilot Studio Integration Mapping

This document describes how PermitPilot's multi-agent architecture maps to GitHub Copilot Studio concepts and implementation patterns.

## Overview

PermitPilot demonstrates key patterns for building production-ready GitHub Copilot agents:
- **Multi-agent orchestration**: Coordinating specialized agents
- **Performance optimization**: Token budgeting, retry logic, streaming strategies
- **Grounding and RAG**: Retrieval-augmented generation with domain documents
- **Quality gates**: Automated review and approval workflows

## Architecture Mapping

### PermitPilot Components → Copilot Studio Concepts

| PermitPilot Component | Copilot Studio Concept | Implementation |
|----------------------|------------------------|----------------|
| `src/main_agent.py` (Orchestrator) | Primary Copilot Agent | Main entry point, workflow coordination |
| `src/agents/classifier_agent.py` | Skill/Sub-agent | Domain classification skill |
| `src/agents/responder_agent.py` | Skill/Sub-agent | Response generation skill |
| `src/agents/reviewer_agent.py` | Skill/Sub-agent | Quality assurance skill |
| `src/utils/retry_utils.py` | Resilience Pattern | Error handling and recovery |
| `src/utils/prompt_utils.py` | Prompt Engineering | Template management, token control |
| `manifests/permitpilot.agent.json` | Agent Manifest | Configuration and metadata |

## Copilot Studio Agent Structure

### 1. Agent Manifest (`permitpilot.agent.json`)

The manifest defines:
- **Agent metadata**: Name, version, description
- **Triggers**: Webhook events that activate the agent
- **Sub-agents/Skills**: Classifier, responder, reviewer configurations
- **Performance settings**: Token budgets, retry policies, streaming
- **Scopes and permissions**: Repository access, API scopes

```json
{
  "name": "permitpilot",
  "version": "0.1.0",
  "agents": {
    "classifier": { /* classification skill */ },
    "responder_legal": { /* legal response skill */ },
    "reviewer": { /* review skill */ }
  },
  "performance": {
    "token_budget": 1600,
    "retry": { "max_attempts": 2 }
  }
}
```

**Mapping**: This is equivalent to a Copilot Studio agent configuration defining the primary agent and its skills.

### 2. Orchestrator (`src/main_agent.py`)

The orchestrator coordinates the multi-agent workflow:

```python
class Orchestrator:
    def process_event(self, event: Dict) -> Dict:
        # 1. Classify domain
        classification = self._classify_with_retry(text)
        
        # 2. Route to responder
        response = self._respond_with_retry(domain, context)
        
        # 3. Review quality
        review = self._review_with_retry(draft)
        
        # 4. Approve or flag for human review
        return result
```

**Mapping**: 
- **Copilot Studio**: This is the main agent logic that orchestrates skills
- **Skills**: Individual agents (classifier, responder, reviewer) are "skills" invoked by the main agent
- **Context passing**: Each skill receives context and returns structured results

### 3. Skills/Sub-Agents

#### Classifier Skill (`src/agents/classifier_agent.py`)
```python
def classify(text: str) -> Dict:
    return {
        "domain": "environmental",
        "confidence": 0.92
    }
```

**Copilot Studio Pattern**:
- **Input**: Raw text from GitHub event
- **Processing**: Domain classification (can be LLM-based or fine-tuned model)
- **Output**: Structured result with domain and confidence
- **Caching**: Results can be cached by input hash

#### Responder Skill (`src/agents/responder_agent.py`)
```python
def respond(domain: str, context: Dict) -> Dict:
    # Retrieve grounding documents
    docs = _retrieve_grounding_docs(domain, query)
    
    # Generate response with RAG
    draft = _generate_response_content(domain, title, body, docs)
    
    return {"draft": draft, "metadata": {...}}
```

**Copilot Studio Pattern**:
- **RAG Integration**: Queries vector database for relevant documents
- **Template-based prompting**: Uses domain-specific templates
- **Token budgeting**: Enforces limits on input/output
- **Grounding**: Cites sources from retrieval

#### Reviewer Skill (`src/agents/reviewer_agent.py`)
```python
def review(draft: str) -> Dict:
    # Quality checks
    issues = []
    issues.extend(_check_hedging(draft))
    issues.extend(_check_informal_language(draft))
    
    # Score and approve/reject
    score = _calculate_quality_score(draft, len(issues))
    approved = score >= threshold
    
    return {"approved": approved, "score": score, "issues": issues}
```

**Copilot Studio Pattern**:
- **Quality gate**: Automated validation before posting
- **Heuristics + LLM**: Combines rule-based and model-based checks
- **Feedback loop**: Provides actionable suggestions for improvement

## Performance Optimization Patterns

### 1. Token Budget Management

**PermitPilot Implementation**:
```python
from utils.prompt_utils import enforce_token_budget

text = enforce_token_budget(
    text=input_text,
    budget_tokens=1200,
    strategy="truncate_tail"
)
```

**Copilot Studio Mapping**:
- Set `max_tokens` in agent configuration
- Truncate input intelligently (preserve most important content)
- Use streaming for long outputs where appropriate

### 2. Retry Logic with Exponential Backoff

**PermitPilot Implementation**:
```python
from utils.retry_utils import retry_with_backoff

@retry_with_backoff(max_attempts=3, base_delay=2.0)
def call_api():
    return model.generate(prompt)
```

**Copilot Studio Mapping**:
- Configure retry policy in manifest: `"retry": {"max_attempts": 2, "backoff_seconds": 2}`
- Use jitter to avoid thundering herd
- Distinguish transient vs. permanent failures

### 3. Streaming vs. Non-Streaming

**PermitPilot Strategy**:
```json
{
  "streaming": {
    "enabled_for": ["reviewer"],
    "reason": "reviewer can stream incremental checks"
  }
}
```

**Decision Matrix**:
| Use Case | Streaming | Reason |
|----------|-----------|--------|
| Classification | ❌ No | Need complete result for routing |
| Response generation | ❌ No | Need full response for review |
| Review/validation | ✅ Yes | Can provide incremental feedback |
| Long-form content | ✅ Yes | Better UX with progressive output |

### 4. Caching and Deduplication

**Pattern**:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def classify_cached(text: str):
    return classify(text)
```

**Copilot Studio Mapping**:
- Cache classification results by input hash
- Cache grounding documents by query embedding
- Deduplicate identical requests within time window

## Grounding and RAG Pattern

### Vector Database Integration

**PermitPilot Pattern**:
```python
def _retrieve_grounding_docs(domain: str, query: str) -> List[Dict]:
    # 1. Generate query embedding
    embedding = embed_model.encode(query)
    
    # 2. Query vector database
    results = vector_db.search(
        embedding=embedding,
        filter={"domain": domain},
        top_k=3
    )
    
    # 3. Return relevant documents
    return [{"id": r.id, "content": r.text} for r in results]
```

**Copilot Studio Implementation**:
1. **Embedding generation**: Use OpenAI `text-embedding-3-small` or similar
2. **Vector store**: Pinecone, Weaviate, or GitHub-hosted vector DB
3. **Indexing**: Pre-index regulatory documents by domain
4. **Retrieval**: Top-k similarity search with domain filtering

**Configuration** (`manifests/permitpilot.agent.json`):
```json
{
  "grounding": {
    "embeddings_index": "s3://permitpilot/embeddings/legal",
    "documents_ref": "REF:LEGAL_DOCS_SECRET",
    "top_k": 3,
    "similarity_threshold": 0.75
  }
}
```

## Workflow Patterns

### Pattern 1: Simple Classification and Response

```
User Query → Classifier → Responder → Post Response
```

**Implementation**:
```python
classification = classify(text)
if classification['confidence'] > 0.7:
    response = respond(classification['domain'], context)
    post_comment(response['draft'])
```

### Pattern 2: Classification → Response → Review (Full Pipeline)

```
User Query → Classifier → Responder → Reviewer → [Approve/Human Review]
```

**Implementation**:
```python
orchestrator = Orchestrator()
result = orchestrator.process_event(event)

if result['status'] == 'approved':
    post_comment(result['response'])
elif result['status'] == 'needs_human_review':
    queue_for_human(result)
```

### Pattern 3: Parallel Multi-Domain Response

```
User Query → Classifier → [Legal Responder, Environmental Responder] → Combine → Review
```

**Implementation**:
```python
from concurrent.futures import ThreadPoolExecutor

def process_multi_domain(text: str):
    classification = classify(text)
    
    if classification['domain'] == 'multi':
        domains = classification['domains']  # e.g., ['legal', 'environmental']
        
        with ThreadPoolExecutor() as executor:
            responses = list(executor.map(
                lambda d: respond(d, context),
                domains
            ))
        
        combined = combine_responses(responses)
        review_result = review(combined)
        return review_result
```

## Integration with GitHub

### Webhook Configuration

**Trigger Events**:
```json
{
  "trigger": {
    "type": "webhook",
    "events": [
      "issue_comment.created",
      "issues.opened",
      "pull_request.opened"
    ]
  }
}
```

**Event Processing**:
```python
def handle_webhook(event: Dict):
    event_type = event['action']
    
    if event_type == 'issue_comment.created':
        text = event['comment']['body']
        title = event['issue']['title']
    elif event_type == 'issues.opened':
        text = event['issue']['body']
        title = event['issue']['title']
    
    return orchestrator.process_event({
        'text': text,
        'title': title,
        'context': event
    })
```

### Response Posting

**API Integration**:
```python
def post_response(issue_number: int, response: str):
    # Use GitHub API to post comment
    github_api.issues.create_comment(
        owner='my-org',
        repo='my-repo',
        issue_number=issue_number,
        body=response
    )
```

## Monitoring and Observability

### Key Metrics

**PermitPilot tracks**:
```python
metrics = {
    "classification_confidence": 0.92,
    "tokens_used": 850,
    "processing_time_ms": 1240,
    "review_score": 85,
    "approved": True,
    "grounding_docs_count": 3
}
```

**Copilot Studio Dashboard**:
- Request volume and success rate
- Average confidence scores by domain
- Token usage and cost tracking
- Human review rate
- Response time percentiles (p50, p95, p99)

### Logging Pattern

```python
import logging

logger = logging.getLogger('permitpilot')

def process_with_logging(event: Dict):
    trace_id = generate_trace_id()
    logger.info(f"[{trace_id}] Processing event", extra={
        "trace_id": trace_id,
        "event_type": event['type']
    })
    
    start = time.time()
    result = orchestrator.process_event(event)
    duration = time.time() - start
    
    logger.info(f"[{trace_id}] Completed", extra={
        "trace_id": trace_id,
        "status": result['status'],
        "duration_ms": duration * 1000
    })
    
    return result
```

## Deployment Considerations

### Environment Variables

```bash
# Model configuration
OPENAI_API_KEY=sk-...
MODEL_CLASSIFIER=gpt-4o-mini
MODEL_RESPONDER=gpt-4o
MODEL_REVIEWER=gpt-4o-mini

# Vector database
VECTOR_DB_URL=https://pinecone.io/...
VECTOR_DB_API_KEY=...

# GitHub integration
GITHUB_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=...

# Performance tuning
TOKEN_BUDGET=1600
CONFIDENCE_THRESHOLD=0.7
RETRY_MAX_ATTEMPTS=2
```

### Scaling Pattern

**Horizontal Scaling**:
```yaml
# Kubernetes deployment
replicas: 3
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi

# Load balancing
service:
  type: LoadBalancer
  sessionAffinity: None
```

**Autoscaling**:
```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilization: 70
  targetMemoryUtilization: 80
```

## Testing Strategy

### Unit Tests

```python
def test_classifier():
    result = classify("EPA emission standards")
    assert result['domain'] == 'environmental'
    assert result['confidence'] > 0.8

def test_responder():
    result = respond('environmental', {
        'title': 'Test',
        'body': 'Query about EPA'
    })
    assert 'draft' in result
    assert result['metadata']['tokens_estimate'] > 0
```

### Integration Tests

```python
def test_full_pipeline():
    orchestrator = Orchestrator()
    result = orchestrator.process_event({
        'text': 'What are EPA guidelines for industrial emissions?',
        'title': 'EPA Question'
    })
    
    assert result['status'] in ['approved', 'needs_human_review']
    assert 'metadata' in result
```

## Migration Path

### From Basic Copilot to PermitPilot Pattern

1. **Start**: Single-agent copilot with basic prompting
2. **Add**: Domain classification skill
3. **Enhance**: Add grounding and RAG for responses
4. **Quality**: Add reviewer skill for validation
5. **Optimize**: Add retry logic, caching, token budgeting
6. **Scale**: Add monitoring, metrics, autoscaling

### Code Example

**Before (Basic)**:
```python
def handle_comment(comment: str):
    response = llm.generate(f"Respond to: {comment}")
    return response
```

**After (PermitPilot Pattern)**:
```python
def handle_comment(comment: str):
    orchestrator = Orchestrator()
    result = orchestrator.process_event({
        'text': comment,
        'title': 'User Query'
    })
    
    if result['status'] == 'approved':
        return result['response']
    else:
        return None  # Route to human
```

## Best Practices Summary

1. **Modular Design**: Separate classification, generation, and review
2. **Performance First**: Token budgeting, retry logic, caching
3. **Quality Gates**: Always review before posting
4. **Grounding**: Use RAG for factual accuracy
5. **Observability**: Log everything with trace IDs
6. **Graceful Degradation**: Route to humans when uncertain
7. **Testing**: Comprehensive unit and integration tests

## References

- [GitHub Copilot Documentation](https://docs.github.com/copilot)
- [OpenAI API Best Practices](https://platform.openai.com/docs/guides/production-best-practices)
- [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401)
- [Prompt Engineering Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)
