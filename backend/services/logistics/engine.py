from typing import List
from schemas.domain import Parcel, InternalRule
from services.logistics.rules import RuleEvaluator
from core.config import logger


class RoutingEngineService:

    ALLOWED_FIELDS = {'weight', 'value', 'postal_code', 'recipient', 'city'}
    
    def __init__(self, departments: List[InternalRule], priority_order: List[str]):
        self._validate_inputs(departments, priority_order)
        
        self.departments = departments
        self.priority_order = priority_order
        logger.info(f"RoutingEngine initialized with {len(departments)} rules, priority: {priority_order}")
    
    def _validate_inputs(self, departments: List[InternalRule], priority_order: List[str]) -> None:
        if not departments:
            logger.warning("RoutingEngine initialized with no department rules")
        
        for dept in departments:
            if dept.field not in self.ALLOWED_FIELDS:
                raise ValueError(f"Invalid department field: {dept.field}")
            
            if dept.type not in {'range', 'match'}:
                raise ValueError(f"Invalid department type: {dept.type}")
            
            if dept.type == 'range':
                if dept.min is not None and dept.max is not None:
                    if dept.min > dept.max:
                        raise ValueError(f"Department '{dept.name}': min > max")
            
            elif dept.type == 'match':
                if not dept.match_value:
                    raise ValueError(f"Department '{dept.name}': match_value is required")
        
        if not priority_order:
            logger.warning("RoutingEngine initialized with empty priority order")
        
        for field in priority_order:
            if field not in self.ALLOWED_FIELDS:
                raise ValueError(f"Invalid priority field: {field}")
     
    def execute_routing(self, parcels: List[Parcel]) -> List[Parcel]:
        if not parcels:
            logger.warning("No parcels to process")
            return parcels
        
        logger.info(f"Processing {len(parcels)} parcels with {len(self.departments)} rules")
        
        sorted_departments = self._sort_by_priority(self.departments)
        
        for parcel in parcels:
            assigned_departments = []
            
            for dept in sorted_departments:
                if RuleEvaluator.matches(parcel, dept):
                    assigned_departments.append(dept.name)
                    logger.debug(f"Parcel {parcel.id} matched department: {dept.name}")
            
            parcel.route = assigned_departments if assigned_departments else ["Unassigned"]
        
        assigned_count = sum(1 for p in parcels if p.route != ["Unassigned"])
        logger.info(f"Routing complete: {assigned_count}/{len(parcels)} parcels assigned")
        
        return parcels

    def _sort_by_priority(self, departments: List[InternalRule]) -> List[InternalRule]:
        """Sort departments based on the priority order of their field attribute."""
        priority_map = {field: idx for idx, field in enumerate(self.priority_order)}
        
        def get_priority(dept: InternalRule) -> int:
            return priority_map.get(dept.field, len(self.priority_order))
        
        return sorted(departments, key=get_priority)