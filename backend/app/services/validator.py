"""
Graph validation and NetworkX conversion service.
Enforces structural integrity, detects dangling edges, deduplicates nodes,
flags low-confidence elements with explicit uncertainty markers.
"""

from typing import Tuple, List, Set
import networkx as nx
from app.models.graph import GraphData, Node, Edge


def validate_and_sanitize_graph(raw_graph: GraphData) -> Tuple[GraphData, List[str]]:
    """
    Validates structural consistency:
    - Deduplicates node IDs while preserving labels.
    - Flags or repairs dangling edges (edges whose source or target does not exist).
    - Checks for low confidence (< 0.70) and attaches explicit uncertainty warnings.
    - Appends all structural issues to warnings.
    """
    warnings: List[str] = list(raw_graph.warnings)
    validated_nodes: List[Node] = []
    seen_node_ids: Set[str] = set()

    for node in raw_graph.nodes:
        if node.id in seen_node_ids:
            warnings.append(f"Duplicate node ID detected and deduplicated: '{node.id}'")
            continue
        seen_node_ids.add(node.id)

        # Flag low confidence if uncertainty isn't already noted
        if node.confidence < 0.70 and not node.uncertainty:
            node.uncertainty = f"Low confidence detection ({node.confidence:.2f})"
            warnings.append(f"Node '{node.label}' ({node.id}) has low confidence ({node.confidence:.2f})")

        validated_nodes.append(node)

    node_id_set = {n.id for n in validated_nodes}
    validated_edges: List[Edge] = []
    seen_edge_ids: Set[str] = set()

    for idx, edge in enumerate(raw_graph.edges):
        edge_id = edge.id or f"edge_{idx + 1}"
        if edge_id in seen_edge_ids:
            edge_id = f"{edge_id}_{idx + 1}"
        seen_edge_ids.add(edge_id)
        edge.id = edge_id

        # Validate endpoints
        source_exists = edge.source in node_id_set
        target_exists = edge.target in node_id_set

        if not source_exists or not target_exists:
            missing = []
            if not source_exists:
                missing.append(f"source '{edge.source}'")
            if not target_exists:
                missing.append(f"target '{edge.target}'")
            warning_msg = f"Dangling edge '{edge.id}' referencing nonexistent {', '.join(missing)}"
            warnings.append(warning_msg)
            # Retain edge but flag high uncertainty so user/screen reader is aware
            edge.uncertainty = f"Uncertain endpoint: missing {', '.join(missing)}"
            edge.confidence = min(edge.confidence, 0.40)

        # Flag low confidence edge
        if edge.confidence < 0.70 and not edge.uncertainty:
            edge.uncertainty = f"Low confidence relationship ({edge.confidence:.2f})"
            warnings.append(f"Edge '{edge.id}' ({edge.source} -> {edge.target}) has low confidence ({edge.confidence:.2f})")

        validated_edges.append(edge)

    sanitized_graph = GraphData(
        nodes=validated_nodes,
        edges=validated_edges,
        warnings=warnings
    )
    return sanitized_graph, warnings


def to_networkx(graph_data: GraphData) -> nx.DiGraph:
    """
    Converts GraphData into a validated NetworkX directed graph.
    Nodes and edges preserve all attributes (label, group, confidence, uncertainty).
    """
    g = nx.DiGraph()

    for node in graph_data.nodes:
        g.add_node(
            node.id,
            label=node.label,
            group=node.group or "default",
            confidence=node.confidence,
            uncertainty=node.uncertainty
        )

    for edge in graph_data.edges:
        g.add_edge(
            edge.source,
            edge.target,
            id=edge.id,
            label=edge.label or "",
            direction=edge.direction,
            confidence=edge.confidence,
            uncertainty=edge.uncertainty
        )
        if edge.direction in ("bidirectional", "undirected"):
            g.add_edge(
                edge.target,
                edge.source,
                id=f"{edge.id}_rev",
                label=edge.label or "",
                direction=edge.direction,
                confidence=edge.confidence,
                uncertainty=edge.uncertainty
            )

    return g


def get_connected_neighbors(graph: GraphData, node_id: str) -> dict:
    """
    Helper for accessible queries: returns incoming and outgoing connections for node_id.
    """
    clean_id = node_id.strip().lower().replace(" ", "_")
    incoming = []
    outgoing = []

    for edge in graph.edges:
        if edge.source == clean_id:
            outgoing.append({
                "target": edge.target,
                "label": edge.label,
                "direction": edge.direction,
                "confidence": edge.confidence,
                "uncertainty": edge.uncertainty
            })
        if edge.target == clean_id:
            incoming.append({
                "source": edge.source,
                "label": edge.label,
                "direction": edge.direction,
                "confidence": edge.confidence,
                "uncertainty": edge.uncertainty
            })

    return {
        "node_id": clean_id,
        "outgoing": outgoing,
        "incoming": incoming,
        "total_connections": len(incoming) + len(outgoing)
    }
