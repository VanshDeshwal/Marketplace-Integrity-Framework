# PowerShell deployment script for local testing and Azure setup

Write-Host "Marketplace Integrity Framework - Deployment Script" -ForegroundColor Green

# Function to check if command exists
function Test-Command($command) {
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

if (!(Test-Command "python")) {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

if (!(Test-Command "git")) {
    Write-Host "❌ Git not found. Please install Git" -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green

# Backend setup
Write-Host "`n🚀 Setting up backend for local testing..." -ForegroundColor Yellow

Push-Location backend

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "❌ Failed to find virtual environment activation script" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "✅ Backend setup complete!" -ForegroundColor Green

Pop-Location

# Frontend setup
Write-Host "`n🌐 Frontend is ready for GitHub Pages deployment!" -ForegroundColor Yellow
Write-Host "The frontend/index.html file is configured to auto-detect local vs hosted environment." -ForegroundColor Cyan

# Dataset information
Write-Host "`n📦 Dataset deployment information:" -ForegroundColor Yellow
Write-Host "1. Create Azure Storage Account" -ForegroundColor Cyan
Write-Host "2. Create container named 'catalog'" -ForegroundColor Cyan
Write-Host "3. Set environment variables:" -ForegroundColor Cyan
Write-Host "   `$env:AZURE_STORAGE_CONNECTION_STRING = 'your_connection_string'" -ForegroundColor Gray
Write-Host "   `$env:AZURE_STORAGE_CONTAINER = 'catalog'" -ForegroundColor Gray
Write-Host "4. Run: python tools/upload_to_blob.py" -ForegroundColor Cyan

# Local testing
Write-Host "`n🧪 To test locally:" -ForegroundColor Yellow
Write-Host "1. Backend: cd backend; python -m uvicorn application:app --reload --port 8000" -ForegroundColor Cyan
Write-Host "2. Media Server: python -m uvicorn media_server.server:app --reload --port 9000" -ForegroundColor Cyan
Write-Host "3. Frontend: Open frontend/index.html in browser" -ForegroundColor Cyan

# Azure deployment information
Write-Host "`n☁️ Azure deployment steps:" -ForegroundColor Yellow
Write-Host "1. Create Azure Web App (Python 3.10)" -ForegroundColor Cyan
Write-Host "2. Enable GitHub Actions deployment" -ForegroundColor Cyan
Write-Host "3. Set AZUREAPPSERVICE_PUBLISHPROFILE secret in GitHub" -ForegroundColor Cyan
Write-Host "4. Set MEDIA_BASE_URL environment variable in Azure Web App" -ForegroundColor Cyan

# GitHub Pages setup
Write-Host "`n📄 GitHub Pages setup:" -ForegroundColor Yellow
Write-Host "1. Go to repository Settings > Pages" -ForegroundColor Cyan
Write-Host "2. Select 'GitHub Actions' as source" -ForegroundColor Cyan
Write-Host "3. Push changes to main branch to trigger deployment" -ForegroundColor Cyan

Write-Host "`n🎉 Setup complete! Check the DEPLOYMENT_GUIDE.md for detailed instructions." -ForegroundColor Green
