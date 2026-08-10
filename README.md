Copyright (C) 2026 ErnestoKade

# GhostFolder

**GhostFolder** is a local, open-source tool that lets you create encrypted Ghost folders. Your files are encrypted, hidden, and can self-destruct under specific security conditions.

No cloud. No telemetry. No background services.

---

## How to use

### 1. First launch

![First launch](assets/screenshoots/01.png)

Choose the folder where all encrypted Ghosts will be stored. This location can be on your computer, an external drive, or a USB device.

---

### 2. Create a Ghost

![Create Ghost](assets/screenshoots/02.png)

Click **Create Ghost Folder** to start creating a new encrypted Ghost.

---

### 3. Configure your Ghost

![Configure Ghost](assets/screenshoots/03.png)

- Enter a name for the Ghost folder.
- Add one or more files using **Add** or **drag & drop**.
- Choose an expiration date.
- Set a strong password.
- Generate and save the **Recovery Key**.
- Choose the destruction mode (**Soft** or **Hard**).
- Click **Create**.

After **3 wrong password attempts**, the Ghost is automatically destroyed to prevent brute-force attacks.

---

### 4. Recover or open a Ghost

![Recover Ghost](assets/screenshoots/04.png)

- Select the Ghost.
- Click **Recover**.
- Enter the password.
- If the password is lost, use the **Recovery Key**.

After successful authentication, choose the folder where the recovered files will be restored.

---

### 5. Wrong password protection

![Wrong password](assets/screenshoots/05.png)

For better control of your encrypted data, avoid creating too many Ghosts unless you can safely manage their passwords and Recovery Keys.

If you lose track of them, recovery can become difficult.

After **3 wrong password attempts**, the Ghost is destroyed. In that situation, **only the Recovery Key can save the Ghost**.

---

### 6. Add files to an existing Ghost

![Add files](assets/screenshoots/06.png)

- Select the Ghost.
- Click **Add Files**.
- Enter the password.
- Choose the files to add.

The new files will be encrypted and added to the existing Ghost.

---

### 7. Select the files to add

![Select files](assets/screenshoots/07.png)

You can select one or multiple files. They will be encrypted automatically when added to the Ghost.

---

### 8. Confirmation message

![Confirmation](assets/screenshoots/08.png)

A confirmation message indicates that the selected file(s) have been successfully added to the Ghost.

---

### 9. Recovery completed

![Recovery completed](assets/screenshoots/09.png)

Once all steps are completed, your recovered files will appear in the destination folder you selected during recovery.

A **JSON file** is also created next to the encrypted Ghost folder. It contains encrypted metadata required for the Ghost to function correctly.

If you download GhostFolder from the internet, always perform your own security checks on:

- `GhostFolder.exe`
- the associated JSON metadata files

If you trust the software after your own verification, keep using it to protect your sensitive data. If not, delete it.

**Enjoy — ErnestoKade**

---

## Features

- Strong encryption (**Fernet + PBKDF2 with 480,000 iterations**)
- Password protection
- Recovery Key
- Expiration date
- Soft / Hard destruction modes
- Failed attempts protection
- Dead Man Switch
- Add files to existing Ghosts
- Fully local storage
- Modern dark UI (CustomTkinter)
- Drag & Drop support

---

## Requirements

- Windows 10 / 11
- Python 3.10 or higher (for source builds)

---

## Installation (from source)

<pre><code>git clone https://github.com/ErnestoKade/GhostFolder.git
cd GhostFolder
pip install -r requirements.txt
python main.py
</code></pre>

---

## Security notes

- If you lose both the password and the Recovery Key, the data is permanently unrecoverable.
- Hard destruction mode securely overwrites data before deletion.
- Everything remains on your computer.
- GhostFolder never connects to the internet.

---

## Disclaimer

GhostFolder is provided **as is**. The author is not responsible for data loss. Always keep a backup of your Recovery Key and important files.

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

