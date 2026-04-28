from argon2 import PasswordHasher
import hashlib
import os


ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, password)
        return True
    except Exception:
        return False

def create_refresh_token() -> str:
    return hashlib.sha256(os.urandom(32)).hexdigest()

