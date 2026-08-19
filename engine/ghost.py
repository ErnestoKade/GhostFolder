# ========== IMPORT ==========
import os
import json
import shutil
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from engine.crypto import (
    encrypt_file, decrypt_file, destroy_file, test_password,
    encrypt_string, decrypt_string
)

# ========== PATHS ==========
CONFIG_DIR = Path(os.getenv("APPDATA")) / "GhostFolder"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = CONFIG_DIR / "config.json"

def get_storage_path() -> Path | None:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
                path = Path(data.get("storage_path", ""))
                if path.exists() and path.is_dir():
                    return path
        except Exception:
            pass
    return None

def set_storage_path(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump({"storage_path": str(path)}, f, indent=4)
    return path

def get_paths():
    storage = get_storage_path()
    if storage is None:
       
        storage = Path(os.getenv("APPDATA")) / "GhostFolder"
        storage.mkdir(parents=True, exist_ok=True)
        set_storage_path(storage)

    ghosts_dir = storage / "ghosts"
    config_file = storage / "ghosts.json"
    return ghosts_dir, config_file

# ========== INIT ==========
def init_storage():
    ghosts_dir, config_file = get_paths()
    ghosts_dir.mkdir(parents=True, exist_ok=True)
    if not config_file.exists():
        with open(config_file, "w") as f:
            json.dump({}, f)

# ========== LOAD / SAVE ==========
def load_ghosts() -> dict:
    init_storage()
    _, config_file = get_paths()
    with open(config_file, "r") as f:
        return json.load(f)

def save_ghosts(data: dict):
    _, config_file = get_paths()
    with open(config_file, "w") as f:
        json.dump(data, f, indent=4)

# ========== CREATE ==========
def create_ghost(name: str, files: list[str], expire_date: str, password: str,
                 destruction_mode: str = "soft", max_attempts: int = 3,
                 dead_man_days: int = None, recovery_key: str = None) -> bool:
    init_storage()
    ghosts = load_ghosts()

    if name in ghosts:
        return False

    ghosts_dir, _ = get_paths()
    ghost_id = name.replace(" ", "_").lower()
    ghost_path = ghosts_dir / ghost_id
    ghost_path.mkdir(exist_ok=True)

    encrypted_files = []
    salts = {}

    for file_path in files:
        if not os.path.exists(file_path):
            continue

        original_name = os.path.basename(file_path)
        dest = ghost_path / original_name

        shutil.move(file_path, dest)

        encrypted_path, salt = encrypt_file(str(dest), password)
        os.remove(dest)

        encrypted_files.append(os.path.basename(encrypted_path))
        salts[os.path.basename(encrypted_path)] = salt.hex()

    encrypted_password = None
    recovery_salt = None
    recovery_hash = None

    if recovery_key:
        encrypted_password, salt = encrypt_string(password, recovery_key)
        recovery_salt = salt.hex()
        recovery_hash = hashlib.sha256(recovery_key.encode()).hexdigest()

    ghosts[name] = {
        "id": ghost_id,
        "path": str(ghost_path),
        "expire_date": expire_date,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": encrypted_files,
        "salts": salts,
        "status": "active",
        "destruction_mode": destruction_mode,
        "failed_attempts": 0,
        "max_attempts": max_attempts,
        "dead_man_days": dead_man_days,
        "has_recovery_key": recovery_key is not None,
        "encrypted_password": encrypted_password,
        "recovery_salt": recovery_salt,
        "recovery_hash": recovery_hash
    }

    save_ghosts(ghosts)
    return True

# ========== ADD FILES ==========
def add_files_to_ghost(name: str, files: list[str], password: str) -> bool:
    ghosts = load_ghosts()
    if name not in ghosts:
        return False

    ghost = ghosts[name]
    if ghost.get("status") != "active" or not ghost.get("files"):
        return False

    ghost_path = Path(ghost["path"])
    first_file = ghost["files"][0]
    encrypted_path = ghost_path / first_file
    salt = bytes.fromhex(ghost["salts"][first_file])

    if not test_password(str(encrypted_path), password, salt):
        ghost["failed_attempts"] = ghost.get("failed_attempts", 0) + 1
        save_ghosts(ghosts)
        if ghost["failed_attempts"] >= ghost.get("max_attempts", 3):
            destroy_ghost(name)
        return False

    ghost["failed_attempts"] = 0
    ghost["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for file_path in files:
        if not os.path.exists(file_path):
            continue

        original_name = os.path.basename(file_path)
        dest = ghost_path / original_name

        if (ghost_path / (original_name + ".ghost")).exists():
            continue

        shutil.move(file_path, dest)
        encrypted_path, salt = encrypt_file(str(dest), password)
        os.remove(dest)

        ghost["files"].append(os.path.basename(encrypted_path))
        ghost["salts"][os.path.basename(encrypted_path)] = salt.hex()

    save_ghosts(ghosts)
    return True

# ========== GET ==========
def get_all_ghosts() -> dict:
    return load_ghosts()

# ========== RECOVER ==========
def recover_ghost(name: str, password: str = None, output_folder: str = "", recovery_key: str = None) -> bool:
    ghosts = load_ghosts()
    if name not in ghosts:
        return False

    ghost = ghosts[name]
    ghost.setdefault("status", "active")
    ghost.setdefault("failed_attempts", 0)
    ghost.setdefault("max_attempts", 3)
    ghost.setdefault("files", [])
    ghost.setdefault("salts", {})

    if ghost["status"] != "active" or not ghost["files"]:
        return False

    ghost_path = Path(ghost["path"])
    first_file = ghost["files"][0]
    encrypted_path = ghost_path / first_file
    salt = bytes.fromhex(ghost["salts"][first_file])

    real_password = None

    # === RECOVERY KEY (strict) ===
    if recovery_key:
       
        if not ghost.get("has_recovery_key") or not ghost.get("recovery_hash"):
            print("→ Pas de recovery key enregistrée")
            return False

        if hashlib.sha256(recovery_key.encode()).hexdigest() != ghost["recovery_hash"]:
            print("→ Hash ne correspond PAS")
            return False

        recovered = decrypt_string(
            ghost["encrypted_password"],
            recovery_key,
            bytes.fromhex(ghost["recovery_salt"])
        )
        if recovered is None:
            print("→ decrypt_string a échoué")
            return False

        real_password = recovered
        print("→ Recovery Key acceptée, mot de passe récupéré")

    # === NORMAL PASSWORD ===
    else:
        if not password:
            return False

        if not test_password(str(encrypted_path), password, salt):
            ghost["failed_attempts"] += 1
            save_ghosts(ghosts)
            if ghost["failed_attempts"] >= ghost["max_attempts"]:
                destroy_ghost(name)
            return False

        real_password = password
        ghost["failed_attempts"] = 0

    # Success
    ghost["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_ghosts(ghosts)

    if not output_folder:
        return True

    success = True
    for file_name in ghost["files"]:
        encrypted_path = ghost_path / file_name
        salt = bytes.fromhex(ghost["salts"][file_name])
        output_path = os.path.join(output_folder, file_name.replace(".ghost", ""))
        if not decrypt_file(str(encrypted_path), real_password, salt, output_path):
            success = False

    return success

    # === RECOVERY KEY (strict) ===
    if recovery_key:
        if not ghost.get("has_recovery_key") or not ghost.get("recovery_hash"):
            return False

        if hashlib.sha256(recovery_key.encode()).hexdigest() != ghost["recovery_hash"]:
            return False

        recovered = decrypt_string(
            ghost["encrypted_password"],
            recovery_key,
            bytes.fromhex(ghost["recovery_salt"])
        )
        if recovered is None:
            return False

        real_password = recovered

    # === NORMAL PASSWORD ===
    else:
        if not password:
            return False

        if not test_password(str(encrypted_path), password, salt):
            ghost["failed_attempts"] += 1
            save_ghosts(ghosts)
            if ghost["failed_attempts"] >= ghost["max_attempts"]:
                destroy_ghost(name)
            return False

        real_password = password
        ghost["failed_attempts"] = 0

    # Success
    ghost["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_ghosts(ghosts)

    if not output_folder:
        return True

    success = True
    for file_name in ghost["files"]:
        encrypted_path = ghost_path / file_name
        salt = bytes.fromhex(ghost["salts"][file_name])
        output_path = os.path.join(output_folder, file_name.replace(".ghost", ""))
        if not decrypt_file(str(encrypted_path), real_password, salt, output_path):
            success = False

    return success

# ========== DESTROY ==========
def destroy_ghost(name: str) -> bool:
    ghosts = load_ghosts()
    if name not in ghosts:
        return False

    ghost = ghosts[name]
    ghost_path = Path(ghost["path"])
    mode = ghost.get("destruction_mode", "soft")

    for file_name in ghost.get("files", []):
        file_path = ghost_path / file_name
        destroy_file(str(file_path), mode=mode)

    try:
        shutil.rmtree(ghost_path, ignore_errors=True)
    except Exception:
        pass

    del ghosts[name]
    save_ghosts(ghosts)
    return True

# ========== CHECK ==========
def check_and_process_ghosts():
    ghosts = load_ghosts()
    now = datetime.now()

    for name, ghost in list(ghosts.items()):
        if ghost.get("status") != "active":
            continue

        try:
            expire_date = datetime.strptime(ghost["expire_date"], "%Y-%m-%d")
            if now.date() > expire_date.date():
                destroy_ghost(name)
                continue
        except Exception:
            pass

        if ghost.get("dead_man_days"):
            try:
                last_activity = datetime.strptime(ghost["last_activity"], "%Y-%m-%d %H:%M:%S")
                if (now - last_activity).days >= ghost["dead_man_days"]:
                    destroy_ghost(name)
            except Exception:
                pass

    return load_ghosts()