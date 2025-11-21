# PermitPilot Azure Function + Copilot Plugin Guide

This folder contains the JSON artifacts and templates you need to expose PermitPilot via an Azure Function and register it as a Custom Plugin for Copilot Studio.

## Files included

- **`openapi.json`** - OpenAPI 3.0.1 specification describing the PermitPilot plugin API endpoints
- **`ai-plugin.json`** - Copilot Studio plugin manifest for registering the plugin
- **`local.settings.json.example`** - Example local settings file for Azure Functions local development
- **`host.json`** - Azure Functions host configuration
- **`functions/*/function.json`** - Individual function binding configurations

## Quick Start

### 1. Deploy the Azure Function

Follow the instructions in `README_DEPLOY.md` to deploy the PermitPilot Azure Functions to your Azure subscription.

### 2. Configure the Plugin Files

After deployment, update the placeholder URLs in the plugin files:

#### Update `openapi.json`
Replace `your-function-app` with your actual Azure Function App name:
```json
"servers": [
  {
    "url": "https://your-actual-app-name.azurewebsites.net/api"
  }
]
```

#### Update `ai-plugin.json`
1. Replace `your-function-app` with your actual Function App name
2. Add your OpenAI verification token (if using OpenAI plugin format)
3. Update contact and legal URLs

```json
{
  "api": {
    "url": "https://your-actual-app-name.azurewebsites.net/api/openapi.json"
  },
  "logo_url": "https://your-actual-app-name.azurewebsites.net/logo.png",
  "contact_email": "your-email@example.com",
  "legal_info_url": "https://your-company.com/legal"
}
```

### 3. Set Up Authentication

The PermitPilot API uses API key authentication via the `x-api-key` header.

#### Generate an API Key
```bash
# Generate a secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Configure in Azure Function App Settings
```bash
az functionapp config appsettings set \
  --name your-function-app-name \
  --resource-group your-resource-group \
  --settings "PERMITPILOT_API_KEY=your-generated-key"
```

### 4. Register as Copilot Studio Plugin

#### Option A: Using Copilot Studio UI

1. Navigate to [Copilot Studio](https://copilotstudio.microsoft.com/)
2. Go to your Copilot or Agent
3. Click on **"Actions"** → **"Add an action"**
4. Select **"From OpenAPI"**
5. Paste the contents of `openapi.json` or provide the hosted URL
6. Configure authentication:
   - Choose **"API Key"**
   - Set header name to `x-api-key`
   - Add your API key value
7. Test the connection using the health endpoint
8. Save and publish

#### Option B: Using Microsoft 365 Copilot Plugin

1. Host both `ai-plugin.json` and `openapi.json` at your Azure Function's root
2. Submit for plugin verification through Microsoft Partner Center
3. Follow Microsoft's plugin certification process

### 5. Test the Plugin

Once registered, test each endpoint:

#### Test Process Endpoint
In Copilot Studio's test pane:
```
Process this permit question: What are the EPA requirements for stormwater permits in California?
```

#### Test Feedback Endpoint
```
Submit feedback for response ID resp-123 with rating 5 and comment "Very helpful"
```

#### Test Health Endpoint
```
Check if PermitPilot plugin is healthy
```

## API Endpoints

### `/permitpilot-process` (POST)
Processes permit and regulatory queries through the multi-agent system.

**Request:**
```json
{
  "query": "What are the EPA requirements for stormwater permits?",
  "context": {
    "jurisdiction": "federal",
    "project_type": "construction"
  }
}
```

**Response:**
```json
{
  "response_id": "resp-abc123",
  "classification": "environmental",
  "response": "EPA stormwater permit requirements...",
  "confidence": 0.95
}
```

### `/permitpilot-feedback` (POST)
Collects user feedback on generated responses for continuous improvement.

**Request:**
```json
{
  "response_id": "resp-abc123",
  "rating": 5,
  "comments": "Very accurate and helpful response"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback recorded"
}
```

### `/permitpilot-health` (GET)
Health check endpoint for monitoring service availability.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Security Considerations

### API Key Management
- **Never commit API keys to source control**
- Store keys in Azure Key Vault
- Rotate keys regularly
- Use different keys for dev/staging/production

### Enable Azure AD Authentication (Optional)
For enhanced security with Copilot Studio:

```bash
az functionapp auth update \
  --name your-function-app \
  --resource-group your-resource-group \
  --enabled true \
  --action LoginWithAzureActiveDirectory
```

### Configure CORS
If calling from web applications:

```bash
az functionapp cors add \
  --name your-function-app \
  --resource-group your-resource-group \
  --allowed-origins https://copilotstudio.microsoft.com
```

## Monitoring and Troubleshooting

### View Logs
```bash
# Stream live logs
az webapp log tail \
  --name your-function-app \
  --resource-group your-resource-group
```

### Common Issues

**Issue: 401 Unauthorized**
- Verify API key is correctly set in Function App settings
- Check that `x-api-key` header is being sent with requests
- Ensure Copilot Studio action has correct authentication configuration

**Issue: 404 Not Found**
- Verify function app URL in `openapi.json` matches deployed app
- Check that functions are properly deployed (use `func azure functionapp list-functions`)

**Issue: Plugin not appearing in Copilot Studio**
- Validate `openapi.json` using [Swagger Editor](https://editor.swagger.io/)
- Ensure all required fields in `ai-plugin.json` are populated
- Check that the API is accessible from Copilot Studio (not behind firewall)

### Test with cURL

```bash
# Set your function app URL and API key
FUNCTION_URL="https://your-app.azurewebsites.net/api"
API_KEY="your-api-key"

# Test health endpoint
curl "${FUNCTION_URL}/permitpilot-health"

# Test process endpoint
curl -X POST "${FUNCTION_URL}/permitpilot-process" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "query": "What are the requirements for a building permit?",
    "context": {"jurisdiction": "local"}
  }'

# Test feedback endpoint
curl -X POST "${FUNCTION_URL}/permitpilot-feedback" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "response_id": "resp-123",
    "rating": 5,
    "comments": "Excellent response"
  }'
```

## Advanced Configuration

### Rate Limiting
Implement rate limiting to prevent abuse:

```python
# In your function code
from functools import wraps
import time

def rate_limit(max_calls=10, time_window=60):
    calls = {}
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Rate limiting logic here
            pass
        return wrapper
    return decorator
```

### Caching
Add caching for frequently asked questions:

```bash
# Create Azure Redis Cache
az redis create \
  --name permitpilot-cache \
  --resource-group your-resource-group \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

### Custom Domain
Use a custom domain for professional appearance:

```bash
az functionapp config hostname add \
  --webapp-name your-function-app \
  --resource-group your-resource-group \
  --hostname api.your-domain.com
```

## Next Steps

1. **Enhance the Agent System** - Integrate with the full PermitPilot multi-agent orchestration
2. **Add Embeddings** - Connect to vector store for RAG-based responses
3. **Implement Feedback Loop** - Use collected feedback to retrain/improve prompts
4. **Create Custom Actions** - Build domain-specific actions in Copilot Studio
5. **Monitor Performance** - Set up Application Insights dashboards
6. **Scale for Production** - Move to Azure Functions Premium plan if needed

## Resources

- [Copilot Studio Plugin Documentation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/copilot-plugins-overview)
- [OpenAPI Specification](https://spec.openapis.org/oas/v3.0.1)
- [Azure Functions Python Guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Microsoft 365 Copilot Extensibility](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/)

## Support

For issues or questions:
- Check the main [PermitPilot README](../README.md)
- Review [Azure Functions deployment guide](README_DEPLOY.md)
- Open an issue on the [GitHub repository](https://github.com/DmaloneMN/permitpilot)
