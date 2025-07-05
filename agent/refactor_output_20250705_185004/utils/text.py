from datetime import datetime
import re


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
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
