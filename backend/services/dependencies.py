from services.logistics.parser import XmlParserService
from services.history.store import HistoryStore
from services.logistics.compute import LogisticsOrchestrator

def get_parser_service():
    return XmlParserService

def get_history_store():
    return HistoryStore

def get_orchestrator():
    return LogisticsOrchestrator(
        parser_service=get_parser_service(),
        history_store=get_history_store()
    )
