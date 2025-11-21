import os
import json
import logging
from typing import Any, Dict

import azure.functions as func

LOG = logging.getLogger("permitpilot.feedback")


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function handler for collecting user feedback on responses.
    Accepts JSON payload with 'response_id', 'rating', and optional 'comments'.
    Returns JSON with 'status' field.
    """
    LOG.info("Processing feedback submission")
    
    try:
        # Parse request body
        req_body = req.get_json()
        response_id = req_body.get("response_id")
        rating = req_body.get("rating")
        comments = req_body.get("comments", "")
        
        if not response_id or rating is None:
            return func.HttpResponse(
                json.dumps({"error": "Missing required fields: response_id, rating"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate rating
        if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            return func.HttpResponse(
                json.dumps({"error": "Rating must be between 1 and 5"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # TODO: Store feedback in database/storage for analysis
        LOG.info(f"Feedback received for response_id: {response_id}, rating: {rating}")
        
        response_data = {
            "status": "success",
            "message": "Feedback received successfully",
            "response_id": response_id
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
        LOG.error(f"Error processing feedback: {e}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )
