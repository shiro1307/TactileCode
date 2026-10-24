"""
Pipeline orchestrator: extracts diagram from image and verifies with validator.
"""

import uuid
from datetime import datetime, timezone
from typing import Tuple
from app.models.graph import GraphData, DiagramMetadata, DiagramResponse
from app.services.model_client import BaseModelClient, get_model_client
from app.services.validator import validate_and_sanitize_graph, to_networkx


class DiagramExtractionPipeline:
    def __init__(self, model_client: BaseModelClient = None):
        self.model_client = model_client or get_model_client()

    async def process_diagram(
        self,
        image_bytes: bytes,
        filename: str,
        mime_type: str = "image/png"
    ) -> DiagramResponse:
        diagram_id = str(uuid.uuid4())[:8]

        # 1. Model extraction
        raw_graph = await self.model_client.extract_graph(image_bytes, mime_type=mime_type)

        # 2. Validation & sanitization (detect dangling edges, deduplicate, flag uncertainty)
        sanitized_graph, warnings = validate_and_sanitize_graph(raw_graph)

        # 3. NetworkX verification (guarantees NetworkX loadability)
        nx_graph = to_networkx(sanitized_graph)

        has_uncertainty = any(n.uncertainty is not None for n in sanitized_graph.nodes) or any(
            e.uncertainty is not None for e in sanitized_graph.edges
        )

        metadata = DiagramMetadata(
            diagram_id=diagram_id,
            filename=filename,
            created_at=datetime.now(timezone.utc).isoformat(),
            node_count=len(sanitized_graph.nodes),
            edge_count=len(sanitized_graph.edges),
            has_uncertainty=has_uncertainty,
            status="completed"
        )

        return DiagramResponse(
            diagram_id=diagram_id,
            status="completed",
            graph=sanitized_graph,
            metadata=metadata
        )
