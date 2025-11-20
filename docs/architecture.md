# PermitPilot Architecture

High-level flow
1. Inbound event (issue or comment) arrives via webhook.
2. Gateway service performs auth, basic rate-limiting, and forwards to the Classifier Agent.
3. Classifier Agent returns domain tag(s) and confidence score.
4. Dispatcher chooses a Responder Agent for the highest-confidence domain.
   - If confidence < threshold, route to human-review queue.
5. Responder Agent composes a candidate response using grounding docs (embeddings or retrieval).
6. Reviewer Agent checks the response for tone, hallucinations, compliance flags, and suggests edits.
7. If Reviewer approves, response is posted; otherwise, a human reviewer is notified.

Design notes
- Agents are stateless workers that receive event + context.
- Grounding data (EPA guidelines, statutes) are stored in an embeddings store (vector DB) and referenced by responder.
- Observability: every request is logged with trace_id and timing; metrics captured (latency, success, approvals).
- Feedback loop: store human votes and failure labels for retraining.

Components
- Gateway / Webhook consumer
- Worker pool for agents (classifier/responder/reviewer)
- Vector DB (e.g., Pinecone, Weaviate, or self-hosted)
- Metrics & dashboard (Prometheus + Grafana or similar)
- Human review UI (simple web app listing flagged items)
