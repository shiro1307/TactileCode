"""
Pydantic data models for TactileCode graph representation.
Strictly follows the data contract defined in AGENTS.md.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class Node(BaseModel):
    id: str = Field(..., description="Stable unique identifier for the node")
    label: str = Field(..., description="Human-readable text or title of the node")
    group: Optional[str] = Field(default=None, description="Logical group or tier, e.g. frontend, backend, database")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Normalized model confidence (0.0 to 1.0)")
    uncertainty: Optional[str] = Field(default=None, description="Explicit description of uncertainty if any")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        clean = v.strip().lower().replace(" ", "_")
        if not clean:
            raise ValueError("Node id cannot be empty")
        return clean


class Edge(BaseModel):
    id: str = Field(..., description="Stable unique identifier for the edge")
    source: str = Field(..., description="Identifier of the source node")
    target: str = Field(..., description="Identifier of the target node")
    direction: Literal["forward", "backward", "bidirectional", "undirected"] = Field(
        default="forward", description="Explicit edge direction"
    )
    label: Optional[str] = Field(default=None, description="Relationship label or protocol")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Normalized model confidence (0.0 to 1.0)")
    uncertainty: Optional[str] = Field(default=None, description="Explicit description of uncertainty if any")

    @field_validator("id")
    @classmethod
    def validate_edge_id(cls, v: str) -> str:
        clean = v.strip().lower().replace(" ", "_")
        if not clean:
            raise ValueError("Edge id cannot be empty")
        return clean


class GraphData(BaseModel):
    nodes: List[Node] = Field(default_factory=list, description="List of nodes in the diagram")
    edges: List[Edge] = Field(default_factory=list, description="List of edges connecting nodes")
    warnings: List[str] = Field(default_factory=list, description="Structural or perceptual warnings")


class DiagramMetadata(BaseModel):
    diagram_id: str
    filename: str
    created_at: str
    node_count: int
    edge_count: int
    has_uncertainty: bool
    status: Literal["processing", "completed", "failed"]


class DiagramResponse(BaseModel):
    diagram_id: str
    status: str
    graph: GraphData
    metadata: DiagramMetadata
