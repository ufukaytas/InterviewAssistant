"""Authentication dependencies: extract and validate the JWT issued by the
Auth Service, per the shared contract (HS256 / issuer auth-servisi /
audience mulakat-hazirlik / subject = user_id).
"""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies.settings import get_app_settings
from app.core.config import Settings
from app.core.exceptions import UnauthorizedError
from app.core.security import TokenPayload, decode_access_token

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    raw_token: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    settings: Settings = Depends(get_app_settings),
) -> CurrentUser:
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("Missing bearer token")

    payload: TokenPayload = decode_access_token(credentials.credentials, settings)
    return CurrentUser(user_id=payload.user_id, raw_token=credentials.credentials)

