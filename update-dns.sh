#!/bin/bash
# Script to update Azure DNS for alpha-research

set -e

SUBSCRIPTION_ID="dd1805ce-ceaf-47fb-b95d-5e2b04ae85cb"
RESOURCE_GROUP="vpn"
NEW_IP="57.155.1.26"
DNS_NAME="alpha-research"
REGION="southeastasia"

echo "🔍 Checking Azure CLI installation..."
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it:"
    echo "   brew install azure-cli"
    exit 1
fi

echo "✅ Azure CLI found"
echo ""

echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "⚠️  Not logged in. Logging in..."
    az login
fi

echo "✅ Logged in to Azure"
echo ""

echo "📋 Setting subscription: $SUBSCRIPTION_ID"
az account set --subscription "$SUBSCRIPTION_ID"
echo ""

echo "🔍 Finding public IP resource for $NEW_IP..."
PUBLIC_IP_NAME=$(az network public-ip list --resource-group "$RESOURCE_GROUP" \
    --query "[?ipAddress=='$NEW_IP'].name" -o tsv)

if [ -z "$PUBLIC_IP_NAME" ]; then
    echo "❌ No public IP found with address $NEW_IP in resource group $RESOURCE_GROUP"
    echo ""
    echo "Available public IPs:"
    az network public-ip list --resource-group "$RESOURCE_GROUP" \
        --query "[].{Name:name, IP:ipAddress, DNS:dnsSettings.fqdn}" -o table
    exit 1
fi

echo "✅ Found public IP: $PUBLIC_IP_NAME"
echo ""

echo "🔧 Updating DNS name to: $DNS_NAME.southeastasia.cloudapp.azure.com"
az network public-ip update \
    --resource-group "$RESOURCE_GROUP" \
    --name "$PUBLIC_IP_NAME" \
    --dns-name "$DNS_NAME" \
    --allocation-method Static

echo ""
echo "✅ DNS updated successfully!"
echo ""

echo "📡 Getting updated DNS information..."
az network public-ip show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$PUBLIC_IP_NAME" \
    --query "{Name:name, IP:ipAddress, FQDN:dnsSettings.fqdn}" -o table

echo ""
echo "🎉 Done! Your application will be available at:"
echo "   http://$DNS_NAME.southeastasia.cloudapp.azure.com:3000"
echo "   http://$DNS_NAME.southeastasia.cloudapp.azure.com:3000/research"
echo ""
echo "⏱  DNS propagation may take a few minutes."
