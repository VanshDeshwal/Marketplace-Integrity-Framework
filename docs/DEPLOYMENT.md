# 🚀 Deployment Guide

## Overview

This guide covers deploying the Marketplace Integrity Framework to various environments, from local development to production cloud platforms.

## 📋 Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4GB | 8GB+ |
| **Storage** | 10GB | 50GB+ |
| **Network** | 100Mbps | 1Gbps |

### Software Dependencies

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.10+ (for local development)
- **Node.js** 18+ (for frontend development)

---

## 🐳 Docker Deployment

### Quick Start

```bash
# Clone the repository
git clone https://github.com/VanshDeshwal/Marketplace-Integrity-Framework.git
cd Marketplace-Integrity-Framework

# Start all services
docker-compose up --build -d

# Verify deployment
curl http://localhost:8000/health
```

### Production Configuration

Create a `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - CORS_ORIGINS=https://your-domain.com
      - LOG_LEVEL=INFO
    volumes:
      - ./dataset:/app/dataset:ro
      - ./backend/data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_URL=https://api.your-domain.com
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

### Environment Variables

Create a `.env` file for production:

```bash
# API Configuration
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
LOG_LEVEL=INFO
WORKERS=4

# Database Configuration
DATABASE_URL=postgresql://user:password@db:5432/marketplace

# Security
SECRET_KEY=your-secret-key-here
API_KEY_HEADER=X-API-Key

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
PROMETHEUS_METRICS=true

# Storage
STORAGE_BACKEND=azure_blob
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER=marketplace-images
```

---

## ☁️ Cloud Deployment

### AWS Deployment

#### ECS with Fargate

1. **Build and push images**:

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com

# Build and tag
docker build -f backend/Dockerfile.prod -t marketplace-api:latest ./backend
docker tag marketplace-api:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/marketplace-api:latest

# Push
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/marketplace-api:latest
```

2. **Create task definition**:

```json
{
  "family": "marketplace-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "marketplace-api",
      "image": "123456789012.dkr.ecr.us-west-2.amazonaws.com/marketplace-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "CORS_ORIGINS",
          "value": "https://your-domain.com"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/marketplace",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create service**:

```bash
aws ecs create-service \
  --cluster marketplace-cluster \
  --service-name marketplace-api \
  --task-definition marketplace-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-abcdef],assignPublicIp=ENABLED}"
```

#### CloudFormation Template

Create `aws-infrastructure.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Marketplace Integrity Framework Infrastructure'

Parameters:
  ImageURI:
    Type: String
    Description: ECR Image URI
  
Resources:
  # VPC and Networking
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: marketplace-cluster

  # Application Load Balancer
  ALB:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: marketplace-alb
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2

  # Auto Scaling
  AutoScalingTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      ServiceNamespace: ecs
      ScalableDimension: ecs:service:DesiredCount
      ResourceId: !Sub 'service/${ECSCluster}/${ECSService}'
      MinCapacity: 2
      MaxCapacity: 10

Outputs:
  LoadBalancerDNS:
    Description: Load Balancer DNS Name
    Value: !GetAtt ALB.DNSName
```

Deploy with:

```bash
aws cloudformation deploy \
  --template-file aws-infrastructure.yaml \
  --stack-name marketplace-infrastructure \
  --parameter-overrides ImageURI=123456789012.dkr.ecr.us-west-2.amazonaws.com/marketplace-api:latest \
  --capabilities CAPABILITY_IAM
```

---

### Azure Deployment

#### Container Instances

```bash
# Create resource group
az group create --name marketplace-rg --location eastus

# Create container instance
az container create \
  --resource-group marketplace-rg \
  --name marketplace-api \
  --image marketplace-api:latest \
  --ports 8000 \
  --dns-name-label marketplace-api-demo \
  --environment-variables CORS_ORIGINS=https://your-domain.com \
  --cpu 2 \
  --memory 4
```

#### App Service

```bash
# Create App Service plan
az appservice plan create \
  --name marketplace-plan \
  --resource-group marketplace-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group marketplace-rg \
  --plan marketplace-plan \
  --name marketplace-app \
  --deployment-container-image-name marketplace-api:latest

# Configure settings
az webapp config appsettings set \
  --resource-group marketplace-rg \
  --name marketplace-app \
  --settings CORS_ORIGINS=https://your-domain.com
```

#### ARM Template

Create `azure-template.json`:

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "siteName": {
      "type": "string",
      "metadata": {
        "description": "Name of the web app"
      }
    },
    "dockerImage": {
      "type": "string",
      "metadata": {
        "description": "Docker image name"
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.Web/serverfarms",
      "apiVersion": "2020-06-01",
      "name": "[concat(parameters('siteName'), '-plan')]",
      "location": "[resourceGroup().location]",
      "sku": {
        "name": "B1",
        "tier": "Basic"
      },
      "kind": "linux",
      "properties": {
        "reserved": true
      }
    },
    {
      "type": "Microsoft.Web/sites",
      "apiVersion": "2020-06-01",
      "name": "[parameters('siteName')]",
      "location": "[resourceGroup().location]",
      "dependsOn": [
        "[resourceId('Microsoft.Web/serverfarms', concat(parameters('siteName'), '-plan'))]"
      ],
      "properties": {
        "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', concat(parameters('siteName'), '-plan'))]",
        "siteConfig": {
          "linuxFxVersion": "[concat('DOCKER|', parameters('dockerImage'))]",
          "appSettings": [
            {
              "name": "WEBSITES_ENABLE_APP_SERVICE_STORAGE",
              "value": "false"
            }
          ]
        }
      }
    }
  ]
}
```

---

### Google Cloud Deployment

#### Cloud Run

```bash
# Build and submit to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/marketplace-api ./backend

# Deploy to Cloud Run
gcloud run deploy marketplace-api \
  --image gcr.io/PROJECT_ID/marketplace-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars CORS_ORIGINS=https://your-domain.com
```

#### Kubernetes Engine

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: marketplace-api
  labels:
    app: marketplace-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: marketplace-api
  template:
    metadata:
      labels:
        app: marketplace-api
    spec:
      containers:
      - name: marketplace-api
        image: gcr.io/PROJECT_ID/marketplace-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: CORS_ORIGINS
          value: "https://your-domain.com"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: marketplace-api-service
spec:
  selector:
    app: marketplace-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy with:

```bash
# Create cluster
gcloud container clusters create marketplace-cluster \
  --num-nodes=3 \
  --zone=us-central1-a

# Apply configuration
kubectl apply -f k8s-deployment.yaml

# Get external IP
kubectl get service marketplace-api-service
```

---

## 🔧 Configuration

### Nginx Configuration

Create `nginx.conf` for production:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=1r/s;

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/ssl/certs/fullchain.pem;
        ssl_certificate_key /etc/ssl/certs/privkey.pem;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # File uploads
        location /dedup/ {
            limit_req zone=upload burst=5 nodelay;
            client_max_body_size 10M;
            proxy_pass http://backend/dedup/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_read_timeout 300s;
        }
    }
}
```

### SSL Certificate Setup

Using Let's Encrypt:

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 Monitoring and Logging

### Prometheus Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'marketplace-api'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboard

Import dashboard JSON for monitoring:

```json
{
  "dashboard": {
    "title": "Marketplace Integrity Framework",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### ELK Stack Setup

Docker Compose for logging:

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"

  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Models Not Loading

**Symptoms**: 503 errors, "models not available" message

**Solutions**:
```bash
# Check model files exist
ls -la backend/data/siamese_artifacts/

# Verify permissions
chmod -R 755 backend/data/

# Check memory usage
docker stats

# Increase memory allocation
docker-compose up --memory=4g
```

#### 2. CORS Errors

**Symptoms**: Browser blocks requests from frontend

**Solutions**:
```bash
# Check CORS configuration
echo $CORS_ORIGINS

# Update environment variable
export CORS_ORIGINS=https://your-domain.com

# Restart service
docker-compose restart backend
```

#### 3. High Memory Usage

**Symptoms**: OOM kills, slow response times

**Solutions**:
```bash
# Monitor memory usage
docker exec -it container_name free -h

# Optimize model loading
# Edit backend/app/main.py - implement lazy loading

# Scale horizontally
docker-compose up --scale backend=2
```

#### 4. Database Connection Issues

**Symptoms**: Cannot load product metadata

**Solutions**:
```bash
# Check dataset directory
ls -la dataset/shopee-product-matching/

# Verify file permissions
chmod 644 dataset/shopee-product-matching/train.csv

# Rebuild indices
docker exec -it backend_container python -m app.build_index
```

### Performance Optimization

#### 1. Image Processing
```bash
# Enable GPU acceleration (if available)
docker run --gpus all marketplace-api:latest

# Optimize image preprocessing
export TORCH_HOME=/tmp/torch_cache
```

#### 2. Database Tuning
```python
# In main.py, optimize FAISS settings
import faiss
index = faiss.read_index("path/to/index")
index.nprobe = 32  # Adjust for speed vs accuracy
```

#### 3. Caching
```yaml
# Add Redis for caching
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  backend:
    environment:
      - REDIS_URL=redis://redis:6379/0
```

---

## 📋 Deployment Checklist

### Pre-deployment

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backups created
- [ ] Monitoring systems configured
- [ ] Load testing completed
- [ ] Security scan passed

### During Deployment

- [ ] Blue-green deployment strategy
- [ ] Health checks passing
- [ ] Rollback plan ready
- [ ] Team notified
- [ ] Monitoring alerts configured

### Post-deployment

- [ ] Functional testing completed
- [ ] Performance metrics validated
- [ ] Error rates monitored
- [ ] User feedback collected
- [ ] Documentation updated

---

## 🎯 Best Practices

1. **Security**
   - Use HTTPS in production
   - Implement API rate limiting
   - Validate all inputs
   - Use secrets management

2. **Performance**
   - Enable compression
   - Use CDN for static assets
   - Implement caching strategies
   - Monitor resource usage

3. **Reliability**
   - Set up health checks
   - Implement circuit breakers
   - Use rolling deployments
   - Configure auto-scaling

4. **Monitoring**
   - Centralized logging
   - Application metrics
   - Business KPIs
   - Alert management
