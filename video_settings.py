import tkinter as tk

class VideoSettings:
    def __init__(self):
        self.file_path = ""
        self.file_directory = ""
        self.file_name = ""
        self.output_name = ""
        self.output_path = ""
        self.output_codec_var = tk.StringVar(value="h265")
        self.output_codec = ""
        self.crf_var = tk.StringVar(value=28)
        self.crf = 0
        self.input_codec = ""
        self.input_width = 0
        self.input_height = 0
        self.frame_rate = 0
        self.bit_depth = 8
        self.pixel_format = ""
        self.total_frames = 1
        self.file_paths = []
        self.input_size = 1
        self.output_size = 1
        self.relative_size = 1
        self.total_frames = 0
        self.codec_map = {
            "hevc": "h265",
            "avc": "h264",
        }
        self.ffmpeg_codec_map = {
            "h265": "libx265",
            "h264": "libx264",
            "rawvideo" : "rawvideo",
            "ffv1": "ffv1"
        }        
        self.ffmpeg_codec = ""
video_settings = VideoSettings()