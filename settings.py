# settings.py
import re
import tkinter as tk
from tkinter import ttk
global progress_pattern, input_codec, input_size, total_frames, file_directory, output_path, explorer_directory, root, columns
global open_output_button, file_button, log_tree, status_label, remove_input_var, progress_var, progress_bar, status_var, file_paths
global log_file, logs_folder, current_file_label, crf_var, crf_entry, crf_label

# Global Variables
progress_pattern = re.compile(r"frame=\s*(\d+)")
input_codec = "Unknown"
input_size = 0
total_frames = 1
file_directory = ""
output_path = ""
explorer_directory = ""

# Log File
log_file = "logs/conversion_log.json"
logs_folder = "logs"
columns = ("Directory", "File Name", "Input Codec", "Output Codec", "Input Size", "Output Size", "Relative Size")

# GUI Elements
file_paths = open_output_button = file_button = None
root = tk.Tk()

# GUI Weights
# Set column weights
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=5)
root.columnconfigure(2, weight=1)
# Set the row weights
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)

status_var = tk.StringVar()
progress_var = tk.IntVar()
remove_input_var = tk.BooleanVar(value=False)

log_tree = ttk.Treeview(root, columns=columns, show="headings")
status_label = tk.Label(root, textvariable=status_var)
remove_input_checkbox = tk.Checkbutton(root, text="Move Input File", variable=remove_input_var)
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)

crf_label = tk.Label(root, text="CRF Value:")
crf_var = tk.StringVar()
crf_var.set("28")  # Set a default value
crf_entry = tk.Entry(root, textvariable=crf_var)



# Gui Locations and Sizes
current_file_label = tk.Label(root, text="Processing: None")

# Place the progress bar
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)

# Add a Treeview widget to display log entries as a table
columns = ("Directory", "File Name", "Input Codec", "Output Codec", "Input Size", "Output Size", "Relative Size")
log_tree = ttk.Treeview(root, columns=columns, show="headings")
