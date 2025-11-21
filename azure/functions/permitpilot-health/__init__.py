import time
import json
import logging
import azure.functions as func

LOG = logging.getLogger("permitpilot.health")


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function handler for health checks.
    Returns JSON with status, timestamp, and version information.
    """
    LOG.info("Health check requested")
    
    try:
        # Get current timestamp
        current_time = time.time()
        
        # Basic health check response
        health_data = {
            "status": "healthy",
            "timestamp": current_time,
            "service": "permitpilot-azure-functions",
            "version": "1.0.0"
        }
        
        LOG.info("Health check passed")
        
        return func.HttpResponse(
            json.dumps(health_data),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        LOG.error(f"Health check failed: {e}", exc_info=True)
        error_data = {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e)
        }
        return func.HttpResponse(
            json.dumps(error_data),
            status_code=503,
            mimetype="application/json"
        )
