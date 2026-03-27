"""Custom exception classes for the API."""


class APIException(Exception):
    """Base exception for API errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class NotFoundError(APIException):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, message)


class ConflictError(APIException):
    """Raised when there's a conflict (e.g., duplicate email)."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(409, message)


class ValidationError(APIException):
    """Raised when validation fails."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(400, message)
