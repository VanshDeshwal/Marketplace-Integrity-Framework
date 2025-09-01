# Azure Container Registry Authentication Setup Script
# This script configures Azure Web App to authenticate with GitHub Container Registry

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [Parameter(Mandatory=$false)]
    [string]$WebAppName = "marketplace-integrity-api",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "marketplace-integrity-rg",
    
    [Parameter(Mandatory=$false)]
    [string]$GitHubUsername = "vanshdeshwal"
)

Write-Host "Setting up GitHub Container Registry authentication for Azure Web App..." -ForegroundColor Green

try {
    # Set Docker registry authentication
    Write-Host "Configuring Docker registry server credentials..." -ForegroundColor Yellow
    
    az webapp config appsettings set `
        --name $WebAppName `
        --resource-group $ResourceGroup `
        --settings `
        "DOCKER_REGISTRY_SERVER_USERNAME=$GitHubUsername" `
        "DOCKER_REGISTRY_SERVER_PASSWORD=$GitHubToken" `
        "DOCKER_REGISTRY_SERVER_URL=https://ghcr.io"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Authentication configured successfully!" -ForegroundColor Green
        Write-Host "Azure Web App can now pull from GitHub Container Registry." -ForegroundColor Green
        
        # Restart the web app to apply changes
        Write-Host "Restarting web app to apply changes..." -ForegroundColor Yellow
        az webapp restart --name $WebAppName --resource-group $ResourceGroup
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Web app restarted successfully!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Failed to restart web app. You may need to restart manually." -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Failed to configure authentication!" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "❌ Error occurred: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Commit and push your changes to trigger the GitHub Actions deployment" -ForegroundColor White
Write-Host "2. Monitor the deployment at: https://github.com/vanshdeshwal/marketplace-integrity-framework/actions" -ForegroundColor White
Write-Host "3. Check your API at: https://api.marketplace.vanshdeshwal.dev" -ForegroundColor White
