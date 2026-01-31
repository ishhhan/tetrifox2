from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional
from validators.logic import BusinessValidator

class DepartmentRuleDTO(BaseModel):
    name: str = Field(..., description="Name of the department")
    field: Literal['weight', 'value', 'postal_code', 'recipient', 'city']
    type: Literal['range', 'match']
    min: Optional[float] = None
    max: Optional[float] = None
    match_value: Optional[str] = None

    @field_validator('max')
    @classmethod
    def validate_range_logic(cls, v, info):
        min_val = info.data.get('min')
        if v is not None and min_val is not None:
            # Call the centralized validator
            BusinessValidator.validate_department_range(min_val, v)
        return v

class LogisticsRequest(BaseModel):
    xml_data: str = Field(..., description="Raw XML string containing parcels")
    departments: List[DepartmentRuleDTO]
    priority_order: List[str]

    @field_validator('xml_data')
    @classmethod
    def check_xml(cls, v):
        BusinessValidator.validate_xml_structure(v)
        return v

    @field_validator('priority_order')
    @classmethod
    def check_priorities(cls, v):
        BusinessValidator.validate_priority_list(v)
        return v