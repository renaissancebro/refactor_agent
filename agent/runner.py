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
import shutil

BACKEND_FILE = "../backend/main.py"
PREVIEW_MODE = False


class CaptureUserOutput:
    def __enter__(self):
        self.buffer = StringIO()
        self._redirect = redirect_stdout(self.buffer)
        self._redirect.__enter__()
        return self

    def __exit__(self, *args):
        self._redirect.__exit__(*args)
        self.output = self.buffer.getvalue()


def create_timestamped_directories():
    """Create before/after directories with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create main refactor directory
    refactor_dir = Path(f"refactor_output_{timestamp}")
    refactor_dir.mkdir(exist_ok=True)

    # Create subdirectories
    before_dir = refactor_dir / "before"
    after_dir = refactor_dir / "after"
    utils_dir = refactor_dir / "utils"

    before_dir.mkdir(exist_ok=True)
    after_dir.mkdir(exist_ok=True)
    utils_dir.mkdir(exist_ok=True)

    return refactor_dir, before_dir, after_dir, utils_dir, timestamp


def run_refactor_agent():
    if not Path(BACKEND_FILE).exists():
        print(f"❌ Source file not found: {BACKEND_FILE}")
        return

    # Create timestamped directories
    refactor_dir, before_dir, after_dir, utils_dir, timestamp = create_timestamped_directories()

    print(f"📁 Created refactor directories: {refactor_dir}")
    print(f"⏰ Timestamp: {timestamp}")

    with open(BACKEND_FILE, "r") as f:
        source_code = f.read()

    # Save original file to before directory
    original_filename = Path(BACKEND_FILE).name
    before_file = before_dir / original_filename
    with open(before_file, "w") as f:
        f.write(source_code)
    print(f"💾 Saved original file to: {before_file}")

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

    if not PREVIEW_MODE:
        # Write files to appropriate directories
        print(f"\n💾 Writing files to {refactor_dir}...")

        # Write refactored main file to after directory
        if 'refactored_main' in preview_dict:
            after_file = after_dir / original_filename
            with open(after_file, "w") as f:
                f.write(preview_dict['refactored_main'])
            print(f"✅ Refactored main file: {after_file}")

        # Write backup file to before directory
        if 'backup_file' in preview_dict:
            backup_file = before_dir / f"{Path(original_filename).stem}_backup.py"
            with open(backup_file, "w") as f:
                f.write(preview_dict['backup_file'])
            print(f"✅ Backup file: {backup_file}")

        # Write utility modules to utils directory
        if 'utility_modules' in preview_dict:
            for util_name, util_content in preview_dict['utility_modules'].items():
                # Remove 'utils/' prefix if present
                clean_name = util_name.replace('utils/', '')
                util_file = utils_dir / clean_name
                with open(util_file, "w") as f:
                    f.write(util_content)
                print(f"✅ Utility module: {util_file}")

        print(f"\n🎉 Refactoring complete! Check: {refactor_dir}")
    else:
        print("\n✋ Preview only — no files were written. Set PREVIEW_MODE = False to apply.")


if __name__ == "__main__":
    run_refactor_agent()
