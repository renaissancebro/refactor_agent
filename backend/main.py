# Sample main.py file for testing refactor agent

import os
import json
import requests
from datetime import datetime

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

def make_api_request(url, method="GET", data=None, headers=None):
    """Make an HTTP request to an API endpoint"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None

def format_timestamp(timestamp=None):
    """Format a timestamp in a readable format"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def log_message(message, level="INFO"):
    """Log a message with timestamp and level"""
    timestamp = format_timestamp()
    formatted_message = f"[{timestamp}] {level}: {message}"
    print(formatted_message)

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def main():
    # Main application logic
    config = read_config_file("config.json")

    if not config:
        log_message("No configuration found, using defaults", "WARNING")
        config = {"api_url": "https://api.example.com", "timeout": 30}

    log_message("Starting application")

    # Make API request
    response = make_api_request(config.get("api_url"))

    if response:
        log_message("API request successful")
        save_config_file("response.json", response)
    else:
        log_message("API request failed", "ERROR")

if __name__ == "__main__":
    main()
