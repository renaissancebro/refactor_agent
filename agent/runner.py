# runner.py
import os
import ast
import json
from main_agent import assistant, user
from tools import extract_top_level_functions
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout
from datetime import datetime

BACKEND_FILE = "../backend/main.py"
PREVIEW_MODE = True


class CaptureUserOutput:
    def __enter__(self):
        self.buffer = StringIO()
        self._redirect = redirect_stdout(self.buffer)
        self._redirect.__enter__()
        return self

    def __exit__(self, *args):
        self._redirect.__exit__(*args)
        self.output = self.buffer.getvalue()


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
    log_data["runner_called"] = True

    # Save to JSON file with UTF-8 encoding and indentation
    with open(log_filename, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    print(f"📝 Refactor log saved: {log_filename}")


def run_refactor_agent():
    if not Path(BACKEND_FILE).exists():
        print(f"❌ Source file not found: {BACKEND_FILE}")
        return

    print(f"🔧 Refactoring: {BACKEND_FILE}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    with open(BACKEND_FILE, "r") as f:
        source_code = f.read()

    # Optional: local AST preview
    print("\n🔍 AST-extracted functions (local preview):")
    extracted = extract_top_level_functions(source_code)
    for name, code in extracted:
        print(f"\n📌 Function: {name}\n{code}\n")

    # Agent task
    task_message = f"""
    Analyze the following Python code. Identify reusable components (functions, classes)
    and extract them into appropriate utils modules (e.g., utils/io.py, utils/text.py).

    For each extracted component:
    - Provide the new filename and code
    - Modify the original code to import the extracted parts

    Output the final result as JSON with these exact keys:
    - 'refactored_main': The refactored version of the original file
    - 'backup_file': The old boilerplate logic to be saved to a separate file
    - 'utility_modules': Dictionary of extracted utility modules (filename -> code)

    Do NOT write any files — just return the JSON preview.

    Here's the code:
    ```python
    {source_code}
    ```
    """

    # Capture agent output
    with CaptureUserOutput() as cap:
        user.initiate_chat(assistant, message=task_message)

    print("\n🧠 Agent output preview:")
    output = cap.output

    try:
        # Extract JSON from the output
        json_start = output.find('```json')
        if json_start == -1:
            json_start = output.find('{')

        json_end = output.rfind('```')
        if json_end == -1:
            json_end = output.rfind('}') + 1

        json_str = output[json_start:json_end].replace('```json', '').replace('```', '').strip()
        preview_dict = json.loads(json_str)

    except Exception as e:
        print(f"⚠️ Could not parse structured preview: {e}")
        print("Raw output:")
        print(output)
        return

    # Display preview
    for filename, content in preview_dict.items():
        if filename == 'utility_modules':
            print(f"\n📄 {filename} Preview:")
            for util_name, util_content in content.items():
                print(f"\n{'='*40}")
                print(f"📁 {util_name}:")
                print(util_content)
        else:
            print(f"\n📄 {filename} Preview:\n{'='*40}\n{content}\n")

    # Log the refactor output
    log_refactor_output(preview_dict, Path(BACKEND_FILE), Path(__file__).parent)

    if not PREVIEW_MODE:
        # Write files directly to the backend directory
        print(f"\n💾 Writing files to backend directory...")

        # Write refactored main file
        if 'refactored_main' in preview_dict:
            with open(BACKEND_FILE, "w") as f:
                f.write(preview_dict['refactored_main'])
            print(f"✅ Refactored main file: {BACKEND_FILE}")

        # Write backup file
        if 'backup_file' in preview_dict:
            backup_file = Path(BACKEND_FILE).with_suffix('.backup')
            with open(backup_file, "w") as f:
                f.write(preview_dict['backup_file'])
            print(f"✅ Backup file: {backup_file}")

        # Write utility modules to utils directory
        if 'utility_modules' in preview_dict:
            utils_dir = Path(BACKEND_FILE).parent / "utils"
            utils_dir.mkdir(exist_ok=True)

            for util_name, util_content in preview_dict['utility_modules'].items():
                # Remove 'utils/' prefix if present
                clean_name = util_name.replace('utils/', '')
                util_file = utils_dir / clean_name
                with open(util_file, "w") as f:
                    f.write(util_content)
                print(f"✅ Utility module: {util_file}")

        print(f"\n🎉 Refactoring complete!")
    else:
        print("\n✋ Preview only — no files were written.")
        print("💡 To accept these changes, run the same command with PREVIEW_MODE = False")

        # Ask user if they want to accept the preview
        try:
            accept = input("\n🤔 Would you like to accept these changes? (y/N): ").strip().lower()
            if accept in ['y', 'yes']:
                print(f"\n💾 Writing files to backend directory...")

                # Write refactored main file
                if 'refactored_main' in preview_dict:
                    with open(BACKEND_FILE, "w") as f:
                        f.write(preview_dict['refactored_main'])
                    print(f"✅ Refactored main file: {BACKEND_FILE}")

                # Write backup file
                if 'backup_file' in preview_dict:
                    backup_file = Path(BACKEND_FILE).with_suffix('.backup')
                    with open(backup_file, "w") as f:
                        f.write(preview_dict['backup_file'])
                    print(f"✅ Backup file: {backup_file}")

                # Write utility modules to utils directory
                if 'utility_modules' in preview_dict:
                    utils_dir = Path(BACKEND_FILE).parent / "utils"
                    utils_dir.mkdir(exist_ok=True)

                    for util_name, util_content in preview_dict['utility_modules'].items():
                        # Remove 'utils/' prefix if present
                        clean_name = util_name.replace('utils/', '')
                        util_file = utils_dir / clean_name
                        with open(util_file, "w") as f:
                            f.write(util_content)
                        print(f"✅ Utility module: {util_file}")

                print(f"\n🎉 Changes accepted!")
            else:
                print("❌ Changes not applied.")
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user.")
        except Exception as e:
            print(f"❌ Error applying changes: {e}")


if __name__ == "__main__":
    run_refactor_agent()
