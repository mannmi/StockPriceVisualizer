import subprocess
import os
import time
import venv

#doxygen generate using ai

def check_and_install_packages():
    """
    @brief Checks if specified packages are installed and installs them if not.

    This function checks for the installation of specific packages using Homebrew
    and installs them if they are not already installed.
    """
    packages = ["python@3.12"]

    for package in packages:
        try:
            # Check if the package is already installed
            subprocess.run(["brew", "list", package], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"{package} is already installed.")
        except subprocess.CalledProcessError:
            # If the package is not installed, install it
            print(f"{package} is not installed. Installing it now...")
            subprocess.run(["brew", "install", package], check=True)

def create_venv(venv_dir):
    """
    @brief Creates a virtual environment.

    This function creates a virtual environment at the specified directory path.
    If the virtual environment already exists, it will not create a new one.

    @param venv_dir The directory where the virtual environment will be created.
    """
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
    """
    @brief Installs pip if it is missing in the virtual environment.

    This function checks if pip is installed in the virtual environment, and if not,
    installs it.

    @param venv_dir The directory of the virtual environment.
    """
    python_executable = os.path.join(venv_dir, 'bin', 'python')
    try:
        # Check if pip is installed
        subprocess.check_call([python_executable, '-m', 'pip', '--version'])
        print("pip is already installed.")
    except subprocess.CalledProcessError:
        print("pip is not installed. Installing pip...")
        subprocess.check_call([python_executable, '-m', 'ensurepip', '--upgrade'])
        subprocess.check_call([python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

def modify_activation_script(venv_dir):
    """
    @brief Modifies the activation script to include PYTHONPATH.

    This function modifies the activation script of the virtual environment to
    include the PYTHONPATH environment variable.

    @param venv_dir The directory of the virtual environment.
    """
    activate_script = os.path.join(venv_dir, 'bin', 'activate')
    if not os.path.exists(activate_script):
        print(f"Activation script not found: {activate_script}")
        return

    pythonpath_line = 'export PYTHONPATH="$PYTHONPATH:$VIRTUAL_ENV/app:$VIRTUAL_ENV/app/src"'

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
    """
    @brief Upgrades pip to the latest version.

    This function upgrades pip to the latest version in the virtual environment.

    @param venv_dir The directory of the virtual environment.
    """
    python_executable = os.path.join(venv_dir, 'bin', 'python')
    subprocess.check_call([python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    print("Upgraded pip")

def install_mysqlclient(venv_dir):
    """
    @brief Installs the mysqlclient package.

    This function installs the mysqlclient package in the virtual environment.

    @param venv_dir The directory of the virtual environment.
    """
    python_executable = os.path.join(venv_dir, 'bin', 'python')
    try:
        subprocess.check_call([python_executable, '-m', 'pip', 'install', 'mysqlclient'])
        print("Installed mysqlclient")
    except subprocess.CalledProcessError as e:
        print(f"Error installing mysqlclient: {e}")

def install_requirements(venv_dir):
    """
    @brief Installs packages from a requirements.txt file.

    This function installs packages listed in a requirements.txt file in the virtual
    environment.

    @param venv_dir The directory of the virtual environment.
    """
    python_executable = os.path.join(venv_dir, 'bin', 'python')
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

def setup_mac(venv_dir):
    """
    @brief Sets up the environment on a macOS system.

    This function sets up the environment on a macOS system by installing necessary
    packages and creating a virtual environment.

    @param venv_dir The directory of the virtual environment.
    """
    print("Setting up on macOS")
    # Install MySQL client libraries
    subprocess.check_call(['brew', 'install', 'mysql-client'])

    check_and_install_packages()
    create_venv(venv_dir)
    upgrade_pip(venv_dir)
    install_mysqlclient(venv_dir)
    install_requirements(venv_dir)

    print("\nSetup is complete! To activate the virtual environment, run the following command:")
    print(f"source {venv_dir}/bin/activate")
