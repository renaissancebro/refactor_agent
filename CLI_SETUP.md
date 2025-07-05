# CLI Refactor Agent Setup Guide

## 🚀 Quick Setup

### 1. Add Alias to Your Shell Configuration

**For Zsh (macOS/Linux):**

```bash
echo 'alias refactor="/Users/joshuafreeman/Desktop/agent_projects/autogen/refactor_agent/refactor_alias.sh"' >> ~/.zshrc
source ~/.zshrc
```

**For Bash:**

```bash
echo 'alias refactor="/Users/joshuafreeman/Desktop/agent_projects/autogen/refactor_agent/refactor_alias.sh"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Set Your OpenAI API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
# Add this to your shell config for persistence
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
```

## 🎯 Usage Examples

### Basic Usage

```bash
# Refactor any Python file
refactor my_file.py

# Preview only (don't apply changes)
refactor my_file.py --preview

# No backup (don't create .backup file)
refactor my_file.py --no-backup
```

### Real-World Examples

```bash
# Refactor a Django view
refactor views.py

# Preview a complex module
refactor complex_module.py --preview

# Refactor without backup (if you're confident)
refactor utils.py --no-backup
```

## 📁 What Happens When You Run It

### 1. File Processing

- ✅ Reads your current file
- ✅ Creates a `.backup` file (unless `--no-backup`)
- ✅ Sends to AI agent for refactoring

### 2. AI Refactoring

- ✅ Analyzes your code
- ✅ Extracts reusable components
- ✅ Creates utility modules
- ✅ Generates clean imports

### 3. File Organization

```
your_project/
├── your_file.py              # Refactored main file
├── your_file.py.backup       # Original backup
└── utils/                    # Extracted utilities
    ├── file_io.py
    ├── api_utils.py
    └── logging_utils.py
```

### 4. Logging

- ✅ Saves complete refactor data to `refactor_agent/refactor_logs/`
- ✅ Includes file paths, timestamps, and metadata
- ✅ Enables debugging and tracking

## 🛡️ Safety Features

### 1. Backup Protection

- ✅ Always creates `.backup` file (unless disabled)
- ✅ Original code is never lost

### 2. Preview Mode

- ✅ `--preview` shows changes without applying
- ✅ Review before accepting

### 3. Interactive Confirmation

- ✅ Asks for confirmation before applying
- ✅ Type `y` to accept, anything else to cancel

### 4. Error Handling

- ✅ Graceful handling of API errors
- ✅ Clear error messages
- ✅ No partial file writes

## 🔧 Advanced Usage

### Multiple Files

```bash
# Refactor multiple files
for file in *.py; do
    refactor "$file" --preview
done
```

### Integration with Git

```bash
# Refactor and commit
refactor my_file.py
git add .
git commit -m "Refactored my_file.py using AI agent"
```

### Custom Workflow

```bash
# Preview, then apply if satisfied
refactor complex_file.py --preview
# If happy with preview:
refactor complex_file.py
```

## 📊 Logging and Tracking

### Log Location

```
refactor_agent/
└── refactor_logs/
    ├── 2025-07-05_1845.json
    ├── 2025-07-05_1850.json
    └── ...
```

### Log Contents

```json
{
  "refactored_main": "...",
  "backup_file": "...",
  "utility_modules": {...},
  "original_file": "/path/to/your/file.py",
  "refactor_timestamp": "2025-07-05_1845",
  "cli_called": true
}
```

## 🚨 Troubleshooting

### Common Issues

**1. "OPENAI_API_KEY not set"**

```bash
export OPENAI_API_KEY="your-key-here"
```

**2. "File not found"**

```bash
# Make sure you're in the right directory
pwd
ls -la your_file.py
```

**3. "No JSON block found"**

- This usually means the AI response was malformed
- Check the logs in `refactor_logs/`
- Try running again

**4. Permission denied**

```bash
chmod +x refactor_alias.sh
chmod +x refactor_cli.py
```

### Debug Mode

```bash
# Run with verbose output
python refactor_cli.py your_file.py --preview
```

## 🎉 Benefits

### 1. Universal Access

- ✅ Call from any project directory
- ✅ Works with any Python file
- ✅ No need to copy files around

### 2. In-Place Refactoring

- ✅ Refactors your current file directly
- ✅ Creates utilities in the same project
- ✅ Maintains project structure

### 3. Complete Logging

- ✅ All refactors tracked centrally
- ✅ Easy debugging and rollback
- ✅ Historical record of changes

### 4. Safety First

- ✅ Always creates backups
- ✅ Preview before applying
- ✅ Interactive confirmation

## 🔄 Workflow Integration

### Typical Workflow

1. **Write code** in your project
2. **Call refactor** when ready to clean up
3. **Review preview** to see changes
4. **Accept changes** if satisfied
5. **Test refactored code**
6. **Commit to version control**

### IDE Integration

You can also call the CLI from your IDE's terminal or create custom commands/shortcuts.

**VS Code Example:**

```json
{
  "key": "cmd+shift+r",
  "command": "workbench.action.terminal.sendSequence",
  "args": {
    "text": "refactor ${file}\n"
  }
}
```

---

**Now you can refactor any Python file from anywhere with a simple `refactor filename.py` command!** 🚀
