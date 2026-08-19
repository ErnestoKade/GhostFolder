# ========== IMPORT ==========
import sys
import os
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from ui.main import MainWindow


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ========== MAIN ==========
def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = TkinterDnD.Tk()
    root.withdraw()

    app = ctk.CTk()
    app.title("GhostFolder by ErnestoKade")

    # Window icon
    try:
        icon_path = resource_path("assets/icon.ico")
        app.iconbitmap(icon_path)
        app.wm_iconbitmap(icon_path)
    except Exception as e:
        print("Icon error:", e)

    # Support Drag & Drop
    app.tk = root.tk
    app.TkdndVersion = root.TkdndVersion

    MainWindow(app)
    app.mainloop()


if __name__ == "__main__":
    main()