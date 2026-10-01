"""JWT validation utilities.

The Interview Service NEVER issues production tokens. Tokens are issued by the
Auth Service (owned by another teammate) using the shared contract:

    algorithm: HS256
    issuer:    auth-servisi
    audience:  mulakat-hazirlik
    subject:   user_id

This module only *validates* tokens against that contract and extracts claims.
The only exception is the development-only POST /dev/token endpoint, which
signs tokens using the exact same secret/algorithm/issuer/audience so that the
service is exercisable locally without a running Auth Service.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import PyJWTError

from app.core.config import Settings
from app.core.exceptions import UnauthorizedError


@dataclass(frozen=True)
class TokenPayload:
    """Decoded and validated JWT claims relevant to this service."""

    user_id: str
    raw_claims: dict[str, Any] = field(default_factory=dict)


def decode_access_token(token: str, settings: Settings) -> TokenPayload:
    """Decode and validate a JWT against the shared Auth Service contract.

    Raises UnauthorizedError on any validation failure (expired, bad
    signature, wrong issuer/audience, missing subject, malformed token).
    """
    try:
        claims = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
    except PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    user_id = claims.get("sub")
    if not user_id:
        raise UnauthorizedError("Token is missing required 'sub' claim")

    return TokenPayload(user_id=str(user_id), raw_claims=claims)


def create_dev_access_token(
    settings: Settings,
    subject: str,
    expires_minutes: int | None = None,
) -> str:
    """Issue a locally-signed token that matches the Auth Service contract.

    Intended for local development/testing only (POST /dev/token). This must
    be disabled or protected in production via settings.ENABLE_DEV_TOKEN_ENDPOINT.
    """
    now = datetime.now(timezone.utc)
    expire_minutes = expires_minutes or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    payload = {
        "sub": subject,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=expire_minutes),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
