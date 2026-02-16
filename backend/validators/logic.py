
import xml.etree.ElementTree as ET
from typing import List, Optional


class ErrorCollector:

    def __init__(self):
        self._errors: List[str] = []
    
    def add(self, error: str) -> None:
        self._errors.append(error)
    
    def add_if(self, condition: bool, error: str) -> None:
        if condition:
            self._errors.append(error)
    
    @property
    def errors(self) -> List[str]:
        return self._errors.copy()
    
    def has_errors(self) -> bool:
        return len(self._errors) > 0
    
    def count(self) -> int:
        return len(self._errors)
    
    def clear(self) -> None:
        self._errors.clear()


class BusinessValidator:
    MAX_WEIGHT = 1000
    MAX_WEIGHT_SPAN = 10
    MAX_VALUE = 100000
    MAX_VALUE_RATIO = 10

    @staticmethod
    def _check_range_rules(min_val: Optional[float], max_val: Optional[float], field_name: str) -> List[str]:

        errors = []
        
        if min_val is not None and min_val < 0:
            errors.append(f"Minimum value cannot be negative: {min_val}")

        if min_val is not None and max_val is not None:
            if min_val > max_val:
                errors.append(f"Min ({min_val}) cannot be greater than Max ({max_val})")
            
            if field_name == "weight":
                if max_val > BusinessValidator.MAX_WEIGHT:
                    errors.append(f"Max weight {max_val} exceeds limit of {BusinessValidator.MAX_WEIGHT} kg")
                if (max_val - min_val) > BusinessValidator.MAX_WEIGHT_SPAN:
                    errors.append(f"Weight range span ({max_val - min_val}) cannot exceed {BusinessValidator.MAX_WEIGHT_SPAN} kg")

            elif field_name == "value":
                if max_val > BusinessValidator.MAX_VALUE:
                    errors.append(f"Max value {max_val} exceeds limit of {BusinessValidator.MAX_VALUE} €")
                
                if min_val > 0 and max_val > (min_val * BusinessValidator.MAX_VALUE_RATIO):
                    errors.append(f"Max value cannot exceed {BusinessValidator.MAX_VALUE_RATIO}x Min value (Min: {min_val}, Max: {max_val})")
        
        return errors


    @staticmethod
    def validate_department_range(min_val: Optional[float], max_val: Optional[float], field_name: str = "generic") -> None:
        errors = BusinessValidator._check_range_rules(min_val, max_val, field_name)
        if errors:
            raise ValueError(errors[0])

    @staticmethod
    def validate_xml_structure(xml_content: str) -> None:
        if not xml_content or not xml_content.strip():
            raise ValueError("XML content is empty")
        
        try:
            ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {str(e)}")

    @staticmethod
    def validate_priority_list(priorities: list) -> None:

        allowed = ['weight', 'value', 'postal_code', 'recipient', 'city']
        for p in priorities:
            if p not in allowed:
                raise ValueError(f"Invalid priority field: {p}")

    @staticmethod
    def validate_department_overlap(rules: list) -> None:

        names = set()
        for r in rules:
            if r.name.lower() in names:
                raise ValueError(f"Duplicate department name: '{r.name}'")
            names.add(r.name.lower())

        by_field = {}
        for r in rules:
            if r.type == 'range':
                by_field.setdefault(r.field, []).append(r)
        
        for field, group in by_field.items():
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    r1 = group[i]
                    r2 = group[j]
                    
                    min1 = r1.min if r1.min is not None else float('-inf')
                    max1 = r1.max if r1.max is not None else float('inf')
                    min2 = r2.min if r2.min is not None else float('-inf')
                    max2 = r2.max if r2.max is not None else float('inf')
                    
                    if max(min1, min2) < min(max1, max2):
                        raise ValueError(f"Overlapping range for field '{field}': '{r1.name}' and '{r2.name}'")


    @staticmethod
    def collect_range_errors(
        min_val: Optional[float],
        max_val: Optional[float],
        dept_name: str,
        field_name: str,
        collector: ErrorCollector
    ) -> None:

        errors = BusinessValidator._check_range_rules(min_val, max_val, field_name)
        for err in errors:
            collector.add(f"Department '{dept_name}': {err}")

    @staticmethod
    def collect_priority_errors(priorities: list, collector: ErrorCollector) -> None:
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
        if not match_value or not match_value.strip():
            collector.add(f"Department '{dept_name}': Match value cannot be empty")

    @staticmethod
    def collect_xml_errors(xml_content: str, collector: ErrorCollector) -> bool:
        if not xml_content or not xml_content.strip():
            collector.add("XML content is empty")
            return False
        
        try:
            ET.fromstring(xml_content)
            return True
        except ET.ParseError as e:
            collector.add(f"Invalid XML format: {str(e)}")
            return False