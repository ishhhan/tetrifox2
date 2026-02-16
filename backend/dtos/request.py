from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Literal, Optional, Any
from validators.logic import BusinessValidator

class DepartmentRuleDTO(BaseModel):
    name: str = Field(..., description="Name of the department")
    field: Literal['weight', 'value', 'postal_code', 'recipient', 'city']
    type: Literal['range', 'match']
    min: Optional[float] = None
    max: Optional[float] = None
    match_value: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def set_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            field = data.get('field')
            min_val = data.get('min')
            max_val = data.get('max')
            
            # Auto-calculate max for 'value' rules if missing
            if field == 'value' and min_val is not None and max_val is None:
                # Default to 10x the min value (as per rule: max <= 10x min)
                # We use the constant from BusinessValidator
                calc_max = min_val * BusinessValidator.MAX_VALUE_RATIO
                
                # Cap at the global maximum allowed
                if calc_max > BusinessValidator.MAX_VALUE:
                    calc_max = BusinessValidator.MAX_VALUE
                
                data['max'] = calc_max

            # # Auto-calculate max for 'weight' rules if missing
            # if field == 'weight' and min_val is not None and max_val is None:
            #     # Default to min + 10 (as per rule: span <= 10kg)
            #     calc_max = min_val + BusinessValidator.MAX_WEIGHT_SPAN
                
            #     # Cap at global max weight
            #     if calc_max > BusinessValidator.MAX_WEIGHT:
            #         calc_max = BusinessValidator.MAX_WEIGHT
                
            #     data['max'] = calc_max
        return data

    @field_validator('max')
    @classmethod
    def validate_range_logic(cls, v, info):
        min_val = info.data.get('min')
        field_type = info.data.get('field', 'generic')
        if v is not None and min_val is not None:
            # Call the centralized validator
            BusinessValidator.validate_department_range(min_val, v, field_type)
        return v

class LogisticsRequest(BaseModel):
    xml_data: str = Field(..., description="Raw XML string containing parcels")
    departments: List[DepartmentRuleDTO]
    priority_order: List[str]

    @field_validator('departments')
    @classmethod
    def check_overlaps(cls, v):
        BusinessValidator.validate_department_overlap(v)
        return v

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

