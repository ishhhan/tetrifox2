"""
Dependency Injection Container.

This module provides factory functions for creating service instances.
Using FastAPI's dependency injection system, we can easily swap implementations
for testing or future requirements (SOLID - Dependency Inversion).
"""
from services.logistics.parser import XmlParserService
from services.history.store import HistoryStore
from services.logistics.compute import LogisticsOrchestrator

def get_parser_service():
    """Return the parser service class or instance."""
    # Currently stateless/static, but we inject it to allow future mocking
    return XmlParserService

def get_history_store():
    """Return the history store."""
    # Currently a singleton/static class
    return HistoryStore

def get_orchestrator():
    """
    Factory for LogisticsOrchestrator.
    
    Demonstrates Dependency Injection: The orchestrator doesn't create
    its dependencies; they are passed to it.
    """
    return LogisticsOrchestrator(
        parser_service=get_parser_service(),
        history_store=get_history_store()
    )
