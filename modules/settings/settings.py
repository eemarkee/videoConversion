# settings.py
import os
import json
from pathlib import Path

class Settings:
    """
    A class to manage various settings for the application. These settings encompass configuration 
    details like paths to logs, columns for display, paths to utilities like ffmpeg and ffprobe, and 
    others. The settings can be loaded from a configuration JSON file or set to default values if 
    the file doesn't exist.

    Attributes:
    - log_file (str): Path to the log file.
    - logs_folder (str): Directory path for logs.
    - columns (tuple): Column names to be used for display.
    - ffmpeg_path (Path): Path to the ffmpeg executable.
    - ffprobe_path (Path): Path to the ffprobe executable.
    - debug (bool): Debug mode flag.
    - explorer_directory (str): Directory to be explored.

    Methods:
    - load_config(config_path): Loads settings from a given configuration file.
    """
    def __init__(self, config_path="settings_config.json"):
        """
        Initializes a new instance of the Settings class. Loads the settings from the provided 
        JSON file or defaults to predefined values if the file doesn't exist.

        Parameters:
        - config_path (str): Path to the configuration file relative to the module's directory. 
                             Defaults to "settings_config.json".
        """
        module_dir = os.path.dirname(os.path.abspath(__file__))
        # Form the path to the configuration file relative to this module's directory
        config_file_path = os.path.join(module_dir,config_path)
        
        self.load_config(config_file_path)
        
    def load_config(self, config_path):
        """
        Load settings from a specified configuration file. If the configuration file doesn't exist, 
        the method sets the settings to default values.

        Parameters:
        - config_path (str): Absolute path to the configuration file to be loaded.
        """
        parent_dir = Path(__file__).resolve().parents[2]
        if os.path.exists(config_path):
            with open(config_path, "r") as config_file:
                config_data = json.load(config_file)
            
            # Load values from the config file or set default values
            self.log_file = config_data.get("log_file", "logs/conversion_log.json")
            self.logs_folder = config_data.get("logs_folder", "logs")
            self.columns = tuple(config_data.get("columns", ("Directory", "File Name", "Input Codec", "Output Codec", "Input Size", "Output Size", "Relative Size")))
            self.ffmpeg_path = parent_dir / 'bin' / 'ffmpeg.exe'
            self.ffprobe_path = parent_dir / 'bin' / 'ffprobe.exe'
            self.debug = config_data.get("debug", False)
            self.explorer_directory = config_data.get("explorer_directory", "")
            
        else:
            # Default values if config file does not exist
            self.log_file = "logs/conversion_log.json"
            self.logs_folder = "logs"
            self.columns = ("Directory", "File Name", "Input Codec", "Output Codec", "Input Size", "Output Size", "Relative Size")
            self.ffmpeg_path = parent_dir / 'bin' / 'ffmpeg.exe'
            self.ffprobe_path = parent_dir / 'bin' / 'ffprobe.exe'
            self.debug = False
            self.explorer_directory = ""

