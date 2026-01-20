# ============================================================
# TODO 3: Custom Exceptions and Error Handling (AI-Generated)
# ============================================================
"""
Custom exception classes for the application.
Provides structured error handling with consistent HTTP responses.

AI-Generated: This file was created with AI assistance for TODO 3.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception for application-specific errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_type: str = "app_error",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_type = error_type


class NotFoundError(AppException):
    """Resource not found exception."""
    
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id {resource_id} not found",
            error_type="not_found"
        )


class ValidationError(AppException):
    """Input validation error exception."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_type="validation_error"
        )


class DatabaseError(AppException):
    """Database operation error exception."""
    
    def __init__(self, detail: str = "A database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_type="database_error"
        )


class LLMError(AppException):
    """LLM service error exception."""
    
    def __init__(self, detail: str = "LLM service encountered an error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_type="llm_error"
        )


class ExtractionError(AppException):
    """Action item extraction error exception."""
    
    def __init__(self, detail: str = "Failed to extract action items"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_type="extraction_error"
        )
