# settings.py
import tkinter as tk
import os
import subprocess
import json
import tkinter as tk
from tkinter import ttk
import re
import threading



global status_var, explorer_directory, input_codec, input_size, total_frames, file_directory, progress_pattern, root
global progress_bar, open_output_button, log_tree, columns, remove_input_var

progress_pattern = re.compile(r"frame=\s*(\d+)")
input_codec = "Unknown"
input_size = 0
total_frames = 1
file_directory = ""
output_path = ""
explorer_directory = ""

# GUI ELEMENTS #
columns = ("Directory", "File Name", "Input Codec", "Output Codec", "Input Size", "Output Size", "Relative Size")
