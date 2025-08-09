# auth/jwt_auth.py
import time
import jwt
import bcrypt
from typing import Optional
from config.settings import JWT_SECRET, JWT_ALGORITHM, JWT_EXP_SECONDS

# A tiny in-memory user store for demo. Replace with DB in production.
# Passwords are stored as bcrypt hashes.
_demo_users = {
    "vinod": {
        "password_hash": bcrypt.hashpw(b"vinod_password", bcrypt.gensalt()).decode()
    },
    "alice": {
        "password_hash": bcrypt.hashpw(b"alice_password", bcrypt.gensalt()).decode()
    }
}

def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), password_hash.encode())

def authenticate_user(username: str, password: str) -> Optional[str]:
    user = _demo_users.get(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    # create jwt
    now = int(time.time())
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + JWT_EXP_SECONDS,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # PyJWT >= 2 returns str; ensure str
    if isinstance(token, bytes):
        token = token.decode()
    return token

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None

def get_current_user(token: str) -> Optional[str]:
    payload = decode_token(token)
    if not payload:
        return None
    return payload.get("sub")
