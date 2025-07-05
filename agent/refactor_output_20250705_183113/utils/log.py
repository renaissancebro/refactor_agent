from datetime import datetime

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
