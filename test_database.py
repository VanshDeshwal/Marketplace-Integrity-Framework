#!/usr/bin/env python3
"""
Quick test script for the Marketplace Integrity Framework
Tests all major database and API functionality
"""

import requests
import os
import json
import time

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ API Health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Health: {e}")
        return False

def test_storage_info():
    """Test storage information endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/storage-info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Storage Type: {data['storage_type']}")
            print(f"   Blob URL: {data.get('blob_url', 'None')}")
            return True
        else:
            print(f"❌ Storage Info: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Storage Info: {e}")
        return False

def test_random_images():
    """Test random images endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/random-images?count=3", timeout=10)
        if response.status_code == 200:
            data = response.json()
            images = data.get('images', [])
            print(f"✅ Random Images: {len(images)} images retrieved")
            for i, img in enumerate(images[:2]):  # Show first 2
                print(f"   Image {i+1}: {img.get('name', 'Unknown')} - {img.get('path', 'No path')}")
            return True
        else:
            print(f"❌ Random Images: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Random Images: {e}")
        return False

def test_image_serving():
    """Test image serving endpoint"""
    try:
        # First get a random image to test
        response = requests.get(f"{BASE_URL}/random-images?count=1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            images = data.get('images', [])
            if images:
                image_path = images[0].get('path', '')
                if image_path:
                    img_response = requests.get(f"{BASE_URL}/images/{image_path}", timeout=10)
                    if img_response.status_code == 200:
                        print(f"✅ Image Serving: Successfully served {image_path}")
                        print(f"   Content Type: {img_response.headers.get('content-type', 'Unknown')}")
                        print(f"   Size: {len(img_response.content)} bytes")
                        return True
                    else:
                        print(f"❌ Image Serving: HTTP {img_response.status_code} for {image_path}")
                        return False
        print("❌ Image Serving: No images to test")
        return False
    except Exception as e:
        print(f"❌ Image Serving: {e}")
        return False

def test_search():
    """Test text search functionality"""
    try:
        payload = {"query": "laptop computer", "limit": 3}
        response = requests.post(f"{BASE_URL}/search", 
                               json=payload, 
                               headers={"Content-Type": "application/json"},
                               timeout=15)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✅ Search: {len(results)} results for 'laptop computer'")
            for i, result in enumerate(results[:2]):  # Show first 2
                print(f"   Result {i+1}: {result.get('title', 'No title')[:50]}...")
            return True
        else:
            print(f"❌ Search: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Search: {e}")
        return False

def test_database_integrity():
    """Test database file integrity"""
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    artifact_dir = os.path.join(backend_dir, 'data', 'siamese_artifacts')
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset', 'shopee-product-matching'))
    
    files_to_check = [
        (os.path.join(artifact_dir, 'meta.csv'), 'Metadata CSV'),
        (os.path.join(artifact_dir, 'text_embs.npy'), 'Text Embeddings'),
        (os.path.join(artifact_dir, 'image_embs.npy'), 'Image Embeddings'),
        (os.path.join(artifact_dir, 'faiss_text.index'), 'Text FAISS Index'),
        (os.path.join(artifact_dir, 'faiss_image.index'), 'Image FAISS Index'),
        (os.path.join(dataset_dir, 'train_images'), 'Training Images Directory'),
    ]
    
    all_good = True
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                count = len([f for f in os.listdir(file_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                print(f"✅ {description}: {count} images")
            else:
                size = os.path.getsize(file_path)
                print(f"✅ {description}: {size:,} bytes")
        else:
            print(f"❌ {description}: Not found at {file_path}")
            all_good = False
    
    return all_good

def main():
    print("🧪 Testing Marketplace Integrity Framework Database Functionality")
    print("=" * 70)
    
    # Test database files
    print("\n📁 Database Integrity Check:")
    db_ok = test_database_integrity()
    
    # Test API
    print("\n🌐 API Tests:")
    api_ok = test_api_health()
    
    if not api_ok:
        print("\n❌ API is not running. Please start the backend with:")
        print("   cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Wait a moment for API to fully initialize
    time.sleep(1)
    
    storage_ok = test_storage_info()
    images_ok = test_random_images()
    serving_ok = test_image_serving()
    search_ok = test_search()
    
    print("\n📊 Test Summary:")
    print(f"   Database Files: {'✅' if db_ok else '❌'}")
    print(f"   API Health: {'✅' if api_ok else '❌'}")
    print(f"   Storage Info: {'✅' if storage_ok else '❌'}")
    print(f"   Random Images: {'✅' if images_ok else '❌'}")
    print(f"   Image Serving: {'✅' if serving_ok else '❌'}")
    print(f"   Search: {'✅' if search_ok else '❌'}")
    
    total_tests = 6
    passed_tests = sum([db_ok, api_ok, storage_ok, images_ok, serving_ok, search_ok])
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your database system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
