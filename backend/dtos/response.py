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
    parcel_id: str
    reason: str  
    details: str 

class ParsingStatsDTO(BaseModel):
    total_elements: int
    valid_parcels: int
    duplicates_removed: int
    skipped_invalid: int
    missing_fields: Dict[str, int] = {}
    duplicate_ids: List[str] = []
    removed_parcels: List[RemovedParcelDTO] = []

class BaseResponseDTO(BaseModel):
    status: str = "success"

class GenericMessageDTO(BaseResponseDTO):
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
    departments: List[Dict[str, Any]]  
    priority_order: List[str]
    parsing_stats: Optional[ParsingStatsDTO] = None

class HistoryListResponse(BaseResponseDTO):
    history: List[HistorySummaryDTO]