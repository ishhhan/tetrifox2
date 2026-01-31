"""
Logistics Orchestrator - Facade Pattern

This module provides a high-level orchestration layer that coordinates
the entire logistics processing flow, keeping business logic separate
from the API controller.
"""
from typing import List, Dict, Any
from core.config import logger
from core.exceptions import AggregatedValidationError
from validators.logic import ErrorCollector, BusinessValidator
from services.logistics.parser import XmlParserService
from services.logistics.engine import RoutingEngineService
from services.history.store import HistoryStore
from schemas.domain import InternalRule
from schemas.parsing import ParsingStats, RemovedParcel
from dtos.request import LogisticsRequest, DepartmentRuleDTO
from dtos.response import LogisticsResponse, ParcelOutputDTO, AddressDTO, ParsingStatsDTO, RemovedParcelDTO


class LogisticsOrchestrator:
    """
    Facade that orchestrates the entire logistics processing flow.
    
    Responsibilities:
    1. Aggregate validation errors across all inputs
    2. Parse XML and deduplicate parcels
    3. Map DTOs to domain objects
    4. Execute the routing engine
    5. Save results to history with full metadata
    6. Return formatted response
    """
    
    @staticmethod
    def process(request: LogisticsRequest) -> Dict[str, Any]:
        """
        Main orchestration method.
        
        Args:
            request: The validated LogisticsRequest from the API
            
        Returns:
            Dictionary with status, total_processed, data, and parsing_stats
            
        Raises:
            AggregatedValidationError: If any validation errors are collected
        """
        logger.info("Starting logistics orchestration...")
        
        # 1. Collect all validation errors
        collector = ErrorCollector()
        
        # Validate departments (service-level check)
        LogisticsOrchestrator._validate_departments(request.departments, collector)
        
        # Validate priority order (service-level check)
        LogisticsOrchestrator._validate_priorities(request.priority_order, collector)
        
        # 2. Parse XML with error collection and stats
        parcels = []
        parsing_stats = None
        try:
            parcels, parsing_stats = XmlParserService.parse_with_stats(request.xml_data)
            if not parcels:
                collector.add("No valid parcels found in XML data")
        except Exception as e:
            collector.add(f"XML parsing failed: {str(e)}")
        
        # Raise aggregated errors if any
        if collector.has_errors():
            raise AggregatedValidationError(collector.errors)
        
        # 3. Map DTO rules to Internal Domain Rules
        domain_rules = [
            InternalRule(
                name=rule.name,
                field=rule.field,
                type=rule.type,
                min=rule.min,
                max=rule.max,
                match_value=rule.match_value
            ) for rule in request.departments
        ]
        
        # 4. Initialize & Run Engine
        engine = RoutingEngineService(
            departments=domain_rules,
            priority_order=request.priority_order
        )
        processed_parcels = engine.execute_routing(parcels)
        
        # 5. Map Domain -> Output DTO
        results = []
        for p in processed_parcels:
            dto = ParcelOutputDTO(
                parcel_id=p.id,
                recipient=p.recipient,
                weight=p.weight,
                value=p.value,
                address=AddressDTO(
                    city=p.city,
                    street=p.street,
                    postal_code=p.postal_code
                ),
                assigned_route=p.route
            )
            results.append(dto)
        
        # 6. Prepare history metadata
        departments_data = [dept.model_dump() for dept in request.departments]
        
        # 7. Save to History with full metadata
        # parsing_stats is now the shared schema object, so we pass it directly
        HistoryStore.add_entry(
            data=[r.model_dump() for r in results],
            total_processed=len(results),
            departments=departments_data,
            priority_order=request.priority_order,
            parsing_stats=parsing_stats
        )
        logger.info(f"Orchestration complete. Processed {len(results)} parcels.")
        
        # 8. Build response with parsing stats
        response = {
            "status": "success",
            "total_processed": len(results),
            "data": results,
            "parsing_stats": None
        }
        
        # Include parsing stats in response if there are issues to report
        if parsing_stats and (parsing_stats.duplicates_removed > 0 or parsing_stats.missing_fields or parsing_stats.removed_parcels):
            response["parsing_stats"] = ParsingStatsDTO(
                total_elements=parsing_stats.total_elements,
                valid_parcels=parsing_stats.valid_parcels,
                duplicates_removed=parsing_stats.duplicates_removed,
                skipped_invalid=parsing_stats.skipped_invalid,
                missing_fields=parsing_stats.missing_fields,
                duplicate_ids=parsing_stats.duplicate_ids,
                removed_parcels=[
                    RemovedParcelDTO(
                        parcel_id=rp.parcel_id,
                        reason=rp.reason,
                        details=rp.details
                    ) for rp in parsing_stats.removed_parcels
                ]
            )
        
        return response
    
    @staticmethod
    def _validate_departments(departments: List[DepartmentRuleDTO], collector: ErrorCollector) -> None:
        """Validate department rules and collect errors."""
        if not departments:
            collector.add("At least one department rule is required")
            return
            
        for i, dept in enumerate(departments):
            # Check range rules
            if dept.type == "range":
                if dept.min is not None and dept.min < 0:
                    collector.add(f"Department '{dept.name}': Minimum value cannot be negative ({dept.min})")
                
                if dept.min is not None and dept.max is not None:
                    if dept.min > dept.max:
                        collector.add(f"Department '{dept.name}': Min ({dept.min}) cannot be greater than Max ({dept.max})")
                    
                    if dept.max > (dept.min * 100) and dept.min > 0:
                        collector.add(f"Department '{dept.name}': Range too wide (Max exceeds 100x Min)")
                    
                    if dept.max > 10000:
                        collector.add(f"Department '{dept.name}': Max value exceeds limit of 10000")
            
            # Check match rules
            elif dept.type == "match":
                if not dept.match_value or not dept.match_value.strip():
                    collector.add(f"Department '{dept.name}': Match value cannot be empty")
    
    @staticmethod
    def _validate_priorities(priorities: List[str], collector: ErrorCollector) -> None:
        """Validate priority order and collect errors."""
        if not priorities:
            collector.add("Priority order cannot be empty")
            return
            
        allowed = {'weight', 'value', 'postal_code', 'recipient', 'city'}
        for p in priorities:
            if p not in allowed:
                collector.add(f"Invalid priority field: '{p}'. Allowed: {', '.join(allowed)}")
        
        # Check for duplicates
        seen = set()
        for p in priorities:
            if p in seen:
                collector.add(f"Duplicate priority field: '{p}'")
            seen.add(p)
