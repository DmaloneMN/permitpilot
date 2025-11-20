# PermitPilot — A Performance-Tuned Copilot for Regulatory Response

PermitPilot is a multi-agent Copilot that routes, composes, reviews, and maintains regulatory responses (e.g., permitting, environmental, procedural queries) with performance best practices baked in.

Core capabilities
- Multi-Agent design:
  - Classifier Agent: routes comments to the correct responder (legal, environmental, procedural).
  - Responder Agent(s): domain-specialized responders grounded with domain docs/embeddings.
  - Reviewer Agent: checks tone, clarity, and compliance before posting.
- Performance best practices: prompt templates with slot filling, token budgeting, streaming vs non-streaming tradeoffs, retry logic, and truncation strategies.
- Feedback loop: human review UI, failure type auto-labeling, weekly retraining or prompt updates.

Quick start (local)
1. Create a Python venv: python -m venv .venv && source .venv/bin/activate
2. Install deps: pip install -r requirements.txt
3. Populate secrets/config (see docs/config.md)
4. Run tests: pytest

Repository layout
- docs/ — design docs and performance guidance
- src/ — agent implementations and utilities
- manifests/ — agent configuration & sample manifests
- examples/ — prompt templates and sample inputs/outputs
- tests/ — unit/integration test skeletons
- dashboard/ — notes and starter for metrics/visualization

Next steps I can take:
- Create the GitHub repo and open the initial commit/PR for you.
- Wire CI to run tests and lint.
- Expand responder agent templates with EPA/regulatory corpora and an embeddings pipeline.