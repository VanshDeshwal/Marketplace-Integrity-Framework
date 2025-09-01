# Azure Secrets Extraction Script for GitHub Actions
# Run this script to get all the secrets needed for GitHub Actions deployment

Write-Host "Extracting Azure Secrets for GitHub Actions..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# 1. Azure Storage Connection String
Write-Host "1. AZURE_STORAGE_CONNECTION_STRING" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow
try {
    $storageConnectionString = az storage account show-connection-string --name marketplacestoragevd --resource-group marketplace-integrity-rg --query connectionString --output tsv
    Write-Host "SUCCESS: Storage Connection String Retrieved" -ForegroundColor Green
    Write-Host "Secret Name: AZURE_STORAGE_CONNECTION_STRING" -ForegroundColor Cyan
    Write-Host "Secret Value: $storageConnectionString" -ForegroundColor White
} catch {
    Write-Host "ERROR: Failed to get Storage Connection String" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. Azure Web App Publish Profile
Write-Host "2. AZURE_WEBAPP_PUBLISH_PROFILE" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow
try {
    $publishProfile = az webapp deployment list-publishing-profiles --name marketplace-integrity-api --resource-group marketplace-integrity-rg --xml
    Write-Host "SUCCESS: Publish Profile Retrieved" -ForegroundColor Green
    Write-Host "Secret Name: AZURE_WEBAPP_PUBLISH_PROFILE" -ForegroundColor Cyan
    Write-Host "Secret Value (XML):" -ForegroundColor White
    Write-Host $publishProfile -ForegroundColor White
} catch {
    Write-Host "ERROR: Failed to get Publish Profile" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Optional: Azure Service Principal (if you want to use Azure CLI in workflows)
Write-Host "3. AZURE_CREDENTIALS (Optional - for Azure CLI)" -ForegroundColor Yellow
Write-Host "-----------------------------------------------" -ForegroundColor Yellow
Write-Host "If you want to use Azure CLI commands in GitHub Actions, you need a Service Principal." -ForegroundColor Magenta
Write-Host "This would require creating a service principal with these commands:" -ForegroundColor Magenta
Write-Host ""
Write-Host "# Create Service Principal (run only if needed):" -ForegroundColor Gray
Write-Host "az ad sp create-for-rbac --name 'github-actions-marketplace' --role contributor --scopes /subscriptions/`$(az account show --query id --output tsv)/resourceGroups/marketplace-integrity-rg --sdk-auth" -ForegroundColor Gray
Write-Host ""
Write-Host "WARNING: We don't need this for the current workflow since we use publish profile!" -ForegroundColor Yellow
Write-Host ""

# Summary
Write-Host "SUMMARY - Required GitHub Secrets:" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "SUCCESS: GITHUB_TOKEN - Automatically provided by GitHub" -ForegroundColor Green
Write-Host "SETUP: AZURE_WEBAPP_PUBLISH_PROFILE - Copy from output above" -ForegroundColor Yellow
Write-Host "SETUP: AZURE_STORAGE_CONNECTION_STRING - Copy from output above" -ForegroundColor Yellow
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Copy the secret values from above" -ForegroundColor White
Write-Host "2. Go to: https://github.com/VanshDeshwal/Marketplace-Integrity-Framework/settings/secrets/actions" -ForegroundColor White
Write-Host "3. Add each secret using the steps in docs/GITHUB_SECRETS_SETUP.md" -ForegroundColor White
