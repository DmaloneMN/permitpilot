"""
Main Orchestrator for PermitPilot
Coordinates the classifier, responder, and reviewer agents to process regulatory comments.

Flow:
1. Receive incoming event (issue/comment)
2. Classify the domain using classifier_agent
3. Route to appropriate responder_agent based on domain
4. Review the response using reviewer_agent
5. Return final response or flag for human review
"""
import sys
from typing import Dict, Optional
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from agents.classifier_agent import classify
from agents.responder_agent import respond
from agents.reviewer_agent import review
from utils.retry_utils import retry_with_backoff, RetryConfig
from utils.prompt_utils import enforce_token_budget


class OrchestratorConfig:
    """Configuration for the orchestrator."""
    def __init__(
        self,
        confidence_threshold: float = 0.7,
        max_token_budget: int = 1600,
        retry_max_attempts: int = 2,
        retry_base_delay: float = 2.0
    ):
        self.confidence_threshold = confidence_threshold
        self.max_token_budget = max_token_budget
        self.retry_max_attempts = retry_max_attempts
        self.retry_base_delay = retry_base_delay


class Orchestrator:
    """
    Main orchestrator that coordinates the multi-agent workflow.
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """Initialize orchestrator with configuration."""
        self.config = config or OrchestratorConfig()
        self.retry_config = RetryConfig(
            max_attempts=self.config.retry_max_attempts,
            base_delay=self.config.retry_base_delay
        )
    
    def process_event(self, event: Dict) -> Dict:
        """
        Process an incoming event through the agent pipeline.
        
        Args:
            event: Event dictionary with 'text', 'title', and optional 'context'
        
        Returns:
            Dictionary with 'status', 'response', and 'metadata'
        """
        try:
            # Extract text from event
            text = event.get('text', '')
            title = event.get('title', '')
            context = event.get('context', {})
            
            if not text:
                return {
                    'status': 'error',
                    'error': 'Missing required field: text',
                    'metadata': {}
                }
            
            # Enforce token budget on input
            text = enforce_token_budget(
                text,
                self.config.max_token_budget,
                strategy="truncate_tail"
            )
            
            # Step 1: Classify the domain
            print(f"[Orchestrator] Classifying text (length: {len(text)} chars)...")
            classification = self._classify_with_retry(text)
            domain = classification.get('domain', 'unknown')
            confidence = classification.get('confidence', 0.0)
            
            print(f"[Orchestrator] Classified as '{domain}' with confidence {confidence:.2f}")
            
            # Check if confidence is below threshold
            if confidence < self.config.confidence_threshold:
                return {
                    'status': 'needs_human_review',
                    'reason': f'Low confidence ({confidence:.2f}) - below threshold',
                    'classification': classification,
                    'metadata': {
                        'domain': domain,
                        'confidence': confidence
                    }
                }
            
            # Step 2: Generate response using responder agent
            print(f"[Orchestrator] Generating response for domain '{domain}'...")
            responder_context = {
                'title': title,
                'body': text,
                'domain': domain,
                **context
            }
            response_data = self._respond_with_retry(domain, responder_context)
            draft = response_data.get('draft', '')
            
            print(f"[Orchestrator] Generated draft (length: {len(draft)} chars)")
            
            # Step 3: Review the response
            print(f"[Orchestrator] Reviewing draft response...")
            review_result = self._review_with_retry(draft)
            approved = review_result.get('approved', False)
            
            print(f"[Orchestrator] Review result: {'APPROVED' if approved else 'REJECTED'}")
            
            # Step 4: Return final result
            if approved:
                return {
                    'status': 'approved',
                    'response': draft,
                    'metadata': {
                        'domain': domain,
                        'confidence': confidence,
                        'review': review_result,
                        'response_metadata': response_data.get('metadata', {})
                    }
                }
            else:
                return {
                    'status': 'needs_human_review',
                    'reason': 'Response failed review checks',
                    'draft': draft,
                    'review': review_result,
                    'metadata': {
                        'domain': domain,
                        'confidence': confidence,
                        'response_metadata': response_data.get('metadata', {})
                    }
                }
        
        except Exception as e:
            print(f"[Orchestrator] Error processing event: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {}
            }
    
    @retry_with_backoff(max_attempts=2, base_delay=2.0)
    def _classify_with_retry(self, text: str) -> Dict:
        """Classify text with retry logic."""
        return classify(text)
    
    @retry_with_backoff(max_attempts=2, base_delay=2.0)
    def _respond_with_retry(self, domain: str, context: Dict) -> Dict:
        """Generate response with retry logic."""
        return respond(domain, context)
    
    @retry_with_backoff(max_attempts=2, base_delay=2.0)
    def _review_with_retry(self, draft: str) -> Dict:
        """Review draft with retry logic."""
        return review(draft)


def main():
    """
    Example usage of the orchestrator.
    """
    # Initialize orchestrator
    config = OrchestratorConfig(
        confidence_threshold=0.7,
        max_token_budget=1600,
        retry_max_attempts=2
    )
    orchestrator = Orchestrator(config)
    
    # Example events
    test_events = [
        {
            'title': 'Air Quality Permit Question',
            'text': 'Is the new permit application conforming to EPA guidance on air emissions?',
            'context': {}
        },
        {
            'title': 'Legal Question',
            'text': 'What is the statute of limitations for liability claims under environmental law?',
            'context': {}
        },
        {
            'title': 'Unclear Query',
            'text': 'Just checking on things.',
            'context': {}
        }
    ]
    
    print("=" * 80)
    print("PermitPilot Orchestrator - Test Run")
    print("=" * 80)
    
    for i, event in enumerate(test_events, 1):
        print(f"\n--- Event {i}: {event['title']} ---")
        result = orchestrator.process_event(event)
        
        print(f"\nResult Status: {result['status']}")
        if result['status'] == 'approved':
            print(f"Response: {result['response']}")
        elif result['status'] == 'needs_human_review':
            print(f"Reason: {result['reason']}")
            if 'draft' in result:
                print(f"Draft: {result['draft']}")
        elif result['status'] == 'error':
            print(f"Error: {result['error']}")
        
        print(f"Metadata: {result['metadata']}")
        print("-" * 80)


if __name__ == "__main__":
    main()
