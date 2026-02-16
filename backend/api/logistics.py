from fastapi import APIRouter, Depends
from dtos.request import LogisticsRequest
from dtos.response import LogisticsResponse
from services.logistics.compute import LogisticsOrchestrator
from services.dependencies import get_orchestrator

router = APIRouter()

@router.post("/process-logistics", response_model=LogisticsResponse)
def process_logistics(
    payload: LogisticsRequest,
    orchestrator: LogisticsOrchestrator = Depends(get_orchestrator)
):
    """
    Process logistics data and assign routes.
    """
    return orchestrator.process(payload)
