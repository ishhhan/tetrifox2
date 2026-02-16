"""
History Store - Stores processing history with full metadata.

Includes departments, priority order, and parsing statistics
for each history entry so they can be restored later.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid
import logging
from schemas.parsing import ParsingStats, RemovedParcel

logger = logging.getLogger("TetrifoxEngine")

# Alias for backward compatibility
HistoryParsingStats = ParsingStats


class HistoryEntry(BaseModel):
    """Full history entry with all metadata."""
    id: str
    timestamp: str
    total_processed: int
    data: List[Any]
    # New fields for restoring state
    departments: List[Dict[str, Any]] = []
    priority_order: List[str] = []
    parsing_stats: Optional[HistoryParsingStats] = None


class HistorySummary(BaseModel):
    """Summary shown in history list."""
    id: str
    timestamp: str
    total_processed: int


class HistoryStore:
    """In-memory store for processing history."""
    _entries: Dict[str, HistoryEntry] = {}
    
    @classmethod
    def add_entry(
        cls,
        data: List[Any],
        total_processed: int,
        departments: List[Dict[str, Any]] = None,
        priority_order: List[str] = None,
        parsing_stats: HistoryParsingStats = None
    ) -> str:
        """
        Add a new history entry with full metadata.
        
        Args:
            data: Processed parcel results
            total_processed: Number of parcels processed
            departments: Department rules used (optional)
            priority_order: Priority order used (optional)
            parsing_stats: Statistics from XML parsing (optional)
            
        Returns:
            The generated entry ID
        """
        entry_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        entry = HistoryEntry(
            id=entry_id,
            timestamp=timestamp,
            total_processed=total_processed,
            data=data,
            departments=departments or [],
            priority_order=priority_order or [],
            parsing_stats=parsing_stats
        )
        cls._entries[entry_id] = entry
        logger.info(f"History entry created: {entry_id} ({total_processed} parcels)")
        return entry_id
    
    @classmethod
    def get_all(cls) -> List[HistorySummary]:
        """Get list of all history entries (summary only)."""
        summaries = [
            HistorySummary(
                id=e.id, timestamp=e.timestamp, total_processed=e.total_processed
            )
            for e in cls._entries.values()
        ]
        summaries.sort(key=lambda x: x.timestamp, reverse=True)
        return summaries
    
    @classmethod
    def get_by_id(cls, entry_id: str) -> Optional[HistoryEntry]:
        """Get full history entry by ID."""
        return cls._entries.get(entry_id)
    
    @classmethod
    def delete_by_id(cls, entry_id: str) -> bool:
        """Delete a history entry by ID. Returns True if deleted."""
        if entry_id in cls._entries:
            del cls._entries[entry_id]
            logger.info(f"History entry deleted: {entry_id}")
            return True
        return False
    
    @classmethod
    def clear(cls) -> None:
        """Clear all history (useful for testing)."""
        cls._entries.clear()