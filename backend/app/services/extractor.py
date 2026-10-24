"""
Pipeline orchestrator: extracts diagram from image and verifies with validator.
"""

import uuid
import logging
import time
from datetime import datetime, timezone
from typing import Tuple
from app.models.graph import GraphData, DiagramMetadata, DiagramResponse
from app.services.model_client import BaseModelClient, get_model_client
from app.services.validator import validate_and_sanitize_graph, to_networkx

logger = logging.getLogger("tactilecode.extractor")


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
        start_time = time.time()

        logger.info(f"Starting extraction for {filename} ({len(image_bytes)} bytes)")

        # 1. Model extraction
        model_start = time.time()
        raw_graph = await self.model_client.extract_graph(image_bytes, mime_type=mime_type)
        model_time = time.time() - model_start
        logger.info(f"Model extraction took {model_time:.2f}s")

        # 2. Validation & sanitization (detect dangling edges, deduplicate, flag uncertainty)
        valid_start = time.time()
        sanitized_graph, warnings = validate_and_sanitize_graph(raw_graph)
        valid_time = time.time() - valid_start
        logger.info(f"Validation took {valid_time:.2f}s")

        # 3. NetworkX verification (guarantees NetworkX loadability)
        nx_start = time.time()
        nx_graph = to_networkx(sanitized_graph)
        nx_time = time.time() - nx_start
        logger.info(f"NetworkX conversion took {nx_time:.2f}s")

        has_uncertainty = any(n.uncertainty is not None for n in sanitized_graph.nodes) or any(
            e.uncertainty is not None for e in sanitized_graph.edges
        )

        total_time = time.time() - start_time
        logger.info(f"Total extraction time: {total_time:.2f}s (model={model_time:.2f}s, validation={valid_time:.2f}s, nx={nx_time:.2f}s)")

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
