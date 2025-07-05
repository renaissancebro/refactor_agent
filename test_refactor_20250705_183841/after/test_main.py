
from processing import process_data
from validation import validate_input
from formatting import format_output


def main():
    data = [1, 2, 3, 4, 5]
    processed = process_data(data)

    for item in processed:
        if validate_input(item):
            print(format_output(item))


if __name__ == "__main__":
    main()
