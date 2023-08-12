import tkinter as tk
from tkinter import ttk, filedialog
from video_settings import video_settings
from processing import VideoProcessor
from settings import Settings
import os
import json
import subprocess
import threading

class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Converter")
        self.video_processor = VideoProcessor()  # Pass the selected codec name
        self.settings = Settings()

        # Create and place GUI elements using grid
        ttk.Button(self.root, text="Select Files", command=self.select_files).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Create a Current File Text 
        # ttk.Label(self.root, text="Current File:").grid(row=0, column=1, padx=5, pady=5, sticky="e")
        self.current_file_label = ttk.Label(self.root, text="")
        self.current_file_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        # CRF Codec Value
        ttk.Label(self.root, text="CRF:").grid(row=1, column=0, padx=(280,0), pady=5, sticky="w")
        
        crf_entry_width = 2  # Adjust the width as needed
        self.crf_entry = ttk.Entry(self.root, textvariable=video_settings.crf_var, width=crf_entry_width)
        self.crf_entry.grid(row=1, column=0, padx=(310,2), pady=5, sticky="w")
        
        self.start_processing_button = ttk.Button(self.root, text="Start Processing", command=self.start_processing)
        self.start_processing_button.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        
        # Create a label for the codec dropdown box
        self.codec_label = tk.Label(self.root, text="Output Codec:", width = 10)
        self.codec_label.grid(row=1, column=0, padx=(110,5), pady=5, sticky="w")

        # Create a dropdown box for selecting the codec
        codec_options = ["ffv1", "rawvideo", "h264", "h265"]
        codec_dropdown = ttk.Combobox(self.root, textvariable=video_settings.output_codec_var, values=codec_options, width=8)
        codec_dropdown.grid(row=1, column=0, padx=(200,0), pady=5, sticky="w")

        # Create a check box for moving the file after processing into it's own folder
        self.remove_input_var =  tk.BooleanVar(value=False)
        self.remove_input_checkbox = ttk.Checkbutton(root, text="Move Input File", variable=self.remove_input_var, width=10)
        self.remove_input_checkbox.grid(row=0, column=0, padx=(87,0), pady=5, sticky="w")

        # Force Overwrites
        self.overwrite_file =  tk.BooleanVar(value=False)
        self.overwrite_file_checkbox = ttk.Checkbutton(root, text="Overwrite Existing", variable=self.overwrite_file, width=17)
        self.overwrite_file_checkbox.grid(row=0, column=0, padx=(175,0), pady=5, sticky="w")

        # Inside the __init__ method of the VideoConverterApp class
        self.open_output_button = ttk.Button(self.root, text="Open Output Directory", command=self.open_output_directory)
        self.open_output_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Create progress and status variables
        self.progress_var = tk.IntVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Select a File")
        # Status Text on bottom of window
        self.status_label = tk.Label(root, textvariable=self.status_var)
        self.status_label.grid(row=7, column=0,columnspan=4, padx=(150,0), pady=5, sticky="w")
        
        # Create progress bar and status text
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        ttk.Label(self.root, text="Log Entries:").grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        columns = ("Directory", "File Name", "Input Codec", "Output Codec", "Input Size", "Output Size", "Relative Size")
        self.log_tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=100)
        self.log_tree.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        self.log_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Load the log file if it exists
        self.load_last_log_entries(video_settings)
    def select_files(self):
        self.file_paths = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.avi *.mkv" "*.3gp" "*.mov" "*.tiff" "*.y4m")])

    def update_log(self):
        
        # Create a new entry dictionary
        self.log_entry = {
            "Directory":        video_settings.file_directory,
            "File Name":        video_settings.file_name,
            "Input Codec":      video_settings.input_codec,
            "Output Codec":     video_settings.output_codec,
            "Input Size":       video_settings.input_size,
            "Output Size":      video_settings.output_size,
            "Relative Size":    video_settings.relative_size
        }

        try:
            # Read the existing log entries or initialize as empty list if log file doesn't exist
            with open(self.settings.log_file, "r") as f:
                log_data_list = json.load(f)
        except FileNotFoundError:
            log_data_list = []

        # Add the new entry to the list of log entries
        log_data_list.append(self.log_entry)

        # Write the updated log entries back to the file
        with open(self.settings.log_file, "w") as f:
            json.dump(log_data_list, f, indent=4)

        # Insert the new entry into the treeview
        self.log_tree.insert("", tk.END, values=(video_settings.file_directory,video_settings.file_name, video_settings.input_codec, video_settings.output_codec, video_settings.input_size, video_settings.output_size, video_settings.relative_size))
    
    def process_files(self):
        self.update_conversion_vars()  # Populate video conversion settings from gui
        try:
            for video_settings.file_path in self.file_paths:
                self.update_current_file_label(video_settings.file_path)
                self.video_processor.convert_video(video_settings,self)
                        
                if self.remove_input_var.get():
                    self.move_input_file(video_settings.file_path)  # Call the function to move the input file

                self.update_log()
        except FileNotFoundError:
            self.status_var.set('Select a File for Conversion')

    def update_current_file_label(self, file_path):
        video_settings.file_name = os.path.basename(file_path)
        self.current_file_label.config(text=f"Current File: {video_settings.file_name}")

    # Read in all conversion variables from the gui
    def update_conversion_vars(self):
        video_settings.crf = video_settings.crf_var.get()
        video_settings.output_codec = video_settings.output_codec_var.get()
    
    def on_tree_select(self,event):
        selected_item = self.log_tree.selection()
        if selected_item:
            values = self.log_tree.item(selected_item, 'values')
            if len(values) >= 3:
                self.settings.explorer_directory = os.path.normpath(values[0])
                self.open_output_button.config(state="normal")

    def move_input_file(self,input_path):
        input_file_name = os.path.basename(input_path)
        input_folder = os.path.join(os.path.dirname(input_path), "inputFiles")
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)
        
        new_input_path = os.path.join(input_folder, input_file_name)
        os.rename(input_path, new_input_path)


    def open_output_directory(self):
        subprocess.Popen(["explorer", os.path.normpath(self.settings.explorer_directory)], shell=True)

    def start_processing(self):
        processing_thread = threading.Thread(target=self.process_files)
        processing_thread.start()

    def load_last_log_entries(self,video_settings):
        try:
            with open(self.settings.log_file, "r") as f:
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

                self.log_tree.insert("", tk.END, values=(file_directory,file_name, input_codec, output_codec, input_size, output_size, relative_size))

        except FileNotFoundError:
            pass  # Handle the case when the log file is not found
    
    
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()