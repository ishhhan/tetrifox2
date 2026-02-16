"""
Logistics Orchestrator - Facade Pattern with Dependency Injection

This module provides a high-level orchestration layer that coordinates
the entire logistics processing flow. It uses Dependency Injection 
to allow for loose coupling and better testability.
"""
from typing import List, Dict, Any
from core.config import logger
from core.exceptions import AggregatedValidationError
from validators.logic import ErrorCollector, BusinessValidator
# Note: We import types for hinting, but actual implementations are injected
from schemas.domain import InternalRule
from schemas.parsing import ParsingStats, RemovedParcel
from dtos.request import LogisticsRequest, DepartmentRuleDTO
from dtos.response import LogisticsResponse, ParcelOutputDTO, AddressDTO, ParsingStatsDTO, RemovedParcelDTO
from services.logistics.engine import RoutingEngineService


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
    
    def __init__(self, parser_service, history_store):
        """
        Initialize with dependencies (Dependency Injection).
        
        Args:
            parser_service: Service to parse XML (e.g., XmlParserService)
            history_store: Store to save results (e.g., HistoryStore)
        """
        self.parser_service = parser_service
        self.history_store = history_store

    def process(self, request: LogisticsRequest) -> Dict[str, Any]:
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
        if not request.departments:
            collector.add("At least one department rule is required")
        else:
            for dept in request.departments:
                if dept.type == "range":
                    BusinessValidator.collect_range_errors(
                        min_val=dept.min, 
                        max_val=dept.max, 
                        dept_name=dept.name, 
                        field_name=dept.field,
                        collector=collector
                    )
                elif dept.type == "match":
                    BusinessValidator.collect_match_errors(
                        match_value=dept.match_value,
                        dept_name=dept.name,
                        collector=collector
                    )
        
        # Validate priority order (service-level check)
        BusinessValidator.collect_priority_errors(request.priority_order, collector)
        
        # 2. Parse XML with error collection and stats
        parcels = []
        parsing_stats = None
        try:
            # delegated to injected parser
            parcels, parsing_stats = self.parser_service.parse_with_stats(request.xml_data)
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
        processed_parcels = []
        try:
            # We still instantiate Engine directly as it's a domain object factory/process
            # Ideally this could be injected too, but it depends on per-request rules.
            engine = RoutingEngineService(
                departments=domain_rules,
                priority_order=request.priority_order
            )
            processed_parcels = engine.execute_routing(parcels)
        except ValueError as e:
            collector.add(f"Routing configuration error: {str(e)}")
            
        # Re-check for errors (in case engine init failed)
        if collector.has_errors():
            raise AggregatedValidationError(collector.errors)
        
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
        
        # 7. Save to History with full metadata (SAFE TRAP)
        try:
            # delegated to injected history store
            self.history_store.add_entry(
                data=[r.model_dump() for r in results],
                total_processed=len(results),
                departments=departments_data,
                priority_order=request.priority_order,
                parsing_stats=parsing_stats
            )
        except Exception as e:
            # Trap system errors (DB/IO) and log them, but don't fail the user request
            # "Fail Open" strategy for auxiliary operations
            logger.error(f"Failed to save request to history: {str(e)}")
            # Optionally we could add a warning to the response, but for now we just log.

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
    

