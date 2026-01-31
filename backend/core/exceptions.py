"""
Custom Exceptions and Exception Handlers for the Tetrifox Engine.
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from typing import List
import logging

logger = logging.getLogger("TetrifoxEngine")


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class XmlParsingError(Exception):
    """Raised when the uploaded XML is malformed or cannot be parsed."""
    pass


class RuleConfigurationError(Exception):
    """Raised when rule logic is invalid."""
    pass


class AggregatedValidationError(Exception):
    """
    Raised when multiple validation errors are collected.
    
    This exception supports the Collector Pattern, allowing the system
    to report all validation errors at once instead of failing on the first.
    """
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"{len(errors)} validation error(s) occurred")


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

async def xml_exception_handler(request: Request, exc: XmlParsingError):
    """Handle XML parsing errors with 422 status."""
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "type": "XML_ERROR",
            "message": str(exc)
        },
    )


async def aggregated_validation_handler(request: Request, exc: AggregatedValidationError):
    """
    Handle aggregated validation errors.
    
    Returns all collected errors in a single response, following
    industry best practices for API error reporting.
    """
    logger.warning(f"Validation failed with {len(exc.errors)} errors")
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "type": "VALIDATION_ERROR",
            "message": f"{len(exc.errors)} validation error(s) occurred",
            "errors": exc.errors
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions with 500 status."""
    logger.error(f"Critical System Failure: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "type": "SERVER_ERROR",
            "message": "Internal processing error."
        },
    )