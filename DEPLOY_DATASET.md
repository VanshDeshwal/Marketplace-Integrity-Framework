# Dataset Upload to Azure Blob Storage

This guide will help you upload your dataset to Azure Blob Storage.

## Prerequisites

1. **Azure Storage Account**: Create one in the Azure Portal
2. **Container**: Create a container named `catalog` (or your preferred name)
3. **Connection String**: Get it from Azure Portal > Storage Account > Access Keys

## Setup

1. Install Azure Storage dependency:
```powershell
pip install azure-storage-blob
```

2. Set environment variables in PowerShell:
```powershell
$env:AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net"
$env:AZURE_STORAGE_CONTAINER = "catalog"
```

3. Upload dataset:
```powershell
python tools/upload_to_blob.py
```

## Custom Domain Setup (Optional)

For production, you can set up a custom domain like `assets.marketplace.vanshdeshwal.dev`:

1. **Azure CDN**: Create an Azure CDN profile
2. **Custom Domain**: Add your custom domain to the CDN endpoint
3. **SSL Certificate**: Enable HTTPS with Azure managed certificate
4. **Environment Variable**: Set `MEDIA_BASE_URL` in your Azure Web App to your custom domain

## Environment Variables for Backend

Set these in your Azure Web App Configuration:

- `MEDIA_BASE_URL`: Your blob storage URL (e.g., `https://yourstorageaccount.blob.core.windows.net/catalog` or your custom domain)

## Verification

After upload, your images will be accessible at:
- Direct: `https://yourstorageaccount.blob.core.windows.net/catalog/train_images/filename.jpg`
- Custom domain: `https://assets.marketplace.vanshdeshwal.dev/train_images/filename.jpg`
