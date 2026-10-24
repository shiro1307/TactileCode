import pytest
from pydantic import ValidationError
from app.models.graph import Node, Edge, GraphData


def test_node_creation_and_id_sanitization():
    node = Node(id="API Gateway", label="API Gateway", group="infrastructure", confidence=0.95)
    assert node.id == "api_gateway"
    assert node.label == "API Gateway"
    assert node.confidence == 0.95
    assert node.uncertainty is None


def test_node_confidence_bounds():
    with pytest.raises(ValidationError):
        Node(id="n1", label="Test", confidence=1.5)

    with pytest.raises(ValidationError):
        Node(id="n2", label="Test", confidence=-0.1)


def test_edge_creation_and_directions():
    edge = Edge(
        id="Edge 1",
        source="client",
        target="server",
        direction="forward",
        label="HTTP POST",
        confidence=0.88
    )
    assert edge.id == "edge_1"
    assert edge.source == "client"
    assert edge.target == "server"
    assert edge.direction == "forward"
    assert edge.label == "HTTP POST"


def test_graph_data_empty_default():
    graph = GraphData()
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0
    assert len(graph.warnings) == 0
