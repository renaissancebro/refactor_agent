import json


def read_config_file(filepath):
    """Read configuration from a JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {filepath}")
        return {}


def save_config_file(filepath, config_data):
    """Save configuration to a JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False
