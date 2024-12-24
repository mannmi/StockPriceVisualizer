# This function is adapted from a private project.
# Original project: https://github.com/mannmi/TPRO
# Author: mannmi
# Date: last modified Nov 29, 2023
# (reduced version of)

## @package yml_loader
#  docs for yml_loader.
#
#
#  Loades and modfies yml_config

import collections
import os
import yaml




def detect_doblicates(tmpdata):
    duplicates = [key for key, value in collections.Counter(tmpdata.values()).items() if value > 1]
    print(duplicates)

## @class Yml_Loader
#  @brief This class is used to load and modify a YAML configuration file.
#
# The Yml_Loader class is used to load and modify a YAML configuration file.
#
# Here’s an example of how you might use it: \n
# Python
# @code
#
#   # Create an instance of the Yml_Loader class
# loader = Yml_Loader('path/to/your/config.yml')
#
# # Get an item from the configuration data
# item = loader['key']
#
#
# # Load the configuration data from the configuration file
# config = loader.load_config()
#
# # Find the project root directory
# project_root = loader.find_project_root()
#
# @endcode

class YmlLoader:
    ## @brief The constructor for the Yml_Loader class.
    #  @param pathConfig The path to the configuration file.
    def __init__(self, path_config):
        ## Path to the config that will be loaded
        self.pathConfig = path_config
        ## Contains the loaded data of the Config
        self.data = self.load_config()

    ## @brief Get an item from the configuration data.
    #  @param key The key of the item to get.
    #  @return The value of the item.
    def __getitem__(self, key):
        return self.data[key]

    ## @brief Set an item in the configuration data.
    #  @param key The key of the item to set.
    #  @param value The new value of the item.
    def __setitem__(self, key, value):
        self.data[key] = value
        # self.save_config()

    ## @brief Load the configuration data from the configuration file.
    #  @return The configuration data.
    def load_config(self):
        # Load the existing config
        if not os.path.exists(self.pathConfig):
            with open(self.pathConfig, 'w') as file:
                pass  # the file is now created

        with open(self.pathConfig, 'r') as file:
            config = yaml.safe_load(file)

        return config if config else {}


    ## @brief Find the project root directory.
    #  @return The path to the project root directory.
    def find_project_root(self):
        # Start at the current directory
        path = os.getcwd()

        # Keep going up until we find the appDemoAsync.py file
        while not os.path.isfile(os.path.join(path, 'appDemoAsync.py')):
            new_path = os.path.dirname(path)
            if new_path == path:
                # We've reached the root of the filesystem, so the project root was not found
                return None
            path = new_path
        self.data["System"]["ProjectRoot"] = path

        # Return the directory that contains setup.py
        return path

