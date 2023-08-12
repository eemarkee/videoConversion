# main.pyw
import tkinter as tk
import sys
import os

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    root = tk.Tk()
    from modules.gui.gui import VideoConverterApp
    app = VideoConverterApp(root)

    root.mainloop()