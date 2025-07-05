
def validate_input(value):
    """Validate input value"""
    if not isinstance(value, (int, float)):
        return False
    return value > 0
