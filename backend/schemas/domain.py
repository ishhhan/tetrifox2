from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Parcel:
    """Internal Domain Object for a Parcel"""
    id: str
    recipient: str
    street: str
    city: str
    postal_code: str
    weight: float
    value: float
    route: List[str] = field(default_factory=list)

@dataclass
class InternalRule:
    """Internal representation of a rule"""
    name: str
    field: str
    type: str
    min: Optional[float] = None
    max: Optional[float] = None
    match_value: Optional[str] = None