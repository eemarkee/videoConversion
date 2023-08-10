# processing functions

from settings import progress_pattern, status_var, progress_var, root, log_file, current_file_label
from settings import open_output_button, log_tree, status_label, remove_input_var, progress_var, progress_bar
from settings import crf_label, crf_entry, crf_var
import os
import subprocess
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import threading


def process_files(file_paths):
    for file_path in file_paths:
        convert_to_h265(file_path, remove_input_var.get())

def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
    if file_paths:
        thread = threading.Thread(target=process_files, args=(file_paths,))
        thread.start()

def get_video_info(file_path):
    ffprobe_command = (
        f"ffprobe -v error -show_entries format:stream=codec_name,format:stream=codec_type,format:stream=r_frame_rate -of json {file_path}"
    )

    try:
        result = subprocess.run(ffprobe_command, shell=True, capture_output=True, check=True)
        ffprobe_output = json.loads(result.stdout)

        input_codec = "Unknown"
        frame_rate = 1

        if "streams" in ffprobe_output:
            streams = ffprobe_output["streams"]
            for stream in streams:
                if "codec_name" in stream and stream["codec_type"] == "video":
                    input_codec = stream.get("codec_name", "Unknown")
                    frame_rate_str = stream.get("r_frame_rate", "30/1")  # Default to 30 FPS
                    frame_rate_parts = frame_rate_str.split('/')
                    frame_rate = int(frame_rate_parts[0]) / int(frame_rate_parts[1]) if (frame_rate_parts[1]) != 0 else 1

        if "format" in ffprobe_output:
            formats = ffprobe_output["format"]

        duration = float(ffprobe_output.get("format", {}).get("duration", 0))
        total_frames = int(duration * frame_rate) if frame_rate > 0 else 0

        input_size = os.path.getsize(file_path)  # Get actual file size on disk

        return input_codec, input_size, total_frames
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print("Error:", e)
        return "Unknown", "Unknown", 0, 0

def convert_to_h265(file_path,remove_input):
    global input_codec, input_size, total_frames, file_directory, root
    
    input_codec, input_size, total_frames = get_video_info(file_path)

    if input_codec == "hevc":
        status_var.set("Input file is already in H.265 format, skipping conversion")
        return

    file_directory = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    base_name, ext = os.path.splitext(file_name)
    output_name = f"{base_name}_h265.mp4"
    output_path = os.path.join(file_directory, output_name)

    if os.path.exists(output_path):
        response = messagebox.askyesno("File Exists", f"The output file '{output_name}' already exists. Do you want to overwrite it?")
        if not response:
            status_var.set("Skipped conversion due to existing output file")
            return
        
    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel", "quiet", "-stats",
        "-i", file_path,
        "-c:v", "libx265",
        "-preset", "medium",
        "-x265-params", "crf=28",
        "-c:a", "copy",
        output_path
    ]

   # Create a pipe to capture the output
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

    # Update the progress and output in real-time
    for line in process.stdout:
        match = progress_pattern.search(line)
        if match:
            frame_num = int(match.group(1))
            progress = min(int((frame_num / total_frames) * 100), 100)
            progress_var.set(progress)
            status_var.set("Converting: " + line.strip())  # Update status with FFmpeg output
            current_file_label.config(text="Processing: " + file_name)  # Update current file label
            root.update_idletasks()  # Update the GUI


    process.communicate()  # Wait for the process to finish

    if process.returncode == 0:
        status_var.set("Conversion complete")
        open_output_button.config(state="normal")  # Enable "Open Output Directory" button
        output_size = os.path.getsize(output_path)
        update_log(file_directory,file_name, input_codec, "h265", input_size, output_size, round(output_size/input_size,3))

        if remove_input:
            move_input_file(file_path)  # Call the function to move the input file

    else:
        status_var.set("Conversion failed")


    root.after(100, lambda: root.update())  # Update the GUI every 100 ms

def update_log(file_directory,file_name, input_codec, output_codec, input_size, output_size, relative_size):
    
    # Create a new entry dictionary
    log_entry = {
        "Directory":        file_directory,
        "File Name":        file_name,
        "Input Codec":      input_codec,
        "Output Codec":     output_codec,
        "Input Size":       input_size,
        "Output Size":      output_size,
        "Relative Size":    relative_size
    }

    try:
        # Read the existing log entries or initialize as empty list if log file doesn't exist
        with open(log_file, "r") as f:
            log_data_list = json.load(f)
    except FileNotFoundError:
        log_data_list = []

    # Add the new entry to the list of log entries
    log_data_list.append(log_entry)

    # Write the updated log entries back to the file
    with open(log_file, "w") as f:
        json.dump(log_data_list, f, indent=4)

    # Insert the new entry into the treeview
    log_tree.insert("", tk.END, values=(file_directory,file_name, input_codec, output_codec, input_size, output_size, relative_size))

def move_input_file(input_path):
    input_file_name = os.path.basename(input_path)
    input_folder = os.path.join(os.path.dirname(input_path), "inputFiles")
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
    
    new_input_path = os.path.join(input_folder, input_file_name)
    os.rename(input_path, new_input_path)

def open_output_directory():
    subprocess.Popen(["explorer", os.path.normpath(explorer_directory)], shell=True)

def on_tree_select(event):
    global explorer_directory
    selected_item = log_tree.selection()
    if selected_item:
        values = log_tree.item(selected_item, 'values')
        if len(values) >= 3:
            explorer_directory = os.path.dirname(values[0])
            open_output_button.config(state="normal")


def load_last_log_entries(log_tree):
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
# Gui Elements
open_output_button = tk.Button(root, text="Open Output Directory", command=open_output_directory, state="disabled")
open_output_button.grid(row=2,column=0, padx=5, pady=5, sticky = 'w')