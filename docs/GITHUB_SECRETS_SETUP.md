# GitHub Secrets Setup Guide

## 🔐 How to Add Secrets to GitHub Repository

### Step 1: Navigate to Secrets Settings
1. Go to your repository: `https://github.com/VanshDeshwal/Marketplace-Integrity-Framework`
2. Click **Settings** tab (at the top)
3. In the left sidebar, click **Secrets and variables** 
4. Click **Actions**

### Step 2: Add Each Secret

#### For each secret, follow these steps:
1. Click **New repository secret**
2. Enter the **Name** exactly as shown below
3. Paste the **Value** from the Azure extraction script
4. Click **Add secret**

---

## 📝 Required Secrets

### Secret 1: AZURE_WEBAPP_PUBLISH_PROFILE
```
Name: AZURE_WEBAPP_PUBLISH_PROFILE
Value: [Copy the XML output from the Azure script]
```
**Description**: Used by GitHub Actions to deploy to Azure Web App

---

### Secret 2: AZURE_STORAGE_CONNECTION_STRING  
```
Name: AZURE_STORAGE_CONNECTION_STRING
Value: [Copy the connection string from the Azure script]
```
**Description**: Used by your app to connect to Azure Blob Storage for images

---

### Secret 3: GITHUB_TOKEN (Already Available)
✅ **No action needed** - GitHub automatically provides this token for all repositories.

---

## 🚀 After Adding Secrets

### Verify Secrets Are Added:
1. Go back to: `https://github.com/VanshDeshwal/Marketplace-Integrity-Framework/settings/secrets/actions`
2. You should see:
   - ✅ `AZURE_WEBAPP_PUBLISH_PROFILE` 
   - ✅ `AZURE_STORAGE_CONNECTION_STRING`

### Test the Deployment:
1. Make a small change to any file in the `backend/` folder
2. Commit and push to the `main` branch
3. Go to the **Actions** tab to watch the deployment
4. Or manually trigger: Go to Actions → "Deploy Backend API to Azure (Docker)" → "Run workflow"

### Expected Result:
- ✅ Docker image builds (1.17GB)
- ✅ Image pushes to GitHub Container Registry  
- ✅ Azure Web App pulls and runs the container
- ✅ API becomes available at: `https://api.marketplace.vanshdeshwal.dev/health`

---

## 🔍 Troubleshooting

### If deployment still fails:
1. Check the **Actions** tab for detailed error logs
2. Verify all secret names are exactly as specified (case-sensitive)
3. Ensure the publish profile XML is complete (starts with `<?xml` and ends with `</publishData>`)
4. Test the storage connection string with: `az storage blob list --connection-string "YOUR_CONNECTION_STRING" --container-name catalog`

### If the app doesn't start:
1. Check Azure Web App logs: Portal → App Service → Log stream
2. Verify container port is set to 8000
3. Ensure the Docker image is public in GitHub Container Registry
