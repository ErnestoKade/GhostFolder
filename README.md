# GhostFolder

**GhostFolder** is a local, open-source tool that lets you create encrypted "Ghost" folders.  
Your files are encrypted, hidden, and can self-destruct under certain conditions.

Perfect for protecting sensitive files with strong encryption, recovery key, expiration date, failed attempts limit, and dead-man switch.

---

## Features

- **Strong encryption** (Fernet + PBKDF2 with 480 000 iterations)
- **Password protection**
- **Recovery Key** (optional but highly recommended)
- **Expiration date** (date or number of days)
- **Destruction modes**:
  - Soft → encrypt + hide
  - Hard → secure overwrite (multiple passes)
- **Failed attempts protection** (3 wrong passwords → permanent destruction)
- **Dead Man Switch** (auto-destroy after X days of inactivity)
- **Add files** to an existing Ghost
- **Fully local** – you choose the storage folder (no cloud, no telemetry)
- Modern dark UI (CustomTkinter)
- Drag & Drop support

---

## Screenshots

*(You can add screenshots here later)*

---

## Requirements

- Windows 10 / 11 (recommended)
- Python 3.10 or higher (only needed if you run from source)

### Python dependencies

```bash
customtkinter
cryptography
tkinterdnd2

Installation (from source)Clone the repository

bash

git clone https://github.com/YOUR_USERNAME/GhostFolder.git
cd GhostFolder

Install dependencies

bash

pip install -r requirements.txt

Run the application

bash

python main.py

How to useFirst launchWhen you start GhostFolder for the first time, it will ask you to choose a storage folder.
This is where all your encrypted Ghosts will be saved.
You can choose any folder on your computer (USB drive, external HDD, etc.).Create a Ghost FolderClick Create Ghost Folder
Give it a name
Add files (drag & drop or use the buttons)
Set an expiration date (or number of days)
Enter a strong password
Generate a Recovery Key (very important!) and save it somewhere safe
Choose destruction mode (Soft / Hard)
Optionally set a Dead Man Switch
Click Create

Recover a GhostSelect the Ghost in the list
Click Recover
Enter your password
or
Enter the Recovery Key (if you forgot the password)
Choose where to save the recovered files

Add files to an existing GhostSelect the Ghost
Click Add Files
Enter the password
Select the new files

Important Security NotesIf you lose both the password and the Recovery Key, your files are permanently unrecoverable.
After 3 wrong password attempts, the Ghost is destroyed forever.
The Hard destruction mode overwrites the data several times before deleting it.
Everything stays on your computer. GhostFolder never connects to the internet.

LicenseThis project is licensed under the MIT License – see the LICENSE file for details.DisclaimerGhostFolder is provided as-is.
The author is not responsible for any data loss.
Always keep a backup of your Recovery Key and important files.

