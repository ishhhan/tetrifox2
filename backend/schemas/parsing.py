from pydantic import BaseModel
from typing import List, Dict, Optional

class RemovedParcel(BaseModel):
    """Represents a parcel that was removed during parsing."""
    parcel_id: str
    reason: str  # "duplicate_id", "duplicate_content", "missing_field"
    details: str  # Additional info like "matches P001" or "missing: recipient"

class ParsingStats(BaseModel):
    """Statistics collected during the XML parsing process."""
    total_elements: int = 0
    valid_parcels: int = 0
    duplicates_removed: int = 0
    skipped_invalid: int = 0
    missing_fields: Dict[str, int] = {}
    duplicate_ids: List[str] = []
    removed_parcels: List[RemovedParcel] = []
