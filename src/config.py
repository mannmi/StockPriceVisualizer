import os

def setup_paths():
    def is_running_in_docker():
        return os.path.exists('/.dockerenv')

    if is_running_in_docker():
        base_path = '/app/'
    else:
        cwd = os.getcwd()
        base_path = cwd + '/src/'

    return base_path

setup_paths()