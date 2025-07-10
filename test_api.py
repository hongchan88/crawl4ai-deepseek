#!/usr/bin/env python3
"""
Test script for the Crawl4AI API
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
DEEPSEEK_API_KEY = ""  # Replace with your actual key
TEST_URL = "https://www.statnews.com/2025/07/08/fda-staff-morale-departures-rfk-jr-sued-covid-shots-hospital-lobbying-trump-tax-cut-bill-dc-diagnosis-newsletter/"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
    
    print()

def test_extract_content():
    """Test the content extraction endpoint"""
    print("🔍 Testing content extraction endpoint...")
    
    payload = {
        "url": TEST_URL,
        "deepseek_api_key": DEEPSEEK_API_KEY
    }
    
    try:
        print(f"   Extracting content from: {TEST_URL}")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/extract",
            json=payload,
            timeout=60  # Give it 60 seconds
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Content extraction successful")
            print(f"   Processing time: {result.get('processing_time', 'N/A'):.2f}s")
            print(f"   Request time: {end_time - start_time:.2f}s")
            
            if result.get('success'):
                print(f"   Content length: {len(result.get('content', ''))} characters")
                print(f"   Images found: {len(result.get('main_content_image_urls', []))}")
                print(f"   Markdown length: {len(result.get('markdown', ''))} characters")
                
                # Print first 200 characters of content
                content = result.get('content', '')
                if content:
                    print(f"   Content preview: {content[:200]}...")
                
                # Print image URLs
                images = result.get('main_content_image_urls', [])
                if images:
                    print("   Image URLs:")
                    for img in images:
                        print(f"     - {img}")
            else:
                print(f"❌ Extraction failed: {result.get('error_message', 'Unknown error')}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print()

def test_invalid_url():
    """Test with an invalid URL"""
    print("🔍 Testing with invalid URL...")
    
    payload = {
        "url": "not-a-valid-url",
        "deepseek_api_key": DEEPSEEK_API_KEY
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/extract",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 422:
            print("✅ Invalid URL properly rejected")
        else:
            print(f"❌ Expected 422, got {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print()

def test_missing_api_key():
    """Test with missing API key"""
    print("🔍 Testing with missing API key...")
    
    payload = {
        "url": TEST_URL
        # No API key provided
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/extract",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Missing API key properly rejected")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print()

def main():
    print("🚀 Starting API tests...")
    print(f"API Base URL: {API_BASE_URL}")
    print("=" * 50)
    
    # Run tests
    test_health_check()
    test_extract_content()
    test_invalid_url()
    test_missing_api_key()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 