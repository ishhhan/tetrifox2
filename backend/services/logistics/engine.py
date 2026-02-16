"""
Routing Engine Service with Service-Level Validation.

Processes parcels through department rules based on priority order,
assigning routes to each parcel.
"""
from typing import List
from schemas.domain import Parcel, InternalRule
from services.logistics.rules import RuleEvaluator
from core.config import logger


class RoutingEngineService:
    """
    Core routing engine that assigns parcels to departments
    based on configured rules and priority order.
    
    Includes service-level validation guards that verify inputs
    even if DTOs have already validated them.
    """
    
    ALLOWED_FIELDS = {'weight', 'value', 'postal_code', 'recipient', 'city'}
    
    def __init__(self, departments: List[InternalRule], priority_order: List[str]):
        """
        Initialize the routing engine with validation.
        
        Args:
            departments: List of department rules
            priority_order: List of field names in priority order
            
        Raises:
            ValueError: If inputs fail validation
        """
        # Service-level validation guards
        self._validate_inputs(departments, priority_order)
        
        self.departments = departments
        self.priority_order = priority_order
        logger.info(f"RoutingEngine initialized with {len(departments)} rules, priority: {priority_order}")
    
    def _validate_inputs(self, departments: List[InternalRule], priority_order: List[str]) -> None:
        """
        Validate inputs independently of DTO validation.
        
        This provides defense-in-depth: even if the orchestrator
        or DTO fails to validate, the engine will catch issues.
        """
        # Check departments
        if not departments:
            logger.warning("RoutingEngine initialized with no department rules")
        
        for dept in departments:
            if dept.field not in self.ALLOWED_FIELDS:
                raise ValueError(f"Invalid department field: {dept.field}")
            
            if dept.type not in {'range', 'match'}:
                raise ValueError(f"Invalid department type: {dept.type}")
            
            # Validate range rules
            if dept.type == 'range':
                if dept.min is not None and dept.max is not None:
                    if dept.min > dept.max:
                        raise ValueError(f"Department '{dept.name}': min > max")
            
            # Validate match rules
            elif dept.type == 'match':
                if not dept.match_value:
                    raise ValueError(f"Department '{dept.name}': match_value is required")
        
        # Check priority order
        if not priority_order:
            logger.warning("RoutingEngine initialized with empty priority order")
        
        for field in priority_order:
            if field not in self.ALLOWED_FIELDS:
                raise ValueError(f"Invalid priority field: {field}")
     
    def execute_routing(self, parcels: List[Parcel]) -> List[Parcel]:
        """
        Process all parcels and assign routes based on department rules.
        
        Rules are evaluated in the priority order specified.
        
        Args:
            parcels: List of parsed Parcel objects
            
        Returns:
            List of Parcel objects with assigned routes
        """
        if not parcels:
            logger.warning("No parcels to process")
            return parcels
        
        logger.info(f"Processing {len(parcels)} parcels with {len(self.departments)} rules")
        
        # Sort departments by priority order
        sorted_departments = self._sort_by_priority(self.departments)
        
        for parcel in parcels:
            assigned_departments = []
            
            # Evaluate each department rule
            for dept in sorted_departments:
                if RuleEvaluator.matches(parcel, dept):
                    assigned_departments.append(dept.name)
                    logger.debug(f"Parcel {parcel.id} matched department: {dept.name}")
            
            # Assign the route to the parcel
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