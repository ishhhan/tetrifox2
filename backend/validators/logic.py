"""
Business Validation Logic with Error Collection Support.

This module provides both throwing validators (for DTO-level validation)
and collecting validators (for service-level aggregated validation).
"""
import xml.etree.ElementTree as ET
from typing import List, Optional


class ErrorCollector:
    """
    Collects validation errors without throwing exceptions.
    
    Implements the Collector Pattern to aggregate multiple validation
    errors before reporting them all at once to the user.
    
    Usage:
        collector = ErrorCollector()
        collector.add("First error")
        collector.add("Second error")
        if collector.has_errors():
            raise AggregatedValidationError(collector.errors)
    """
    
    def __init__(self):
        self._errors: List[str] = []
    
    def add(self, error: str) -> None:
        """Add an error message to the collection."""
        self._errors.append(error)
    
    def add_if(self, condition: bool, error: str) -> None:
        """Add an error message only if condition is True."""
        if condition:
            self._errors.append(error)
    
    @property
    def errors(self) -> List[str]:
        """Get the list of collected errors."""
        return self._errors.copy()
    
    def has_errors(self) -> bool:
        """Check if any errors have been collected."""
        return len(self._errors) > 0
    
    def count(self) -> int:
        """Get the number of collected errors."""
        return len(self._errors)
    
    def clear(self) -> None:
        """Clear all collected errors."""
        self._errors.clear()


class BusinessValidator:
    """
    Centralized validation logic for business rules and inputs.
    
    Provides both throwing validators (for DTO-level validation)
    and collecting validators (for service-level aggregated validation).
    """

    # ========================================================================
    # CONSTANTS
    # ========================================================================
    MAX_WEIGHT = 1000
    MAX_WEIGHT_SPAN = 10
    MAX_VALUE = 100000
    MAX_VALUE_RATIO = 10

    # ========================================================================
    # SHARED LOGIC
    # ========================================================================

    @staticmethod
    def _check_range_rules(min_val: Optional[float], max_val: Optional[float], field_name: str) -> List[str]:
        """
        Single source of truth for range validation logic.
        Returns a list of error messages.
        
        Example Input:
            min_val: 10.5, max_val: 20.0, field_name: "weight"
        """
        errors = []
        
        # Check if minimum value is negative
        if min_val is not None and min_val < 0:
            errors.append(f"Minimum value cannot be negative: {min_val}")

        # Check logic when both thresholds are provided
        if min_val is not None and max_val is not None:
            # Ensure min doesn't exceed max
            if min_val > max_val:
                errors.append(f"Min ({min_val}) cannot be greater than Max ({max_val})")
            
            # Apply weight-specific limits
            if field_name == "weight":
                # Compare against absolute maximum weight
                if max_val > BusinessValidator.MAX_WEIGHT:
                    errors.append(f"Max weight {max_val} exceeds limit of {BusinessValidator.MAX_WEIGHT} kg")
                # Verify weight span stays within 10kg limit
                if (max_val - min_val) > BusinessValidator.MAX_WEIGHT_SPAN:
                    errors.append(f"Weight range span ({max_val - min_val}) cannot exceed {BusinessValidator.MAX_WEIGHT_SPAN} kg")

            # Apply value-specific limits
            elif field_name == "value":
                # Compare against absolute maximum value
                if max_val > BusinessValidator.MAX_VALUE:
                    errors.append(f"Max value {max_val} exceeds limit of {BusinessValidator.MAX_VALUE} €")
                
                # Verify value ratio doesn't exceed 10x
                if min_val > 0 and max_val > (min_val * BusinessValidator.MAX_VALUE_RATIO):
                    errors.append(f"Max value cannot exceed {BusinessValidator.MAX_VALUE_RATIO}x Min value (Min: {min_val}, Max: {max_val})")
        
        return errors

    # ========================================================================
    # THROWING VALIDATORS (for DTO-level validation)
    # ========================================================================

    @staticmethod
    def validate_department_range(min_val: Optional[float], max_val: Optional[float], field_name: str = "generic") -> None:
        """
        Validates range logic. Raises ValueError on first error.
        
        Rules:
        1. Min cannot be negative
        2. Min cannot exceed Max
        3. Weight: Max <= 1000, Span <= 10
        4. Value: Max <= 100000, Max <= 10 * Min

        Example Input:
            min_val: 100.0, max_val: 500.0, field_name: "value"
        """
        errors = BusinessValidator._check_range_rules(min_val, max_val, field_name)
        if errors:
            raise ValueError(errors[0])

    @staticmethod
    def validate_xml_structure(xml_content: str) -> None:
        """
        Validates XML structure. Raises ValueError on error.
        
        Example Input:
            xml_content: "<package><weight>10.5</weight><value>100</value></package>"
        """
        if not xml_content or not xml_content.strip():
            raise ValueError("XML content is empty")
        
        try:
            ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {str(e)}")

    @staticmethod
    def validate_priority_list(priorities: list) -> None:
        """
        Validates priority list. Raises ValueError on error.
        
        Example Input:
            priorities: ["weight", "postal_code", "recipient", "value"]
        """
        allowed = ['weight', 'value', 'postal_code', 'recipient', 'city']
        for p in priorities:
            if p not in allowed:
                raise ValueError(f"Invalid priority field: {p}")

    @staticmethod
    def validate_department_overlap(rules: list) -> None:
        """
        Validates that no departments have duplicate names or overlapping ranges.
        Raises ValueError on error.
        
        Example Input:
            rules: [
                DepartmentRule(name="Express", type="range", field="weight", min=0, max=5),
                DepartmentRule(name="Standard", type="range", field="weight", min=5.1, max=10)
            ]
        """
        # 1. Unique Name Check: Prevent two departments from having the same name
        names = set()
        for r in rules:
            # Check case-insensitive name uniqueness
            if r.name.lower() in names:
                raise ValueError(f"Duplicate department name: '{r.name}'")
            names.add(r.name.lower())

        # 2. Overlap Check: Ensure ranges for the same field don't clash
        # Group departments by field (e.g., grouping all 'weight' rules together)
        by_field = {}
        for r in rules:
            if r.type == 'range':
                by_field.setdefault(r.field, []).append(r)
        
        # Iterate through each field group to find overlapping ranges
        for field, group in by_field.items():
            # Nested loop to compare every pair of rules (r1 vs r2)
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    r1 = group[i]
                    r2 = group[j]
                    
                    # Normalize ranges: if min or max is None, use infinity
                    min1 = r1.min if r1.min is not None else float('-inf')
                    max1 = r1.max if r1.max is not None else float('inf')
                    min2 = r2.min if r2.min is not None else float('-inf')
                    max2 = r2.max if r2.max is not None else float('inf')
                    
                    # Check for overlap: If the start of the later range is before 
                    # the end of the earlier range, they overlap.
                    # Formula: max(min1, min2) < min(max1, max2)
                    if max(min1, min2) < min(max1, max2):
                        raise ValueError(f"Overlapping range for field '{field}': '{r1.name}' and '{r2.name}'")

    # ========================================================================
    # COLLECTING VALIDATORS (for service-level aggregated validation)
    # ========================================================================

    @staticmethod
    def collect_range_errors(
        min_val: Optional[float],
        max_val: Optional[float],
        dept_name: str,
        field_name: str,
        collector: ErrorCollector
    ) -> None:
        """
        Validates range and adds errors to collector instead of throwing.
        
        Example Input:
            min_val: 10, max_val: 5, dept_name: "Electronics", field_name: "weight"
        """
        errors = BusinessValidator._check_range_rules(min_val, max_val, field_name)
        for err in errors:
            collector.add(f"Department '{dept_name}': {err}")

    @staticmethod
    def collect_priority_errors(priorities: list, collector: ErrorCollector) -> None:
        """
        Validates priorities and adds errors to collector.
        
        Example Input:
            priorities: ["weight", "invalid_field", "weight"]
        """
        allowed = {'weight', 'value', 'postal_code', 'recipient', 'city'}
        
        if not priorities:
            collector.add("Priority order cannot be empty")
            return
        
        seen = set()
        for p in priorities:
            if p not in allowed:
                collector.add(f"Invalid priority field: '{p}'. Allowed: {', '.join(sorted(allowed))}")
            if p in seen:
                collector.add(f"Duplicate priority field: '{p}'")
            seen.add(p)

    @staticmethod
    def collect_match_errors(match_value: Optional[str], dept_name: str, collector: ErrorCollector) -> None:
        """
        Validates match rules and adds errors to collector.
        
        Example Input:
            match_value: "John Doe", dept_name: "Premium Delivery"
        """
        if not match_value or not match_value.strip():
            collector.add(f"Department '{dept_name}': Match value cannot be empty")

    @staticmethod
    def collect_xml_errors(xml_content: str, collector: ErrorCollector) -> bool:
        """
        Validates XML and adds errors to collector.
        
        Returns:
            True if XML is valid, False otherwise

        Example Input:
            xml_content: "<root>unclosed_tag"
        """
        if not xml_content or not xml_content.strip():
            collector.add("XML content is empty")
            return False
        
        try:
            ET.fromstring(xml_content)
            return True
        except ET.ParseError as e:
            collector.add(f"Invalid XML format: {str(e)}")
            return False