import tkinter as tk
from tkinter import ttk
import os
from settings import root, columns, open_output_button, file_button, log_tree, status_label, remove_input_var, progress_var, progress_bar
from settings import remove_input_var, status_var, remove_input_checkbox, file_paths, log_file, logs_folder, current_file_label
from settings import crf_label, crf_entry, crf_var
from processingFunctions import load_last_log_entries, open_output_directory, on_tree_select, select_files
from tkinter import filedialog
import threading



# Initialize tkinter variables
status_var.set("Select a File")

# Gui Element Calls
file_button = tk.Button(root, text="Select Files", command=select_files) # file_button and remove_input_checkbox need to be defined in processingFunctions to prevent circular import errors

# Gui Element Locations
    # Row 0
file_button.grid(row=0, column=0, padx=0, pady=5)
progress_bar.grid(row=0, column=1,columnspan=2,padx=0, pady=5, sticky='ew')
current_file_label.grid(row=0, column=3, padx=5, pady=5,sticky="e")

# Row 1
remove_input_checkbox.grid(row=1, column=0, padx=5, pady=5,sticky="w")
crf_label.grid(row=1, column=1,columnspan=1, padx=5, pady=5,sticky='e')
crf_entry.grid(row=1, column=2,columnspan=1, padx=5, pady=5,sticky='e')

# Row 2

status_label.grid(row=2,column=1,columnspan=3,padx=0,pady=5,sticky='e')

# Row 3
log_tree.grid(row=3, columnspan=4, padx=5, pady=5)

# Set column headings
for col in columns:
    log_tree.heading(col, text=col)
    log_tree.column(col, width=100)  # Adjust the column width as needed

log_tree.bind("<<TreeviewSelect>>", on_tree_select)
# Create the "logs" subfolder if it doesn't exist
logs_folder = "logs"
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)

# Call the function to load the last log entries on startup
load_last_log_entries(log_tree)

root.mainloop()
