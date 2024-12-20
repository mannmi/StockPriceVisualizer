import os
import platform
import subprocess
import sys
import venv
import argparse
import time


def get_venv_path():
    venv_path = os.environ.get('VIRTUAL_ENV', None)
    if venv_path:
        print(f"Virtual environment path: {venv_path}")
    else:
        print("No virtual environment detected")


def modify_activation_script(venv_dir):
    if platform.system() == "Windows":
        activate_script = os.path.join(venv_dir, 'Scripts', 'activate.bat')
        with open(activate_script, 'a') as f:
            f.write('\nset PYTHONPATH=%PYTHONPATH%;%VIRTUAL_ENV%\\app;%VIRTUAL_ENV%\\app\\src\n')
    else:
        activate_script = os.path.join(venv_dir, 'bin', 'activate')
        with open(activate_script, 'a') as f:
            f.write('\nexport PYTHONPATH=$PYTHONPATH:$VIRTUAL_ENV/app:$VIRTUAL_ENV/app/src\n')


def create_and_activate_venv(venv_dir):
    if not os.path.exists(venv_dir):
        venv.create(venv_dir, with_pip=True)
        print(f"Virtual environment created at {venv_dir}")
    else:
        print(f"Virtual environment already exists at {venv_dir}")

    modify_activation_script(venv_dir)

    if platform.system() == "Windows":
        activate_script = os.path.join(venv_dir, 'Scripts', 'activate.bat')
        subprocess.run([activate_script], shell=True)
    else:
        activate_script = os.path.join(venv_dir, 'bin', 'activate')
        subprocess.run(['source', activate_script], shell=True)

    print(f"Virtual environment activated")


def upgrade_pip(venv_dir):
    subprocess.check_call([os.path.join(venv_dir, 'Scripts', 'python'), '-m', 'pip', 'install', '--upgrade', 'pip'])
    print("Upgraded pip")


def install_requirements(venv_dir):
    if os.path.exists('requirements.txt'):
        for _ in range(3):  # Retry up to 3 times
            try:
                subprocess.check_call(
                    [os.path.join(venv_dir, 'Scripts', 'python'), '-m', 'pip', 'install', '-r', 'requirements.txt'])
                print("Installed packages from requirements.txt")
                break
            except subprocess.CalledProcessError as e:
                print(f"Error installing packages: {e}")
                time.sleep(5)  # Wait for 5 seconds before retrying
        else:
            print("Failed to install packages after 3 attempts")
    else:
        print("requirements.txt not found")


def setup_linux(venv_dir):
    print("Setting up on Linux")
    create_and_activate_venv(venv_dir)
    upgrade_pip(venv_dir)
    #purge_packages(venv_dir)
    install_requirements(venv_dir)


def setup_mac(venv_dir):
    print("Setting up on macOS")
    create_and_activate_venv(venv_dir)
    upgrade_pip(venv_dir)
    #purge_packages(venv_dir)
    install_requirements(venv_dir)


def setup_windows(venv_dir):
    print("Setting up on Windows")
    create_and_activate_venv(venv_dir)
    upgrade_pip(venv_dir)
    #purge_packages(venv_dir)
    install_requirements(venv_dir)


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


if __name__ == "__main__":
    main()