# ========== IMPORT ==========
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES
from datetime import datetime, timedelta
import secrets
from pathlib import Path
from engine.ghost import create_ghost, get_storage_path, set_storage_path

# ========== SELECT STORAGE DIALOG ==========
class SelectStorageDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Choose Storage Folder")
        self.geometry("520x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result = None

        ctk.CTkLabel(
            self,
            text="Choose where GhostFolder will store your encrypted files",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(pady=(25, 10), padx=20)

        ctk.CTkLabel(
            self,
            text="You can select an existing folder or create a new one.\nThis folder will contain all your Ghosts.",
            font=ctk.CTkFont(size=13),
            justify="left"
        ).pack(pady=(0, 20), padx=20)

        self.path_var = ctk.StringVar()
        self.path_entry = ctk.CTkEntry(self, textvariable=self.path_var, height=38, state="readonly")
        self.path_entry.pack(fill="x", padx=25, pady=(0, 15))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Browse...", width=140, height=36, command=self.browse).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Confirm", width=140, height=36, command=self.confirm).pack(side="left", padx=8)

    def browse(self):
        folder = filedialog.askdirectory(title="Select or create a folder for GhostFolder")
        if folder:
            self.path_var.set(folder)

    def confirm(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("Error", "Please select a folder.")
            return

        try:
            set_storage_path(path)
            self.result = path
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot use this folder:\n{e}")


# ========== CREATE DIALOG ==========
class CreateGhostDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Ghost Folder")
        self.geometry("560x820")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.selected_files = []
        self.result = None
        self.recovery_key = None

        self.create_widgets()

    # ========== UI ==========
    def create_widgets(self):
        pad_x = 25

        # Name
        ctk.CTkLabel(self, text="Name", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=pad_x, pady=(20, 4))
        self.name_entry = ctk.CTkEntry(self, height=36)
        self.name_entry.pack(fill="x", padx=pad_x)

        # Files
        ctk.CTkLabel(self, text="Files (drag & drop or use buttons)", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=pad_x, pady=(16, 4))

        file_frame = ctk.CTkFrame(self, fg_color="transparent")
        file_frame.pack(fill="x", padx=pad_x)

        self.files_list = ctk.CTkTextbox(file_frame, height=100, activate_scrollbars=True)
        self.files_list.pack(side="left", fill="both", expand=True)
        self.files_list.configure(state="disabled")

        self.files_list.drop_target_register(DND_FILES)
        self.files_list.dnd_bind('<<Drop>>', self.on_drop)

        btn_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        btn_frame.pack(side="left", padx=(10, 0), fill="y")

        ctk.CTkButton(btn_frame, text="Add", width=90, command=self.add_files).pack(pady=(0, 8))
        ctk.CTkButton(btn_frame, text="Remove", width=90, command=self.remove_file).pack()

        # Expire date
        ctk.CTkLabel(self, text="Expire date (YYYY-MM-DD) or days", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=pad_x, pady=(16, 4))
        self.date_entry = ctk.CTkEntry(self, height=36)
        self.date_entry.pack(fill="x", padx=pad_x)
        self.date_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))

        # Password
        ctk.CTkLabel(self, text="Password", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=pad_x, pady=(16, 4))
        self.password_entry = ctk.CTkEntry(self, height=36, show="*")
        self.password_entry.pack(fill="x", padx=pad_x)

        # ========== RECOVERY KEY ==========
        ctk.CTkLabel(self, text="Recovery Key (optional but recommended)", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=pad_x, pady=(16, 4))

        key_frame = ctk.CTkFrame(self, fg_color="transparent")
        key_frame.pack(fill="x", padx=pad_x)

        self.key_entry = ctk.CTkEntry(key_frame, height=36, state="disabled")
        self.key_entry.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(key_frame, text="Generate", width=90, command=self.generate_key).pack(side="left", padx=(8, 0))
        ctk.CTkButton(key_frame, text="Copy", width=70, command=self.copy_key).pack(side="left", padx=(6, 0))
        ctk.CTkButton(key_frame, text="Save", width=70, command=self.save_key).pack(side="left", padx=(6, 0))
       
       # Warning
        warning = ctk.CTkLabel(
            self,
            text="Warning: If you do not generate and save a recovery key,\nforgetting your password will make your files permanently unrecoverable.",
            font=ctk.CTkFont(size=12),
            text_color="#FF6B6B",
            justify="left"
        )
        warning.pack(anchor="w", padx=pad_x, pady=(8, 0))

        # Destruction mode
        ctk.CTkLabel(self, text="Destruction mode", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=pad_x, pady=(16, 4))
        self.mode_var = ctk.StringVar(value="soft")
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=pad_x)
        ctk.CTkRadioButton(mode_frame, text="Soft (encrypt + hide)", variable=self.mode_var, value="soft").pack(anchor="w")
        ctk.CTkRadioButton(mode_frame, text="Hard (secure overwrite)", variable=self.mode_var, value="hard").pack(anchor="w", pady=(4, 0))

        # Dead man switch
        ctk.CTkLabel(self, text="Dead man switch (days without activity, 0 = disabled)", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=pad_x, pady=(16, 4))
        self.dead_man_entry = ctk.CTkEntry(self, height=36)
        self.dead_man_entry.pack(fill="x", padx=pad_x)
        self.dead_man_entry.insert(0, "0")

        # Bottom buttons
        btn_bottom = ctk.CTkFrame(self, fg_color="transparent")
        btn_bottom.pack(side="bottom", pady=20)

        ctk.CTkButton(btn_bottom, text="Create", width=130, height=38, command=self.on_create).pack(side="left", padx=12)
        ctk.CTkButton(btn_bottom, text="Cancel", width=130, height=38, fg_color="gray", command=self.destroy).pack(side="left", padx=12)

    # ========== ACTIONS ==========
    def generate_key(self):
        self.recovery_key = secrets.token_urlsafe(32)
        self.key_entry.configure(state="normal")
        self.key_entry.delete(0, "end")
        self.key_entry.insert(0, self.recovery_key)
        self.key_entry.configure(state="disabled")

    def copy_key(self):
        if self.recovery_key:
            self.clipboard_clear()
            self.clipboard_append(self.recovery_key)
            messagebox.showinfo("Copied", "Recovery key copied to clipboard.")
        else:
            messagebox.showwarning("Warning", "Generate a recovery key first.")
            
    def save_key(self):
        if not self.recovery_key:
            messagebox.showwarning("Warning", "Generate a recovery key first.")
            return

        default_name = self.name_entry.get().strip() or "recovery"
        default_name = "".join(c for c in default_name if c.isalnum() or c in (" ", "-", "_")).strip()
        default_name = default_name.replace(" ", "_") or "recovery"

        path = filedialog.asksaveasfilename(
            title="Save Recovery Key",
            defaultextension=".key",
            initialfile=f"{default_name}.key",
            filetypes=[("Recovery Key", "*.key"), ("All files", "*.*")]
        )

        if not path:
            return

        if not path.lower().endswith(".key"):
            path += ".key"

        content = f"""GhostFolder Recovery Key
========================
Ghost name : {self.name_entry.get().strip() or "Unknown"}
Created    : {datetime.now().strftime("%Y-%m-%d %H:%M")}

RECOVERY KEY:
{self.recovery_key}

IMPORTANT:
- Keep this file in a safe place
- Do not share it
- Without this key and the password, your files cannot be recovered
"""

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Recovery key saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot save file:\n{e}")        

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        for f in files:
            f = f.strip()
            if f and f not in self.selected_files:
                self.selected_files.append(f)
        self.update_files_list()

    def add_files(self):
        files = filedialog.askopenfilenames(title="Select files")
        for f in files:
            if f not in self.selected_files:
                self.selected_files.append(f)
        self.update_files_list()

    def remove_file(self):
        if self.selected_files:
            self.selected_files.pop()
            self.update_files_list()

    def update_files_list(self):
        self.files_list.configure(state="normal")
        self.files_list.delete("1.0", "end")
        for f in self.selected_files:
            self.files_list.insert("end", f + "\n")
        self.files_list.configure(state="disabled")

    def on_create(self):
        name = self.name_entry.get().strip()
        password = self.password_entry.get()
        date_text = self.date_entry.get().strip()
        mode = self.mode_var.get()
        dead_man_text = self.dead_man_entry.get().strip()

        if not name or not password or not self.selected_files:
            messagebox.showwarning("Error", "Please fill all fields and select at least one file.")
            return

        try:
            if date_text.isdigit():
                expire_date = (datetime.now() + timedelta(days=int(date_text))).strftime("%Y-%m-%d")
            else:
                datetime.strptime(date_text, "%Y-%m-%d")
                expire_date = date_text
        except ValueError:
            messagebox.showwarning("Error", "Invalid date format. Use YYYY-MM-DD or number of days.")
            return

        try:
            dead_man_days = int(dead_man_text)
            if dead_man_days <= 0:
                dead_man_days = None
        except ValueError:
            messagebox.showwarning("Error", "Dead man switch must be a number.")
            return

        success = create_ghost(
            name=name,
            files=self.selected_files,
            expire_date=expire_date,
            password=password,
            destruction_mode=mode,
            dead_man_days=dead_man_days,
            recovery_key=self.recovery_key
        )

        if success:
            messagebox.showinfo("Success", f"Ghost Folder '{name}' created successfully.")
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Error", "A Ghost Folder with this name already exists.")