"""
Tests for the GraphQueryEngine query interface.
Validates path finding, dependency analysis, group operations, and reachability.
"""

import pytest
from app.models.graph import GraphData, Node, Edge
from app.services.query_engine import GraphQueryEngine


@pytest.fixture
def sample_graph_data() -> GraphData:
    """Create a sample graph for testing queries."""
    nodes = [
        Node(id="frontend", label="Frontend App", group="client", confidence=0.95),
        Node(id="api_gateway", label="API Gateway", group="infrastructure", confidence=0.92),
        Node(id="auth_service", label="Auth Service", group="backend", confidence=0.88),
        Node(id="user_db", label="User Database", group="database", confidence=0.96),
        Node(id="api_server", label="API Server", group="backend", confidence=0.91),
        Node(id="cache", label="Redis Cache", group="infrastructure", confidence=0.85),
    ]

    edges = [
        Edge(
            id="edge_1",
            source="frontend",
            target="api_gateway",
            direction="forward",
            label="HTTP request",
            confidence=0.93,
        ),
        Edge(
            id="edge_2",
            source="api_gateway",
            target="auth_service",
            direction="forward",
            label="Authentication",
            confidence=0.90,
        ),
        Edge(
            id="edge_3",
            source="api_gateway",
            target="api_server",
            direction="forward",
            label="Route request",
            confidence=0.92,
        ),
        Edge(
            id="edge_4",
            source="auth_service",
            target="user_db",
            direction="forward",
            label="Query user",
            confidence=0.91,
        ),
        Edge(
            id="edge_5",
            source="api_server",
            target="cache",
            direction="forward",
            label="Cache hit",
            confidence=0.87,
        ),
        Edge(
            id="edge_6",
            source="api_server",
            target="user_db",
            direction="forward",
            label="Query data",
            confidence=0.89,
        ),
    ]

    return GraphData(nodes=nodes, edges=edges, warnings=[])


def test_get_neighbors_found(sample_graph_data: GraphData):
    """Test getting neighbors for a node that exists."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.get_neighbors("api_gateway")

    assert result["status"] == "found"
    assert result["node_id"] == "api_gateway"
    assert result["node_label"] == "API Gateway"
    assert len(result["incoming"]) == 1  # frontend -> api_gateway
    assert len(result["outgoing"]) == 2  # api_gateway -> auth_service, api_server


def test_get_neighbors_not_found(sample_graph_data: GraphData):
    """Test getting neighbors for a node that doesn't exist."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.get_neighbors("nonexistent_node")

    assert result["status"] == "not_found"
    assert result["node_id"] == "nonexistent_node"
    assert len(result["incoming"]) == 0
    assert len(result["outgoing"]) == 0


def test_find_path_exists(sample_graph_data: GraphData):
    """Test finding a path between two connected nodes."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.find_path("frontend", "user_db")

    assert result["status"] == "found"
    assert result["source_id"] == "frontend"
    assert result["target_id"] == "user_db"
    assert result["path_length"] > 0
    # Path should be: frontend -> api_gateway -> auth_service -> user_db (3 edges)
    node_steps = [p for p in result["path"] if p.get("node_label")]
    assert len(node_steps) == 4  # 4 nodes in the path


def test_find_path_no_path(sample_graph_data: GraphData):
    """Test finding a path when no path exists (DAG with only forward edges)."""
    # In this sample graph, all edges go forward, so user_db can't reach frontend
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.find_path("user_db", "frontend")

    assert result["status"] == "no_path"
    assert result["source_id"] == "user_db"
    assert result["target_id"] == "frontend"
    assert len(result["path"]) == 0


def test_find_path_source_not_found(sample_graph_data: GraphData):
    """Test finding a path with a nonexistent source node."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.find_path("nonexistent", "user_db")

    assert result["status"] == "source_not_found"
    assert len(result["path"]) == 0


def test_find_path_target_not_found(sample_graph_data: GraphData):
    """Test finding a path with a nonexistent target node."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.find_path("frontend", "nonexistent")

    assert result["status"] == "target_not_found"
    assert len(result["path"]) == 0


def test_get_dependents(sample_graph_data: GraphData):
    """Test finding all nodes that depend on a given node."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.get_dependents("user_db")

    assert result["status"] == "found"
    assert result["node_id"] == "user_db"
    # user_db is a target of auth_service and api_server, so they depend on it
    assert result["dependent_count"] == 2
    dependent_ids = {d["node_id"] for d in result["dependents"]}
    assert "auth_service" in dependent_ids
    assert "api_server" in dependent_ids


def test_get_dependencies(sample_graph_data: GraphData):
    """Test finding all nodes that a given node depends on."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.get_dependencies("api_server")

    assert result["status"] == "found"
    assert result["node_id"] == "api_server"
    # api_server depends on cache and user_db
    assert result["dependency_count"] == 2
    dep_ids = {d["node_id"] for d in result["dependencies"]}
    assert "cache" in dep_ids
    assert "user_db" in dep_ids


def test_find_nodes_by_group(sample_graph_data: GraphData):
    """Test finding all nodes in a specific group."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.find_nodes_by_group("backend")

    assert result["status"] == "found"
    assert result["group_name"] == "backend"
    assert result["node_count"] == 2  # auth_service and api_server
    node_ids = {n["node_id"] for n in result["nodes"]}
    assert "auth_service" in node_ids
    assert "api_server" in node_ids


def test_find_nodes_by_group_not_found(sample_graph_data: GraphData):
    """Test finding nodes in a group that doesn't exist."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.find_nodes_by_group("nonexistent_group")

    assert result["status"] == "found"
    assert result["node_count"] == 0
    assert len(result["nodes"]) == 0


def test_summarize_group(sample_graph_data: GraphData):
    """Test summarizing a group including internal/external connections."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.summarize_group("backend")

    assert result["status"] == "found"
    assert result["group_name"] == "backend"
    assert result["node_count"] == 2
    assert "auth_service" in {n["node_id"] for n in result["nodes"]}
    assert "summary_text" in result
    assert "internal_connection_count" in result
    assert "external_connection_count" in result


def test_summarize_group_not_found(sample_graph_data: GraphData):
    """Test summarizing a group that doesn't exist."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.summarize_group("nonexistent_group")

    assert result["status"] == "not_found"


def test_get_all_groups(sample_graph_data: GraphData):
    """Test getting a summary of all groups in the graph."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.get_all_groups()

    assert result["status"] == "found"
    assert result["total_groups"] == 4  # client, infrastructure, backend, database
    group_names = {g["group_name"] for g in result["groups"]}
    assert "client" in group_names
    assert "infrastructure" in group_names
    assert "backend" in group_names
    assert "database" in group_names


def test_reachability_analysis(sample_graph_data: GraphData):
    """Test analyzing reachability from a given node."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.reachability_analysis("frontend")

    assert result["status"] == "found"
    assert result["node_id"] == "frontend"
    # From frontend, we can reach: api_gateway, auth_service, user_db, api_server, cache
    assert result["reachable_count"] == 5
    reachable_ids = {n["node_id"] for n in result["reachable_nodes"]}
    assert "api_gateway" in reachable_ids
    assert "user_db" in reachable_ids
    assert "cache" in reachable_ids


def test_reachability_analysis_no_outgoing_edges(sample_graph_data: GraphData):
    """Test reachability from a leaf node (no outgoing edges)."""
    engine = GraphQueryEngine(sample_graph_data)
    result = engine.reachability_analysis("user_db")

    assert result["status"] == "found"
    assert result["node_id"] == "user_db"
    assert result["reachable_count"] == 0
    assert len(result["reachable_nodes"]) == 0


def test_query_engine_with_uncertainty():
    """Test query engine preserves uncertainty information."""
    nodes = [
        Node(id="node1", label="Node 1", confidence=0.95),
        Node(id="node2", label="Node 2", confidence=0.60, uncertainty="Low confidence"),
    ]
    edges = [
        Edge(
            id="edge1",
            source="node1",
            target="node2",
            confidence=0.85,
            uncertainty="Uncertain connection type",
        )
    ]

    graph_data = GraphData(nodes=nodes, edges=edges)
    engine = GraphQueryEngine(graph_data)
    result = engine.get_neighbors("node1")

    assert len(result["outgoing"]) == 1
    outgoing = result["outgoing"][0]
    assert outgoing["uncertainty"] == "Uncertain connection type"


def test_query_engine_empty_graph():
    """Test query engine with an empty graph."""
    graph_data = GraphData(nodes=[], edges=[])
    engine = GraphQueryEngine(graph_data)

    result = engine.get_neighbors("any_node")
    assert result["status"] == "not_found"

    result = engine.get_all_groups()
    assert result["total_groups"] == 0
    assert len(result["groups"]) == 0
