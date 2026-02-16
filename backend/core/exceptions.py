from fastapi import Request
from fastapi.responses import JSONResponse
from typing import List
import logging

logger = logging.getLogger("TetrifoxEngine")

class XmlParsingError(Exception):
    pass


class RuleConfigurationError(Exception):
    pass


class AggregatedValidationError(Exception):
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"{len(errors)} validation error(s) occurred")


async def xml_exception_handler(request: Request, exc: XmlParsingError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "type": "XML_ERROR",
            "message": str(exc)
        },
    )


async def aggregated_validation_handler(request: Request, exc: AggregatedValidationError):
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
    logger.error(f"Critical System Failure: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "type": "SERVER_ERROR",
            "message": "Internal processing error."
        },
    )