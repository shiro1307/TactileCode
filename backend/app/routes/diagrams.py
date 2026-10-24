"""
API route handlers for diagram processing, graph retrieval, and queries.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Dict, Any
from app.models.graph import DiagramResponse
from app.services.extractor import DiagramExtractionPipeline
from app.services.storage import diagram_storage
from app.services.validator import get_connected_neighbors
from app.config import settings

router = APIRouter(prefix="/api/diagrams", tags=["Diagrams"])
pipeline = DiagramExtractionPipeline()


@router.post("", response_model=DiagramResponse, status_code=status.HTTP_201_CREATED)
async def upload_diagram(file: UploadFile = File(...)):
    """
    Upload an architecture diagram or flowchart image.
    Extracts structured nodes, edges, labels, directions, and confidence scores.
    """
    if file.content_type not in settings.allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{file.content_type}'. Supported: {', '.join(settings.allowed_content_types)}"
        )

    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum size of {settings.max_upload_size_bytes / (1024 * 1024)}MB."
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    response = await pipeline.process_diagram(
        image_bytes=content,
        filename=file.filename or "diagram.png",
        mime_type=file.content_type
    )

    diagram_storage.save(response)
    return response


@router.get("/sample/architecture", response_model=DiagramResponse)
async def get_sample_architecture():
    """
    Returns a pre-extracted sample architecture diagram graph.
    Useful for instant offline demos, testing, and screen reader verification.
    """
    # Create sample using pipeline with dummy bytes
    response = await pipeline.process_diagram(
        image_bytes=b"sample_architecture_image",
        filename="sample_architecture.png",
        mime_type="image/png"
    )
    diagram_storage.save(response)
    return response


@router.get("/{diagram_id}", response_model=DiagramResponse)
async def get_diagram(diagram_id: str):
    """
    Retrieve an extracted graph and metadata by diagram ID.
    """
    diagram = diagram_storage.get(diagram_id)
    if not diagram:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagram with ID '{diagram_id}' not found."
        )
    return diagram


@router.get("/{diagram_id}/nodes/{node_id}/neighbors")
async def get_node_neighbors(diagram_id: str, node_id: str) -> Dict[str, Any]:
    """
    Query connections (incoming and outgoing) for a specific node in an extracted diagram.
    """
    diagram = diagram_storage.get(diagram_id)
    if not diagram:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagram with ID '{diagram_id}' not found."
        )

    return get_connected_neighbors(diagram.graph, node_id)
