import unittest
from gui import get_video_info, convert_to_h265
import os

class Testgui(unittest.TestCase):
    def test_get_video_info(self):
        input_codec, input_size, total_frames = get_video_info("test_video.mp4")
        self.assertEqual(input_codec, "h264")
        self.assertGreater(input_size, 0)
        self.assertGreater(total_frames, 0)

    def test_convert_to_h265(self):
        # Prepare a test video file
        test_input_file = "test_input.mp4"

        # Perform the conversion
        convert_to_h265(test_input_file, remove_input=False)

        # Check if the output file was created
        self.assertTrue(os.path.exists("test_input_h265.mp4"))

if __name__ == '__main__':
    unittest.main()