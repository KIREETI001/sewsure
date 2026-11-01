"""Authentication interface. Routes depend on `get_current_user` only.

The real provider (token verification) plugs in via `AuthProvider`. Until one is configured
every request is rejected; tests install a stub (see tests/conftest.py).
"""

from dataclasses import dataclass
from typing import Protocol

from fastapi import Depends, HTTPException, Request, status


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


def get_auth_provider(request: Request) -> AuthProvider:
    return request.app.state.auth_provider


def get_current_user(
    request: Request, provider: AuthProvider = Depends(get_auth_provider)
) -> CurrentUser:
    user = provider.authenticate(request)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "authentication required")
    return user
