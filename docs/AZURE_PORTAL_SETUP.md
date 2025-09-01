# Setting Environment Variables via Azure Portal

## 🌐 Azure Portal Method (Recommended)

### Step 1: Navigate to Azure Portal
1. Go to: https://portal.azure.com
2. Sign in with your Azure account

### Step 2: Find Your Web App
1. In the search bar at the top, type: `marketplace-integrity-api`
2. Click on your web app from the search results
3. Or navigate: **All resources** → **marketplace-integrity-api**

### Step 3: Access Configuration Settings
1. In the left sidebar, click **Settings**
2. Click **Environment variables** (or **Configuration** in older portal versions)

### Step 4: Add Application Settings
Click **+ New application setting** for each of the following:

#### Setting 1: Storage Connection String
```
Name: AZURE_STORAGE_CONNECTION_STRING
Value: [Use the connection string from the PowerShell script output - starts with DefaultEndpointsProtocol=https...]
```

#### Setting 2: Container Port
```
Name: WEBSITES_PORT
Value: 8000
```

#### Setting 3: Disable Source Builds
```
Name: ENABLE_ORYX_BUILD
Value: false
```

#### Setting 4: Disable Build During Deployment
```
Name: SCM_DO_BUILD_DURING_DEPLOYMENT
Value: false
```

#### Setting 5: Disable App Service Storage
```
Name: WEBSITES_ENABLE_APP_SERVICE_STORAGE
Value: false
```

### Step 5: Save Changes
1. Click **Save** at the top of the page
2. Wait for the "Successfully updated web app settings" notification
3. Click **Continue** if prompted about restart

### Step 6: Restart the Web App
1. Go back to the **Overview** page (click on the web app name at the top)
2. Click **Restart** button
3. Click **Yes** to confirm
4. Wait for the restart to complete

### Step 7: Verify Settings
1. Go back to **Settings** → **Environment variables**
2. Verify all 5 settings are listed with correct values
3. Check that no values show as "null"

---

## 🔍 Alternative: General Settings Tab

If you don't see "Environment variables", look for:
1. **Settings** → **Configuration**
2. Click on the **Application settings** tab
3. Follow the same steps above

---

## 🧪 Test After Configuration

### Check if the container is running:
1. Go to **Settings** → **Container settings**
2. You should see: `ghcr.io/vanshdeshwal/marketplace-integrity-framework-backend:latest`
3. Check **Logs** tab for container startup logs

### Test the API:
- Visit: https://api.marketplace.vanshdeshwal.dev/health
- Should return: `{"status": "healthy"}`

---

## 📋 Summary Checklist

After completing these steps, verify:
- ✅ 5 environment variables are set
- ✅ Web app has been restarted  
- ✅ Container shows as running in logs
- ✅ API health endpoint responds

If the API still doesn't work, check:
1. **Log stream**: Settings → Log stream (for real-time logs)
2. **Container logs**: Settings → Container settings → Logs
3. **Diagnose and solve problems**: For detailed troubleshooting
