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


def create_venv(venv_dir):
    if not os.path.exists(venv_dir):
        venv.create(venv_dir, with_pip=True)
        print(f"Virtual environment created at {venv_dir}")
    else:
        print(f"Virtual environment already exists at {venv_dir}")

    modify_activation_script(venv_dir)


def upgrade_pip(venv_dir):
    python_executable = os.path.join(venv_dir, 'Scripts', 'python') if platform.system() == "Windows" else os.path.join(
        venv_dir, 'bin', 'python')
    subprocess.check_call([python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    print("Upgraded pip")


def install_mysqlclient(venv_dir):
    python_executable = os.path.join(venv_dir, 'Scripts', 'python') if platform.system() == "Windows" else os.path.join(
        venv_dir, 'bin', 'python')
    try:
        subprocess.check_call([python_executable, '-m', 'pip', 'install', 'mysqlclient'])
        print("Installed mysqlclient")
    except subprocess.CalledProcessError as e:
        print(f"Error installing mysqlclient: {e}")


def install_requirements(venv_dir):
    python_executable = os.path.join(venv_dir, 'Scripts', 'python') if platform.system() == "Windows" else os.path.join(
        venv_dir, 'bin', 'python')
    if os.path.exists('requirements.txt'):
        for _ in range(3):  # Retry up to 3 times
            try:
                subprocess.check_call([python_executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
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
    # Install MySQL client libraries
    subprocess.check_call(
        ['sudo', 'apt-get', 'install', '-y', 'python3-dev', 'default-libmysqlclient-dev', 'build-essential'])

    create_venv(venv_dir)
    upgrade_pip(venv_dir)
    install_mysqlclient(venv_dir)
    install_requirements(venv_dir)


def setup_mac(venv_dir):
    print("Setting up on macOS")
    # Install Homebrew if not installed
    try:
        subprocess.check_call(
            ['/bin/bash', '-c', '"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'])
    except subprocess.CalledProcessError:
        print("Homebrew is already installed")

    # Add Homebrew to PATH and install MySQL client libraries
    subprocess.check_call(['/bin/bash', '-c', 'echo \'eval "$(/opt/homebrew/bin/brew shellenv)"\' >> ~/.zshrc'])
    subprocess.check_call(['/bin/bash', '-c', 'source ~/.zshrc'])
    subprocess.check_call(['brew', 'install', 'mysql-client'])
    subprocess.check_call(
        ['/bin/bash', '-c', 'echo \'export PATH="/usr/local/opt/mysql-client/bin:$PATH"\' >> ~/.zshrc'])
    subprocess.check_call(
        ['/bin/bash', '-c', 'echo \'export LDFLAGS="-L/usr/local/opt/mysql-client/lib"\' >> ~/.zshrc'])
    subprocess.check_call(
        ['/bin/bash', '-c', 'echo \'export CPPFLAGS="-I/usr/local/opt/mysql-client/include"\' >> ~/.zshrc'])
    subprocess.check_call(['/bin/bash', '-c', 'source ~/.zshrc'])

    create_venv(venv_dir)
    upgrade_pip(venv_dir)
    install_mysqlclient(venv_dir)
    install_requirements(venv_dir)


def setup_windows(venv_dir):
    print("Setting up on Windows")
    create_venv(venv_dir)
    upgrade_pip(venv_dir)
    install_mysqlclient(venv_dir)
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