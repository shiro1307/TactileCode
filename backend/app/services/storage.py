"""
Diagram storage service for keeping diagram responses in memory and disk cache.
"""

from typing import Dict, Optional
from app.models.graph import DiagramResponse


class DiagramStorage:
    def __init__(self):
        self._store: Dict[str, DiagramResponse] = {}

    def save(self, response: DiagramResponse) -> None:
        self._store[response.diagram_id] = response

    def get(self, diagram_id: str) -> Optional[DiagramResponse]:
        return self._store.get(diagram_id)

    def list_all(self) -> Dict[str, DiagramResponse]:
        return self._store


diagram_storage = DiagramStorage()
