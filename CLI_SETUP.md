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
# Refactor any Python file (applies changes immediately)
refactor my_file.py

# Preview only (don't apply changes)
refactor my_file.py --preview

# No backup (don't create .backup file)
refactor my_file.py --no-backup
```

### Suggestion Categories

```bash
# Different types of improvements
refactor --type refactor my_file.py      # Extract utilities (default)
refactor --type optimize my_file.py      # Performance optimization
refactor --type document my_file.py      # Add documentation & type hints
refactor --type style my_file.py         # PEP 8 style improvements
refactor --type security my_file.py      # Security improvements

# Combine with other options
refactor --type optimize --preview my_file.py
refactor --type document --no-backup my_file.py
```

### Real-World Examples

```bash
# Refactor a Django view (extract utilities)
refactor views.py

# Optimize performance of a data processing script
refactor --type optimize data_processor.py

# Add comprehensive documentation
refactor --type document api_client.py

# Improve code style and formatting
refactor --type style utils.py

# Security review of authentication code
refactor --type security auth.py

# Preview complex changes before applying
refactor --type optimize complex_module.py --preview
```

## 📁 What Happens When You Run It

### 1. File Processing

- ✅ Reads your current file
- ✅ Creates a `.backup` file (unless `--no-backup`)
- ✅ Sends to AI agent for improvement

### 2. AI Improvement

- ✅ Analyzes your code based on improvement type
- ✅ Extracts reusable components (refactor mode)
- ✅ Optimizes performance (optimize mode)
- ✅ Adds documentation (document mode)
- ✅ Improves style (style mode)
- ✅ Reviews security (security mode)

### 3. File Organization

```
your_project/
├── your_file.py              # Improved main file
├── your_file.py.backup       # Original backup
└── utils/                    # Extracted utilities (if any)
    ├── file_io.py
    ├── api_utils.py
    └── logging_utils.py
```

### 4. Logging

- ✅ Saves complete improvement data to `refactor_agent/refactor_logs/`
- ✅ Includes file paths, timestamps, and metadata
- ✅ Enables debugging and tracking

## 🛡️ Safety Features

### 1. Backup Protection

- ✅ Always creates `.backup` file (unless disabled)
- ✅ Original code is never lost

### 2. Immediate Application

- ✅ Changes applied immediately by default
- ✅ Faster workflow for confident users

### 3. Preview Mode

- ✅ `--preview` shows changes without applying
- ✅ Review before accepting when needed

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

# Optimize all files in a directory
for file in *.py; do
    refactor --type optimize "$file"
done
```

### Integration with Git

```bash
# Refactor and commit
refactor my_file.py
git add .
git commit -m "Refactored my_file.py using AI agent"

# Optimize and commit
refactor --type optimize performance_critical.py
git add .
git commit -m "Optimized performance_critical.py"
```

### Custom Workflow

```bash
# Preview, then apply if satisfied
refactor complex_file.py --preview
# If happy with preview:
refactor complex_file.py

# Document all files in a project
for file in *.py; do
    refactor --type document "$file"
done
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

### 2. Specialized Improvements

- ✅ Choose exactly what you want to improve
- ✅ Refactor, optimize, document, style, or secure
- ✅ Tailored AI prompts for each improvement type

### 3. In-Place Improvement

- ✅ Improves your current file directly
- ✅ Creates utilities in the same project
- ✅ Maintains project structure

### 4. Complete Logging

- ✅ All improvements tracked centrally
- ✅ Easy debugging and rollback
- ✅ Historical record of changes

### 5. Safety First

- ✅ Always creates backups
- ✅ Immediate application for speed
- ✅ Preview mode when needed

## 🔄 Workflow Integration

### Typical Workflow

1. **Write code** in your project
2. **Choose improvement type** based on your needs
3. **Call refactor** with appropriate flags
4. **Review changes** (if using preview mode)
5. **Test improved code**
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

## 🎯 Improvement Types Explained

### `--type refactor` (Default)

- Extracts reusable functions into utility modules
- Improves code organization and modularity
- Creates clean import statements

### `--type optimize`

- Focuses on performance improvements
- Suggests algorithm optimizations
- Improves memory usage and efficiency

### `--type document`

- Adds comprehensive docstrings
- Includes type hints
- Improves code readability and maintainability

### `--type style`

- Applies PEP 8 formatting standards
- Improves naming conventions
- Enhances overall code aesthetics

### `--type security`

- Reviews for security vulnerabilities
- Suggests input validation improvements
- Focuses on secure coding practices

---

**Now you can improve any Python file from anywhere with specialized AI assistance!** 🚀

# 🛠 CLI Setup Guide

The `refactor` command-line tool is now globally available via a shell alias.

---

## ✅ What's Set Up

- Alias added to `.zshrc`
- Automatically activates virtual environment
- Runs `refactor_cli.py` with any arguments
- Works from **any directory**

---

## 🚀 How to Use

```bash
refactor --help
refactor my_file.py --preview
refactor main.py --no-backup
```
