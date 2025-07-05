# runner.py
import os
import ast
import json
from agent.main_agent import assistant, user
from agent.tools import extract_top_level_functions
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout

BACKEND_FILE = "backend/main.py"
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


def run_refactor_agent():
    if not Path(BACKEND_FILE).exists():
        print(f"❌ Source file not found: {BACKEND_FILE}")
        return

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

    Output the final result as:
    - A dictionary with keys 'modified_main.py' and the module filenames
    - Each value is a string of the Python code for that file

    Do NOT write any files — just return the preview.

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
        preview_dict = json.loads(output.strip().split("```json")[-1].split("```")[
            0
        ])
    except Exception:
        print("⚠️ Could not parse structured preview. Raw output:")
        print(output)
        return

    for filename, content in preview_dict.items():
        print(f"\n📄 {filename} Preview:\n{'='*40}\n{content}\n")

    if not PREVIEW_MODE:
        for filename, content in preview_dict.items():
            target_path = Path(filename)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w") as f:
                f.write(content)
        print("\n✅ Files written to disk.")
    else:
        print("\n✋ Preview only — no files were written. Set PREVIEW_MODE = False to apply.")


if __name__ == "__main__":
    run_refactor_agent()
