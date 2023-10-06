# processing.py
import os
import subprocess
import json
import re
import tkinter as tk
from tkinter import messagebox
from modules.settings.settings import Settings
import tempfile

progress_pattern = re.compile(r"frame=\s*(\d+)")

class VideoProcessor:
    """
    A class for processing video inputs using the ffmpeg library.

    Methods:
    - get_video_info(file_path): Returns a dictionary containing information about the video file at the given path.
    - map_codec(output_codec, codec_map): Maps the output codec to the corresponding ffmpeg codec.
    """    
    def __init__(self):
        self.settings = Settings()
    def get_video_info(self, file_path):
        """
        Returns a dictionary containing information about the video file at the given path.

        Parameters:
        - file_path: The path to the video file

        Returns:
        A dictionary containing the following keys:
        - input_codec: The codec used in the input video
        - input_size: The size of the input video file in bytes
        - total_frames: The total number of frames in the input video
        - frame_rate: The frame rate of the input video in frames per second

        Raises:
        - subprocess.CalledProcessError: If there's an error executing the ffprobe command
        """
        ffprobe_command = (
            f'{self.settings.ffprobe_path} -v error -show_entries format:stream=codec_name,format:stream=codec_type,format:stream=r_frame_rate -of json "{file_path}"'
        )

        try:
            result = subprocess.run(ffprobe_command, shell=True, capture_output=True, check=True)
            
            ffprobe_output = json.loads(result.stdout)
            if self.settings.debug:
                print(ffprobe_output)
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

            return input_codec, input_size, total_frames, frame_rate
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            print(e.output.decode())  # print the actual output of the command for more information
        
    def map_codec(self,codec,codec_map):
        """
        Maps the input codec to the corresponding ffmpeg codec using the given codec map.

        Parameters:
        - codec: The input codec to map
        - codec_map: A dictionary mapping input codecs to ffmpeg codecs

        Returns:
        The corresponding ffmpeg codec for the input codec, or the input codec if it's not in the codec map.
        """
        if codec in codec_map:
            return codec_map[codec]
        else:
            return codec

    def convert_video(self,video_settings, app):
        """
        Converts a video file to a different codec using ffmpeg.

        Parameters:
        - video_settings: A settings object containing video-related configurations
        - app: The main application or GUI object to update progress

        Returns:
        - "SKIPPED" if the input file is already in the desired output codec and overwrite_file is False
        - None if the conversion is successful

        Raises:
        - Exception: If there's an error during conversion
        """        
        # Gather input video information
        video_settings.input_codec, video_settings.input_size, video_settings.total_frames, video_settings.input_frame_rate = self.get_video_info(video_settings.file_path)
        video_settings.input_codec = self.map_codec(video_settings.input_codec, video_settings.codec_map)
        video_settings.file_directory = os.path.dirname(video_settings.file_path)
        video_settings.file_name = os.path.basename(video_settings.file_path)
        base_name, ext = os.path.splitext(video_settings.file_name)
    
        # Create ouput video path path information
        output_ext = self.map_codec(video_settings.output_codec,video_settings.output_ext_map)
        video_settings.output_name = f"{base_name}_out{output_ext}"
        video_settings.output_path = os.path.normpath(os.path.join(video_settings.file_directory, video_settings.output_name))
        # Check if the input file codec matches the desired output codec
        if (self.map_codec(video_settings.input_codec,video_settings.codec_map) == video_settings.output_codec) and not app.overwrite_file.get():  # Check if input codec matches selected codec
            app.status_var.set(f"Input file is already in {video_settings.output_codec} format, skipping conversion")
            return "SKIPPED"
        
        # Check if a converted version of the output file exists
        if os.path.exists(video_settings.output_path) and not app.overwrite_file.get():
            response = messagebox.askyesno("File Exists", f"The output file '{video_settings.output_name}' already exists. Do you want to overwrite it?")
            if not response:
                app.status_var.set("Skipped conversion due to existing output file")
                return "SKIPPED"
        
        # Check if we want to overwrite the frame rate
        if app.overwrite_fps.get():
            video_settings.output_frame_rate = video_settings.input_frame_rate

        # Create our FFMPEG function call
        video_settings.ffmpeg_codec = self.map_codec(video_settings.output_codec,video_settings.ffmpeg_codec_map)
        # Build the base command with common options
        cmd = [
            f'{self.settings.ffmpeg_path}',
            "-y",
            "-loglevel", "error", "-stats",
        ]
        if app.use_start_stop.get():
            cmd.extend([
                "-ss", video_settings.start_time
            ])
            if video_settings.stop_time != "-1":
                cmd.extend([
                "-to", video_settings.stop_time
            ])
        cmd.extend([
            "-i", str(video_settings.file_path),
        ])
        if app.overwrite_fps.get():
            cmd.extend(["-r", str(int(video_settings.output_frame_rate))])
        # Check if video_settings.scale_width or video_settings.scale_height are not equal to one
        if video_settings.scale_width != 1 or video_settings.scale_height != 1:
            cmd.append("-vf")
            cmd.append(
                f"scale=iw*{video_settings.scale_width}:ih*{video_settings.scale_height}"
            )
        # Add codec-specific options based on output_codec
        if video_settings.output_codec == "ffv1":
            cmd.extend([
                "-c:v", "ffv1",
                "-level", "3", "-coder", "1", "-context", "1",
            ])
        elif video_settings.output_codec == "h264":
            cmd.extend([
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", str(video_settings.crf),
            ])
        elif video_settings.output_codec == "h265":
            cmd.extend([
                "-c:v", "libx265",
                "-preset", "medium",
                "-crf", str(video_settings.crf),
            ])
        elif video_settings.output_codec == "rawvideo":
            cmd.extend([
                "-c:v", "rawvideo",
                "-pix_fmt", "yuv420p",
            ])
            
        
        # Add common options for audio and output file
        cmd.extend([
            #"-c:a", "copy", # this sometimes causes an error during conversion... might just let ffmpeg determine the audio codec
            video_settings.output_path,
        ])

        # Create a pipe to capture the output
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

        # Update the progress and output in real-time
        for line in process.stdout:
            match = progress_pattern.search(line)
            if self.settings.debug:
                print(line)
            if match:
                frame_num = int(match.group(1))
                progress = min(int((frame_num / video_settings.total_frames) * 100), 100)
                app.progress_var.set(progress)
                app.status_var.set("Converting: " + line.strip())  # Update status with FFmpeg output
                app.current_file_label.config(text="Processing: " + video_settings.file_name)  # Update current file label
                app.root.update_idletasks()  # Update the GUI

        # Capture the error message if the process fails
        _, stderr = process.communicate()

        if process.returncode == 0:
            app.status_var.set("Conversion complete")
            app.open_output_button.config(state="normal")  # Enable "Open Output Directory" button
            video_settings.output_size = os.path.getsize(video_settings.output_path)
            video_settings.relative_size = round(video_settings.output_size/video_settings.input_size,3)

        else:
            video_settings.cmd = ' '.join(cmd)
            video_settings.error = stderr
            app.status_var.set(f"Conversion failed: {stderr}")

        app.root.after(100, lambda: app.root.update())  # Update the GUI every 200 ms
        app.progress_var.set(100)
    
    def process_tiffs_to_video(self, tiff_files, ffmpeg_path, video_settings, app):
        """
        Converts a sequence of TIFF images to a video.
        
        Parameters:
        - tiff_files: List of paths to the TIFF images
        - ffmpeg_path: Path to the ffmpeg executable
        - video_settings: A settings object containing video-related configurations
        - app: The main application or GUI object to update progress
        
        Returns:
        None
        
        Raises:
        - Exception: If there's an error during conversion
        """
        # Make sure the files are in the correct order
        sorted_files = sorted(tiff_files)
        
        # Create a temporary text file to list all TIFFs
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as list_file:
            for file in sorted_files:
                list_file.write(f"file '{file}'\n")
            temp_filename = list_file.name

        # Define the output video name based on the first file
        first_file = sorted_files[0]
        dir_name = os.path.dirname(first_file)
        output_file = os.path.join(dir_name, os.path.basename(first_file).split('.')[0] + '_output.mp4')
        
        # Create our FFMPEG function call
        video_settings.ffmpeg_codec = self.map_codec(video_settings.output_codec,video_settings.ffmpeg_codec_map)
        # Build the base command with common options

        f'{ffmpeg_path} -y -f concat -safe 0 -r 30 -i "{temp_filename}" -c:v libx264 -pix_fmt yuv420p "{output_file}"'
        cmd = [
            f'{self.settings.ffmpeg_path}',
            "-y",
            "-loglevel", "quiet", "-stats",
            "concat", "-safe 0", "-r",
            video_settings.output_frame_rate,
            "-i", video_settings.file_path,
        ]
        # Add codec-specific options based on output_codec
        if video_settings.output_codec == "ffv1":
            cmd.extend([
                "-c:v", "ffv1",
                "-level", "3", "-coder", "1", "-context", "1",
            ])
        elif video_settings.output_codec == "h264":
            cmd.extend([
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", str(video_settings.crf),
            ])
        elif video_settings.output_codec == "h265":
            cmd.extend([
                "-c:v", "libx265",
                "-preset", "medium",
                "-crf", str(video_settings.crf),
            ])
        elif video_settings.output_codec == "rawvideo":
            cmd.extend([
                "-c:v", "rawvideo",
                "-pix_fmt", "yuv420p",
            ])
            video_settings.output_path = os.path.normpath(os.path.join(video_settings.file_directory, f"{video_settings.output_name}.avi"))

        # Add common options for audio and output file
        cmd.extend([
            #"-c:a", "copy",
            video_settings.output_path,
        ])


        # Construct the ffmpeg command
        cmd = f'{ffmpeg_path} -y -f concat -safe 0 -r 30 -i "{temp_filename}" -c:v libx264 -pix_fmt yuv420p "{output_file}"'
        
        # Execute the command
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

            for line in process.stdout:
                match = progress_pattern.search(line)
                if match:
                    frame_num = int(match.group(1))
                    progress = min(int((frame_num / video_settings.total_frames) * 100), 100)
                    app.progress_var.set(progress)
                    app.status_var.set("Converting: " + line.strip())  # Update status with FFmpeg output
                    app.current_file_label.config(text="Processing: " + video_settings.file_name)  # Update current file label
                    app.root.update_idletasks()  # Update the GUI
            
            process.communicate()

            if process.returncode == 0:
                print(f"Video created successfully: {output_file}")
                # Create log information
                video_settings.file_directory = os.path.dirname(video_settings.file_path)
                video_settings.file_name = os.path.basename(first_file)
                base_name, ext = os.path.splitext(video_settings.file_name)
                video_settings.output_name = f"{base_name}_out.mp4"
                video_settings.output_path = os.path.normpath(os.path.join(video_settings.file_directory, video_settings.output_name))
                video_settings.input_codec = 'TIFF'
                video_settings.output_codec = video_settings.output_codec
                video_settings.input_size = os.path.getsize(first_file) * len(sorted_files)  # Multiplying size of first file with total number of files
                video_settings.output_size = os.path.getsize(output_file)
                video_settings.relative_size = round(os.path.getsize(output_file) / (os.path.getsize(first_file) * len(sorted_files)),3)
            else:
                # Handle error
                print("Error converting TIFFs to video:")
            # add log file information
        finally:
            os.remove(temp_filename)  # Clean up the temporary file