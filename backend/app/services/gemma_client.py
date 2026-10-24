"""
Gemma 4 API Client using official google-genai SDK.
Supports gemma-4-26b-a4b-it and other Gemma models via Google AI Studio.

Clean, official integration. No dependencies on Ollama.
"""

import json
import base64
import logging
import asyncio
from typing import Optional
from abc import ABC, abstractmethod
from app.models.graph import GraphData, Node, Edge
from app.config import settings

logger = logging.getLogger("tactilecode.gemma_client")

DIAGRAM_EXTRACTION_SYSTEM = """You are TactileCode Vision Extractor for architecture diagrams.

Extract every component and relationship from this diagram.

OUTPUT EXACTLY THIS JSON:
{
  "nodes": [
    {"id": "node_id", "label": "Display Name", "group": "category", "confidence": 0.95, "uncertainty": null}
  ],
  "edges": [
    {"id": "edge_1", "source": "id_a", "target": "id_b", "direction": "forward", "label": "relationship", "confidence": 0.90, "uncertainty": null}
  ],
  "warnings": []
}

RULES:
- Node IDs: snake_case, unique
- Groups: frontend, backend, database, api, cache, queue, etc.
- Direction: "forward", "backward", "bidirectional", "undirected"
- Confidence: 0.0 to 1.0
- If unclear, mark with uncertainty field
- RETURN ONLY VALID JSON
"""


class GemmaClient:
    """Gemma 4 vision model via official google-genai SDK."""

    def __init__(self, api_key: str, model: str = "gemma-4-26b-a4b-it", timeout_seconds: int = 60):
        from google import genai
        from google.genai import types

        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.types = types
        
        # Initialize client
        self.client = genai.Client(api_key=api_key)

        logger.info(f"Initialized GemmaClient with model: {model}, timeout: {timeout_seconds}s")

    async def extract_graph(self, image_bytes: bytes, mime_type: str = "image/png") -> GraphData:
        """Extract nodes and edges from diagram image using Gemma 4 with timeout."""
        try:
            from google.genai import types

            logger.info(f"Extracting graph from image ({len(image_bytes)} bytes), timeout={self.timeout_seconds}s")

            # Create image part
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

            # Run with timeout
            result = await asyncio.wait_for(
                self._call_gemma(image_part),
                timeout=self.timeout_seconds
            )
            return result

        except asyncio.TimeoutError:
            logger.warning(f"Gemma extraction timed out after {self.timeout_seconds}s, falling back to mock")
            return self._get_mock_fallback()
        except Exception as e:
            logger.error(f"Gemma extraction failed: {e}", exc_info=True)
            raise Exception(f"Gemma extraction failed: {str(e)}")

    async def _call_gemma(self, image_part) -> GraphData:
        """Call Gemma API synchronously wrapped in executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._call_gemma_sync, image_part)

    def _call_gemma_sync(self, image_part) -> GraphData:
        """Synchronous Gemma API call."""
        from google.genai import types

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                image_part,
                "Extract all nodes (boxes/components) and edges (arrows/connections) from this architecture diagram. "
                "Return ONLY valid JSON.",
            ],
            config=types.GenerateContentConfig(
                system_instruction=DIAGRAM_EXTRACTION_SYSTEM,
                temperature=0.1,  # Deterministic
                response_mime_type="application/json",
            ),
        )

        # Parse response
        response_text = response.text or "{}"
        logger.debug(f"Gemma response: {response_text[:200]}...")

        # Extract JSON
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > 0:
                parsed = json.loads(response_text[json_start:json_end])
            else:
                logger.error(f"Could not parse JSON from: {response_text[:500]}")
                raise ValueError("Invalid JSON in response")

        # Build graph
        nodes = []
        for node_data in parsed.get("nodes", []):
            node = Node(
                id=str(node_data.get("id", "")).lower().replace(" ", "_"),
                label=str(node_data.get("label", "Unknown")),
                group=node_data.get("group"),
                confidence=float(node_data.get("confidence", 0.85)),
                uncertainty=node_data.get("uncertainty"),
            )
            nodes.append(node)

        edges = []
        for edge_data in parsed.get("edges", []):
            edge = Edge(
                id=str(edge_data.get("id", f"edge_{len(edges)+1}")),
                source=str(edge_data.get("source", "")).lower().replace(" ", "_"),
                target=str(edge_data.get("target", "")).lower().replace(" ", "_"),
                direction=str(edge_data.get("direction", "forward")),
                label=edge_data.get("label"),
                confidence=float(edge_data.get("confidence", 0.85)),
                uncertainty=edge_data.get("uncertainty"),
            )
            edges.append(edge)

        warnings = parsed.get("warnings", [])
        logger.info(f"Extracted {len(nodes)} nodes, {len(edges)} edges")

        return GraphData(nodes=nodes, edges=edges, warnings=warnings)

    def _get_mock_fallback(self) -> GraphData:
        """Return mock data when timeout occurs."""
        nodes = [
            Node(id="client_browser", label="Web Browser Client", group="frontend", confidence=0.98, uncertainty=None),
            Node(id="api_gateway", label="Cloud API Gateway", group="infrastructure", confidence=0.95, uncertainty=None),
            Node(id="auth_service", label="Authentication Service", group="backend", confidence=0.92, uncertainty=None),
            Node(id="order_service", label="Order Processing Service", group="backend", confidence=0.94, uncertainty=None),
            Node(id="inventory_db", label="Inventory PostgreSQL DB", group="database", confidence=0.91, uncertainty=None),
            Node(id="kafka_bus", label="Kafka Event Bus", group="messaging", confidence=0.88, uncertainty=None),
            Node(id="notification_worker", label="Notification Worker", group="worker", confidence=0.76, uncertainty="Blurry icon label, inferred from worker queue"),
        ]
        edges = [
            Edge(id="e1", source="client_browser", target="api_gateway", direction="forward", label="HTTPS / REST", confidence=0.97, uncertainty=None),
            Edge(id="e2", source="api_gateway", target="auth_service", direction="forward", label="Verify JWT Token", confidence=0.94, uncertainty=None),
            Edge(id="e3", source="api_gateway", target="order_service", direction="forward", label="Forward Order Request", confidence=0.95, uncertainty=None),
            Edge(id="e4", source="order_service", target="inventory_db", direction="bidirectional", label="Read/Write Stock", confidence=0.92, uncertainty=None),
            Edge(id="e5", source="order_service", target="kafka_bus", direction="forward", label="Publish 'OrderCreated'", confidence=0.90, uncertainty=None),
            Edge(id="e6", source="kafka_bus", target="notification_worker", direction="forward", label="Consume Event", confidence=0.74, uncertainty="Unclear arrow head angle, assumed forward stream"),
        ]
        warnings = [
            "API extraction timed out (>60s). Showing cached demo data. Try uploading a simpler diagram for faster real extraction.",
        ]
        return GraphData(nodes=nodes, edges=edges, warnings=warnings)

    async def health_check(self) -> bool:
        """Verify API key is valid."""
        try:
            from google.genai import types

            # Simple API call to verify connection
            response = self.client.models.generate_content(
                model=self.model,
                contents="Say OK",
                config=types.GenerateContentConfig(temperature=0.1),
            )
            return bool(response.text)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

