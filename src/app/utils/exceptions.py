# Packages
from fastapi import HTTPException


class ExtensionNotAllowed(HTTPException):
    """
    This exception is raised when file extension is not
     in ALLOWED_EXTENSIONS list
    """

    def __init__(
            self,
            status_code: int,
            detail: str,
            headers=None
    ) -> None:
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}

        super().__init__(status_code=status_code, detail=detail, headers=headers)
