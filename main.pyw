import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    from gui import VideoConverterApp
    app = VideoConverterApp(root)

    root.mainloop()