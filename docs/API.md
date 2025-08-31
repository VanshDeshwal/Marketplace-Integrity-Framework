# 🔧 API Reference

## Overview

The Marketplace Integrity Framework provides a comprehensive REST API for product analysis, duplicate detection, semantic search, and fraud analysis. All endpoints return JSON responses and support CORS for web applications.

## Base URL

```
Development: http://localhost:8000
Production: https://your-api-domain.com
```

## Authentication

Currently, the API does not require authentication. For production deployments, consider implementing:
- API Keys
- OAuth 2.0
- JWT tokens

## Rate Limiting

- **Development**: No limits
- **Production**: 1000 requests/hour per IP

---

## Endpoints

### Health Check

Check API availability and system status.

```http
GET /health
```

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2025-09-01T12:00:00Z",
  "version": "2.0.0",
  "models_loaded": {
    "image_model": true,
    "text_model": true,
    "fraud_model": true
  },
  "database": {
    "status": "connected",
    "records": 34252
  }
}
```

#### Status Codes

- `200` - API is healthy
- `503` - Service unavailable (models not loaded)

---

### Duplicate Detection

#### Image-based Duplicate Detection

Find visually similar products using image analysis.

```http
POST /dedup/image
Content-Type: multipart/form-data
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | ✅ | Image file (JPG, PNG, WebP, GIF) |
| `top_k` | Integer | ❌ | Number of results (default: 5, max: 50) |

#### Request Example

```bash
curl -X POST "http://localhost:8000/dedup/image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@product_image.jpg" \
  -F "top_k=10"
```

#### Response

```json
{
  "results": [
    {
      "idx": 12345,
      "score": 0.947,
      "meta": {
        "title": "Wireless Bluetooth Headphones",
        "posting_id": "abc123xyz",
        "seller_id": "seller_456"
      },
      "image_key": "1a2b3c4d5e.jpg",
      "image_url": "http://localhost:8000/images/train_images/1a2b3c4d5e.jpg"
    }
  ]
}
```

#### Status Codes

- `200` - Success
- `400` - Invalid file format or size
- `413` - File too large (>10MB)
- `422` - Missing required parameters

---

#### Text-based Duplicate Detection

Find similar products using title/description analysis.

```http
POST /dedup/title
Content-Type: application/json
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | String | ✅ | Product title or description |
| `top_k` | Integer | ❌ | Number of results (default: 5, max: 50) |

#### Request Example

```bash
curl -X POST "http://localhost:8000/dedup/title" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "wireless bluetooth headphones noise cancelling",
    "top_k": 10
  }'
```

#### Response

```json
{
  "results": [
    {
      "idx": 12345,
      "score": 0.892,
      "meta": {
        "title": "Wireless Bluetooth Headphones with Active Noise Cancellation",
        "posting_id": "def456ghi",
        "seller_id": "seller_789"
      },
      "image_key": "2b3c4d5e6f.jpg",
      "image_url": "http://localhost:8000/images/train_images/2b3c4d5e6f.jpg"
    }
  ]
}
```

---

#### Fused Duplicate Detection

Combine image and text analysis for enhanced accuracy.

```http
POST /dedup/fused
Content-Type: multipart/form-data
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | ✅ | Product image |
| `title` | String | ✅ | Product title/description |
| `top_k` | Integer | ❌ | Number of results (default: 5) |
| `alpha` | Float | ❌ | Image weight (0.0-1.0, default: 0.7) |

#### Request Example

```bash
curl -X POST "http://localhost:8000/dedup/fused" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@product.jpg" \
  -F "title=gaming mechanical keyboard rgb" \
  -F "top_k=5" \
  -F "alpha=0.8"
```

---

### Fraud Analysis

Analyze products for potential fraud indicators.

```http
POST /fraud/analyze
Content-Type: multipart/form-data
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image` | File | ✅ | Product image for analysis |
| `seller_id` | String | ❌ | Seller identifier |
| `price` | Float | ❌ | Product price |
| `category` | String | ❌ | Product category |

#### Request Example

```bash
curl -X POST "http://localhost:8000/fraud/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@suspicious_product.jpg" \
  -F "seller_id=seller_123" \
  -F "price=19.99" \
  -F "category=electronics"
```

#### Response

```json
{
  "risk_level": "medium",
  "fraud_score": 0.67,
  "confidence": 0.84,
  "analysis_details": {
    "image_quality": "low",
    "price_anomaly": true,
    "seller_history": "concerning",
    "pattern_match": "suspicious"
  },
  "recommendations": [
    "Manual review recommended",
    "Verify seller credentials",
    "Request additional product images"
  ]
}
```

#### Risk Levels

- **low** (0.0-0.3): Minimal fraud indicators
- **medium** (0.3-0.7): Some concerning patterns
- **high** (0.7-1.0): Strong fraud indicators

---

### Utility Endpoints

#### Get Random Sample Images

Retrieve random product images for testing.

```http
GET /random-images?count=6
```

#### Response

```json
{
  "images": [
    {
      "name": "product_001.jpg",
      "url": "http://localhost:8000/images/train_images/abc123.jpg"
    }
  ]
}
```

#### Storage Information

Get information about data storage configuration.

```http
GET /storage-info
```

#### Response

```json
{
  "storage_type": "local",
  "base_url": "http://localhost:8000",
  "blob_url": null,
  "dataset_path": "/app/dataset/shopee-product-matching"
}
```

#### Serve Images

Access product images directly.

```http
GET /images/{image_path}
```

Example: `GET /images/train_images/abc123.jpg`

---

## Error Handling

### Error Response Format

```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2025-09-01T12:00:00Z",
  "request_id": "req_123456"
}
```

### Common Error Codes

| Code | Description | Status |
|------|-------------|---------|
| `INVALID_FILE_FORMAT` | Unsupported image format | 400 |
| `FILE_TOO_LARGE` | File exceeds size limit | 413 |
| `MODEL_NOT_LOADED` | ML model unavailable | 503 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server error | 500 |

---

## SDKs and Libraries

### Python SDK

```python
import requests

class MarketplaceAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def detect_duplicates(self, image_path, top_k=5):
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'top_k': top_k}
            response = requests.post(
                f"{self.base_url}/dedup/image",
                files=files,
                data=data
            )
        return response.json()
    
    def semantic_search(self, title, top_k=10):
        payload = {"title": title, "top_k": top_k}
        response = requests.post(
            f"{self.base_url}/dedup/title",
            json=payload
        )
        return response.json()

# Usage
api = MarketplaceAPI()
results = api.detect_duplicates("product.jpg")
```

### JavaScript SDK

```javascript
class MarketplaceAPI {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async detectDuplicates(file, topK = 5) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('top_k', topK);

    const response = await fetch(`${this.baseUrl}/dedup/image`, {
      method: 'POST',
      body: formData
    });

    return response.json();
  }

  async semanticSearch(title, topK = 10) {
    const response = await fetch(`${this.baseUrl}/dedup/title`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ title, top_k: topK })
    });

    return response.json();
  }
}

// Usage
const api = new MarketplaceAPI();
const results = await api.detectDuplicates(fileInput.files[0]);
```

---

## Performance Guidelines

### Best Practices

1. **Image Optimization**
   - Resize images to 224x224 for faster processing
   - Use JPEG format for better compression
   - Limit file size to 2MB for optimal performance

2. **Batch Processing**
   - Process multiple items in parallel
   - Implement retry logic for failed requests
   - Use connection pooling for high-throughput scenarios

3. **Caching**
   - Cache duplicate detection results
   - Implement client-side result caching
   - Use CDN for static image assets

### Rate Limiting

- Implement exponential backoff for retries
- Monitor rate limit headers in responses
- Consider upgrading to higher tier for increased limits

---

## Changelog

### v2.0.0 (2025-09-01)
- ✅ Added fused duplicate detection
- ✅ Enhanced fraud analysis with ML models
- ✅ Improved error handling and validation
- ✅ Added CORS support for web applications
- ✅ Performance optimizations for large datasets

### v1.0.0 (2025-08-01)
- 🎉 Initial release
- ✅ Basic duplicate detection
- ✅ Semantic search functionality
- ✅ REST API foundation
