TOKEN_ALGORITHM = "HS256"
TOKEN_LIFETIME = 600
TOKEN_SECRET = "secret"

from utils import verify_password

def validate_credentials(password: str, hashed_password: str) -> bool:
    return verify_password(password, hashed_password)

