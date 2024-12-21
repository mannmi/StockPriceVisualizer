import os
import platform
import argparse
import sys

from linux.setup_linux import setup_linux
from mac.setup_mac import setup_mac
from windows.setup_windows import setup_windows




def get_venv_path():
    venv_path = os.environ.get('VIRTUAL_ENV', None)
    if venv_path:
        print(f"Virtual environment path: {venv_path}")
    else:
        print("No virtual environment detected")

def main():
    parser = argparse.ArgumentParser(description="Setup virtual environment")
    parser.add_argument('--venv', type=str, default='venv', help='Path to the virtual environment directory')
    args = parser.parse_args()

    venv_dir = args.venv

    os_type = platform.system()
    if os_type == "Linux":
        setup_linux(venv_dir)
    elif os_type == "Darwin":
        setup_mac(venv_dir)
    elif os_type == "Windows":
        setup_windows(venv_dir)
    else:
        print("Unknown OS")

    get_venv_path()
    print(f"\033Setup complete\n Enable the virtual environment\n"
          " source {}/bin/activate\033".format(venv_dir))

if __name__ == "__main__":
    main()
    sys.exit(0)
