#!/bin/bash
# Install man page for refactor tool

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - install to /usr/local/share/man/man1/
    MAN_DIR="/usr/local/share/man/man1"
    echo "Installing man page for macOS..."
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - install to /usr/local/man/man1/
    MAN_DIR="/usr/local/man/man1"
    echo "Installing man page for Linux..."
else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
fi

# Create man directory if it doesn't exist
sudo mkdir -p "$MAN_DIR"

# Copy the man page
sudo cp "$SCRIPT_DIR/refactor.1" "$MAN_DIR/"

# Update man database
if command -v mandb &> /dev/null; then
    # Linux systems with mandb
    sudo mandb
elif command -v makewhatis &> /dev/null; then
    # macOS systems with makewhatis
    sudo makewhatis
else
    echo "Warning: Could not update man database. You may need to run 'sudo makewhatis' manually."
fi

echo "✅ Man page installed successfully!"
echo "You can now use: man refactor"
