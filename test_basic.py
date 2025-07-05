#!/usr/bin/env python3
"""
Basic test script for the refactor agent - minimal API usage
"""

import os
import sys
sys.path.append('agent')

from main_agent import assistant, user

def test_basic_response():
    """Test if the agent can respond to a simple message"""

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return

    print("🧪 Testing basic agent response...")

    # Simple test message
    test_message = "Hello! Can you confirm you're working? Just respond with 'Yes, I'm working' and stop."

    try:
        # Use a simple chat initiation with minimal back-and-forth
        user.initiate_chat(
            assistant,
            message=test_message,
            max_turns=1  # Only allow 1 turn to prevent loops
        )
        print("\n✅ Basic test completed!")

    except Exception as e:
        print(f"\n❌ Basic test failed: {e}")

if __name__ == "__main__":
    test_basic_response()
