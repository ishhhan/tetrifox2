from pydantic import BaseModel
from typing import List, Dict, Optional

class RemovedParcel(BaseModel):
    parcel_id: str
    reason: str 
    details: str 

class ParsingStats(BaseModel):
    total_elements: int = 0
    valid_parcels: int = 0
    duplicates_removed: int = 0
    skipped_invalid: int = 0
    missing_fields: Dict[str, int] = {}
    duplicate_ids: List[str] = []
    removed_parcels: List[RemovedParcel] = []
