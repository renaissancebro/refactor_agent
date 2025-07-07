#!/usr/bin/env python3
"""
Test script to demonstrate the Refactor Agent API functionality
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add the parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))
sys.path.append(str(parent_dir / "agent"))

# Import our API modules
from api.main import app, api_keys, generate_api_key, refactor_code_async
from main_agent import assistant, user

def simulate_api_key_creation():
    """Simulate creating an API key for testing"""
    api_key = generate_api_key()
    api_keys[api_key] = {
        "credits": 5,
        "total_requests": 0,
        "created_at": datetime.now(),
        "status": "active"
    }
    return api_key

async def test_refactor_code():
    """Test the refactor functionality directly"""
    print("🧪 Testing Refactor Agent API")
    print("=" * 50)
    
    # Test code snippet
    test_code = '''
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total

def apply_discount(total, discount_percent):
    return total * (1 - discount_percent / 100)

def calculate_tax(total, tax_rate):
    return total * tax_rate

def process_order(items, discount_percent=0, tax_rate=0.08):
    subtotal = calculate_total(items)
    discounted_total = apply_discount(subtotal, discount_percent)
    tax_amount = calculate_tax(discounted_total, tax_rate)
    final_total = discounted_total + tax_amount
    return {
        'subtotal': subtotal,
        'discount': subtotal - discounted_total,
        'tax': tax_amount,
        'total': final_total
    }
'''
    
    print("📝 Original Code:")
    print(test_code)
    print("\n" + "=" * 50)
    
    try:
        # Test the refactor function
        print("🔄 Refactoring code...")
        result = await refactor_code_async(test_code, "refactor")
        
        print("\n✅ API Response:")
        print(json.dumps(result, indent=2))
        
        print("\n📄 Refactored Main Code:")
        print(result.get('refactored_main', 'No main code returned'))
        
        if 'utility_modules' in result:
            print("\n📁 Utility Modules:")
            for filename, content in result['utility_modules'].items():
                print(f"\n--- {filename} ---")
                print(content)
        
        return result
        
    except Exception as e:
        print(f"❌ Error during refactoring: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_api_key_management():
    """Test API key creation and management"""
    print("\n🔑 Testing API Key Management")
    print("=" * 30)
    
    # Create test API key
    api_key = simulate_api_key_creation()
    print(f"✅ Generated API Key: {api_key}")
    
    # Check key info
    key_info = api_keys[api_key]
    print(f"📊 Key Info: {json.dumps(key_info, default=str, indent=2)}")
    
    return api_key

def demonstrate_full_api_flow():
    """Demonstrate the complete API flow"""
    print("\n🔄 Complete API Flow Demonstration")
    print("=" * 40)
    
    # Step 1: Create API key
    api_key = test_api_key_management()
    
    # Step 2: Show what a payment request would look like
    print("\n💳 Payment Request Example:")
    payment_request = {
        "amount": 500,  # $5.00
        "currency": "usd",
        "description": "Refactor Agent API Credits"
    }
    print(json.dumps(payment_request, indent=2))
    
    # Step 3: Show what a refactor request would look like
    print("\n🔧 Refactor Request Example:")
    refactor_request = {
        "code": "def add(a, b): return a + b\ndef multiply(a, b): return a * b",
        "suggestion_type": "refactor",
        "language": "python"
    }
    print(json.dumps(refactor_request, indent=2))
    
    # Step 4: Show usage tracking
    print("\n📈 Usage Tracking:")
    usage_info = {
        "api_key": api_key,
        "total_requests": api_keys[api_key]["total_requests"],
        "remaining_credits": api_keys[api_key]["credits"],
        "created_at": api_keys[api_key]["created_at"].isoformat()
    }
    print(json.dumps(usage_info, indent=2))

if __name__ == "__main__":
    import asyncio
    
    print("🚀 Refactor Agent API Test Suite")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    print("✅ OpenAI API Key is configured")
    
    # Run async test
    asyncio.run(test_refactor_code())
    
    # Run sync tests
    demonstrate_full_api_flow()
    
    print("\n🎉 Test completed!")