"""
Tetrifox Logistics Engine - Main Entry Point

FastAPI application with CORS, exception handlers, and API routes.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.exceptions import (
    XmlParsingError,
    AggregatedValidationError,
    xml_exception_handler,
    aggregated_validation_handler,
    generic_exception_handler
)
from api.routes import router
from core.config import setup_logging

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Tetrifox Logistics Engine",
    description="Rule-based parcel routing and logistics processing",
    version="2.0.0"
)

# CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers (order matters - more specific first)
app.add_exception_handler(XmlParsingError, xml_exception_handler)
app.add_exception_handler(AggregatedValidationError, aggregated_validation_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API routes with /api/v1 prefix
app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
