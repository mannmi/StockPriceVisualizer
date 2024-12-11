# import only system from os
import os
from os import system, name

# import sleep to show output for some time period
from time import sleep


def clear():
    """
    clears the screen windows or linux
    :return: no return
    """
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def is_running_in_docker():
    """
    checks if its running docker path may differ between docker and non docker
    :return:
    """
    # Check for the presence of the Docker environment file
    if os.path.exists('/.dockerenv'):
        return True

    # Check for the presence of Docker-specific cgroup files
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read()
    except FileNotFoundError:
        return False

#how to run it :)
# if is_running_in_docker():
#     print("Running inside a Docker container")
# else:
#     print("Not running inside a Docker container")
