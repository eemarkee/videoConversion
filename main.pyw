# This is the main Python file that launches the GUI for the video converter application.
# It adds the current directory to the system path and imports the VideoConverterApp class from the GUI module.
# It then creates an instance of the VideoConverterApp class and starts the main event loop.
import tkinter as tk
import sys
import os

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    root = tk.Tk()
    from modules.gui.gui import VideoConverterApp
    app = VideoConverterApp(root)

    root.mainloop()