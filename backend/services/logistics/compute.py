from typing import List, Dict, Any
from core.config import logger
from core.exceptions import AggregatedValidationError
from validators.logic import ErrorCollector, BusinessValidator
from schemas.domain import InternalRule
from schemas.parsing import ParsingStats, RemovedParcel
from dtos.request import LogisticsRequest, DepartmentRuleDTO
from dtos.response import LogisticsResponse, ParcelOutputDTO, AddressDTO, ParsingStatsDTO, RemovedParcelDTO
from services.logistics.engine import RoutingEngineService


class LogisticsOrchestrator: 
    def __init__(self, parser_service, history_store):
        self.parser_service = parser_service
        self.history_store = history_store

    def process(self, request: LogisticsRequest) -> Dict[str, Any]:
        logger.info("Starting logistics orchestration...")
        
        collector = ErrorCollector()
        
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
        
        BusinessValidator.collect_priority_errors(request.priority_order, collector)
        
        parcels = []
        parsing_stats = None
        try:
            parcels, parsing_stats = self.parser_service.parse_with_stats(request.xml_data)
            if not parcels:
                collector.add("No valid parcels found in XML data")
        except Exception as e:
            collector.add(f"XML parsing failed: {str(e)}")
        
        if collector.has_errors():
            raise AggregatedValidationError(collector.errors)
        
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
        
        processed_parcels = []
        try:
            engine = RoutingEngineService(
                departments=domain_rules,
                priority_order=request.priority_order
            )
            processed_parcels = engine.execute_routing(parcels)
        except ValueError as e:
            collector.add(f"Routing configuration error: {str(e)}")
            
        if collector.has_errors():
            raise AggregatedValidationError(collector.errors)
        
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
        
        departments_data = [dept.model_dump() for dept in request.departments]
        
        try:
            self.history_store.add_entry(
                data=[r.model_dump() for r in results],
                total_processed=len(results),
                departments=departments_data,
                priority_order=request.priority_order,
                parsing_stats=parsing_stats
            )
        except Exception as e:
            logger.error(f"Failed to save request to history: {str(e)}")

        logger.info(f"Orchestration complete. Processed {len(results)} parcels.")
        
        response = {
            "status": "success",
            "total_processed": len(results),
            "data": results,
            "parsing_stats": None
        }
        
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
    

