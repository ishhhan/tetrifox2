import sys
import os
from unittest.mock import MagicMock
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_root)

from validators.logic import BusinessValidator, ErrorCollector
from services.logistics.rules import RuleEvaluator
from schemas.domain import Parcel, InternalRule

class MockRule:
    def __init__(self, name, field, type, min, max):
        self.name = name
        self.field = field
        self.type = type
        self.min = min
        self.max = max

def test_range_matching():
    print("--- Testing Range Matching Logic (min < val <= max) ---")
    
    rule = InternalRule(
        name="Test Rule",
        field="weight",
        type="range",
        min=10.0,
        max=20.0
    )
    
    print(f"\nRule: ({rule.min}, {rule.max}]")
    
    p1 = Parcel(id="p1", weight=10.0, value=100, postal_code="12345", recipient="Test", city="Test", street="Test Street")
    res1 = RuleEvaluator.matches(p1, rule)
    print(f"Match 10.0: {res1} {'✅ Correct' if not res1 else '❌ FAILED'}")

    p2 = Parcel(id="p2", weight=11.0, value=100, postal_code="12345", recipient="Test", city="Test", street="Test Street")
    res2 = RuleEvaluator.matches(p2, rule)
    print(f"Match 11.0: {res2} {'✅ Correct' if res2 else '❌ FAILED'}")

    p3 = Parcel(id="p3", weight=20.0, value=100, postal_code="12345", recipient="Test", city="Test", street="Test Street")
    res3 = RuleEvaluator.matches(p3, rule)
    print(f"Match 20.0: {res3} {'✅ Correct' if res3 else '❌ FAILED'}")
    
    p4 = Parcel(id="p4", weight=21.0, value=100, postal_code="12345", recipient="Test", city="Test", street="Test Street")
    res4 = RuleEvaluator.matches(p4, rule)
    print(f"Match 21.0: {res4} {'✅ Correct' if not res4 else '❌ FAILED'}")

def test_overlap_logic():
    print("\n--- Testing Overlap Logic (Max(min) < Min(max)) ---")
    
    r1 = MockRule("R1", "weight", "range", 0.0, 10.0)
    r2 = MockRule("R2", "weight", "range", 10.0, 20.0)
    
    print(f"\nComparing ({r1.min}, {r1.max}] and ({r2.min}, {r2.max}]")
    try:
        BusinessValidator.validate_department_overlap([r1, r2])
        print("✅ No overlap detected (Correct)")
    except ValueError as e:
        print(f"❌ FAILED: Overlap detected incorrectly: {e}")

    r3 = MockRule("R3", "weight", "range", 0.0, 11.0)
    print(f"\nComparing ({r3.min}, {r3.max}] and ({r2.min}, {r2.max}]")
    try:
        BusinessValidator.validate_department_overlap([r3, r2])
        print("❌ FAILED: No overlap detected")
    except ValueError as e:
        print(f"✅ Overlap detected correctly: {e}")

from dtos.request import DepartmentRuleDTO

def test_dto_defaults():
    print("\n--- Testing DTO Defaults (Auto-fill Max) ---")
    
    data_weight = {'name': 'Heavy', 'field': 'weight', 'type': 'range', 'min': 10.0}
    processed_weight = DepartmentRuleDTO.set_defaults(data_weight)
    expected_weight_max = 20.0
    actual_weight_max = processed_weight.get('max')
    
    print(f"Weight (Min=10.0): Max -> {actual_weight_max}")
    if actual_weight_max == expected_weight_max:
        print("✅ Correct (min + 10)")
    else:
        print(f"❌ FAILED: Expected {expected_weight_max}, got {actual_weight_max}")

    data_value = {'name': 'Insure', 'field': 'value', 'type': 'range', 'min': 100.0}
    processed_value = DepartmentRuleDTO.set_defaults(data_value)
    expected_value_max = 1000.0
    actual_value_max = processed_value.get('max')
    
    print(f"Value (Min=100.0): Max -> {actual_value_max}")
    if actual_value_max == expected_value_max:
        print("✅ Correct (min * 10)")
    else:
        print(f"❌ FAILED: Expected {expected_value_max}, got {actual_value_max}")

if __name__ == "__main__":
    test_range_matching()
    test_overlap_logic()
    test_dto_defaults()
