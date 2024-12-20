import threading

from src.config_loader.configLoader import YmlLoader


class Runner(threading.Thread):
    def __init__(self, api_key_load, docker_config, config_path):
        threading.Thread.__init__(self)
        self.api_key_Load = api_key_load  # Replace with your actual API key
        self.docker_config = docker_config
        self.config_path = config_path
        self.config = YmlLoader(self.docker_config)
