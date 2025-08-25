# Complete Deployment Guide

This guide will walk you through deploying the Marketplace Integrity Framework to your three target platforms:

1. **Frontend** → GitHub Pages
2. **Backend** → Azure Web App
3. **Dataset** → Azure Blob Storage

## Prerequisites

- GitHub account with this repository
- Azure account with subscription
- Azure CLI installed (for local deployment testing)
- Python 3.10+ installed locally

## Step 1: Deploy Dataset to Azure Blob Storage

### 1.1 Create Azure Storage Account

1. Log into [Azure Portal](https://portal.azure.com)
2. Create a new **Storage Account**:
   - Resource group: Create new or use existing
   - Storage account name: `marketplacedata[yourname]` (must be globally unique)
   - Performance: Standard
   - Redundancy: LRS (or RA-GRS for production)
3. After creation, go to **Containers** and create a container named `catalog`
4. Set container access level to **Blob** (anonymous read access for blobs)

### 1.2 Get Connection String

1. In your Storage Account, go to **Access Keys**
2. Copy the **Connection string** from key1 or key2

### 1.3 Upload Dataset

```powershell
# Set environment variables (replace with your values)
$env:AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net"
$env:AZURE_STORAGE_CONTAINER = "catalog"

# Install Azure Storage library
pip install azure-storage-blob

# Upload dataset
python tools/upload_to_blob.py
```

### 1.4 (Optional) Setup Custom Domain

For production, you can setup a custom domain like `assets.marketplace.vanshdeshwal.dev`:

1. Create **Azure CDN** profile
2. Create CDN endpoint pointing to your storage account
3. Configure custom domain with SSL certificate
4. Update the `MEDIA_BASE_URL` environment variable in your Azure Web App

## Step 2: Deploy Backend to Azure Web App

### 2.1 Create Azure Web App

1. In Azure Portal, create a new **Web App**:
   - Resource group: Same as storage account
   - Name: `marketplace-integrity-api` (must be globally unique)
   - Runtime stack: **Python 3.10**
   - Operating System: Linux
   - Pricing tier: B1 Basic (minimum recommended)

### 2.2 Configure Environment Variables

In your Web App, go to **Configuration** → **Application settings** and add:

- `MEDIA_BASE_URL`: `https://yourstorageaccount.blob.core.windows.net/catalog`
- `SCM_DO_BUILD_DURING_DEPLOYMENT`: `true`
- `ENABLE_ORYX_BUILD`: `true`

### 2.3 Setup GitHub Actions Deployment

1. In your Web App, go to **Deployment Center**
2. Select **GitHub** as source
3. Authorize GitHub and select your repository
4. Select branch: `main`
5. Build provider: **GitHub Actions**
6. This will create a publish profile secret in your GitHub repository

### 2.4 Manual Deployment Alternative

If you prefer manual deployment:

```powershell
# Install Azure CLI
# Login to Azure
az login

# Deploy to Web App
cd backend
zip -r ../backend-deploy.zip . -x "__pycache__/*" "*.pyc"
az webapp deployment source config-zip --resource-group your-rg --name marketplace-integrity-api --src ../backend-deploy.zip
```

## Step 3: Deploy Frontend to GitHub Pages

### 3.1 Enable GitHub Pages

1. Go to your GitHub repository settings
2. Navigate to **Pages** section
3. Source: **GitHub Actions**

### 3.2 Update Frontend URLs (if needed)

The frontend automatically detects if it's running locally or hosted. For custom domains:

In `frontend/index.html`, update these lines if you have different URLs:
```javascript
const API_BASE = IS_LOCAL ? 'http://localhost:8000' : 'https://your-api-domain.azurewebsites.net'
const MEDIA_BASE = IS_LOCAL ? (localStorage.getItem('mediaBase') || '') : 'https://your-storage-account.blob.core.windows.net/catalog'
```

### 3.3 Deploy

Simply push to main branch:
```bash
git add .
git commit -m "Setup deployment configuration"
git push origin main
```

GitHub Actions will automatically deploy your frontend to GitHub Pages.

## Step 4: Test Your Deployment

### 4.1 Backend Health Check

Visit: `https://your-api-name.azurewebsites.net/health`

Should return:
```json
{
  "status": "ok",
  "artifacts_loaded": {...}
}
```

### 4.2 Frontend Access

Visit your GitHub Pages URL (usually `https://yourusername.github.io/repository-name`)

### 4.3 Image Access

Test if images are accessible:
`https://your-storage-account.blob.core.windows.net/catalog/train_images/some-image.jpg`

## Step 5: Upload AI Artifacts

Your backend needs the pre-trained artifacts to work fully:

1. Generate artifacts using the Jupyter notebook in `notebooks/`
2. Place the following files in `backend/data/siamese_artifacts/`:
   - `meta.csv`
   - `text_embs.npy`
   - `image_embs.npy`
   - `faiss_text.index`
   - `faiss_image.index`
   - `threshold_clf.pkl`
   - `manifest.json`

3. Re-deploy the backend with artifacts included

## Troubleshooting

### Backend Issues

- **Timeout errors**: Increase the command timeout in Azure Web App configuration
- **Memory issues**: Upgrade to a higher pricing tier (B2 or higher)
- **Import errors**: Ensure all dependencies are in `requirements.txt`

### Frontend Issues

- **CORS errors**: Verify your backend CORS configuration includes your frontend domain
- **API not found**: Check the API_BASE URL in your frontend code
- **Images not loading**: Verify MEDIA_BASE_URL and container permissions

### Dataset Issues

- **Upload failures**: Check your connection string and container permissions
- **Access denied**: Ensure container is set to public blob access
- **Slow loading**: Consider implementing Azure CDN

## Production Optimizations

1. **Enable CDN** for faster image loading
2. **Setup custom domains** with SSL certificates
3. **Implement caching** strategies
4. **Monitor performance** with Application Insights
5. **Setup backup** for your storage account
6. **Configure scaling** for your Web App

## Environment Summary

After successful deployment, you'll have:

- **Frontend**: `https://yourusername.github.io/repository-name`
- **Backend API**: `https://your-api-name.azurewebsites.net`
- **Dataset**: `https://your-storage-account.blob.core.windows.net/catalog`
- **API Docs**: `https://your-api-name.azurewebsites.net/docs`

## Next Steps

1. Generate and upload your AI artifacts
2. Test all functionality thoroughly
3. Setup monitoring and alerts
4. Configure custom domains if desired
5. Implement any additional security measures
