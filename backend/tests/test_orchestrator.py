
import pytest
from unittest.mock import MagicMock, patch
from services.logistics.compute import LogisticsOrchestrator
from dtos.request import LogisticsRequest, DepartmentRuleDTO
from schemas.domain import Parcel
from schemas.parsing import ParsingStats
from core.exceptions import AggregatedValidationError


@pytest.fixture
def mock_parser():
    return MagicMock()

@pytest.fixture
def mock_history():
    return MagicMock()

@pytest.fixture
def orchestrator(mock_parser, mock_history):
    return LogisticsOrchestrator(mock_parser, mock_history)

@pytest.fixture
def valid_request():
    return LogisticsRequest(
        xml_data="<dummy>data</dummy>",
        departments=[
            DepartmentRuleDTO(name="Heavy", field="weight", type="range", min=10, max=15)
        ],
        priority_order=["weight"]
    )

@pytest.fixture
def mock_parcel():
    return Parcel(
        id="P001", recipient="Alice", street="Main St", city="NY", 
        postal_code="10001", weight=50, value=100
    )


def test_process_success(orchestrator, mock_parser, mock_history, valid_request, mock_parcel):
    mock_parser.parse_with_stats.return_value = ([mock_parcel], ParsingStats())
    
    response = orchestrator.process(valid_request)
    
    assert response["status"] == "success"
    assert len(response["data"]) == 1
    assert response["data"][0].parcel_id == "P001"
    
    mock_parser.parse_with_stats.assert_called_once()
    mock_history.add_entry.assert_called_once()

def test_process_history_failure_trapped(orchestrator, mock_parser, mock_history, valid_request, mock_parcel):
    mock_parser.parse_with_stats.return_value = ([mock_parcel], ParsingStats())
    mock_history.add_entry.side_effect = Exception("Database connection failed")
    
    response = orchestrator.process(valid_request)
    
    assert response["status"] == "success"
    assert len(response["data"]) == 1
    
    mock_history.add_entry.assert_called_once()


def test_validation_department_overlap(orchestrator, valid_request):
    valid_request.departments[0].min = 200
    valid_request.departments[0].max = 100
    
    with pytest.raises(AggregatedValidationError) as exc:
        orchestrator.process(valid_request)
    
    assert any("cannot be greater than Max" in e for e in exc.value.errors)

def test_xml_parser_failure(orchestrator, mock_parser, valid_request):
    mock_parser.parse_with_stats.side_effect = Exception("Malformed XML")
    
    with pytest.raises(AggregatedValidationError) as exc:
        orchestrator.process(valid_request)
    
    assert any("XML parsing failed" in e for e in exc.value.errors)

def test_routing_engine_failure_caught(orchestrator, mock_parser, valid_request, mock_parcel):
    mock_parser.parse_with_stats.return_value = ([mock_parcel], ParsingStats())
    
    with patch("services.logistics.compute.RoutingEngineService") as MockEngine:
        MockEngine.side_effect = ValueError("Invalid Priority")
        
        with pytest.raises(AggregatedValidationError) as exc:
            orchestrator.process(valid_request)
        
        assert any("Routing configuration error" in e for e in exc.value.errors)
