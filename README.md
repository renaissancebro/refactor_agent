# 🤖 AI-Powered Code Refactor Agent

An intelligent Python code refactoring system that uses GPT-4 to automatically extract reusable components, organize code structure, and maintain clean, modular codebases.

## ✨ Features

### 🧠 AI-Powered Refactoring

- **Smart Component Extraction** - Identifies and extracts reusable functions and classes
- **Automatic Import Management** - Generates clean import statements
- **Code Organization** - Groups related functionality into logical modules
- **Boilerplate Reduction** - Removes redundant code and improves readability

### 🛡️ Safety & Control

- **Preview Mode** - Review changes before applying
- **Interactive Confirmation** - Accept or reject refactoring suggestions
- **Automatic Backups** - Original files are always preserved
- **Error Handling** - Graceful failure with detailed error messages

### 📁 Flexible Output Options

- **Directory Structure** - Organized before/after/utils directories
- **In-Place Refactoring** - Refactor files directly in their location
- **Centralized Logging** - Complete audit trail of all refactoring operations
- **CLI Integration** - Universal command-line tool for any project

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

### Installation

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd refactor_agent
```

2. **Set up virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install autogen openai
```

4. **Set your OpenAI API key**

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 🎯 Usage Options

### Option 1: CLI Tool (Recommended)

**Set up the CLI alias:**

```bash
echo 'alias refactor="/path/to/refactor_agent/refactor_alias.sh"' >> ~/.zshrc
source ~/.zshrc
```

**Use from any project:**

```bash
# Refactor any Python file (applies changes immediately)
refactor my_file.py

# Different improvement types
refactor --type refactor my_file.py      # Extract utilities (default)
refactor --type optimize my_file.py      # Performance optimization
refactor --type document my_file.py      # Add documentation
refactor --type style my_file.py         # PEP 8 style improvements
refactor --type security my_file.py      # Security improvements

# Preview only
refactor --preview complex_module.py

# No backup
refactor --no-backup utils.py

# Combine options
refactor --type optimize --preview my_file.py
```

### Improvement Types

The refactor agent supports 5 specialized improvement categories:

- **`--type refactor`** (Default) - Extracts reusable components into utility modules
- **`--type optimize`** - Focuses on performance improvements and efficiency
- **`--type document`** - Adds comprehensive documentation and type hints
- **`--type style`** - Applies PEP 8 formatting and style improvements
- **`--type security`** - Reviews code for security vulnerabilities

### Option 2: Runner Script

**For batch processing:**

```bash
cd agent
python runner.py
```

**Configure in `agent/runner.py`:**

```python
BACKEND_FILE = "../your_file.py"  # File to refactor
PREVIEW_MODE = True               # Set to False to apply changes
```

### Option 3: Test Script

**For development and testing:**

```bash
python test_directory_structure.py
```

## 📁 Project Structure

```
refactor_agent/
├── agent/
│   ├── main_agent.py          # AI agent configuration
│   ├── runner.py              # Main refactor orchestrator
│   └── tools.py               # Utility functions
├── backend/
│   └── main.py                # Sample code to refactor
├── refactor_cli.py            # Universal CLI tool
├── refactor_alias.sh          # Shell alias script
├── test_directory_structure.py # Test script with logging
├── CLI_SETUP.md               # CLI setup guide
└── refactor_logs/             # Centralized refactor logs
    └── YYYY-MM-DD_HHMM.json
```

## 🔧 How It Works

### 1. Code Analysis

The AI agent analyzes your Python code to identify:

- Reusable functions and classes
- Related functionality that can be grouped
- Import dependencies and requirements
- Code patterns that can be extracted

### 2. Refactoring Strategy

Based on the analysis, the agent:

- Extracts utility functions into separate modules
- Creates clean import statements
- Maintains the original functionality
- Improves code organization and readability

### 3. Output Organization

**Directory Structure Mode:**

```
refactor_output_20250705_184521/
├── before/
│   ├── main.py              # Original file
│   └── main_backup.py       # Extracted boilerplate
├── after/
│   └── main.py              # Refactored main file
└── utils/
    ├── io.py                # File I/O utilities
    ├── network.py           # HTTP utilities
    └── log.py               # Logging utilities
```

**In-Place Mode:**

```
your_project/
├── your_file.py              # Refactored file
├── your_file.py.backup       # Original backup
└── utils/                    # Extracted utilities
    ├── file_io.py
    ├── api_utils.py
    └── logging_utils.py
```

## 🛡️ Safety Features

### Backup Protection

- **Automatic backups** - Original files are never lost
- **Timestamped directories** - Each refactor creates unique output
- **Backup files** - `.backup` extension for easy identification

### Preview & Confirmation

- **Immediate application** - Changes applied by default for faster workflow
- **Preview mode** - Use `--preview` flag to see changes before applying
- **Backup protection** - Automatic backups ensure you can always rollback
- **Rollback capability** - Use backup files to restore original code

### Error Handling

- **Graceful failures** - Clear error messages and recovery options
- **Partial operation protection** - No incomplete file writes
- **API error handling** - Retry logic and fallback options

## 📊 Logging & Tracking

### Centralized Logs

All refactoring operations are logged to `refactor_logs/` with:

- Complete refactor data
- Original file paths
- Timestamps and metadata
- CLI usage tracking

### Log Format

```json
{
  "refactored_main": "...",
  "backup_file": "...",
  "utility_modules": {...},
  "original_file": "/path/to/file.py",
  "refactor_timestamp": "2025-07-05_1845",
  "cli_called": true
}
```

## 🔄 Workflow Integration

### Typical Development Workflow

1. **Write code** in your project
2. **Call refactor** when ready to clean up
3. **Review preview** to see proposed changes
4. **Accept changes** if satisfied
5. **Test refactored code** to ensure functionality
6. **Commit to version control**

### Git Integration

```bash
# Refactor and commit
refactor my_file.py
git add .
git commit -m "Refactored my_file.py using AI agent"
```

### IDE Integration

You can integrate the CLI into your IDE's terminal or create custom shortcuts.

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

## 🚨 Troubleshooting

### Common Issues

**1. API Key Not Set**

```bash
export OPENAI_API_KEY="your-key-here"
```

**2. File Not Found**

```bash
# Check file path and permissions
ls -la your_file.py
```

**3. Permission Denied**

```bash
chmod +x refactor_alias.sh
chmod +x refactor_cli.py
```

**4. Import Errors**

```bash
# Ensure virtual environment is activated
source venv/bin/activate
```

### Debug Mode

```bash
# Run with verbose output
python refactor_cli.py your_file.py --preview
```

## 🎯 Use Cases

### Code Refactoring

- Extract utility functions from large files
- Organize related functionality into modules
- Remove duplicate code and improve maintainability

### Performance Optimization

- Identify and fix performance bottlenecks
- Optimize algorithms and data structures
- Improve memory usage and efficiency

### Documentation & Style

- Add comprehensive docstrings and type hints
- Apply PEP 8 formatting standards
- Improve code readability and maintainability

### Security Review

- Identify potential security vulnerabilities
- Improve input validation and error handling
- Follow secure coding best practices

### Legacy Code Modernization

- Refactor old code to follow modern Python practices
- Improve code organization and readability
- Extract reusable components for future use

### Project Organization

- Standardize code structure across projects
- Create consistent utility modules
- Improve code maintainability and collaboration

### Learning & Development

- Learn improvement patterns from AI suggestions
- Understand code organization best practices
- Improve coding skills through AI-assisted development

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [AutoGen](https://github.com/microsoft/autogen) framework
- Powered by OpenAI GPT-4
- Inspired by modern code refactoring practices

---

**Transform your Python code with AI-powered refactoring!** 🚀

For detailed CLI setup instructions, see [CLI_SETUP.md](CLI_SETUP.md).
