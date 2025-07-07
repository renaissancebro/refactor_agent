#!/usr/bin/env python3
"""
Simple test to demonstrate the refactor agent functionality
"""

import sys
import os
import json
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout

# Add the parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))
sys.path.append(str(parent_dir / "agent"))

# Import the existing refactor functionality
from main_agent import assistant, user
from refactor_cli import get_suggestion_prompt

def test_refactor_agent():
    """Test the refactor agent directly"""
    print("🧪 Testing Refactor Agent API Functionality")
    print("=" * 50)
    
    # Test code snippet - a simple example
    test_code = '''def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def calculate_interest(principal, rate, time):
    return principal * rate * time

def calculate_compound_interest(principal, rate, time, compounds_per_year):
    return principal * (1 + rate / compounds_per_year) ** (compounds_per_year * time)'''
    
    print("📝 Original Code:")
    print(test_code)
    print("\n" + "=" * 50)
    
    try:
        # Get suggestion prompt
        suggestion_prompt = get_suggestion_prompt("refactor")
        
        # Prepare message
        message = f"""
        {suggestion_prompt}

        Return the structured JSON output with these exact keys:
        - 'refactored_main': The improved version of the original file
        - 'backup_file': The old code to be saved to a separate file
        - 'utility_modules': Dictionary of extracted utility modules (filename -> code)

        Code to improve:
        ```python
        {test_code}
        ```
        """
        
        print("🔄 Sending to refactor agent...")
        
        # Capture stdout to get the agent's response
        output_buffer = StringIO()
        with redirect_stdout(output_buffer):
            user.initiate_chat(assistant, message=message)
        
        # Get the captured output
        captured_output = output_buffer.getvalue()
        
        print("\n📤 Raw Agent Response:")
        print(captured_output)
        
        # Parse the JSON response
        json_start = captured_output.find('```json')
        if json_start == -1:
            json_start = captured_output.find('{')
        
        json_end = captured_output.rfind('```')
        if json_end == -1:
            json_end = captured_output.rfind('}') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = captured_output[json_start:json_end].replace('```json', '').replace('```', '').strip()
            try:
                parsed_response = json.loads(json_str)
                
                print("\n✅ Parsed API Response:")
                print(json.dumps(parsed_response, indent=2))
                
                print("\n📄 Refactored Main Code:")
                print(parsed_response.get('refactored_main', 'No main code returned'))
                
                if 'utility_modules' in parsed_response:
                    print("\n📁 Utility Modules:")
                    for filename, content in parsed_response['utility_modules'].items():
                        print(f"\n--- {filename} ---")
                        print(content)
                
                return parsed_response
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Raw JSON string: {json_str}")
                return None
        else:
            print("❌ No JSON block found in response")
            return None
            
    except Exception as e:
        print(f"❌ Error during refactoring: {e}")
        import traceback
        traceback.print_exc()
        return None

def show_api_example():
    """Show what the API request/response would look like"""
    print("\n🔗 API Request/Response Example")
    print("=" * 40)
    
    # What the API request would look like
    print("📥 API Request:")
    request_example = {
        "code": "def add(a, b): return a + b\ndef multiply(a, b): return a * b",
        "suggestion_type": "refactor",
        "language": "python"
    }
    print(json.dumps(request_example, indent=2))
    
    # What the API response would look like
    print("\n📤 API Response:")
    response_example = {
        "success": True,
        "refactored_main": "# Main application logic\nfrom utils.math_operations import add, multiply\n\n# Your main code here",
        "utility_modules": {
            "utils/math_operations.py": "def add(a, b):\n    return a + b\n\ndef multiply(a, b):\n    return a * b"
        },
        "backup_file": "# Original code backup\ndef add(a, b): return a + b\ndef multiply(a, b): return a * b",
        "message": "Code refactored successfully",
        "usage_count": 1,
        "session_id": "12345-abcde-67890"
    }
    print(json.dumps(response_example, indent=2))

if __name__ == "__main__":
    print("🚀 Refactor Agent API Test")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    print("✅ OpenAI API Key is configured")
    
    # Run the test
    result = test_refactor_agent()
    
    # Show API example
    show_api_example()
    
    print("\n🎉 Test completed!")