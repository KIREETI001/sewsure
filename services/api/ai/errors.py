"""Recoverable model-side failures."""

from __future__ import annotations


class ModelError(Exception):
    """Recoverable model failure; the job can be retried or resumed."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(f"{code}: {message}" if message else code)
        self.code = code


class ModelTimeout(ModelError):
    def __init__(self, message: str = "") -> None:
        super().__init__("MODEL_TIMEOUT", message)
