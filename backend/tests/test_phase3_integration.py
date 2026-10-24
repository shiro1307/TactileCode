"""
Phase 3 Integration Tests: Keyboard Navigation and Query Workflows.

Tests the end-to-end interaction between diagram extraction, graph storage,
and query execution as presented to a blind/low-vision user via API.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.graph import GraphData, Node, Edge, DiagramResponse, DiagramMetadata


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_diagram_response():
    """Create a sample diagram response with realistic data."""
    nodes = [
        Node(id="web_frontend", label="Web Frontend", group="client", confidence=0.95),
        Node(id="mobile_frontend", label="Mobile Frontend", group="client", confidence=0.92),
        Node(id="api_gateway", label="API Gateway", group="infrastructure", confidence=0.97),
        Node(id="auth_service", label="Authentication Service", group="backend", confidence=0.90),
        Node(id="user_service", label="User Service", group="backend", confidence=0.88),
        Node(id="order_service", label="Order Service", group="backend", confidence=0.85),
        Node(id="postgres_db", label="PostgreSQL", group="data", confidence=0.99),
        Node(id="redis_cache", label="Redis Cache", group="data", confidence=0.92),
        Node(id="message_queue", label="Message Queue", group="infrastructure", confidence=0.87),
    ]

    edges = [
        Edge(id="e1", source="web_frontend", target="api_gateway", direction="forward", label="HTTP/REST", confidence=0.94),
        Edge(id="e2", source="mobile_frontend", target="api_gateway", direction="forward", label="REST API", confidence=0.93),
        Edge(id="e3", source="api_gateway", target="auth_service", direction="forward", label="Authenticate", confidence=0.95),
        Edge(id="e4", source="api_gateway", target="user_service", direction="forward", label="Get User", confidence=0.91),
        Edge(id="e5", source="api_gateway", target="order_service", direction="forward", label="Place Order", confidence=0.89),
        Edge(id="e6", source="auth_service", target="postgres_db", direction="forward", label="Query", confidence=0.98),
        Edge(id="e7", source="user_service", target="postgres_db", direction="forward", label="Query", confidence=0.97),
        Edge(id="e8", source="user_service", target="redis_cache", direction="forward", label="Cache", confidence=0.90),
        Edge(id="e9", source="order_service", target="postgres_db", direction="forward", label="Store", confidence=0.96),
        Edge(id="e10", source="order_service", target="message_queue", direction="forward", label="Publish", confidence=0.88),
    ]

    graph = GraphData(nodes=nodes, edges=edges, warnings=[])

    metadata = DiagramMetadata(
        diagram_id="test-diagram-001",
        filename="sample_architecture.png",
        created_at="2024-10-24T10:00:00Z",
        node_count=len(nodes),
        edge_count=len(edges),
        has_uncertainty=False,
        status="completed",
    )

    return DiagramResponse(
        diagram_id="test-diagram-001",
        status="completed",
        graph=graph,
        metadata=metadata,
    )


class TestPhase3Queries:
    """Test Phase 3 graph query endpoints."""

    def test_get_neighbors_api(self, client, sample_diagram_response):
        """Test neighbors query returns accessible structure."""
        # Mock the storage to return our sample diagram
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        response = client.get("/api/diagrams/test-diagram-001/nodes/api_gateway/neighbors")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "found"
        assert data["node_id"] == "api_gateway"
        assert data["node_label"] == "API Gateway"
        assert data["total_connections"] == 5  # 2 incoming + 3 outgoing

        # Verify incoming connections
        assert len(data["incoming"]) == 2
        incoming_sources = {c["source_id"] for c in data["incoming"]}
        assert incoming_sources == {"web_frontend", "mobile_frontend"}

        # Verify outgoing connections
        assert len(data["outgoing"]) == 3
        outgoing_targets = {c["target_id"] for c in data["outgoing"]}
        assert outgoing_targets == {"auth_service", "user_service", "order_service"}

    def test_path_query_api(self, client, sample_diagram_response):
        """Test path finding via API."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        response = client.get("/api/diagrams/test-diagram-001/query/path?source=web_frontend&target=postgres_db")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "found"
        assert data["source_id"] == "web_frontend"
        assert data["target_id"] == "postgres_db"
        assert data["path_length"] > 0

        # Path should exist: web_frontend -> api_gateway -> (auth_service|user_service) -> postgres_db
        node_labels = [p["node_label"] for p in data["path"] if p.get("node_label")]
        assert "Web Frontend" in node_labels
        assert "PostgreSQL" in node_labels

    def test_path_query_no_path(self, client, sample_diagram_response):
        """Test path query when no path exists."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        # postgres_db can't reach web_frontend (forward edges only)
        response = client.get("/api/diagrams/test-diagram-001/query/path?source=postgres_db&target=web_frontend")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "no_path"
        assert len(data["path"]) == 0

    def test_dependents_query_api(self, client, sample_diagram_response):
        """Test dependents query (who depends on postgres_db)."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        response = client.get("/api/diagrams/test-diagram-001/query/dependents?node_id=postgres_db")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "found"
        assert data["node_label"] == "PostgreSQL"
        # auth_service, user_service, order_service depend on postgres_db
        assert data["dependent_count"] == 3
        dependent_ids = {d["node_id"] for d in data["dependents"]}
        assert dependent_ids == {"auth_service", "user_service", "order_service"}

    def test_dependencies_query_api(self, client, sample_diagram_response):
        """Test dependencies query (what does order_service depend on)."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        response = client.get("/api/diagrams/test-diagram-001/query/dependencies?node_id=order_service")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "found"
        assert data["node_label"] == "Order Service"
        # order_service depends on postgres_db and message_queue
        assert data["dependency_count"] == 2
        dep_ids = {d["node_id"] for d in data["dependencies"]}
        assert dep_ids == {"postgres_db", "message_queue"}

    def test_group_summary_query_api(self, client, sample_diagram_response):
        """Test group summary query."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        response = client.get("/api/diagrams/test-diagram-001/query/group/backend/summary")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "found"
        assert data["group_name"] == "backend"
        assert data["node_count"] == 3  # auth_service, user_service, order_service
        assert "internal_connection_count" in data
        assert "external_connection_count" in data
        assert "summary_text" in data

    def test_reachable_query_api(self, client, sample_diagram_response):
        """Test reachability query."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        response = client.get("/api/diagrams/test-diagram-001/query/reachable/web_frontend")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "found"
        assert data["node_label"] == "Web Frontend"
        # From web_frontend, can reach everything except mobile_frontend
        assert data["reachable_count"] == 7
        reachable_ids = {n["node_id"] for n in data["reachable_nodes"]}
        assert "api_gateway" in reachable_ids
        assert "postgres_db" in reachable_ids
        assert "message_queue" in reachable_ids

    def test_all_groups_query_api(self, client, sample_diagram_response):
        """Test listing all groups."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        response = client.get("/api/diagrams/test-diagram-001/query/groups")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "found"
        assert data["total_groups"] == 4  # client, infrastructure, backend, data
        group_names = {g["group_name"] for g in data["groups"]}
        assert group_names == {"client", "infrastructure", "backend", "data"}

    def test_query_nonexistent_diagram(self, client):
        """Test query on non-existent diagram returns 404."""
        response = client.get("/api/diagrams/nonexistent/query/path?source=a&target=b")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_query_nonexistent_node(self, client, sample_diagram_response):
        """Test query on non-existent node returns appropriate status."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        response = client.get("/api/diagrams/test-diagram-001/nodes/nonexistent_node/neighbors")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "not_found"
        assert len(data["incoming"]) == 0
        assert len(data["outgoing"]) == 0

    def test_query_workflow_sequence(self, client, sample_diagram_response):
        """Test realistic user workflow: explore -> find path -> jump to node -> analyze dependencies."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        # Step 1: User gets neighbors of api_gateway
        response1 = client.get("/api/diagrams/test-diagram-001/nodes/api_gateway/neighbors")
        assert response1.status_code == 200
        neighbors = response1.json()
        assert neighbors["status"] == "found"

        # Step 2: User finds path from web_frontend to postgres_db
        response2 = client.get("/api/diagrams/test-diagram-001/query/path?source=web_frontend&target=postgres_db")
        assert response2.status_code == 200
        path = response2.json()
        assert path["status"] == "found"

        # Step 3: User clicks on user_service from path and analyzes its dependencies
        response3 = client.get("/api/diagrams/test-diagram-001/query/dependencies?node_id=user_service")
        assert response3.status_code == 200
        deps = response3.json()
        assert deps["status"] == "found"
        assert deps["dependency_count"] == 2  # postgres_db and redis_cache

        # Step 4: User analyzes backend group to understand architecture
        response4 = client.get("/api/diagrams/test-diagram-001/query/group/backend/summary")
        assert response4.status_code == 200
        group_summary = response4.json()
        assert group_summary["status"] == "found"
        assert group_summary["node_count"] == 3

        # All responses are valid and queries chain together
        assert all(
            r.status_code == 200 for r in [response1, response2, response3, response4]
        )


class TestAccessibilityConstraints:
    """Verify accessibility requirements are met in query results."""

    def test_results_never_fabricate_connections(self, client, sample_diagram_response):
        """Verify that query results never invent missing relationships."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        # Query path from postgres_db to web_frontend (no path exists)
        response = client.get("/api/diagrams/test-diagram-001/query/path?source=postgres_db&target=web_frontend")
        data = response.json()

        # Must report "no_path", not invent a path
        assert data["status"] == "no_path"
        assert len(data["path"]) == 0

    def test_results_explicit_confidence_and_uncertainty(self, client, sample_diagram_response):
        """Verify results include confidence and uncertainty information."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        response = client.get("/api/diagrams/test-diagram-001/nodes/api_gateway/neighbors")
        data = response.json()

        # All connections should include confidence
        for conn in data["outgoing"]:
            assert "confidence" in conn
            assert 0.0 <= conn["confidence"] <= 1.0

        # Uncertainty may be None, but field should exist
        for conn in data["outgoing"]:
            assert "uncertainty" in conn

    def test_query_results_screen_readable_format(self, client, sample_diagram_response):
        """Verify query results are structured for screen reader consumption."""
        from app.services.storage import diagram_storage
        diagram_storage.save(sample_diagram_response)

        response = client.get("/api/diagrams/test-diagram-001/query/path?source=web_frontend&target=postgres_db")
        data = response.json()

        # Results should have:
        # - Clear status field
        # - Labels, not just IDs
        # - Relationships with descriptions
        # - Readable structure

        assert "status" in data
        for path_item in data["path"]:
            if "node_label" in path_item:
                # Human-readable label present
                assert len(path_item["node_label"]) > 0
            if "relationship" in path_item:
                # Relationship description for screen reader
                assert isinstance(path_item["relationship"], str)

    def test_error_messages_accessible(self, client):
        """Verify error messages are descriptive, not cryptic."""
        response = client.get("/api/diagrams/nonexistent/query/path?source=a&target=b")
        assert response.status_code == 404

        error = response.json()
        assert "detail" in error
        # Error message should be human-readable
        assert "nonexistent" in error["detail"] or "not found" in error["detail"].lower()
