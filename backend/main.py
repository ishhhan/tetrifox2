
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
from api.logistics import router as logistics_router
from api.history import router as history_router
from core.config import setup_logging

setup_logging()

app = FastAPI(
    title="Tetrifox Logistics Engine",
    description="Rule-based parcel routing and logistics processing",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(XmlParsingError, xml_exception_handler)
app.add_exception_handler(AggregatedValidationError, aggregated_validation_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(logistics_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1/history", tags=["History"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
