def process_data(data_list):
    """Process a list of data items"""
    results = []
    for item in data_list:
        processed = item * 2
        results.append(processed)
    return results
