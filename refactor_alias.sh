#!/bin/bash
# Refactor CLI alias script
# Add this to your .bashrc or .zshrc:
# alias refactor="/path/to/refactor_agent/refactor_alias.sh"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment if it exists
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Run the refactor CLI tool
python3 "$SCRIPT_DIR/refactor_cli.py" "$@"
