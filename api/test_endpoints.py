#!/usr/bin/env python3
"""
Test the API endpoints to show what they return
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://127.0.0.1:8000"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🏥 Testing Health Endpoint")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_pricing_endpoint():
    """Test the pricing endpoint"""
    print("\n💰 Testing Pricing Endpoint")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/pricing", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Pricing check failed: {e}")
        return False

def test_payment_endpoint():
    """Test the payment intent creation"""
    print("\n💳 Testing Payment Intent Creation")
    print("=" * 40)
    
    try:
        payload = {
            "amount": 500,
            "currency": "usd",
            "description": "Test purchase"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/payment/create-intent",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Request: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Payment test failed: {e}")
        return False

def test_refactor_endpoint_without_auth():
    """Test the refactor endpoint without authentication"""
    print("\n🔧 Testing Refactor Endpoint (No Auth)")
    print("=" * 40)
    
    try:
        payload = {
            "code": "def hello(): print('Hello World')",
            "suggestion_type": "refactor",
            "language": "python"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/refactor",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Request: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Should return 401 or 403 for missing auth
        return response.status_code in [401, 403]
        
    except Exception as e:
        print(f"❌ Refactor test failed: {e}")
        return False

def test_with_mock_api_key():
    """Test endpoints with a mock API key"""
    print("\n🔑 Testing with Mock API Key")
    print("=" * 30)
    
    # First, simulate creating an API key
    mock_api_key = "rfa_test_key_12345"
    
    # Test usage endpoint with mock key
    try:
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/usage",
            headers=headers,
            timeout=5
        )
        
        print(f"Usage endpoint - Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Should return 401 for invalid key
        return response.status_code == 401
        
    except Exception as e:
        print(f"❌ Mock key test failed: {e}")
        return False

def show_expected_responses():
    """Show what successful responses would look like"""
    print("\n📋 Expected Successful Responses")
    print("=" * 40)
    
    print("✅ Health Check Response:")
    health_response = {
        "status": "healthy",
        "timestamp": "2024-01-01T12:00:00.000000",
        "version": "1.0.0",
        "openai_configured": True,
        "stripe_configured": False
    }
    print(json.dumps(health_response, indent=2))
    
    print("\n💰 Pricing Response:")
    pricing_response = {
        "plans": {
            "starter": {
                "price": 500,
                "credits": 5,
                "description": "5 refactor requests"
            },
            "professional": {
                "price": 2000,
                "credits": 25,
                "description": "25 refactor requests"
            },
            "enterprise": {
                "price": 5000,
                "credits": 75,
                "description": "75 refactor requests"
            }
        },
        "currency": "usd",
        "note": "Prices are in cents. 1 credit = 1 refactor request"
    }
    print(json.dumps(pricing_response, indent=2))
    
    print("\n🔧 Successful Refactor Response:")
    refactor_response = {
        "success": True,
        "refactored_main": "from utils.helpers import helper_function\n\ndef main():\n    return helper_function()",
        "utility_modules": {
            "utils/helpers.py": "def helper_function():\n    return 'Hello, World!'"
        },
        "backup_file": "def main():\n    return 'Hello, World!'",
        "message": "Code refactored successfully",
        "usage_count": 1,
        "session_id": "abc123-def456"
    }
    print(json.dumps(refactor_response, indent=2))

def main():
    """Run all tests"""
    print("🧪 API Endpoint Testing Suite")
    print("=" * 50)
    
    # Note: These tests will likely fail because the server isn't running
    # but they show what the API calls would look like
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Pricing", test_pricing_endpoint),
        ("Payment Intent", test_payment_endpoint),
        ("Refactor (No Auth)", test_refactor_endpoint_without_auth),
        ("Mock API Key", test_with_mock_api_key),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    # Show expected responses
    show_expected_responses()
    
    print("\n📝 Note: Tests may fail if server is not running.")
    print("To start server: uvicorn main:app --host 127.0.0.1 --port 8000")

if __name__ == "__main__":
    main()