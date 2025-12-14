from __future__ import annotations

from fastapi import HTTPException, status


class GatewayError(HTTPException):
    def __init__(self, code: str, message: str, http_status: int = status.HTTP_400_BAD_REQUEST) -> None:
        super().__init__(status_code=http_status, detail={"error": {"code": code, "message": message}})
        self.code = code
        self.message = message


class ValidationError(GatewayError):
    def __init__(self, message: str) -> None:
        super().__init__(code="VALIDATION_ERROR", message=message, http_status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class NotFoundError(GatewayError):
    def __init__(self, message: str) -> None:
        super().__init__(code="NOT_FOUND", message=message, http_status=status.HTTP_404_NOT_FOUND)


class InternalError(GatewayError):
    def __init__(self, message: str = "Internal server error") -> None:
        super().__init__(code="INTERNAL", message=message, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
