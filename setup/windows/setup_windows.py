# AI generated based on setup_linux.py
import subprocess
import os
import time
import venv


def check_and_install_packages():
    packages = ["python3.12", "mysql", "chocolatey"]  # Chocolatey is needed to install packages on Windows

    for package in packages:
        try:
            # Check if the package is already installed
            subprocess.run(["choco", "list", "-l", package], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"{package} is already installed.")
        except subprocess.CalledProcessError:
            # If the package is not installed, install it
            print(f"{package} is not installed. Installing it now...")
            subprocess.run(["choco", "install", "-y", package], check=True)


def create_venv(venv_dir):
    print(f"Creating virtual environment at {venv_dir}")

    if not os.path.exists(venv_dir):
        try:
            venv.create(venv_dir, with_pip=True)
            print(f"Virtual environment created at {venv_dir}")
        except Exception as e:
            print(f"Error creating virtual environment: {e}")
            return
    else:
        print(f"Virtual environment already exists at {venv_dir}")

    install_pip_if_missing(venv_dir)
    modify_activation_script(venv_dir)


def install_pip_if_missing(venv_dir):
    python_executable = os.path.join(venv_dir, 'Scripts', 'python')
    try:
        # Check if pip is installed
        subprocess.check_call([python_executable, '-m', 'pip', '--version'])
        print("pip is already installed.")
    except subprocess.CalledProcessError:
        print("pip is not installed. Installing pip...")
        subprocess.check_call([python_executable, '-m', 'ensurepip', '--upgrade'])
        subprocess.check_call([python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'])


def modify_activation_script(venv_dir):
    activate_script = os.path.join(venv_dir, 'Scripts', 'activate')
    if not os.path.exists(activate_script):
        print(f"Activation script not found: {activate_script}")
        return

    pythonpath_line = 'set PYTHONPATH=%PYTHONPATH%;%VIRTUAL_ENV%\\app;%VIRTUAL_ENV%\\app\\src'

    # Check if the line already exists
    with open(activate_script, 'r') as f:
        lines = f.readlines()
        if any(pythonpath_line in line for line in lines):
            print("PYTHONPATH line already exists in the activation script.")
            return

    # If the line doesn't exist, add it
    with open(activate_script, 'a') as f:
        f.write(f'\n{pythonpath_line}\n')
    print("Activation script modified to include PYTHONPATH.")


def upgrade_pip(venv_dir):
    python_executable = os.path.join(venv_dir, 'Scripts', 'python')
    subprocess.check_call([python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    print("Upgraded pip")


def install_mysqlclient(venv_dir):
    python_executable = os.path.join(venv_dir, 'Scripts', 'python')
    try:
        subprocess.check_call([python_executable, '-m', 'pip', 'install', 'mysqlclient'])
        print("Installed mysqlclient")
    except subprocess.CalledProcessError as e:
        print(f"Error installing mysqlclient: {e}")


def install_requirements(venv_dir):
    python_executable = os.path.join(venv_dir, 'Scripts', 'python')
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


def setup_windows(venv_dir):
    print("Setting up on Windows")

    # Install Chocolatey if it's not installed
    try:
        subprocess.run(["choco", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Chocolatey is not installed. Installing it now...")
        subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                        "Set-ExecutionPolicy AllSigned; "
                        "Set-ExecutionPolicy Bypass -Scope Process; "
                        "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
                        "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"], check=True)

    check_and_install_packages()
    create_venv(venv_dir)
    upgrade_pip(venv_dir)
    install_mysqlclient(venv_dir)
    install_requirements(venv_dir)

    print("\nSetup is complete! To activate the virtual environment, run the following command:")
    print(f"{venv_dir}\\Scripts\\activate")
