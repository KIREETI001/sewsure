"""HTTP errors. Every non-2xx body is the contract ApiError (see app.py handlers)."""

from fastapi import HTTPException


class ApiProblem(HTTPException):
    def __init__(
        self, status_code: int, code: str, message: str, *, recoverable: bool = False
    ) -> None:
        super().__init__(status_code, message)
        self.code = code
        self.recoverable = recoverable


class NotFound(ApiProblem):
    """Also used for wrong-user access, so existence is not leaked."""

    def __init__(self, what: str = "resource") -> None:
        super().__init__(404, "NOT_FOUND", f"{what} not found")


class Conflict(ApiProblem):
    def __init__(self, message: str, code: str = "CONFLICT", *, recoverable: bool = False) -> None:
        super().__init__(409, code, message, recoverable=recoverable)


class Unprocessable(ApiProblem):
    def __init__(self, message: str, code: str = "VALIDATION_FAILED") -> None:
        super().__init__(422, code, message, recoverable=True)
