"""
Ollama local vision model client for TactileCode.
Runs Gemma, LLaVA, or other vision models locally without API keys.

Supports:
- LLaVA (recommended for diagrams)
- Gemma 2 Vision
- Other vision models

No internet required. Works offline.
"""

import json
import base64
import logging
from typing import Optional
import aiohttp
from app.models.graph import GraphData, Node, Edge
from app.config import settings

logger = logging.getLogger("tactilecode.ollama_client")

DIAGRAM_EXTRACTION_PROMPT = """You are TactileCode Vision Extractor, a specialized visual assistant for analyzing software architecture diagrams.

Your task is to extract every component and relationship from this architecture or flowchart diagram.

EXTRACT EXACTLY THESE:
1. Every distinct box, component, or node
2. Every arrow or connector between nodes
3. Labels on boxes and arrows
4. Direction of arrows (forward, backward, bidirectional)

OUTPUT MUST BE VALID JSON:
{
  "nodes": [
    {"id": "node_id_lowercase", "label": "Display Name", "group": "category_like_database_or_frontend", "confidence": 0.95, "uncertainty": null},
    ...
  ],
  "edges": [
    {"id": "edge_1", "source": "node_a", "target": "node_b", "direction": "forward", "label": "interaction_label", "confidence": 0.90, "uncertainty": null},
    ...
  ],
  "warnings": ["list of any ambiguous elements"]
}

RULES:
- Node IDs must be snake_case
- Group each node (frontend, backend, database, api, cache, queue, etc.)
- Every edge needs source and target node ID
- Direction: "forward" (→), "backward" (←), "bidirectional" (↔), "undirected" (---)
- Confidence 0.0 to 1.0 (how sure you are)
- If unclear, use uncertainty field with explanation
- Return ONLY valid JSON, no other text
"""


class OllamaClient:
    """Local vision model client using Ollama."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llava:7b-v1.6",
        timeout: int = 300,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def extract_graph(self, image_bytes: bytes, mime_type: str = "image/png") -> GraphData:
        """
        Extract diagram structure from image using local Ollama model.

        Args:
            image_bytes: Raw image data
            mime_type: Image MIME type (image/png, image/jpeg)

        Returns:
            GraphData with extracted nodes, edges, confidence, uncertainty
        """
        # Convert image to base64
        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        # Call Ollama vision model
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": DIAGRAM_EXTRACTION_PROMPT,
                        "images": [b64_image],
                        "stream": False,
                        "temperature": 0.1,  # Deterministic
                    },
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"Ollama API error: {resp.status} - {error_text}")

                    response_data = await resp.json()
                    model_output = response_data.get("response", "")

        except aiohttp.ClientConnectorError:
            raise Exception(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Is Ollama running? Start with: ollama serve"
            )
        except aiohttp.ClientTimeout:
            raise Exception(
                f"Ollama request timed out after {self.timeout}s. "
                f"Model is slow or stuck. Try smaller model."
            )
        except Exception as e:
            raise Exception(f"Ollama extraction failed: {str(e)}")

        # Parse JSON from model output
        try:
            # Model might include explanation text before JSON
            # Extract JSON block
            json_start = model_output.find("{")
            json_end = model_output.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                logger.error(f"No JSON found in response: {model_output[:200]}")
                raise ValueError("Model did not return valid JSON")

            json_str = model_output[json_start:json_end]
            parsed = json.loads(json_str)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Model output: {model_output[:500]}")
            raise Exception(f"Could not parse model JSON response: {str(e)}")

        # Build Pydantic models
        try:
            nodes = []
            for node_data in parsed.get("nodes", []):
                node = Node(
                    id=node_data.get("id", "").lower().replace(" ", "_"),
                    label=node_data.get("label", "Unknown"),
                    group=node_data.get("group"),
                    confidence=float(node_data.get("confidence", 0.8)),
                    uncertainty=node_data.get("uncertainty"),
                )
                nodes.append(node)

            edges = []
            for edge_data in parsed.get("edges", []):
                edge = Edge(
                    id=edge_data.get("id", f"edge_{len(edges)+1}"),
                    source=edge_data.get("source", "").lower().replace(" ", "_"),
                    target=edge_data.get("target", "").lower().replace(" ", "_"),
                    direction=edge_data.get("direction", "forward"),
                    label=edge_data.get("label"),
                    confidence=float(edge_data.get("confidence", 0.8)),
                    uncertainty=edge_data.get("uncertainty"),
                )
                edges.append(edge)

            warnings = parsed.get("warnings", [])

            return GraphData(nodes=nodes, edges=edges, warnings=warnings)

        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error constructing graph: {e}")
            raise Exception(f"Could not construct graph from model response: {str(e)}")

    async def health_check(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status != 200:
                        return False

                    data = await resp.json()
                    models = data.get("models", [])
                    model_names = [m.get("name", "") for m in models]

                    # Check if our model is available
                    model_available = any(self.model in name for name in model_names)

                    if not model_available:
                        logger.warning(
                            f"Model '{self.model}' not found in Ollama. "
                            f"Available: {model_names}"
                        )

                    return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
