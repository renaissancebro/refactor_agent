# runner.py
import os
from agent.main_agent import assistant, user
from pathlib import Path

BACKEND_FILE = "backend/main.py"

PREVIEW_MODE = True  # Set False to enable actual file edits


def run_refactor_agent():
    if not Path(BACKEND_FILE).exists():
        print(f"❌ Source file not found: {BACKEND_FILE}")
        return

    with open(BACKEND_FILE, "r") as f:
        source_code = f.read()

    # System message describes the transformation goal
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

    user.initiate_chat(
        assistant,
        message=task_message
    )


if __name__ == "__main__":
    run_refactor_agent()
