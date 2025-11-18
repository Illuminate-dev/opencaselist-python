"""Custom exceptions for the OpenCaselist API client"""

from typing import Optional


class OpenCaselistError(Exception):
    """Base exception for all OpenCaselist API errors"""

    pass


class AuthenticationError(OpenCaselistError):
    """Raised when authentication fails"""

    pass


class NotFoundError(OpenCaselistError):
    """Raised when a resource is not found (404)"""

    pass


class ValidationError(OpenCaselistError):
    """Raised when request validation fails"""

    pass


class APIError(OpenCaselistError):
    """Raised when the API returns an error response"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code
