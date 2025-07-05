#!/usr/bin/env python3
"""
Test script to demonstrate the directory structure with before/after/utils
"""

import os
import sys
sys.path.append('agent')

from main_agent import assistant, user
from datetime import datetime
from pathlib import Path

def test_directory_structure():
    """Test the refactor agent with directory structure"""

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return

    # Create timestamped directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    refactor_dir = Path(f"test_refactor_{timestamp}")
    refactor_dir.mkdir(exist_ok=True)

    before_dir = refactor_dir / "before"
    after_dir = refactor_dir / "after"
    utils_dir = refactor_dir / "utils"

    before_dir.mkdir(exist_ok=True)
    after_dir.mkdir(exist_ok=True)
    utils_dir.mkdir(exist_ok=True)

    print(f"📁 Created test directories: {refactor_dir}")
    print(f"⏰ Timestamp: {timestamp}")

    # Test code
    test_code = '''
def process_data(data_list):
    """Process a list of data items"""
    results = []
    for item in data_list:
        processed = item * 2
        results.append(processed)
    return results

def validate_input(value):
    """Validate input value"""
    if not isinstance(value, (int, float)):
        return False
    return value > 0

def format_output(result):
    """Format output for display"""
    return f"Result: {result}"

def main():
    data = [1, 2, 3, 4, 5]
    processed = process_data(data)

    for item in processed:
        if validate_input(item):
            print(format_output(item))

if __name__ == "__main__":
    main()
'''

    # Save original to before directory
    original_file = before_dir / "test_main.py"
    with open(original_file, "w") as f:
        f.write(test_code)
    print(f"💾 Saved original file: {original_file}")

    print("\n🧪 Testing refactor with directory structure...")

    # Send to agent
    message = f"""
    Please refactor this Python code and return the structured JSON output.
    Extract reusable components into utility modules.

    Code to refactor:
    ```python
    {test_code}
    ```
    """

    try:
        user.initiate_chat(assistant, message=message)
        print("\n✅ Test completed! Check the directory structure.")
        print(f"📂 Directory: {refactor_dir}")
        print("   ├── before/ (original files)")
        print("   ├── after/ (refactored main files)")
        print("   └── utils/ (extracted utility modules)")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    test_directory_structure()
