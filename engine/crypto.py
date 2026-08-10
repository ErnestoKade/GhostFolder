# ========== IMPORT ==========
import os
import base64
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ========== KEY GENERATION ==========
def generate_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Generate a Fernet key from a password.
    Returns (key, salt)
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

# ========== ENCRYPT ==========
def encrypt_file(file_path: str, password: str) -> tuple[str, bytes]:
    """
    Encrypt a file.
    Returns (encrypted_file_path, salt)
    """
    key, salt = generate_key(password)
    fernet = Fernet(key)

    with open(file_path, "rb") as f:
        data = f.read()

    encrypted_data = fernet.encrypt(data)

    encrypted_path = file_path + ".ghost"
    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)

    return encrypted_path, salt

# ========== DECRYPT ==========
def decrypt_file(encrypted_path: str, password: str, salt: bytes, output_path: str) -> bool:
    """
    Decrypt a file.
    Returns True if success, False otherwise.
    """
    try:
        key, _ = generate_key(password, salt)
        fernet = Fernet(key)

        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()

        decrypted_data = fernet.decrypt(encrypted_data)

        with open(output_path, "wb") as f:
            f.write(decrypted_data)

        return True
    except Exception:
        return False

# ========== HARD DESTRUCTION (SHRED) ==========
def secure_delete(file_path: str, passes: int = 3) -> bool:
    """
    Écrase complètement un fichier (mode Hard).
    - passe plusieurs fois des données aléatoires
    - puis supprime le fichier
    """
    try:
        if not os.path.isfile(file_path):
            return False

        file_size = os.path.getsize(file_path)

        with open(file_path, "ba+", buffering=0) as f:
            for _ in range(passes):
                f.seek(0)
                f.write(secrets.token_bytes(file_size))
                f.flush()
                os.fsync(f.fileno())

        os.remove(file_path)
        return True
    except Exception:
        return False

# ========== HELPER : DELETE (Soft ou Hard) ==========
def destroy_file(file_path: str, mode: str = "soft") -> bool:
    """
    mode = "soft"  → simple suppression
    mode = "hard"  → écrasement sécurisé (shred)
    """
    if mode == "hard":
        return secure_delete(file_path)
    else:
        try:
            os.remove(file_path)
            return True
        except Exception:
            return False
            
# ========== TEST PASSWORD (in memory) ==========
def test_password(encrypted_path: str, password: str, salt: bytes) -> bool:
    """
    Test if password is correct without writing any file.
    Returns True if password is good.
    """
    try:
        key, _ = generate_key(password, salt)
        fernet = Fernet(key)

        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()

        fernet.decrypt(encrypted_data)  # just try to decrypt
        return True
    except Exception:
        return False
        
# ========== ENCRYPT / DECRYPT STRING (for recovery key) ==========
def encrypt_string(text: str, password: str) -> tuple[str, bytes]:
    """
    Encrypt a string (used to protect the real password with recovery key).
    Returns (encrypted_base64, salt)
    """
    key, salt = generate_key(password)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(text.encode())
    return base64.urlsafe_b64encode(encrypted).decode(), salt

def decrypt_string(encrypted_b64: str, password: str, salt: bytes) -> str | None:
    """
    Decrypt a string.
    Returns the original text or None if failed.
    """
    try:
        key, _ = generate_key(password, salt)
        fernet = Fernet(key)
        encrypted = base64.urlsafe_b64decode(encrypted_b64.encode())
        return fernet.decrypt(encrypted).decode()
    except Exception:
        return None        