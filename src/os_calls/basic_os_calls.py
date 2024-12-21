# import only system from os
import os
from os import system, name


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

    ## @brief Find the project root directory.
    #  @return The path to the project root directory.


def find_project_root():
    # Start at the current directory
    path = os.getcwd()

    # Keep going up until we find the main.py file
    while not os.path.isfile(os.path.join(path, '.gitignore')):
        new_path = os.path.dirname(path)
        if new_path == path:
            # We've reached the root of the filesystem, so the project root was not found
            return None
        path = new_path
    # Return the directory that contains setup.py
    return path


def get_root_path():
    if is_running_in_docker():
        cpath_root = os.path.abspath("/app/")
    else:
        cpath_root = find_project_root()

    return cpath_root


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

# how to run it :)
# if is_running_in_docker():
#     logger.info("Running inside a Docker container")
# else:
#     logger.info("Not running inside a Docker container")
#
