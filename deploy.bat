@echo off
REM Deployment script for Windows - Marketplace Integrity Framework

echo 🚀 Starting deployment of Marketplace Integrity Framework

REM Build the Docker image
echo 📦 Building Docker image...
docker build -t marketplace-integrity-backend:latest ./backend
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker build failed
    exit /b 1
)

REM Stop existing container if running
echo 🛑 Stopping existing containers...
docker-compose down

REM Start the services
echo 🔄 Starting services...
docker-compose up -d
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start services
    exit /b 1
)

REM Wait for services to be healthy
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak

REM Check health
echo 🏥 Checking service health...
curl -f http://localhost:8000/health
if %ERRORLEVEL% neq 0 (
    echo ❌ Backend health check failed
    docker-compose logs backend
    exit /b 1
)

echo 🎉 Deployment completed successfully!
echo 📊 Backend API: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
