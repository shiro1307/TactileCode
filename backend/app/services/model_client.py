"""
Model client abstraction for TactileCode diagram extraction.
Supports live Gemma/Gemini vision models via google-genai SDK,
with a deterministic cached mock client for offline demos and reliable testing.
"""

from abc import ABC, abstractmethod
from typing import Optional
import json
import logging
from app.models.graph import GraphData, Node, Edge
from app.config import settings

logger = logging.getLogger("tactilecode.model_client")

EXTRACTION_SYSTEM_INSTRUCTION = """
You are TactileCode Vision Extractor, a specialized visual assistant for blind and low-vision software engineers.
Your mission is to convert visual architecture diagrams, flowcharts, and system schemas into an accurate, structured graph.

RULES:
1. Extract every distinct node/box/component. Assign a clean snake_case `id`, descriptive `label`, and logical `group` (e.g. client, api, backend, database, queue, cache, auth).
2. Extract every directed or undirected connector/arrow as an `edge`.
3. Provide explicit `direction`: 'forward' (source -> target), 'backward' (target -> source), 'bidirectional' (<->), or 'undirected' (--).
4. Extract connector labels (protocols, methods, payload descriptions like "HTTPS", "Publishes to", "SQL Query", "JSON response") if present.
5. Provide a realistic `confidence` score (0.0 to 1.0) for each element.
6. If an arrow target is blurry, occluded, or ambiguous, do NOT invent a connection. Explicitly mark `uncertainty` with a clear explanation.
7. Return ONLY valid JSON matching this schema:
{
  "nodes": [
    {"id": "string", "label": "string", "group": "string or null", "confidence": 0.95, "uncertainty": null}
  ],
  "edges": [
    {"id": "string", "source": "string", "target": "string", "direction": "forward", "label": "string or null", "confidence": 0.90, "uncertainty": null}
  ],
  "warnings": []
}
"""


class BaseModelClient(ABC):
    @abstractmethod
    async def extract_graph(self, image_bytes: bytes, mime_type: str = "image/png") -> GraphData:
        """Extract nodes, edges, labels, directions, and confidence from an image."""
        pass


class MockGemmaClient(BaseModelClient):
    """
    Offline/Cached model client providing deterministic, realistic graphs
    for automated tests and reliable offline demonstrations.
    """

    def __init__(self, sample_type: str = "architecture"):
        self.sample_type = sample_type

    async def extract_graph(self, image_bytes: bytes, mime_type: str = "image/png") -> GraphData:
        logger.info("Using Cached/Mock Gemma Client for extraction")
        # Return a realistic microservices architecture diagram graph
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
            "Notification Worker has low visual resolution (flagged for review)",
            "Kafka to Notification Worker edge has ambiguous arrow orientation",
        ]
        return GraphData(nodes=nodes, edges=edges, warnings=warnings)


class GeminiGemmaClient(BaseModelClient):
    """
    Live Vision model client using Google GenAI SDK (compatible with Gemma 4 & Gemini models).
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        from google import genai
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)
        self.mock_fallback = MockGemmaClient()

    async def extract_graph(self, image_bytes: bytes, mime_type: str = "image/png") -> GraphData:
        from google.genai import types

        prompt = (
            "Analyze this diagram image. Extract every component node and connecting edge "
            "into structured JSON with confidence and uncertainty notes as instructed."
        )

        try:
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=EXTRACTION_SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            text_output = response.text or "{}"
            parsed_json = json.loads(text_output)

            # Construct Pydantic model
            raw_nodes = [Node(**n) for n in parsed_json.get("nodes", [])]
            raw_edges = [Edge(**e) for e in parsed_json.get("edges", [])]
            raw_warnings = parsed_json.get("warnings", [])

            return GraphData(nodes=raw_nodes, edges=raw_edges, warnings=raw_warnings)

        except Exception as err:
            logger.error(f"Error during live vision model extraction: {err}")
            if settings.fallback_to_mock:
                logger.warning("Falling back to cached/mock model extraction for resilience")
                mock_graph = await self.mock_fallback.extract_graph(image_bytes, mime_type)
                mock_graph.warnings.append(f"Live model failed ({str(err)}). Fallback demo data served.")
                return mock_graph
            raise


def get_model_client() -> BaseModelClient:
    """
    Factory function returning model client in priority order:
    1. Gemma 4 API (official google-genai SDK) - RECOMMENDED
    2. Ollama (if enabled and available locally)
    3. Gemini API (legacy, if key configured)
    4. Mock client (fallback for demo)
    """
    # Try Gemma 4 API first (primary)
    if settings.gemma_api_key and settings.gemma_api_key.strip():
        logger.info("Initializing GemmaClient (Gemma 4 via Google AI Studio)")
        from app.services.gemma_client import GemmaClient
        return GemmaClient(api_key=settings.gemma_api_key.strip())
    
    # Try Ollama (if enabled)
    if settings.ollama_enabled:
        logger.info(f"Initializing OllamaClient (model: {settings.ollama_model})")
        from app.services.ollama_client import OllamaClient
        return OllamaClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout=settings.ollama_timeout_seconds,
        )
    
    # Try Gemini API (legacy fallback)
    if settings.gemini_api_key and settings.gemini_api_key.strip():
        logger.info(f"Initialized GeminiGemmaClient with model '{settings.model_name}'")
        return GeminiGemmaClient(api_key=settings.gemini_api_key.strip(), model_name=settings.model_name)
    
    # Fall back to mock
    logger.info("No API keys configured; using MockGemmaClient")
    return MockGemmaClient()
