# ========== IMPORT ==========
import os
import customtkinter as ctk
from tkinter import messagebox, filedialog
from engine.ghost import recover_ghost, load_ghosts, add_files_to_ghost, get_storage_path
from engine.timer import check_expired_ghosts, get_active_ghosts, get_time_remaining
from engine.crypto import test_password
from ui.dialogs import CreateGhostDialog, SelectStorageDialog
from pathlib import Path

# ========== CLASS ==========
class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.configure(fg_color="#0f0f0f")
        self.root.title("GhostFolder by ErnestoKade")
        self.root.geometry("960x700")
        self.root.minsize(820, 620)

        self.selected_ghost = None

        if get_storage_path() is None:
            dialog = SelectStorageDialog(self.root)
            self.root.wait_window(dialog)
            if dialog.result is None:
                self.root.destroy()
                return

        check_expired_ghosts()
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        title = ctk.CTkLabel(self.root, text="GhostFolder", font=ctk.CTkFont(size=28))
        title.pack(pady=(25, 15))

        btn_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Create Ghost Folder", width=180, height=40,
                      command=self.open_create_dialog).pack(side="left", padx=8)

        ctk.CTkButton(btn_frame, text="Recover", width=120, height=40,
                      command=self.recover_selected).pack(side="left", padx=8)

        ctk.CTkButton(btn_frame, text="Add Files", width=110, height=40,
                      command=self.add_files_selected).pack(side="left", padx=8)

        ctk.CTkButton(btn_frame, text="Refresh", width=110, height=40,
                      fg_color="gray", command=self.refresh_list).pack(side="left", padx=8)

        list_container = ctk.CTkFrame(self.root, fg_color="#1E1E1E")
        list_container.pack(fill="both", expand=True, padx=30, pady=15)

        self.scrollable_frame = ctk.CTkScrollableFrame(list_container, fg_color="#1E1E1E")
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.ghost_buttons = {}

        self.status = ctk.CTkLabel(self.root, text="Ready", anchor="w",
                                   font=ctk.CTkFont(size=13))
        self.status.pack(side="bottom", fill="x", padx=20, pady=8)

    def open_create_dialog(self):
        dialog = CreateGhostDialog(self.root)
        self.root.wait_window(dialog)
        if dialog.result:
            self.refresh_list()

    def refresh_list(self):
        check_expired_ghosts()

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.ghost_buttons.clear()
        self.selected_ghost = None

        ghosts = get_active_ghosts()

        if not ghosts:
            label = ctk.CTkLabel(self.scrollable_frame, text="No active Ghost Folder.",
                                 font=ctk.CTkFont(size=14))
            label.pack(pady=20)
        else:
            for name, data in ghosts.items():
                expire = data["expire_date"]
                mode = data.get("destruction_mode", "soft").upper()
                remaining = get_time_remaining(name) or "?"
                
                text = f"{name}   |   {mode}   |   expires: {expire}   |   remaining: {remaining}"

                btn = ctk.CTkButton(
                    self.scrollable_frame,
                    text=text,
                    anchor="w",
                    height=40,
                    fg_color=("gray85", "gray25"),
                    hover_color=("gray75", "gray35"),
                    command=lambda n=name: self.select_ghost(n)
                )
                btn.pack(fill="x", pady=4, padx=5)
                self.ghost_buttons[name] = btn

        self.status.configure(text=f"{len(ghosts)} active Ghost Folder(s)")

    def select_ghost(self, name):
        self.selected_ghost = name
        for n, btn in self.ghost_buttons.items():
            if n == name:
                btn.configure(fg_color=("#3B8ED0", "#1F6AA5"))
            else:
                btn.configure(fg_color=("gray85", "gray25"))

    def add_files_selected(self):
        if not self.selected_ghost:
            messagebox.showwarning("Warning", "Please select a Ghost Folder first.")
            return

        name = self.selected_ghost

        password_dialog = ctk.CTkToplevel(self.root)
        password_dialog.title("Password")
        password_dialog.geometry("400x190")
        password_dialog.resizable(False, False)
        password_dialog.transient(self.root)
        password_dialog.grab_set()

        ctk.CTkLabel(password_dialog, text=f"Password for '{name}':",
                     font=ctk.CTkFont(size=14)).pack(pady=(25, 12))

        password_entry = ctk.CTkEntry(password_dialog, show="*", width=300, height=36)
        password_entry.pack()
        password_entry.focus()

        def do_add():
            password = password_entry.get()
            if not password:
                messagebox.showwarning("Warning", "Password is required.")
                return

            ghosts = load_ghosts()
            ghost = ghosts.get(name)
            if not ghost or ghost["status"] != "active" or not ghost["files"]:
                messagebox.showerror("Error", "Ghost Folder not available.")
                password_dialog.destroy()
                return

            first_file = ghost["files"][0]
            encrypted_path = Path(ghost["path"]) / first_file
            salt = bytes.fromhex(ghost["salts"][first_file])

            password_ok = test_password(str(encrypted_path), password, salt)

            if not password_ok:
                recover_ghost(name, password=password, output_folder="")
                ghosts = load_ghosts()
                ghost = ghosts.get(name)

                if ghost is None or ghost.get("status") == "destroyed":
                    messagebox.showerror("Destroyed", "Your Ghost Folder has been destroyed.")
                else:
                    remaining = ghost.get("max_attempts", 3) - ghost.get("failed_attempts", 0)
                    if remaining == 2:
                        msg = "Incorrect password.\nYou have 2 attempts remaining."
                    elif remaining == 1:
                        msg = "Incorrect password.\nYou have 1 attempt remaining."
                    else:
                        msg = "Incorrect password."
                    messagebox.showerror("Error", msg)

                password_dialog.destroy()
                self.refresh_list()
                return

            password_dialog.destroy()
            files = filedialog.askopenfilenames(title="Select files to add")
            if not files:
                return

            success = add_files_to_ghost(name, list(files), password)
            if success:
                messagebox.showinfo("Success", f"Files added successfully to '{name}'.")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Failed to add files.")

        ctk.CTkButton(password_dialog, text="OK", width=150, height=36,
                      command=do_add).pack(pady=20)
        password_dialog.bind("<Return>", lambda event: do_add())

    def recover_selected(self):
        if not self.selected_ghost:
            messagebox.showwarning("Warning", "Please select a Ghost Folder first.")
            return

        name = self.selected_ghost

        password_dialog = ctk.CTkToplevel(self.root)
        password_dialog.title("Recover")
        password_dialog.geometry("420x300")
        password_dialog.resizable(False, False)
        password_dialog.transient(self.root)
        password_dialog.grab_set()

        ctk.CTkLabel(password_dialog, text=f"Recover '{name}'",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(18, 10))

        ctk.CTkLabel(password_dialog, text="Password:",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=40)
        password_entry = ctk.CTkEntry(password_dialog, show="*", width=320, height=34)
        password_entry.pack(pady=(0, 12))
        password_entry.focus()

        ctk.CTkLabel(password_dialog, text="Recovery Key (emergency only):",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=40)

        key_frame = ctk.CTkFrame(password_dialog, fg_color="transparent")
        key_frame.pack(pady=(0, 8))

        recovery_entry = ctk.CTkEntry(key_frame, width=250, height=34)
        recovery_entry.pack(side="left")

        def load_key_file():
            path = filedialog.askopenfilename(
                title="Load Recovery Key",
                filetypes=[("Recovery Key", "*.key"), ("All files", "*.*")]
            )
            if not path:
                return
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                key = None
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if "RECOVERY KEY:" in line.upper():
                        if i + 1 < len(lines):
                            key = lines[i + 1].strip()
                        break
                if not key:
                    key = content.strip()
                if key:
                    recovery_entry.delete(0, "end")
                    recovery_entry.insert(0, key)
                    messagebox.showinfo("Loaded", "Recovery key loaded from file.")
                else:
                    messagebox.showerror("Error", "No recovery key found in this file.")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot read file:\n{e}")

        ctk.CTkButton(key_frame, text="Load .key", width=70, height=34,
                      command=load_key_file).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(password_dialog,
                     text="Leave Recovery Key empty to use password.\nFill Recovery Key only if you forgot the password.",
                     font=ctk.CTkFont(size=11),
                     text_color="#AAAAAA").pack(pady=(0, 12))

        def do_recover():
            password = password_entry.get().strip()
            recovery_key = recovery_entry.get().strip()

            if not password and not recovery_key:
                messagebox.showwarning("Warning", "Please enter a password or a recovery key.")
                return

            if recovery_key:
                success = recover_ghost(name, recovery_key=recovery_key, output_folder="")
                if not success:
                    messagebox.showerror("Error", "Invalid Recovery Key.")
                    return

                password_dialog.destroy()
                output_folder = filedialog.askdirectory(title="Choose recovery folder")
                if not output_folder:
                    return

                success = recover_ghost(name, recovery_key=recovery_key, output_folder=output_folder)
                if success:
                    messagebox.showinfo("Success", f"Ghost Folder '{name}' recovered with Recovery Key.")
                    self.refresh_list()
                else:
                    messagebox.showerror("Error", "Recovery failed.")
                return

            ghosts = load_ghosts()
            ghost = ghosts.get(name)
            if not ghost or ghost["status"] != "active" or not ghost["files"]:
                messagebox.showerror("Error", "Ghost Folder not available.")
                password_dialog.destroy()
                return

            first_file = ghost["files"][0]
            encrypted_path = Path(ghost["path"]) / first_file
            salt = bytes.fromhex(ghost["salts"][first_file])

            password_ok = test_password(str(encrypted_path), password, salt)

            if not password_ok:
                recover_ghost(name, password=password, output_folder="")
                ghosts = load_ghosts()
                ghost = ghosts.get(name)

                if ghost is None:
                    messagebox.showerror("Destroyed", "Your Ghost Folder has been destroyed.")
                else:
                    remaining = ghost.get("max_attempts", 3) - ghost.get("failed_attempts", 0)
                    if remaining == 2:
                        msg = "Incorrect password.\nYou have 2 attempts remaining."
                    elif remaining == 1:
                        msg = "Incorrect password.\nYou have 1 attempt remaining."
                    else:
                        msg = "Incorrect password."
                    messagebox.showerror("Error", msg)

                password_dialog.destroy()
                self.refresh_list()
                return

            password_dialog.destroy()
            output_folder = filedialog.askdirectory(title="Choose recovery folder")
            if not output_folder:
                return

            success = recover_ghost(name, password=password, output_folder=output_folder)
            if success:
                messagebox.showinfo("Success", f"Ghost Folder '{name}' recovered successfully.")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Recovery failed.")

        ctk.CTkButton(password_dialog, text="Recover", width=150, height=36,
                      command=do_recover).pack(pady=5)
        password_dialog.bind("<Return>", lambda event: do_recover())