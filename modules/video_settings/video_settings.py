# video_settings.py
import tkinter as tk
import os
import json

class VideoSettings:    
    """
    A class to handle the settings for video processing. These settings include codec details,
    video dimensions, file paths, and other related configurations. The settings can be loaded from 
    a configuration JSON file, or set to default values if the file doesn't exist.

    Attributes:
    Various attributes related to video settings and configurations.

    Methods:
    - load_config(config_file_path): Loads video settings from a given configuration file.
    - set_defaults(): Sets the default values for the video settings.
    """
    def __init__(self, config_path="video_settings.json"):
        """
        Initializes a new instance of the VideoSettings class. It sets up the configuration 
        based on the provided JSON file or defaults if the file doesn't exist.

        Parameters:
        - config_path (str): Path to the configuration file relative to the module's directory. 
                             Defaults to "video_settings.json".
        """
           
        module_dir = os.path.dirname(os.path.abspath(__file__))

        # Form the path to the configuration file relative to this module's directory
        config_file_path = os.path.join(module_dir,config_path)

        self.load_config(config_file_path)
        
        self.output_codec_var = tk.StringVar(value=self.output_codec)
        self.crf_var = tk.StringVar(value=self.crf)
        self.scale_width_var = tk.DoubleVar(value=self.scale_width)
        self.scale_height_var = tk.DoubleVar(value=self.scale_height)
        self.start_time_var = tk.StringVar(value=self.start_time)
        self.stop_time_var = tk.StringVar(value=self.stop_time)
        self.frame_rate_var = tk.StringVar(value=self.frame_rate)
        
    def load_config(self, config_file_path):
        """
        Load video settings from a configuration file. If the configuration file doesn't exist, 
        default values are set using the `set_defaults` method.

        Parameters:
        - config_file_path (str): Absolute path to the configuration file to be loaded.
        """
        if os.path.exists(config_file_path):
            self.set_defaults()
            with open(config_file_path, "r") as config_file:
                config_data = json.load(config_file)

            # Load values from the config file or set default values
            self.file_path = config_data.get("file_path", "")
            self.file_directory = config_data.get("file_directory", "")
            self.file_name = config_data.get("file_name", "")
            self.output_name = config_data.get("output_name", "")
            self.output_path = config_data.get("output_path", "")
            self.output_codec = config_data.get("output_codec", "h265")
            self.crf = config_data.get("crf", 28)
            self.input_codec = config_data.get("input_codec", "")
            self.input_width = config_data.get("input_width", 0)
            self.input_height = config_data.get("input_height", 0)
            self.frame_rate = config_data.get("frame_rate", 30)
            self.bit_depth = config_data.get("bit_depth", 8)
            self.pixel_format = config_data.get("pixel_format", "")
            self.total_frames = config_data.get("total_frames", 1)
            self.file_paths = config_data.get("file_paths", [])
            self.input_size = config_data.get("input_size", 1)
            self.output_size = config_data.get("output_size", 1)
            self.relative_size = config_data.get("relative_size", 1)
            self.start_time = config_data.get("start_time", 0.0)
            self.scale_width = config_data.get("scale_width", 1)
            self.scale_height = config_data.get("scale_height", 1)
            self.stop_time = config_data.get("stop_time", -1)
            self.codec_map = config_data.get("codec_map", {
                "hevc": "h265",
                "avc": "h264",
            })
            self.ffmpeg_codec_map = config_data.get("ffmpeg_codec_map", {
                "h265": "libx265",
                "h264": "libx264",
                "rawvideo" : "rawvideo",
                "ffv1": "ffv1"
            })
            self.output_ext_map = config_data.get("output_ext_map", {
                "h265": ".mp4",
                "h264": ".mp4",
                "rawvideo" : ".avi",
                "ffv1": ".mkv"
            })
            self.ffmpeg_codec = config_data.get("ffmpeg_codec", "")
        else:
            # Default values if config file does not exist
            self.set_defaults()

    def set_defaults(self):
        """
        Set default values for the video settings. This method is called when a configuration file 
        doesn't exist or when there's a need to reset the settings to their default values.
        """
        self.file_path = ""
        self.file_directory = ""
        self.file_name = ""
        self.output_name = ""
        self.output_path = ""
        self.output_codec = "h264"
        self.crf = 28
        self.frame_rate = 30
        self.output_frame_rate = 30
        self.input_frame_rate = 30
        self.input_codec = ""
        self.input_width = 0
        self.input_height = 0
        self.bit_depth = 8
        self.pixel_format = ""
        self.total_frames = 1
        self.file_paths = []
        self.input_size = 1
        self.output_size = 1
        self.relative_size = 1
        self.start_time = 0.0
        self.stop_time = -1
        self.codec_map = {
            "hevc": "h265",
            "avc": "h264",
        }
        self.ffmpeg_codec_map = {
            "h265": "libx265",
            "h264": "libx264",
            "rawvideo" : "rawvideo",
            "ffv1": "ffv1"
        },
        self.output_ext_map = {
                "h265": ".mp4",
                "h264": ".mp4",
                "rawvideo" : ".avi",
                "ffv1": ".mkv"
        },
        self.ffmpeg_codec = ""

video_settings = VideoSettings()
