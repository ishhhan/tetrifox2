from pydantic import BaseModel, Field
from typing import List, Any, Optional, Dict

class AddressDTO(BaseModel):
    city: str
    postal_code: str
    street: str

class ParcelOutputDTO(BaseModel):
    parcel_id: str
    recipient: str
    weight: float
    value: float
    address: AddressDTO
    assigned_route: List[str]

class RemovedParcelDTO(BaseModel):
    """A parcel that was removed during parsing."""
    parcel_id: str
    reason: str  # "duplicate_id", "duplicate_content", "missing_field"
    details: str  # "matches P001" or "missing: recipient"

class ParsingStatsDTO(BaseModel):
    """Statistics from XML parsing."""
    total_elements: int
    valid_parcels: int
    duplicates_removed: int
    skipped_invalid: int
    missing_fields: Dict[str, int] = {}
    duplicate_ids: List[str] = []
    removed_parcels: List[RemovedParcelDTO] = []

class BaseResponseDTO(BaseModel):
    """Base model for all success responses to ensure consistency."""
    status: str = "success"

class GenericMessageDTO(BaseResponseDTO):
    """Simple response with a message."""
    message: str

class LogisticsResponse(BaseResponseDTO):
    total_processed: int
    data: List[ParcelOutputDTO]
    parsing_stats: Optional[ParsingStatsDTO] = None

class HistorySummaryDTO(BaseModel):
    id: str
    timestamp: str
    total_processed: int

class HistoryDetailDTO(BaseResponseDTO):
    id: str
    timestamp: str
    total_processed: int
    data: List[ParcelOutputDTO]
    departments: List[Dict[str, Any]]  # Raw dump from input rules
    priority_order: List[str]
    parsing_stats: Optional[ParsingStatsDTO] = None

class HistoryListResponse(BaseResponseDTO):
    history: List[HistorySummaryDTO]