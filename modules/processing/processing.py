# processing.py
import os
import subprocess
import json
import re
import tkinter as tk
from tkinter import messagebox

progress_pattern = re.compile(r"frame=\s*(\d+)")

class VideoProcessor:
    def get_video_info(self, file_path):
        
        ffprobe_command = (
            f'ffprobe -v error -show_entries format:stream=codec_name,format:stream=codec_type,format:stream=r_frame_rate -of json "{file_path}"'
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
        
    def map_codec(self,codec,codec_map):
        if codec in codec_map:
            return codec_map[codec]
        else:
            return codec

    def convert_video(self,video_settings, app):
        # Gather input video information
        video_settings.input_codec, video_settings.input_size, video_settings.total_frames = self.get_video_info(video_settings.file_path)
        video_settings.file_directory = os.path.dirname(video_settings.file_path)
        video_settings.file_name = os.path.basename(video_settings.file_path)
        base_name, ext = os.path.splitext(video_settings.file_name)
        
        # Create ouput video path path information
        video_settings.output_name = f"{base_name}_out.mp4"
        video_settings.output_path = os.path.normpath(os.path.join(video_settings.file_directory, video_settings.output_name))

        # Check if the input file codec matches the desired output codec
        if self.map_codec(video_settings.input_codec,video_settings.codec_map) == video_settings.output_codec:  # Check if input codec matches selected codec
            app.status_var.set(f"Input file is already in {video_settings.output_codec} format, skipping conversion")
            return
        # Check if a converted version of the output file exists
        if os.path.exists(video_settings.output_path):
            response = messagebox.askyesno("File Exists", f"The output file '{video_settings.output_name}' already exists. Do you want to overwrite it?")
            if not response and ~app.overwrite_file.get():
                app.status_var.set("Skipped conversion due to existing output file")
                return
        
        # Create our FFMPEG function call
        video_settings.ffmpeg_codec = self.map_codec(video_settings.output_codec,video_settings.ffmpeg_codec_map)
        # Build the base command with common options
        cmd = [
            "ffmpeg",
            "-y",
            "-loglevel", "quiet", "-stats",
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
            "-c:a", "copy",
            video_settings.output_path,
        ])
    # Create a pipe to capture the output
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

        # Update the progress and output in real-time
        for line in process.stdout:
            match = progress_pattern.search(line)
            if match:
                frame_num = int(match.group(1))
                progress = min(int((frame_num / video_settings.total_frames) * 100), 100)
                app.progress_var.set(progress)
                app.status_var.set("Converting: " + line.strip())  # Update status with FFmpeg output
                app.current_file_label.config(text="Processing: " + video_settings.file_name)  # Update current file label
                app.root.update_idletasks()  # Update the GUI


        process.communicate()  # Wait for the process to finish

        if process.returncode == 0:
            app.status_var.set("Conversion complete")
            app.open_output_button.config(state="normal")  # Enable "Open Output Directory" button
            video_settings.output_size = os.path.getsize(video_settings.output_path)
            video_settings.relative_size = round(video_settings.output_size/video_settings.input_size,3)

        else:
            app.status_var.set("Conversion failed")


        app.root.after(100, lambda: app.root.update())  # Update the GUI every 100 ms



