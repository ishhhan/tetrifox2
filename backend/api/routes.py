"""
API Routes - Thin Controller Layer

This module defines the API endpoints. Business logic is delegated
to the LogisticsOrchestrator (Facade Pattern).
"""
from fastapi import APIRouter, HTTPException

# Import DTOs
from dtos.request import LogisticsRequest
from dtos.response import LogisticsResponse

# Import Services
from compute import LogisticsOrchestrator
from services.history.store import HistoryStore

# Define Router
router = APIRouter()


@router.post("/process-logistics", response_model=LogisticsResponse)
def process_logistics(payload: LogisticsRequest):
    """
    Process logistics data and assign routes.
    
    This endpoint delegates all business logic to the LogisticsOrchestrator,
    keeping the controller thin and focused on HTTP concerns.
    """
    return LogisticsOrchestrator.process(payload)


@router.get("/history", response_model=dict)
def get_history():
    """Get list of all processing history entries."""
    return {"history": HistoryStore.get_all()}


@router.get("/history/{entry_id}")
def get_history_entry(entry_id: str):
    """Get full data for a specific history entry including metadata."""
    entry = HistoryStore.get_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    response = {
        "status": "success",
        "total_processed": entry.total_processed,
        "data": entry.data,
        "departments": entry.departments,
        "priority_order": entry.priority_order
    }
    
    # Include parsing stats if available
    if entry.parsing_stats:
        response["parsing_stats"] = entry.parsing_stats.model_dump()
    
    return response


@router.delete("/history/{entry_id}")
def delete_history_entry(entry_id: str):
    """Delete a history entry."""
    success = HistoryStore.delete_by_id(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "success", "message": "History entry deleted"}