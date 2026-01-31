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
    
    Provides both throwing validators (raise on first error) and
    collecting validators (add errors to collector).
    """

    # ========================================================================
    # THROWING VALIDATORS (for DTO-level validation)
    # ========================================================================

    @staticmethod
    def validate_department_range(min_val: Optional[float], max_val: Optional[float]) -> None:
        """
        Validates range logic. Raises ValueError on first error.
        
        Rules:
        1. Min cannot be negative
        2. Min cannot exceed Max
        3. Range cannot be too wide (Max > 100x Min)
        4. Max cannot exceed 10000
        """
        if min_val is not None and min_val < 0:
            raise ValueError(f"Minimum value cannot be negative: {min_val}")

        if min_val is not None and max_val is not None:
            if min_val > max_val:
                raise ValueError(f"Min ({min_val}) cannot be greater than Max ({max_val})")
            
            if max_val > (min_val * 100) and min_val > 0:
                raise ValueError(f"Range too wide: Max ({max_val}) exceeds 100x Min ({min_val})")

            if max_val > 10000:
                raise ValueError(f"Max value {max_val} exceeds global limit of 10000")

    @staticmethod
    def validate_xml_structure(xml_content: str) -> None:
        """Validates XML structure. Raises ValueError on error."""
        if not xml_content or not xml_content.strip():
            raise ValueError("XML content is empty")
        
        try:
            ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {str(e)}")

    @staticmethod
    def validate_priority_list(priorities: list) -> None:
        """Validates priority list. Raises ValueError on error."""
        allowed = ['weight', 'value', 'postal_code', 'recipient', 'city']
        for p in priorities:
            if p not in allowed:
                raise ValueError(f"Invalid priority field: {p}")

    # ========================================================================
    # COLLECTING VALIDATORS (for service-level aggregated validation)
    # ========================================================================

    @staticmethod
    def collect_range_errors(
        min_val: Optional[float],
        max_val: Optional[float],
        dept_name: str,
        collector: ErrorCollector
    ) -> None:
        """Validates range and adds errors to collector instead of throwing."""
        if min_val is not None and min_val < 0:
            collector.add(f"Department '{dept_name}': Minimum value cannot be negative ({min_val})")

        if min_val is not None and max_val is not None:
            if min_val > max_val:
                collector.add(f"Department '{dept_name}': Min ({min_val}) cannot be greater than Max ({max_val})")
            
            if max_val > (min_val * 100) and min_val > 0:
                collector.add(f"Department '{dept_name}': Range too wide (Max exceeds 100x Min)")

            if max_val > 10000:
                collector.add(f"Department '{dept_name}': Max value {max_val} exceeds limit of 10000")

    @staticmethod
    def collect_priority_errors(priorities: list, collector: ErrorCollector) -> None:
        """Validates priorities and adds errors to collector."""
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
    def collect_xml_errors(xml_content: str, collector: ErrorCollector) -> bool:
        """
        Validates XML and adds errors to collector.
        
        Returns:
            True if XML is valid, False otherwise
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