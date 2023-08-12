# settings.py
import re
import tkinter as tk
class Settings:
    def __init__(self):
        self.file_paths = []
        # Global Variables
        self.explorer_directory = ""
        # Log File
        self.log_file = "logs/conversion_log.json"
        self.logs_folder = "logs"
        self.columns = ("Directory", "File Name", "Input Codec", "Output Codec", "Input Size", "Output Size", "Relative Size")