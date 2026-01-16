"""Custom exceptions for the application."""
from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class HorizonException(Exception):
    """Base exception for Horizon ERP."""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_http_exception(self) -> HTTPException:
        """Convert to HTTPException."""
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": self.message,
                "code": self.code,
                "details": self.details
            }
        )


class NotFoundError(HorizonException):
    """Resource not found error."""
    
    def __init__(
        self,
        resource: str,
        identifier: Any = None,
        message: Optional[str] = None
    ):
        self.resource = resource
        self.identifier = identifier
        msg = message or f"{resource} not found"
        if identifier:
            msg = f"{resource} with ID '{identifier}' not found"
        super().__init__(msg, code="NOT_FOUND")
    
    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": self.message,
                "code": self.code,
                "resource": self.resource,
                "identifier": str(self.identifier) if self.identifier else None
            }
        )


class ValidationError(HorizonException):
    """Validation error."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        errors: Optional[list] = None
    ):
        self.field = field
        self.errors = errors or []
        super().__init__(message, code="VALIDATION_ERROR")
    
    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": self.message,
                "code": self.code,
                "field": self.field,
                "errors": self.errors
            }
        )


class PermissionDeniedError(HorizonException):
    """Permission denied error."""
    
    def __init__(
        self,
        message: str = "Permission denied",
        required_permission: Optional[str] = None
    ):
        self.required_permission = required_permission
        super().__init__(message, code="PERMISSION_DENIED")
    
    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": self.message,
                "code": self.code,
                "required_permission": self.required_permission
            }
        )


class AuthenticationError(HorizonException):
    """Authentication error."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTHENTICATION_ERROR")
    
    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": self.message,
                "code": self.code
            },
            headers={"WWW-Authenticate": "Bearer"}
        )


class ConflictError(HorizonException):
    """Conflict error (e.g., duplicate resource)."""
    
    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        field: Optional[str] = None
    ):
        self.resource = resource
        self.field = field
        super().__init__(message, code="CONFLICT")
    
    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": self.message,
                "code": self.code,
                "resource": self.resource,
                "field": self.field
            }
        )


class RateLimitError(HorizonException):
    """Rate limit exceeded error."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        self.retry_after = retry_after
        super().__init__(message, code="RATE_LIMITED")
    
    def to_http_exception(self) -> HTTPException:
        headers = {}
        if self.retry_after:
            headers["Retry-After"] = str(self.retry_after)
        
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": self.message,
                "code": self.code,
                "retry_after": self.retry_after
            },
            headers=headers
        )


class TenantIsolationError(HorizonException):
    """Tenant isolation violation error."""
    
    def __init__(self, message: str = "Tenant isolation violation"):
        super().__init__(message, code="TENANT_ISOLATION_VIOLATION")
    
    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": self.message,
                "code": self.code
            }
        )


class SubscriptionError(HorizonException):
    """Subscription-related error (limit exceeded, expired, etc.)."""
    
    def __init__(
        self,
        message: str,
        limit_type: Optional[str] = None,
        current_usage: Optional[int] = None,
        limit: Optional[int] = None
    ):
        self.limit_type = limit_type
        self.current_usage = current_usage
        self.limit = limit
        super().__init__(message, code="SUBSCRIPTION_LIMIT")
    
    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": self.message,
                "code": self.code,
                "limit_type": self.limit_type,
                "current_usage": self.current_usage,
                "limit": self.limit
            }
        )


class ServiceUnavailableError(HorizonException):
    """External service unavailable error."""
    
    def __init__(
        self,
        service: str,
        message: Optional[str] = None
    ):
        self.service = service
        msg = message or f"Service '{service}' is currently unavailable"
        super().__init__(msg, code="SERVICE_UNAVAILABLE")
    
    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": self.message,
                "code": self.code,
                "service": self.service
            }
        )
