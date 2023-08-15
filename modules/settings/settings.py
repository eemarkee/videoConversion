# settings.py
import os
import json
from pathlib import Path

class Settings:
    def __init__(self, config_path="settings_config.json"):
        module_dir = os.path.dirname(os.path.abspath(__file__))
        # Form the path to the configuration file relative to this module's directory
        config_file_path = os.path.join(module_dir,config_path)
        
        self.load_config(config_file_path)
        
    def load_config(self, config_path):
        """Load settings from a configuration file."""
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

