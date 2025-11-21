# Deploying PermitPilot Azure Functions (step-by-step)

This guide walks through implementing the Azure Function handlers, running locally for testing, and deploying to Azure via CLI or GitHub Actions.

## Overview

PermitPilot provides three Azure Functions for serverless deployment:

1. **permitpilot-process** - Handles permit/regulatory query processing
2. **permitpilot-feedback** - Collects user feedback on responses
3. **permitpilot-health** - Health check endpoint for monitoring

All functions are compatible with Azure Functions v4 and Python 3.10+.

### Available Documentation

- **This file (README_DEPLOY.md)** - Azure Functions deployment guide
- **[README_CopilotPlugin.md](README_CopilotPlugin.md)** - Copilot Studio plugin integration guide

### Configuration Files

The `azure/` directory includes these configuration files:

- `host.json` - Azure Functions host configuration
- `openapi.json` - OpenAPI 3.0.1 specification for the plugin API
- `ai-plugin.json` - Copilot Studio plugin manifest
- `local.settings.json.example` - Example local development settings
- `functions/*/function.json` - Individual function binding configurations

## Prerequisites

- Python 3.10 or higher
- [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local) v4.x
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) (for deployment)
- An Azure subscription with appropriate permissions

## Local Development and Testing

### 1. Set up your local environment

```bash
# Navigate to the azure directory
cd azure

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Create a local.settings.json file

Create `azure/local.settings.json` based on the example file (this file is git-ignored):

```bash
# Copy the example file
cp local.settings.json.example local.settings.json

# Edit and add your API key
nano local.settings.json
```

The file should contain:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "PERMITPILOT_API_KEY": "your-secure-key-here",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing"
  }
}
```

### 3. Start the Azure Functions runtime locally

```bash
# From the azure directory
func start
```

You should see output indicating that your functions are running:
```
Functions:
  permitpilot-feedback: [POST] http://localhost:7071/api/permitpilot-feedback
  permitpilot-health: [GET] http://localhost:7071/api/permitpilot-health
  permitpilot-process: [POST] http://localhost:7071/api/permitpilot-process
```

### 4. Test the functions locally

**Health check:**
```bash
curl http://localhost:7071/api/permitpilot-health
```

**Process endpoint:**
```bash
curl -X POST http://localhost:7071/api/permitpilot-process \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the EPA requirements for stormwater permits?",
    "context": {"jurisdiction": "federal"}
  }'
```

**Feedback endpoint:**
```bash
curl -X POST http://localhost:7071/api/permitpilot-feedback \
  -H "Content-Type: application/json" \
  -d '{
    "response_id": "resp-123",
    "rating": 5,
    "comments": "Very helpful response"
  }'
```

## Deployment Options

### Option 1: Deploy via Azure CLI Script

The included deployment script automates resource creation and code deployment.

#### Step 1: Configure deployment variables

Set environment variables or edit the script directly:

```bash
export AZURE_RESOURCE_GROUP="permitpilot-rg"
export AZURE_LOCATION="eastus"
export AZURE_STORAGE_ACCOUNT="permitpilotstorage"  # Must be globally unique
export AZURE_FUNCTION_APP_NAME="permitpilot-func"  # Must be globally unique
```

#### Step 2: Log in to Azure

```bash
az login
az account set --subscription "your-subscription-id"
```

#### Step 3: Run the deployment script

```bash
cd azure/deploy
./deploy_function_app.sh
```

The script will:
1. Create a resource group
2. Create a storage account
3. Create a Function App with Python 3.10 runtime
4. Deploy your function code
5. Display the function URLs

#### Step 4: Verify deployment

```bash
# Test the health endpoint
curl https://permitpilot-func.azurewebsites.net/api/permitpilot-health

# Get function keys for authenticated endpoints
az functionapp function keys list \
  --name permitpilot-func \
  --resource-group permitpilot-rg \
  --function-name permitpilot-process
```

### Option 2: Deploy via GitHub Actions

For automated CI/CD deployment on every push to main branch:

#### Step 1: Get the Publish Profile

```bash
az functionapp deployment list-publishing-profiles \
  --name permitpilot-func \
  --resource-group permitpilot-rg \
  --xml
```

#### Step 2: Add GitHub Secret

1. Go to your GitHub repository settings
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
5. Value: Paste the entire XML output from Step 1

#### Step 3: Update workflow file

Edit `.github/workflows/deploy-azure-functions.yml` and update:
- `AZURE_FUNCTIONAPP_NAME` to your function app name
- Ensure `PYTHON_VERSION` matches your requirement

#### Step 4: Deploy

Push to the main branch, and the GitHub Action will automatically deploy your functions.

## Security Best Practices

### 1. Use Azure Key Vault for Secrets

Never commit secrets to your repository. Use Azure Key Vault references:

```bash
# Create a Key Vault
az keyvault create \
  --name permitpilot-vault \
  --resource-group permitpilot-rg \
  --location eastus

# Add a secret
az keyvault secret set \
  --vault-name permitpilot-vault \
  --name "ApiKey" \
  --value "your-secret-value"

# Reference in Function App settings
az functionapp config appsettings set \
  --name permitpilot-func \
  --resource-group permitpilot-rg \
  --settings "API_KEY=@Microsoft.KeyVault(SecretUri=https://permitpilot-vault.vault.azure.net/secrets/ApiKey/)"
```

### 2. Enable Managed Identity

```bash
# Enable system-assigned managed identity
az functionapp identity assign \
  --name permitpilot-func \
  --resource-group permitpilot-rg

# Grant access to Key Vault
az keyvault set-policy \
  --name permitpilot-vault \
  --object-id <managed-identity-object-id> \
  --secret-permissions get list
```

### 3. Configure Authentication

For production, enable Azure AD authentication:

```bash
az functionapp auth update \
  --name permitpilot-func \
  --resource-group permitpilot-rg \
  --enabled true \
  --action LoginWithAzureActiveDirectory
```

## Monitoring and Logging

### Enable Application Insights

```bash
# Create Application Insights resource
az monitor app-insights component create \
  --app permitpilot-insights \
  --location eastus \
  --resource-group permitpilot-rg

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app permitpilot-insights \
  --resource-group permitpilot-rg \
  --query instrumentationKey -o tsv)

# Configure Function App
az functionapp config appsettings set \
  --name permitpilot-func \
  --resource-group permitpilot-rg \
  --settings "APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY"
```

### View Logs

```bash
# Stream live logs
az webapp log tail \
  --name permitpilot-func \
  --resource-group permitpilot-rg

# View Application Insights logs
az monitor app-insights query \
  --app permitpilot-insights \
  --resource-group permitpilot-rg \
  --analytics-query "requests | limit 10"
```

## Scaling and Performance

### Configure Scaling

```bash
# Set maximum instance count
az functionapp config appsettings set \
  --name permitpilot-func \
  --resource-group permitpilot-rg \
  --settings "FUNCTIONS_WORKER_PROCESS_COUNT=4"
```

### Enable Premium Plan (Optional)

For always-on functions and VNet integration:

```bash
# Create Premium plan
az functionapp plan create \
  --name permitpilot-plan \
  --resource-group permitpilot-rg \
  --location eastus \
  --sku EP1

# Update function app to use Premium plan
az functionapp update \
  --name permitpilot-func \
  --resource-group permitpilot-rg \
  --plan permitpilot-plan
```

## Troubleshooting

### Common Issues

**Issue: Function app not responding**
```bash
# Check function app status
az functionapp show \
  --name permitpilot-func \
  --resource-group permitpilot-rg \
  --query state

# Restart the function app
az functionapp restart \
  --name permitpilot-func \
  --resource-group permitpilot-rg
```

**Issue: Deployment fails**
```bash
# Check deployment logs
az webapp log download \
  --name permitpilot-func \
  --resource-group permitpilot-rg

# Verify app settings
az functionapp config appsettings list \
  --name permitpilot-func \
  --resource-group permitpilot-rg
```

**Issue: Import errors**
- Ensure all dependencies are in `requirements.txt`
- Verify Python version matches between local and Azure (3.10)
- Check that function bindings are correct in `function.json`

## Copilot Studio Plugin Integration

After deploying your Azure Functions, you can integrate PermitPilot with Microsoft Copilot Studio as a custom plugin. See the detailed guide:

📄 **[Copilot Studio Plugin Setup Guide](README_CopilotPlugin.md)**

This guide covers:
- Setting up the OpenAPI specification (`openapi.json`)
- Configuring the AI plugin manifest (`ai-plugin.json`)
- Registering the plugin in Copilot Studio
- Testing and troubleshooting the integration

Quick start:
```bash
# After deployment, update the URLs in the plugin files
sed -i 's/your-function-app/your-actual-app-name/g' openapi.json
sed -i 's/your-function-app/your-actual-app-name/g' ai-plugin.json

# Then follow the steps in README_CopilotPlugin.md to register with Copilot Studio
```

## Next Steps

1. **Set up Copilot Studio Plugin** - Follow [README_CopilotPlugin.md](README_CopilotPlugin.md) to register as a custom plugin
2. **Integrate with PermitPilot agents** - Update function handlers to call the actual agent system from `src/`
3. **Add authentication** - Implement API key or OAuth validation (see plugin guide)
4. **Set up database** - Store queries and feedback in Azure Cosmos DB or SQL Database
5. **Add caching** - Use Azure Redis Cache for frequently accessed data
6. **Implement rate limiting** - Protect against abuse
7. **Add CORS configuration** - If calling from web applications

## Additional Resources

- [Azure Functions Python Developer Guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Azure Functions Best Practices](https://docs.microsoft.com/en-us/azure/azure-functions/functions-best-practices)
- [Azure Key Vault Documentation](https://docs.microsoft.com/en-us/azure/key-vault/)
- [Application Insights Documentation](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)

## Support

For issues or questions:
- Check the [PermitPilot repository](https://github.com/DmaloneMN/permitpilot)
- Review Azure Functions [troubleshooting guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-recover-storage-account)
- Contact the development team
