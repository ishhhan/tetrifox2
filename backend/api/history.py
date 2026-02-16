from fastapi import APIRouter, HTTPException
from dtos.response import HistoryListResponse, HistoryDetailDTO, GenericMessageDTO
from services.history.store import HistoryStore

router = APIRouter()

@router.get("", response_model=HistoryListResponse)
def get_history():
    """Get list of all processing history entries."""
    return {"history": HistoryStore.get_all()}


@router.get("/{entry_id}", response_model=HistoryDetailDTO)
def get_history_entry(entry_id: str):
    """Get full data for a specific history entry including metadata."""
    entry = HistoryStore.get_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")   
    return entry

@router.delete("/{entry_id}", response_model=GenericMessageDTO)
def delete_history_entry(entry_id: str):
    """Delete a history entry."""
    success = HistoryStore.delete_by_id(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "History entry deleted"}


