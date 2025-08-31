# 🛒 Marketplace Integrity Framework

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-18.2.0-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![CI/CD](https://img.shields.io/badge/CI%2FCD-automated-green.svg)

**An advanced AI-powered marketplace integrity solution featuring duplicate detection, semantic search, and fraud analysis.**

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [🎯 Features](#-features) • [🔧 API Reference](#-api-reference) • [🐳 Deployment](#-deployment)

</div>

---

## 🌟 Overview

The Marketplace Integrity Framework is a comprehensive solution designed to maintain marketplace quality through advanced AI technologies. It combines computer vision, natural language processing, and machine learning to detect duplicates, analyze content semantically, and identify potential fraud patterns.

### 🎯 Key Capabilities

- **🔍 Duplicate Detection**: State-of-the-art Siamese networks for image and text similarity
- **🧠 Semantic Search**: Advanced embedding-based product discovery
- **🛡️ Fraud Analysis**: ML-powered anomaly detection and risk assessment
- **⚡ Real-time Processing**: Optimized for production-scale operations
- **🌐 Modern UI**: Responsive React interface with professional design
- **🐳 Container-ready**: Full Docker support for seamless deployment

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Docker** (optional, for containerized deployment)
- **Git** for version control

### 1️⃣ Clone & Setup

```bash
# Clone the repository
git clone https://github.com/VanshDeshwal/Marketplace-Integrity-Framework.git
cd Marketplace-Integrity-Framework

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### 2️⃣ Data Preparation

```bash
# Download the Shopee Product Matching dataset
# Place it in: dataset/shopee-product-matching/

# Build search indices (one-time setup)
cd backend
python -m app.build_index
```

### 3️⃣ Launch Services

**Option A: Development Mode**
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm start
```

**Option B: Docker Deployment**
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### 4️⃣ Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 🎯 Features

### 🔍 Duplicate Detection

- **Multi-modal Analysis**: Combines image and text features
- **OpenCLIP Integration**: State-of-the-art vision-language models
- **FAISS Optimization**: Lightning-fast similarity search
- **Configurable Thresholds**: Adaptive similarity scoring
- **Batch Processing**: Efficient large-scale operations

**Supported Formats**: JPG, PNG, WebP, GIF (up to 10MB)

### 🧠 Semantic Search

- **SentenceTransformers**: Multilingual text embeddings
- **Context Understanding**: Beyond keyword matching
- **Relevance Ranking**: Advanced scoring algorithms
- **Real-time Indexing**: Dynamic content updates
- **Fuzzy Matching**: Handles typos and variations

**Languages Supported**: English, Spanish, French, German, Chinese, Japanese

### 🛡️ Fraud Analysis

- **Isolation Forest**: Anomaly detection for seller behavior
- **Feature Engineering**: Multi-dimensional risk factors
- **Risk Scoring**: Probabilistic fraud assessment
- **Pattern Recognition**: Historical trend analysis
- **Real-time Alerts**: Immediate threat detection

**Risk Factors**: Seller history, product patterns, pricing anomalies, image quality

### 🎨 Modern Interface

- **Responsive Design**: Mobile-first approach
- **Dark/Light Themes**: User preference support
- **Drag & Drop**: Intuitive file uploads
- **Real-time Updates**: Live status indicators
- **Progressive Enhancement**: Graceful degradation
- **Accessibility**: WCAG 2.1 compliant

**Browser Support**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

---

## 🔧 API Reference

### Core Endpoints

#### Duplicate Detection
```http
POST /dedup/image
Content-Type: multipart/form-data

{
  "file": <image_file>,
  "top_k": 5
}
```

#### Semantic Search
```http
POST /dedup/title
Content-Type: application/json

{
  "title": "wireless bluetooth headphones",
  "top_k": 10
}
```

#### Fraud Analysis
```http
POST /fraud/analyze
Content-Type: multipart/form-data

{
  "image": <image_file>,
  "seller_id": "seller_123",
  "price": 29.99
}
```

#### Health Check
```http
GET /health
```

### Response Format

```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "idx": 12345,
        "score": 0.94,
        "meta": {
          "title": "Product Name",
          "posting_id": "abc123"
        },
        "image_url": "http://api.domain.com/images/abc123.jpg"
      }
    ]
  },
  "timestamp": "2025-09-01T12:00:00Z"
}
```

---

## 🐳 Deployment

### Docker Deployment

```bash
# Production build
docker build -f backend/Dockerfile.prod -t marketplace-api:latest ./backend

# Multi-service deployment
docker-compose up --build

# Health check
curl http://localhost:8000/health
```

### Cloud Platforms

**AWS**, **Azure**, and **Google Cloud** ready with provided deployment configurations.

---

## 🛠️ Development

### Project Structure

```
marketplace-integrity-framework/
├── 📁 backend/                 # FastAPI application
│   ├── 📁 app/                # Application modules
│   │   ├── main.py           # API server
│   │   └── build_index.py    # Index building
│   ├── 📁 data/              # ML artifacts (ignored)
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Container definition
├── 📁 frontend/               # React application
│   ├── 📁 src/               # Source code
│   │   ├── 📁 components/    # React components
│   │   ├── 📁 hooks/         # Custom hooks
│   │   └── 📁 utils/         # Utility functions
│   ├── package.json         # Node dependencies
│   └── Dockerfile           # Container definition
├── 📁 dataset/               # Data files (ignored)
├── 📁 docs/                  # Documentation
├── 📁 .github/workflows/     # CI/CD pipelines
├── docker-compose.yml       # Multi-service config
└── README.md                # This file
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by the Marketplace Integrity Team

</div>