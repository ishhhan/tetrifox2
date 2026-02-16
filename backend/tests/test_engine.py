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
    
    rule_match = InternalRule(name="R1", field="weight", type="range", min=5, max=15)
    assert RuleEvaluator.matches(p, rule_match) is True
    
    rule_low = InternalRule(name="R2", field="weight", type="range", min=15, max=20)
    assert RuleEvaluator.matches(p, rule_low) is False

def test_rule_evaluator_string_match():
    p = Parcel(id="1", recipient="R", street="S", city="Berlin", postal_code="Z", weight=10, value=10)
    
    rule_match = InternalRule(name="R1", field="city", type="match", match_value="berlin")
    assert RuleEvaluator.matches(p, rule_match) is True
    
    rule_fail = InternalRule(name="R2", field="city", type="match", match_value="Munich")
    assert RuleEvaluator.matches(p, rule_fail) is False

def test_priority_sorting(sample_parcel):
    dept_city = InternalRule(name="CityDept", field="city", type="match", match_value="Berlin")
    dept_weight = InternalRule(name="WeightDept", field="weight", type="range", min=10, max=20)
    
    rules = [dept_city, dept_weight] 
    priority = ["weight", "city"]    
    engine = RoutingEngineService(departments=rules, priority_order=priority)
    
    results = engine.execute_routing([sample_parcel])
    
    assert results[0].route == ["WeightDept", "CityDept"]

def test_no_match(sample_parcel):
    """Test parcel with no matching rules."""
    rule = InternalRule(name="Impossible", field="weight", type="range", min=1000, max=2000)
    engine = RoutingEngineService(departments=[rule], priority_order=["weight"])
    
    results = engine.execute_routing([sample_parcel])
    
    assert results[0].route == ["Unassigned"]  
