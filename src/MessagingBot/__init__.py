import os
import sys

def check_file_exists(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)

    # Check if the file is accessible
    if not os.access(file_path, os.R_OK):
        print(f"Error: The file '{file_path}' is not accessible (no read permissions).")
        sys.exit(1)

    print(f"The file '{file_path}' exists and is accessible.")


# Example usage
#file_path = '/app/src/config_loader/configLoader.py'
#check_file_exists(file_path)