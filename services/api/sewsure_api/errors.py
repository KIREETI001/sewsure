from fastapi import HTTPException, status


class NotFound(HTTPException):
    """Also used for wrong-user access, so existence is not leaked."""

    def __init__(self, what: str = "resource") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, f"{what} not found")


class Conflict(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(status.HTTP_409_CONFLICT, message)


class Unprocessable(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(422, message)
