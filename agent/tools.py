# tools.py
from typing import List, Tuple
import ast
from typing import List, Tuple


# Example tool: categorize functions for extraction (stub logic)
def suggest_utils_categories(code: str) -> List[Tuple[str, str]]:
    """
    Accepts a full Python script and returns a list of (filename, code_block)
    suggesting how to split reusable components into utils modules.
    
    This is a stub — actual logic may involve AST parsing or LLM assistance.
    """
    return [
        ("utils/io.py", "def save_file(path: str, data: str): ..."),
        ("utils/text.py", "def clean_text(text: str): ...")
    ]


# tools.py

def extract_top_level_functions(code: str) -> List[Tuple[str, str]]:
    """
    Parses Python source code and extracts all top-level functions.
    Returns a list of (function_name, function_code) tuples.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [("__error__", f"Syntax error: {e}")]

    results = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_code = ast.unparse(node)
            results.append((node.name, func_code))

    return results
