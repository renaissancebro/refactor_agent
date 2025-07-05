#!/usr/bin/env python3
"""
Test script to demonstrate the directory structure with before/after/utils
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout

sys.path.append('agent')

from main_agent import assistant, user

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
        # Capture stdout to get the agent's response
        output_buffer = StringIO()
        with redirect_stdout(output_buffer):
            user.initiate_chat(assistant, message=message)

        # Get the captured output
        captured_output = output_buffer.getvalue()
        print(f"\n📝 Captured output length: {len(captured_output)} characters")

        # Parse the JSON response from the markdown block
        try:
            # Find the JSON block in the markdown
            json_start = captured_output.find('```json')
            if json_start == -1:
                json_start = captured_output.find('{')

            json_end = captured_output.rfind('```')
            if json_end == -1:
                json_end = captured_output.rfind('}') + 1

            if json_start != -1 and json_end != -1:
                json_str = captured_output[json_start:json_end].replace('```json', '').replace('```', '').strip()
                parsed_response = json.loads(json_str)

                print("\n✅ Successfully parsed LLM response as dictionary:")
                print(f"📊 Response keys: {list(parsed_response.keys())}")

                # Display the parsed content
                for key, value in parsed_response.items():
                    if key == 'utility_modules':
                        print(f"\n📁 {key}:")
                        for util_name, util_content in value.items():
                            print(f"   - {util_name}: {len(util_content)} characters")
                    else:
                        print(f"\n📄 {key}: {len(value)} characters")

                return parsed_response
            else:
                print("⚠️ No JSON block found in the response")
                print("Raw output preview:")
                print(captured_output[:500] + "..." if len(captured_output) > 500 else captured_output)

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print("Raw output preview:")
            print(captured_output[:500] + "..." if len(captured_output) > 500 else captured_output)

        print(f"\n✅ Test completed! Check the directory structure.")
        print(f"📂 Directory: {refactor_dir}")
        print("   ├── before/ (original files)")
        print("   ├── after/ (refactored main files)")
        print("   └── utils/ (extracted utility modules)")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    test_directory_structure()
