import networkx as nx
from app.models.graph import Node, Edge, GraphData
from app.services.validator import validate_and_sanitize_graph, to_networkx, get_connected_neighbors


def test_duplicate_node_id_handling():
    raw_graph = GraphData(
        nodes=[
            Node(id="api_gw", label="API Gateway 1"),
            Node(id="api_gw", label="API Gateway 2"),
            Node(id="db", label="Database"),
        ],
        edges=[]
    )
    sanitized, warnings = validate_and_sanitize_graph(raw_graph)
    assert len(sanitized.nodes) == 2
    assert any("Duplicate node ID detected" in w for w in warnings)


def test_dangling_edge_flagged_with_uncertainty():
    raw_graph = GraphData(
        nodes=[
            Node(id="service_a", label="Service A"),
        ],
        edges=[
            Edge(id="e1", source="service_a", target="nonexistent_db", direction="forward", confidence=0.9)
        ]
    )
    sanitized, warnings = validate_and_sanitize_graph(raw_graph)
    assert len(sanitized.edges) == 1
    edge = sanitized.edges[0]
    assert edge.uncertainty is not None
    assert "missing target 'nonexistent_db'" in edge.uncertainty
    assert edge.confidence <= 0.40
    assert any("Dangling edge" in w for w in warnings)


def test_low_confidence_node_flagged():
    raw_graph = GraphData(
        nodes=[
            Node(id="fuzzy_icon", label="Fuzzy Component", confidence=0.55),
        ],
        edges=[]
    )
    sanitized, warnings = validate_and_sanitize_graph(raw_graph)
    assert sanitized.nodes[0].uncertainty is not None
    assert "Low confidence" in sanitized.nodes[0].uncertainty
    assert any("has low confidence" in w for w in warnings)


def test_to_networkx_conversion():
    graph_data = GraphData(
        nodes=[
            Node(id="frontend", label="React App", group="ui", confidence=0.95),
            Node(id="backend", label="FastAPI", group="api", confidence=0.92),
        ],
        edges=[
            Edge(id="e1", source="frontend", target="backend", direction="forward", label="REST", confidence=0.90)
        ]
    )
    nx_graph = to_networkx(graph_data)
    assert isinstance(nx_graph, nx.DiGraph)
    assert nx_graph.number_of_nodes() == 2
    assert nx_graph.number_of_edges() == 1
    assert nx_graph.has_edge("frontend", "backend")
    assert nx_graph.nodes["frontend"]["label"] == "React App"
    assert nx_graph.edges["frontend", "backend"]["label"] == "REST"


def test_get_connected_neighbors():
    graph_data = GraphData(
        nodes=[
            Node(id="a", label="A"),
            Node(id="b", label="B"),
            Node(id="c", label="C"),
        ],
        edges=[
            Edge(id="e1", source="a", target="b", direction="forward"),
            Edge(id="e2", source="c", target="a", direction="forward"),
        ]
    )
    neighbors = get_connected_neighbors(graph_data, "a")
    assert neighbors["node_id"] == "a"
    assert len(neighbors["outgoing"]) == 1
    assert neighbors["outgoing"][0]["target"] == "b"
    assert len(neighbors["incoming"]) == 1
    assert neighbors["incoming"][0]["source"] == "c"
    assert neighbors["total_connections"] == 2
