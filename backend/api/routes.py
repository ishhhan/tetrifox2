"""
API Routes - Thin Controller Layer

This module defines the API endpoints. Business logic is delegated
to the LogisticsOrchestrator (Facade Pattern) via Dependency Injection.
"""
from fastapi import APIRouter, HTTPException, Depends

# Import DTOs
from dtos.request import LogisticsRequest
from dtos.response import (
    LogisticsResponse, 
    HistoryListResponse, 
    HistoryDetailDTO,
    GenericMessageDTO
)

# Import Services & DI
from services.logistics.compute import LogisticsOrchestrator
from services.dependencies import get_orchestrator
from services.history.store import HistoryStore

# Define Router
router = APIRouter()


@router.post("/process-logistics", response_model=LogisticsResponse)
def process_logistics(
    payload: LogisticsRequest,
    orchestrator: LogisticsOrchestrator = Depends(get_orchestrator)
):
    """
    Process logistics data and assign routes.
    
    Uses Dependency Injection to get the orchestrator instance.
    """
    return orchestrator.process(payload)


@router.get("/history", response_model=HistoryListResponse)
def get_history():
    """Get list of all processing history entries."""
    return {"history": HistoryStore.get_all()}


@router.get("/history/{entry_id}", response_model=HistoryDetailDTO)
def get_history_entry(entry_id: str):
    """Get full data for a specific history entry including metadata."""
    entry = HistoryStore.get_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")   
    return entry


@router.delete("/history/{entry_id}", response_model=GenericMessageDTO)
def delete_history_entry(entry_id: str):
    """Delete a history entry."""
    success = HistoryStore.delete_by_id(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "History entry deleted"}