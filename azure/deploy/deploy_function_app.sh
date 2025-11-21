#!/usr/bin/env bash
set -euo pipefail

# Simple Azure CLI deployment helper (requires az CLI + logged in user with permissions)
# Replace placeholders before running. This script creates a resource group, storage account,
# and a Function App on Linux with a Python runtime, then deploys via zip deploy.

# ==============================================================================
# CONFIGURATION - Replace these placeholders with your actual values
# ==============================================================================
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-permitpilot-rg}"
LOCATION="${AZURE_LOCATION:-eastus}"
STORAGE_ACCOUNT="${AZURE_STORAGE_ACCOUNT:-permitpilotstorage}"
FUNCTION_APP_NAME="${AZURE_FUNCTION_APP_NAME:-permitpilot-func}"
PYTHON_VERSION="3.10"

echo "==================================================================="
echo "PermitPilot Azure Functions Deployment Script"
echo "==================================================================="
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Function App: $FUNCTION_APP_NAME"
echo "Python Version: $PYTHON_VERSION"
echo "==================================================================="
echo ""

# ==============================================================================
# STEP 1: Create Resource Group
# ==============================================================================
echo "Step 1: Creating resource group..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION"

echo "✓ Resource group created"
echo ""

# ==============================================================================
# STEP 2: Create Storage Account
# ==============================================================================
echo "Step 2: Creating storage account..."
az storage account create \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Standard_LRS

echo "✓ Storage account created"
echo ""

# ==============================================================================
# STEP 3: Create Function App
# ==============================================================================
echo "Step 3: Creating Function App..."
az functionapp create \
  --resource-group "$RESOURCE_GROUP" \
  --consumption-plan-location "$LOCATION" \
  --runtime python \
  --runtime-version "$PYTHON_VERSION" \
  --functions-version 4 \
  --name "$FUNCTION_APP_NAME" \
  --storage-account "$STORAGE_ACCOUNT" \
  --os-type Linux

echo "✓ Function App created"
echo ""

# ==============================================================================
# STEP 4: Configure App Settings (Environment Variables)
# ==============================================================================
echo "Step 4: Configuring app settings..."
# Add any required environment variables here
# Example:
# az functionapp config appsettings set \
#   --name "$FUNCTION_APP_NAME" \
#   --resource-group "$RESOURCE_GROUP" \
#   --settings "API_KEY=@Microsoft.KeyVault(SecretUri=https://your-vault.vault.azure.net/secrets/api-key/)"

echo "✓ App settings configured (add secrets via Key Vault)"
echo ""

# ==============================================================================
# STEP 5: Deploy Function Code
# ==============================================================================
echo "Step 5: Deploying function code..."
# Navigate to the azure directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AZURE_DIR="$(dirname "$SCRIPT_DIR")"

cd "$AZURE_DIR"

# Deploy using Azure Functions Core Tools (func CLI) or zip deploy
# Option 1: Using func CLI (recommended for local testing)
# func azure functionapp publish "$FUNCTION_APP_NAME"

# Option 2: Using az CLI with zip deploy
echo "Creating deployment package..."
TEMP_DIR=$(mktemp -d)
cp -r functions/* "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"

# Create host.json if it doesn't exist
if [ ! -f "$TEMP_DIR/host.json" ]; then
  cat > "$TEMP_DIR/host.json" << 'EOF'
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[3.*, 4.0.0)"
  }
}
EOF
fi

cd "$TEMP_DIR"
zip -r ../deploy.zip .
cd ..

echo "Uploading deployment package..."
az functionapp deployment source config-zip \
  --resource-group "$RESOURCE_GROUP" \
  --name "$FUNCTION_APP_NAME" \
  --src deploy.zip

# Cleanup
rm -rf "$TEMP_DIR" deploy.zip

echo "✓ Function code deployed"
echo ""

# ==============================================================================
# STEP 6: Get Function URLs
# ==============================================================================
echo "Step 6: Retrieving function URLs..."
echo ""
echo "Function App URL: https://${FUNCTION_APP_NAME}.azurewebsites.net"
echo ""
echo "To get function keys, run:"
echo "  az functionapp function keys list --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --function-name permitpilot-process"
echo "  az functionapp function keys list --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --function-name permitpilot-feedback"
echo ""

# ==============================================================================
# DEPLOYMENT COMPLETE
# ==============================================================================
echo "==================================================================="
echo "✓ Deployment complete!"
echo "==================================================================="
echo ""
echo "Next steps:"
echo "1. Set up Application Insights for monitoring"
echo "2. Configure Key Vault for secrets management"
echo "3. Set up custom domain and SSL if needed"
echo "4. Test your functions:"
echo "   curl https://${FUNCTION_APP_NAME}.azurewebsites.net/api/permitpilot-health"
echo ""
