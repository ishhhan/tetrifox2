from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid
import logging
from schemas.parsing import ParsingStats, RemovedParcel

logger = logging.getLogger("TetrifoxEngine")

HistoryParsingStats = ParsingStats

class HistoryEntry(BaseModel):
    id: str
    timestamp: str
    total_processed: int
    data: List[Any]
    departments: List[Dict[str, Any]] = []
    priority_order: List[str] = []
    parsing_stats: Optional[HistoryParsingStats] = None


class HistorySummary(BaseModel):
    id: str
    timestamp: str
    total_processed: int


class HistoryStore:
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
        return cls._entries.get(entry_id)
    
    @classmethod
    def delete_by_id(cls, entry_id: str) -> bool:
        if entry_id in cls._entries:
            del cls._entries[entry_id]
            logger.info(f"History entry deleted: {entry_id}")
            return True
        return False
    
    @classmethod
    def clear(cls) -> None:
        cls._entries.clear()