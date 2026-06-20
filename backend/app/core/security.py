from datetime import UTC, datetime, timedelta
import hashlib
from typing import Any
from uuid import UUID

import jwt
from jwt.exceptions import PyJWTError
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.exceptions import UnauthorizedError
from app.core.settings import Settings, get_settings

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

_password_hasher = PasswordHash((BcryptHasher(),))


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _password_hasher.verify(plain_password, hashed_password)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _encode_token(
    payload: dict[str, Any],
    *,
    settings: Settings | None = None,
) -> str:
    settings = settings or get_settings()
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(
    subject: str | UUID,
    tenant_id: str | UUID,
    *,
    settings: Settings | None = None,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    settings = settings or get_settings()
    expire = datetime.now(UTC) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "tenant_id": str(tenant_id),
        "type": TOKEN_TYPE_ACCESS,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    if extra_claims:
        payload.update(extra_claims)
    return _encode_token(payload, settings=settings)


def create_refresh_token_jwt(
    subject: str | UUID,
    token_id: str | UUID,
    *,
    settings: Settings | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    settings = settings or get_settings()
    expire = datetime.now(UTC) + (
        expires_delta
        if expires_delta is not None
        else timedelta(days=settings.refresh_token_expire_days)
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "jti": str(token_id),
        "type": TOKEN_TYPE_REFRESH,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return _encode_token(payload, settings=settings)


def decode_token(
    token: str,
    *,
    expected_type: str,
    settings: Settings | None = None,
) -> dict[str, Any]:
    settings = settings or get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    if payload.get("type") != expected_type:
        raise UnauthorizedError("Invalid token type")
    return payload


def decode_access_token(
    token: str,
    *,
    settings: Settings | None = None,
) -> dict[str, Any]:
    return decode_token(token, expected_type=TOKEN_TYPE_ACCESS, settings=settings)


def decode_refresh_token(
    token: str,
    *,
    settings: Settings | None = None,
) -> dict[str, Any]:
    return decode_token(token, expected_type=TOKEN_TYPE_REFRESH, settings=settings)
