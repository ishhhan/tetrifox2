"""
Unit Tests for RoutingEngineService.
"""
import pytest
from services.logistics.engine import RoutingEngineService
from schemas.domain import Parcel, InternalRule
from services.logistics.rules import RuleEvaluator

@pytest.fixture
def sample_parcel():
    return Parcel(
        id="P1", recipient="R", street="S", city="Berlin", 
        postal_code="10115", weight=15.0, value=200.0
    )

def test_rule_evaluator_range():
    p = Parcel(id="1", recipient="R", street="S", city="C", postal_code="Z", weight=10, value=10)
    
    # Matches
    rule_match = InternalRule(name="R1", field="weight", type="range", min=5, max=15)
    assert RuleEvaluator.matches(p, rule_match) is True
    
    # No Match (Too low)
    rule_low = InternalRule(name="R2", field="weight", type="range", min=15, max=20)
    assert RuleEvaluator.matches(p, rule_low) is False

def test_rule_evaluator_string_match():
    p = Parcel(id="1", recipient="R", street="S", city="Berlin", postal_code="Z", weight=10, value=10)
    
    # Matches (Case insensitive)
    rule_match = InternalRule(name="R1", field="city", type="match", match_value="berlin")
    assert RuleEvaluator.matches(p, rule_match) is True
    
    # No match
    rule_fail = InternalRule(name="R2", field="city", type="match", match_value="Munich")
    assert RuleEvaluator.matches(p, rule_fail) is False

def test_priority_sorting(sample_parcel):
    """Test that departments are applied in priority order."""
    # Rules: Weight (Priority 1), City (Priority 2)
    # But we pass them in reverse order to engine
    dept_city = InternalRule(name="CityDept", field="city", type="match", match_value="Berlin")
    dept_weight = InternalRule(name="WeightDept", field="weight", type="range", min=10, max=20)
    
    rules = [dept_city, dept_weight] # City first in list
    priority = ["weight", "city"]     # But Weight is higher priority
    
    engine = RoutingEngineService(departments=rules, priority_order=priority)
    
    # Execute
    results = engine.execute_routing([sample_parcel])
    
    # Check Route: Should be [WeightDept, CityDept] because Weight is higher priority
    # Note: Engine sorts internally before matching
    assert results[0].route == ["WeightDept", "CityDept"]

def test_no_match(sample_parcel):
    """Test parcel with no matching rules."""
    rule = InternalRule(name="Impossible", field="weight", type="range", min=1000, max=2000)
    engine = RoutingEngineService(departments=[rule], priority_order=["weight"])
    
    results = engine.execute_routing([sample_parcel])
    
    assert results[0].route == ["Unassigned"]  # Or empty list, depending on implementation
