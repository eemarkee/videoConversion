import os
import subprocess
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import re
import threading
from processingFunctions import open_output_directory, on_tree_select, select_files, process_files
from settings import  columns

# List of global gui elements 
global status_var, open_output_button, log_tree, file_button, status_label, remove_input_var, remove_input_checkbox
# Create the main root window
root = tk.Tk()
root.title("Video Converter")

# # Initialize tkinter variables
status_var = tk.StringVar()
status_var.set("Select a File")

open_output_button = tk.Button(root, text="Open Output Directory", command=open_output_directory, state="disabled")
open_output_button.pack(pady=5)

progress_var = tk.IntVar()

progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=5)

log_tree = ttk.Treeview(root, columns=columns, show="headings")
log_tree.bind("<<TreeviewSelect>>", on_tree_select)

file_button = tk.Button(root, text="Select Files", command=select_files)
file_button.pack(pady=5)

status_label = tk.Label(root, textvariable=status_var)
status_label.pack(pady=5)

remove_input_var = tk.BooleanVar(value=False)  # Create a BooleanVar to hold the checkbox value
remove_input_checkbox = tk.Checkbutton(root, text="Remove input file after completion", variable=remove_input_var)
remove_input_checkbox.pack(pady=5)


# Set column headings
for col in columns:
    log_tree.heading(col, text=col)
    log_tree.column(col, width=100)  # Adjust the column width as needed


log_tree.pack(pady=5)

######################################################

def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.avi *.mkv *.3gp *.mov")])
    if file_paths:
        thread = threading.Thread(target=process_files, args=(file_paths,))
        thread.start()


def load_last_log_entries(log_tree):
    log_file = "conversion_log.json"
    try:
        with open(log_file, "r") as f:
            log_data_list = json.load(f)

        # Get the last 5 entries or all entries if there are less than 5
        last_entries = log_data_list[-15:]

        for entry in last_entries:
            # Extract relevant values and insert into the treeview
            file_directory =     entry.get("Directory", "Unknown")
            file_name =         entry.get("File Name", "Unknown")
            input_codec  =     entry.get("Input Codec", "Unknown")
            output_codec =     entry.get("Output Codec", "Unknown")
            input_size =         entry.get("Input Size", "Unknown")
            output_size =       entry.get("Output Size", "Unknown")
            relative_size =     entry.get("Relative Size", "Unknown")

            log_tree.insert("", tk.END, values=(file_directory,file_name, input_codec, output_codec, input_size, output_size, relative_size))

    except FileNotFoundError:
        pass  # Handle the case when the log file is not found

def move_input_file(input_path):
    input_file_name = os.path.basename(input_path)
    input_folder = os.path.join(os.path.dirname(input_path), "inputFiles")
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
    
    new_input_path = os.path.join(input_folder, input_file_name)
    os.rename(input_path, new_input_path)

# Call the function to load the last log entries on startup
load_last_log_entries(log_tree)

# Start it up
root.mainloop()