# ========== IMPORT ==========
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from ui.main import MainWindow

# ========== MAIN ==========
def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = TkinterDnD.Tk()
    root.withdraw()

    app = ctk.CTk()
    app.title("GhostFolder by ErnestoKade")

    # Support Drag & Drop
    app.tk = root.tk
    app.TkdndVersion = root.TkdndVersion

    MainWindow(app)
    app.mainloop()

if __name__ == "__main__":
    main()