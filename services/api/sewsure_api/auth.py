"""Authentication interface. Routes depend on `get_current_user` only.

`JwtAuth` verifies the contract's bearer JWT against the configured issuer. Until that is
configured every request is rejected; tests install a stub (see tests/conftest.py).
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

import jwt
from fastapi import Depends, HTTPException, Request, status

from sewsure_api.settings import Settings

_ALGORITHMS = ["RS256", "ES256"]  # asymmetric only; never "none" or a shared secret
_MAX_USER_ID_LENGTH = 80  # owner_id column size


@dataclass(frozen=True)
class CurrentUser:
    id: str


class AuthProvider(Protocol):
    def authenticate(self, request: Request) -> CurrentUser | None:
        """Return the caller, or None if credentials are missing or invalid."""
        ...


class RejectAllAuth:
    def authenticate(self, request: Request) -> CurrentUser | None:
        return None


class JwtAuth:
    def __init__(self, issuer: str, audience: str, signing_key_for: Callable[[str], Any]) -> None:
        self._issuer = issuer
        self._audience = audience
        self._signing_key_for = signing_key_for

    def authenticate(self, request: Request) -> CurrentUser | None:
        scheme, _, token = request.headers.get("Authorization", "").partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None
        try:
            claims = jwt.decode(
                token,
                self._signing_key_for(token).key,
                algorithms=_ALGORITHMS,
                issuer=self._issuer,
                audience=self._audience,
                options={"require": ["exp", "iss", "aud", "sub"]},
            )
        except jwt.PyJWTError:
            return None
        subject = claims["sub"]
        return CurrentUser(id=subject) if 0 < len(subject) <= _MAX_USER_ID_LENGTH else None


def auth_from_settings(settings: Settings) -> AuthProvider:
    if not (settings.auth_issuer and settings.auth_audience and settings.auth_jwks_url):
        return RejectAllAuth()
    jwks = jwt.PyJWKClient(settings.auth_jwks_url)
    return JwtAuth(settings.auth_issuer, settings.auth_audience, jwks.get_signing_key_from_jwt)


def get_auth_provider(request: Request) -> AuthProvider:
    return request.app.state.auth_provider


def get_current_user(
    request: Request, provider: AuthProvider = Depends(get_auth_provider)
) -> CurrentUser:
    user = provider.authenticate(request)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "authentication required")
    return user
