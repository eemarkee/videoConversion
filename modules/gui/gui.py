# gui.py
import json
import tkinter as tk
from tkinter import ttk, filedialog
from modules.video_settings.video_settings import video_settings
from modules.processing.processing import VideoProcessor
from modules.settings.settings import Settings
import os
import subprocess
import threading



class VideoConverterApp:
    """
    A GUI application for converting video files using ffmpeg.

    Methods:
    - __init__(self): Initializes the application and sets up the GUI
    - browse_file(self): Opens a file dialog to select a video file to convert
    - browse_output_dir(self): Opens a directory dialog to select the output directory
    - convert_video(self): Converts the selected video file to the desired output codec
    - update_progress(self, progress): Updates the progress bar with the given value
    """
    def __init__(self, root, config_path="gui_config.json"):
        """
        Initializes the application and sets up the GUI.
        """
        # Determine the directory of the current module
        module_dir = os.path.dirname(os.path.abspath(__file__))

        # Form the path to the configuration file relative to this module's directory
        config_file_path = os.path.join(module_dir, config_path)

        self.config = self.load_config(config_file_path)

        # UI related variables
        self.root = root
        self.root.title(self.config['window']['title'])
        self.video_processor = VideoProcessor()  # Pass the selected codec name
        self.settings = Settings()
        self.config = self.load_config(config_file_path)

        # Create and place GUI elements using grid
        ttk.Button(self.root, text="Select Files", command=self.select_files).grid(row=0, column=0, padx=5, pady=0, sticky="w")

        # Create a Current File Text
        # ttk.Label(self.root, text="Current File:").grid(row=0, column=1, padx=5, pady=0, sticky="e")
        self.current_file_label = ttk.Label(self.root, text="")
        self.current_file_label.grid(row=4, column=0, padx=120, pady=0, sticky="w")

        scale_width_x = 0
        scale_width_x_box = scale_width_x + 80
        # Scale Width Value
        ttk.Label(self.root, text="Scale Width:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.scale_width_entry = ttk.Entry(self.root,textvariable=video_settings.scale_width_var, width=3)
        self.scale_width_entry.grid(row=3, column=0, padx=scale_width_x_box, pady=5, sticky="w")

        scale_height_x = scale_width_x_box + 20
        scale_height_x_box = scale_height_x + 80
        # Scale Height Value
        ttk.Label(self.root, text="Scale Height:").grid(row=3, column=0, padx=scale_height_x, pady=5, sticky="w")
        self.scale_height_entry = ttk.Entry(self.root,textvariable=video_settings.scale_height_var, width=3)
        self.scale_height_entry.grid(row=3, column=0,padx=scale_height_x_box, pady=5, sticky="w")

        
        # CRF Codec Value
        crf_x = 280
        ttk.Label(self.root, text="CRF:").grid(row=1, column=0, padx=(crf_x,0), pady=0, sticky="w")
        
        crf_entry_width = 2  # Adjust the width as needed
        self.crf_entry = ttk.Entry(self.root, textvariable=video_settings.crf_var, width=crf_entry_width)
        self.crf_entry.grid(row=1, column=0, padx=(crf_x+30,2), pady=0, sticky="w")

        # Start Time Value
        start_time_x = 430
        ttk.Label(self.root, text="Start Time:").grid(row=1, column=0, padx=(start_time_x,0), pady=0, sticky="w")
        
        start_time_entry_width = 5  # Adjust the width as needed
        self.crf_entry = ttk.Entry(self.root, textvariable=video_settings.start_time_var, width=start_time_entry_width)
        self.crf_entry.grid(row=1, column=0, padx=(start_time_x+60,2), pady=0, sticky="w")

        # Stop Time Value
        stop_time_x = 525
        ttk.Label(self.root, text="Stop Time:").grid(row=1, column=0, padx=(stop_time_x,0), pady=0, sticky="w")
        
        stop_time_entry_width = 5  # Adjust the width as needed
        self.crf_entry = ttk.Entry(self.root, textvariable=video_settings.stop_time_var, width=stop_time_entry_width)
        self.crf_entry.grid(row=1, column=0, padx=(stop_time_x+60,2), pady=0, sticky="w")

         # Frame Rate Value
        frame_rate_x = 330
        ttk.Label(self.root, text="Frame Rate:").grid(row=1, column=0, padx=(frame_rate_x,0), pady=0, sticky="w")
        
        frame_rate_entry_width = 4  # Adjust the width as needed
        self.frame_rate = ttk.Entry(self.root, textvariable=video_settings.frame_rate_var, width=frame_rate_entry_width)
        self.frame_rate.grid(row=1, column=0, padx=(frame_rate_x+65,2), pady=0, sticky="w")
        
        # Create a button to start processing
        self.start_processing_button = ttk.Button(self.root, text="Start Processing", command=self.start_processing)
        self.start_processing_button.grid(row=1, column=0, columnspan=3, padx=5, pady=0, sticky="w")
        
        # Create a button to wipe the log file
        self.clear_log_btn = ttk.Button(self.root, text="Clear Log", command=self.clear_log)
        self.clear_log_btn.grid(row=5, column=2, columnspan=1, padx=5, pady=0, sticky="e")
        
        # Create a label for the codec dropdown box
        self.codec_label = tk.Label(self.root, text="Output Codec:", width = 10)
        self.codec_label.grid(row=1, column=0, padx=(110,5), pady=0, sticky="w")

        # Create a dropdown box for selecting the codec
        codec_options = ["ffv1", "rawvideo", "h264", "h265"]
        codec_dropdown = ttk.Combobox(self.root, textvariable=video_settings.output_codec_var, values=codec_options, width=8)
        codec_dropdown.grid(row=1, column=0, padx=(200,0), pady=0, sticky="w")

        # Create a check box for moving the file after processing into it's own folder
        self.remove_input_var =  tk.BooleanVar(value=False)
        self.remove_input_checkbox = ttk.Checkbutton(root, text="Move Input File", variable=self.remove_input_var, width=10)
        self.remove_input_checkbox.grid(row=0, column=0, padx=(87,0), pady=0, sticky="w")

        # Force Overwrites
        self.overwrite_file =  tk.BooleanVar(value=False)
        self.overwrite_file_checkbox = ttk.Checkbutton(root, text="Force Output", variable=self.overwrite_file, width=17)
        self.overwrite_file_checkbox.grid(row=0, column=0, padx=(175,0), pady=0, sticky="w")

        # Overwrite Framerate
        force_frame_x = 270
        self.overwrite_fps =  tk.BooleanVar(value=False)
        self.overwrite_fps_checkbox = ttk.Checkbutton(root, text="Force Frame Rate", variable=self.overwrite_fps, width=17)
        self.overwrite_fps_checkbox.grid(row=0, column=0, padx=(force_frame_x,0), pady=0, sticky="w")

        # Use Start/Stop Time
        use_start_stop_x = 385
        self.use_start_stop =  tk.BooleanVar(value=False)
        self.overwrite_fps_checkbox = ttk.Checkbutton(root, text="Use Start/Stop Time", variable=self.use_start_stop, width=20)
        self.overwrite_fps_checkbox.grid(row=0, column=0, padx=(use_start_stop_x,0), pady=0, sticky="w")

        # Open Output Directory
        self.open_output_button = ttk.Button(self.root, text="Open Output Directory", command=self.open_output_directory)
        self.open_output_button.grid(row=7, column=0, columnspan=2, padx=0, pady=0, sticky="w")
        
        # Create progress and status variables
        self.progress_var = tk.IntVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Select a File")

        # Status Text on bottom of window
        self.status_label = tk.Label(root, textvariable=self.status_var,wraplength=500)
        self.status_label.grid(row=7, column=0,columnspan=4, padx=(150,0), pady=0, sticky="w")
        
        # Create progress bar and status text
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, padx=5, pady=2, sticky="w")

        ttk.Label(self.root, text="Log Entries:").grid(row=5, column=0, columnspan=3, padx=5, pady=0, sticky="w")


        # Extract columns configuration
        columns_config = self.config['columns']

        ttk.Label(self.root, text="Log Entries:").grid(row=5, column=0, columnspan=3, padx=5, pady=0, sticky="w")

        column_names = [col['name'] for col in columns_config]

        self.log_tree = ttk.Treeview(self.root, columns=column_names, show="headings")

        for col_config in columns_config:
            col_name = col_config['name']
            width = col_config['width']
            anchor = col_config['alignment']

            self.log_tree.heading(col_name, text=col_name)
            self.log_tree.column(col_name, width=width, anchor=anchor)

        self.log_tree.grid(row=6, column=0, columnspan=3, padx=5, pady=0, sticky="w")
        self.log_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Load the log file if it exists
        self.load_last_log_entries()
    def select_files(self):
        """
        Opens a file dialog to select a video file to convert.

        Returns:
        The path to the selected file, or None if no file is selected.
        """
        self.file_paths = filedialog.askopenfilenames(filetypes=[
            ("Video Files", "*.mp4;*.avi;*.m4v;*.mkv;*.3gp;*.mov;*.wmv"),
            ("Image Files", "*.tif;*.tiff"),
        ])
    def update_log(self):
        """
        Updates the log file with the current video conversion settings and adds a new entry to the log treeview.

        Returns:
        None
        """
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
            with open(self.settings.log_file, 'r+') as log_file:
                log_data_list = json.load(log_file)
                log_data_list.reverse()
                # Append the new log data
                log_data_list.append(self.log_entry)
                
                # Go back to the start of the file
                log_file.seek(0)
                
                # Write the updated log data
                json.dump(log_data_list, log_file, indent=4)
                
                # Truncate the file to the current position (this will remove any data beyond this point)
                log_file.truncate()

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
        """
        Processes the selected video files and converts them to the desired output codec.

        Returns:
        None
        """
        self.update_conversion_vars()  # Populate video conversion settings from gui
        try:
            video_settings.output_frame_rate = int(self.frame_rate.get())
            # Check if all files have the .tif or .tiff extension
            if all(fp.lower().endswith(('.tif', '.tiff')) for fp in self.file_paths):
                # Process all TIFFs as one video
                video_settings.file_path = self.file_paths[0]
                self.update_current_file_label(video_settings.file_path)
                result = self.video_processor.process_tiffs_to_video(self.file_paths, self.settings.ffmpeg_path, video_settings, self)
                if result == "SKIPPED":
                    print(f"Skipped conversion for {video_settings.file_name}")
                else:
                    self.update_log()
            else:
                for video_settings.file_path in self.file_paths:
                    self.update_current_file_label(video_settings.file_path)
                    result = self.video_processor.convert_video(video_settings,self)

                    if result == "SKIPPED":
                        print(f"Skipped conversion for {video_settings.file_name}")
                    else:
                        self.update_log()

                    if self.remove_input_var.get():
                        self.move_input_file(video_settings.file_path)  # Call the function to move the input file
        except FileNotFoundError:
            self.status_var.set('Select a File for Conversion')

    def update_current_file_label(self, file_path):
        """
        Updates the current file label with the name of the current file being processed.

        Parameters:
        - file_path: The path to the current file being processed.

        Returns:
        None
        """        
        video_settings.file_name = os.path.basename(file_path)
        self.current_file_label.config(text=f"Current File: {video_settings.file_name}")

    # Read in all conversion variables from the gui
    def update_conversion_vars(self):
        """
        Reads in all conversion variables from the GUI and updates the corresponding video settings object.

        Returns:
        None
        """
        video_settings.crf = video_settings.crf_var.get()
        video_settings.scale_width = video_settings.scale_width_var.get()
        video_settings.scale_height = video_settings.scale_height_var.get()
        video_settings.frame_rate = video_settings.frame_rate_var.get()
        video_settings.output_codec = video_settings.output_codec_var.get()
        video_settings.start_time = video_settings.start_time_var.get()
        video_settings.stop_time = video_settings.stop_time_var.get()
    
    def on_tree_select(self,event): 
        """
        Updates the current file label and video settings object with the selected file from the log treeview.

        Parameters:
        - event: The event object containing information about the treeview selection.

        Returns:
        None
        """
        selected_item = self.log_tree.selection()
        if selected_item:
            values = self.log_tree.item(selected_item, 'values')
            if len(values) >= 3:
                self.settings.explorer_directory = os.path.normpath(values[0])
                self.open_output_button.config(state="normal")

    def move_input_file(self,input_path):
        """
        Moves the specified input file to a subdirectory called 'inputFiles' within the directory 
        of the provided path. If the 'inputFiles' directory does not exist, it is created.

        Parameters:
        - input_path (str): The absolute path of the file to be moved.

        Returns:
        None
        """
        input_file_name = os.path.basename(input_path)
        input_folder = os.path.join(os.path.dirname(input_path), "inputFiles")
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)
        
        new_input_path = os.path.join(input_folder, input_file_name)
        os.rename(input_path, new_input_path)


    def open_output_directory(self):
        """
        Opens the output directory using the system's default file explorer. The directory is 
        specified by the `explorer_directory` attribute of the `settings` instance.

        Returns:
        None
        """
        subprocess.Popen(["explorer", os.path.normpath(self.settings.explorer_directory)], shell=True)

    def start_processing(self):
        """
        Initiates the file processing by spawning a new thread. The processing task is defined by 
        the `process_files` method of this instance.

        Returns:
        None
        """
        processing_thread = threading.Thread(target=self.process_files)
        processing_thread.start()

    def load_last_log_entries(self):
        """
        Loads the last 15 entries from the log file (or all entries if there are fewer than 15). 
        Each log entry contains details about file processing. The details are extracted and inserted 
        into the `log_tree` attribute, which is presumably a treeview widget.

        In case the log file does not exist, the function silently continues without any action.

        Returns:
        None
        """
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
    
    def clear_log(self):

        """
        Clears the log file by overwriting it with an empty JSON array. Also updates any related GUI 
        components to reflect the cleared log, such as a status indicator and a treeview widget.

        Returns:
        None
        """
        with open(self.settings.log_file, 'w') as log_file:
            log_file.write("[]")

        # Optionally: Notify the user
        self.status_var.set("Log cleared successfully!")
        self.log_tree.delete(*self.log_tree.get_children())
    
    def load_config(self,config_file_path):        
        """
        Loads the configuration from a specified JSON file.

        Parameters:
        - config_file_path (str): The path to the configuration file to be loaded.

        Returns:
        dict: A dictionary containing the configuration data. If the file is not found, 
              an empty dictionary is returned.
        """
        try:
            with open(config_file_path, 'r') as file:
                config = json.load(file)
            return config
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_file_path}' not found.")
            return {}

    
    
