#!/usr/bin/env python3
"""
Simple test script for the refactor agent
"""

import os
import sys
sys.path.append('agent')

from main_agent import assistant, user

def test_simple_refactor():
    """Test the refactor agent with a simple code snippet"""

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return

    # Simple code to refactor
    test_code = '''
def add_numbers(a, b):
    return a + b

def multiply_numbers(a, b):
    return a * b

def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total

def main():
    result1 = add_numbers(5, 3)
    result2 = multiply_numbers(4, 2)
    result3 = calculate_total([1, 2, 3, 4, 5])
    print(f"Results: {result1}, {result2}, {result3}")

if __name__ == "__main__":
    main()
'''

    print("🧪 Testing Refactor Agent...")
    print("📝 Input code:")
    print(test_code)
    print("\n" + "="*50)

    # Send to agent
    message = f"""
    Please refactor this simple Python code according to your instructions.
    Extract reusable components and return the structured output as JSON.

    Code to refactor:
    ```python
    {test_code}
    ```
    """

    try:
        # Set a timeout for the conversation
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Conversation timed out after 60 seconds")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(60)  # 60 second timeout

        user.initiate_chat(assistant, message=message)
        signal.alarm(0)  # Cancel the alarm
        print("\n✅ Test completed successfully!")
    except TimeoutError:
        print("\n⏰ Test timed out - conversation took too long")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    test_simple_refactor()
