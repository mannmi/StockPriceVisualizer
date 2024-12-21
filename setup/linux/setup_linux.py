import subprocess
import os
import time
import venv


def check_and_install_packages():
    packages = ["python3.12-venv", "libxcb-cursor0", "libxcb1", "libx11-xcb1", "libxkbcommon-x11-0"]

    for package in packages:
        try:
            # Check if the package is already installed
            subprocess.run(["dpkg", "-l", package], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"{package} is already installed.")
        except subprocess.CalledProcessError:
            # If the package is not installed, install it
            print(f"{package} is not installed. Installing it now...")
            subprocess.run(["sudo", "apt-get", "install", "-y", package], check=True)


def set_qt_plugin_path():
    # Set the environment variable for Qt plugin path
    qt_plugin_path = "/usr/lib/x86_64-linux-gnu/qt5/plugins"
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_plugin_path
    print(f"QT_QPA_PLATFORM_PLUGIN_PATH set to {qt_plugin_path}")


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
    python_executable = os.path.join(venv_dir, 'bin', 'python')
    subprocess.check_call([python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    print("Upgraded pip")


def install_mysqlclient(venv_dir):
    python_executable = os.path.join(venv_dir, 'bin', 'python')
    try:
        subprocess.check_call([python_executable, '-m', 'pip', 'install', 'mysqlclient'])
        print("Installed mysqlclient")
    except subprocess.CalledProcessError as e:
        print(f"Error installing mysqlclient: {e}")


def install_requirements(venv_dir):
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


def setup_linux(venv_dir):
    print("Setting up on Linux")
    # Install MySQL client libraries
    subprocess.check_call(
        ['sudo', 'apt-get', 'install', '-y', 'python3-dev', 'default-libmysqlclient-dev', 'build-essential'])

    check_and_install_packages()
    set_qt_plugin_path()
    create_venv(venv_dir)
    upgrade_pip(venv_dir)
    install_mysqlclient(venv_dir)
    install_requirements(venv_dir)

    print("\nSetup is complete! To activate the virtual environment, run the following command:")
    print(f"source {venv_dir}/bin/activate")