DEFAULT_USERNAME = "user"
DEFAULT_PASSWORD = "password"

TOKEN_ALGORITHM = "HS256"
TOKEN_LIFETIME = 600
TOKEN_SECRET = "secret"

def validate_credentials(username: str, password: str) -> bool:
    return username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD

