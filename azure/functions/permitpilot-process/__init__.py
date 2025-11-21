import os
import json
import logging
from typing import Any, Dict

import azure.functions as func

LOG = logging.getLogger("permitpilot.process")


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function handler for processing permit/regulatory queries.
    Accepts JSON payload with 'query' and optional 'context' fields.
    Returns JSON with 'response' and 'status' fields.
    """
    LOG.info("Processing request for permitpilot-process")
    
    try:
        # Parse request body
        req_body = req.get_json()
        query = req_body.get("query")
        context = req_body.get("context", {})
        
        if not query:
            return func.HttpResponse(
                json.dumps({"error": "Missing required field: query"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # TODO: Integrate with PermitPilot agent system
        # For now, return a placeholder response
        LOG.info(f"Processing query: {query[:50]}...")
        
        response_data = {
            "status": "success",
            "response": "Query received and queued for processing",
            "query": query,
            "context": context
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as e:
        LOG.error(f"Invalid JSON in request: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON payload"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        LOG.error(f"Error processing request: {e}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )
