#!/usr/bin/env python3
"""
CLI tool for refactoring any file in place using the refactor agent.
Usage: python refactor_cli.py [file_path] [options]
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout

# Add the agent directory to path
current_dir = Path(__file__).parent
agent_dir = current_dir / "agent"
sys.path.append(str(agent_dir))

from main_agent import assistant, user

def log_refactor_output(preview_dict: dict, original_file: Path, refactor_dir: Path):
    """
    Log the refactor output to a JSON file for tracking and debugging.

    Args:
        preview_dict: Dictionary containing the agent's refactor response
        original_file: Path to the original file that was refactored
        refactor_dir: Path to the refactor agent directory
    """
    # Create refactor_logs directory if it doesn't exist
    logs_dir = refactor_dir / "refactor_logs"
    logs_dir.mkdir(exist_ok=True)

    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    log_filename = logs_dir / f"{timestamp}.json"

    # Add metadata to the dictionary
    log_data = preview_dict.copy()
    log_data["original_file"] = str(original_file.absolute())
    log_data["refactor_timestamp"] = timestamp
    log_data["cli_called"] = True

    # Save to JSON file with UTF-8 encoding and indentation
    with open(log_filename, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    print(f"📝 Refactor log saved: {log_filename}")

def get_suggestion_prompt(suggestion_type: str) -> str:
    """
    Get the appropriate prompt based on suggestion type.

    Args:
        suggestion_type: Type of suggestion (refactor, optimize, document, style, security)

    Returns:
        Formatted prompt string
    """
    prompts = {
        "refactor": "Refactor this Python code by extracting reusable components into utility modules. Focus on code organization and modularity.",
        "optimize": "Optimize this Python code for performance, efficiency, and best practices. Suggest improvements for speed, memory usage, and algorithm efficiency.",
        "document": "Add comprehensive documentation to this Python code. Include docstrings, comments, and type hints to improve code readability and maintainability.",
        "style": "Improve the code style and formatting according to PEP 8 standards. Focus on naming conventions, spacing, and overall code aesthetics.",
        "security": "Review this Python code for security vulnerabilities and suggest improvements. Focus on input validation, error handling, and secure coding practices."
    }

    return prompts.get(suggestion_type, prompts["refactor"])

def refactor_file(file_path: str, suggestion_type: str = "refactor", preview_only: bool = False, backup: bool = True):
    """
    Refactor a single file in place.

    Args:
        file_path: Path to the file to refactor
        suggestion_type: Type of suggestion (refactor, optimize, document, style, security)
        preview_only: If True, only show preview without applying changes
        backup: If True, create a backup of the original file
    """
    # Convert to Path object
    file_path = Path(file_path)

    # Check if file exists
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return False

    print(f"🔧 {suggestion_type.title()}ing: {file_path}")

    # Read the original file
    with open(file_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    # Create backup if requested
    if backup:
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original_content)
        print(f"💾 Backup created: {backup_path}")

    # Get suggestion prompt
    suggestion_prompt = get_suggestion_prompt(suggestion_type)

    # Send to agent
    message = f"""
    {suggestion_prompt}

    Return the structured JSON output with these exact keys:
    - 'refactored_main': The improved version of the original file
    - 'backup_file': The old code to be saved to a separate file
    - 'utility_modules': Dictionary of extracted utility modules (filename -> code)

    Code to improve:
    ```python
    {original_content}
    ```
    """

    try:
        # Capture stdout to get the agent's response
        output_buffer = StringIO()
        with redirect_stdout(output_buffer):
            user.initiate_chat(assistant, message=message)

        # Get the captured output
        captured_output = output_buffer.getvalue()

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

                print("\n✅ Successfully parsed LLM response")

                # Show preview
                if 'refactored_main' in parsed_response:
                    print(f"\n📄 Improved main file ({len(parsed_response['refactored_main'])} characters):")
                    print("=" * 50)
                    print(parsed_response['refactored_main'])
                    print("=" * 50)

                if 'utility_modules' in parsed_response:
                    print(f"\n📁 Utility modules:")
                    for util_name, util_content in parsed_response['utility_modules'].items():
                        print(f"   - {util_name}: {len(util_content)} characters")

                # Apply changes immediately by default, or ask for confirmation if preview mode
                if preview_only:
                    print("\n✋ Preview only - no changes applied.")
                    return True
                else:
                    # Apply the changes immediately
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(parsed_response['refactored_main'])
                    print(f"✅ Changes applied to: {file_path}")

                    # Log the refactor
                    log_refactor_output(parsed_response, file_path, current_dir)

                    # Create utility files in the same directory
                    if 'utility_modules' in parsed_response:
                        utils_dir = file_path.parent / "utils"
                        utils_dir.mkdir(exist_ok=True)

                        for util_name, util_content in parsed_response['utility_modules'].items():
                            # Remove 'utils/' prefix if present
                            clean_name = util_name.replace('utils/', '')
                            util_file = utils_dir / clean_name
                            with open(util_file, "w", encoding="utf-8") as f:
                                f.write(util_content)
                            print(f"✅ Utility module: {util_file}")

                    return True
            else:
                print("⚠️ No JSON block found in the response")
                return False

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            return False

    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Improve Python files using AI agent")
    parser.add_argument("file", help="Path to the Python file to improve")
    parser.add_argument("--type", "-t", choices=["refactor", "optimize", "document", "style", "security"],
                       default="refactor", help="Type of improvement to apply (default: refactor)")
    parser.add_argument("--preview", "-p", action="store_true",
                       help="Show preview only, don't apply changes")
    parser.add_argument("--no-backup", action="store_true",
                       help="Don't create a backup of the original file")

    args = parser.parse_args()

    # Run the refactor
    success = refactor_file(
        file_path=args.file,
        suggestion_type=args.type,
        preview_only=args.preview,
        backup=not args.no_backup
    )

    if success:
        print("\n🎉 Operation completed successfully!")
    else:
        print("\n❌ Operation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
