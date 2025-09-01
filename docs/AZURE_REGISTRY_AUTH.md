# GitHub Container Registry Authentication Setup

## Problem
Your Azure Web App deployment is failing with "Failed to get app runtime OS" because Azure cannot authenticate with GitHub Container Registry to pull your private Docker image.

## Solution
Configure Azure Web App with GitHub Container Registry credentials.

## Steps

### Option 1: Using GitHub Personal Access Token (Recommended)

1. **Create a GitHub Personal Access Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: `Azure Container Registry Access`
   - Expiration: Choose appropriate duration (90 days or custom)
   - Scopes: Select `read:packages` and `write:packages`
   - Click "Generate token" and copy it

2. **Configure Azure Web App**:
   ```powershell
   # Run this command with your GitHub token
   .\tools\setup_azure_registry_auth.ps1 -GitHubToken "your_github_token_here"
   ```

3. **Add the token to GitHub Secrets** (for CI/CD):
   - Go to: https://github.com/vanshdeshwal/marketplace-integrity-framework/settings/secrets/actions
   - Click "New repository secret"
   - Name: `GITHUB_CONTAINER_REGISTRY_TOKEN`
   - Value: Your GitHub token
   - Click "Add secret"

### Option 2: Make Package Public (Quick Fix)

1. Go to: https://github.com/vanshdeshwal/marketplace-integrity-framework/pkgs/container/marketplace-integrity-framework-backend
2. Click "Package settings"
3. Scroll down to "Danger Zone"
4. Click "Change visibility" → "Public"
5. Confirm the change

### Option 3: Use Azure Container Registry (Most Secure)

If you prefer using Azure's own container registry:

1. **Create Azure Container Registry**:
   ```bash
   az acr create --resource-group marketplace-integrity-rg --name marketplaceintegrity --sku Basic
   ```

2. **Update workflow to push to ACR**:
   - Replace `ghcr.io` with `marketplaceintegrity.azurecr.io`
   - Configure ACR authentication in GitHub Actions

## Current Status

Your Docker image builds successfully and is optimized (1.17GB), but Azure cannot pull it due to authentication issues.

## Test Deployment

After configuring authentication, trigger a deployment:

```bash
# Trigger manual deployment
gh workflow run "Deploy Backend API to Azure (Docker)"
```

Or push changes to the main branch to trigger automatic deployment.

## Verification

Once deployed, test your API:
- Health check: https://api.marketplace.vanshdeshwal.dev/health
- API docs: https://api.marketplace.vanshdeshwal.dev/docs
