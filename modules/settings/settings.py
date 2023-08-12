# settings.py
import os
import json

class Settings:
    def __init__(self, config_path="config.json"):
        # Load settings from configuration file
        self.load_config(config_path)
        
        # Global Variables - unsure about the purpose of this, but retained it
        self.explorer_directory = ""

    def load_config(self, config_path):
        """Load settings from a configuration file."""
        if os.path.exists(config_path):
            with open(config_path, "r") as config_file:
                config_data = json.load(config_file)
            
            # Load values from the config file or set default values
            self.log_file = config_data.get("log_file", "logs/conversion_log.json")
            self.logs_folder = config_data.get("logs_folder", "logs")
            self.columns = tuple(config_data.get("columns", ("Directory", "File Name", "Input Codec", "Output Codec", "Input Size", "Output Size", "Relative Size")))
        else:
            # Default values if config file does not exist
            self.log_file = "logs/conversion_log.json"
            self.logs_folder = "logs"
            self.columns = ("Directory", "File Name", "Input Codec", "Output Codec", "Input Size", "Output Size", "Relative Size")

