import os
import platform
import subprocess
import sys
import venv


def modify_activation_script(venv_dir):
    if platform.system() == "Windows":
        activate_script = os.path.join(venv_dir, 'Scripts', 'activate.bat')
        with open(activate_script, 'a') as f:
            f.write('\nset PYTHONPATH=%PYTHONPATH%;%VIRTUAL_ENV%\\app;%VIRTUAL_ENV%\\app\\src\n')
    else:
        activate_script = os.path.join(venv_dir, 'bin', 'activate')
        with open(activate_script, 'a') as f:
            f.write('\nexport PYTHONPATH=$PYTHONPATH:$VIRTUAL_ENV/app:$VIRTUAL_ENV/app/src\n')


def create_and_activate_venv():
    venv_dir = 'venv'
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


def upgrade_pip():
    subprocess.check_call([os.path.join('venv', 'Scripts', 'python'), '-m', 'pip', 'install', '--upgrade', 'pip'])
    print("Upgraded pip")


def install_requirements():
    if os.path.exists('requirements.txt'):
        subprocess.check_call(
            [os.path.join('venv', 'Scripts', 'python'), '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Installed packages from requirements.txt")
    else:
        print("requirements.txt not found")


def setup_linux():
    print("Setting up on Linux")
    create_and_activate_venv()
    upgrade_pip()
    install_requirements()


def setup_mac():
    print("Setting up on macOS")
    create_and_activate_venv()
    upgrade_pip()
    install_requirements()


def setup_windows():
    print("Setting up on Windows")
    create_and_activate_venv()
    upgrade_pip()
    install_requirements()


def main():
    os_type = platform.system()
    if os_type == "Linux":
        setup_linux()
    elif os_type == "Darwin":
        setup_mac()
    elif os_type == "Windows":
        setup_windows()
    else:
        print("Unknown OS")


if __name__ == "__main__":
    main()