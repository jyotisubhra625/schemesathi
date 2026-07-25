import os
import base64
from typing import Tuple
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VAULT_DIR = os.path.dirname(__file__)
SALT_FILE = os.path.join(VAULT_DIR, "vault_salt.bin")
STORAGE_DIR = os.path.join(VAULT_DIR, "secure_storage")

def get_or_create_salt() -> bytes:
    """Gets existing salt or creates and saves a new random 16-byte salt."""
    os.makedirs(VAULT_DIR, exist_ok=True)
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, "rb") as f:
            return f.read()
    else:
        salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
        return salt

def derive_key(passphrase: str, salt: bytes = None) -> bytes:
    """Derives a Fernet encryption key from passphrase using PBKDF2HMAC."""
    if salt is None:
        salt = get_or_create_salt()
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))
    return key

def encrypt_bytes(passphrase: str, data: bytes) -> bytes:
    """Encrypts raw bytes using derived key."""
    key = derive_key(passphrase)
    fernet = Fernet(key)
    return fernet.encrypt(data)

def decrypt_bytes(passphrase: str, encrypted_data: bytes) -> bytes:
    """
    Decrypts encrypted bytes using derived key.
    Raises ValueError if passphrase is incorrect or data is corrupted.
    """
    key = derive_key(passphrase)
    fernet = Fernet(key)
    try:
        return fernet.decrypt(encrypted_data)
    except InvalidToken:
        raise ValueError("Invalid passphrase. Could not decrypt document.")

def encrypt_file(passphrase: str, file_bytes: bytes, output_filename: str) -> str:
    """Encrypts file bytes and saves to secure_storage/."""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    out_path = os.path.join(STORAGE_DIR, output_filename)
    encrypted = encrypt_bytes(passphrase, file_bytes)
    with open(out_path, "wb") as f:
        f.write(encrypted)
    return out_path

def decrypt_file(passphrase: str, filepath: str) -> bytes:
    """Decrypts file from disk into raw bytes."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Encrypted file not found at: {filepath}")
    with open(filepath, "rb") as f:
        encrypted_bytes = f.read()
    return decrypt_bytes(passphrase, encrypted_bytes)

if __name__ == "__main__":
    passphrase = "mySecretVaultPassword"
    test_data = b"Sensitive Aadhaar Details: 1234-5678-9012"
    
    enc = encrypt_bytes(passphrase, test_data)
    print("Encrypted bytes length:", len(enc))
    
    dec = decrypt_bytes(passphrase, enc)
    print("Decrypted content:", dec.decode("utf-8"))
    
    # Test wrong passphrase
    try:
        decrypt_bytes("wrongPassword", enc)
    except ValueError as e:
        print("Expected error caught:", e)
