import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from jose import JWTError, jwt

from app.core.config import get_settings

PBKDF2_ITERATIONS = 390_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = hashed_password.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected = base64.b64decode(digest_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_token(subject: str, token_type: str) -> str:
    settings = get_settings()
    if token_type == "access":
        expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    else:
        expires = datetime.now(UTC) + timedelta(days=settings.refresh_token_days)
    payload = {"sub": subject, "type": token_type, "exp": expires}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: str = "access") -> str:
    payload = decode_token_payload(token, expected_type)
    return str(payload["sub"])


def create_telegram_link_token(user_id: str, company_id: str, expires_minutes: int = 15) -> str:
    settings = get_settings()
    payload = {
        "sub": user_id,
        "company_id": company_id,
        "type": "telegram_link",
        "exp": datetime.now(UTC) + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token_payload(token: str, expected_type: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise ValueError("Invalid token")
    return payload
