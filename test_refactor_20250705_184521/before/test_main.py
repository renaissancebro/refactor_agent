
def process_data(data_list):
    """Process a list of data items"""
    results = []
    for item in data_list:
        processed = item * 2
        results.append(processed)
    return results

def validate_input(value):
    """Validate input value"""
    if not isinstance(value, (int, float)):
        return False
    return value > 0

def format_output(result):
    """Format output for display"""
    return f"Result: {result}"

def main():
    data = [1, 2, 3, 4, 5]
    processed = process_data(data)

    for item in processed:
        if validate_input(item):
            print(format_output(item))

if __name__ == "__main__":
    main()
