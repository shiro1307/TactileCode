"""
Labeled benchmark dataset for TactileCode.
Small curated diagrams with known-good extraction results.
Measures accuracy before/after verification.
"""

from app.models.graph import GraphData, Node, Edge, DiagramResponse, DiagramMetadata
from datetime import datetime


# Diagram 1: Simple 3-tier architecture
DIAGRAM_1_SIMPLE = GraphData(
    nodes=[
        Node(id="frontend", label="Web Frontend", group="presentation", confidence=0.95),
        Node(id="api", label="REST API", group="application", confidence=0.93),
        Node(id="database", label="PostgreSQL", group="data", confidence=0.98),
    ],
    edges=[
        Edge(id="e1", source="frontend", target="api", direction="forward", label="HTTP request", confidence=0.94),
        Edge(id="e2", source="api", target="database", direction="forward", label="SQL query", confidence=0.96),
    ],
    warnings=[],
)

# Diagram 2: Microservices with shared dependencies
DIAGRAM_2_MICROSERVICES = GraphData(
    nodes=[
        Node(id="client", label="Client App", group="frontend", confidence=0.94),
        Node(id="gateway", label="API Gateway", group="gateway", confidence=0.91),
        Node(id="auth", label="Auth Service", group="services", confidence=0.88),
        Node(id="user", label="User Service", group="services", confidence=0.90),
        Node(id="order", label="Order Service", group="services", confidence=0.85),
        Node(id="cache", label="Redis", group="data", confidence=0.96),
        Node(id="db", label="PostgreSQL", group="data", confidence=0.97),
        Node(id="queue", label="Message Queue", group="infrastructure", confidence=0.82),
    ],
    edges=[
        Edge(id="e1", source="client", target="gateway", direction="forward", label="REST", confidence=0.93),
        Edge(id="e2", source="gateway", target="auth", direction="forward", label="Validate", confidence=0.91),
        Edge(id="e3", source="gateway", target="user", direction="forward", label="Get user", confidence=0.89),
        Edge(id="e4", source="gateway", target="order", direction="forward", label="Create order", confidence=0.87),
        Edge(id="e5", source="auth", target="db", direction="forward", label="Query", confidence=0.95),
        Edge(id="e6", source="user", target="db", direction="forward", label="Query", confidence=0.94),
        Edge(id="e7", source="user", target="cache", direction="forward", label="Cache", confidence=0.88),
        Edge(id="e8", source="order", target="db", direction="forward", label="Insert", confidence=0.93),
        Edge(id="e9", source="order", target="queue", direction="forward", label="Publish", confidence=0.84),
    ],
    warnings=[],
)

# Diagram 3: With low-confidence elements (uncertainty)
DIAGRAM_3_WITH_UNCERTAINTY = GraphData(
    nodes=[
        Node(id="front", label="Frontend", group="client", confidence=0.92),
        Node(id="middle", label="Unknown Service", group="unknown", confidence=0.55, 
             uncertainty="Low confidence detection, label unclear"),
        Node(id="back", label="Backend", group="server", confidence=0.91),
        Node(id="store", label="Data Store", group="data", confidence=0.94),
    ],
    edges=[
        Edge(id="e1", source="front", target="middle", direction="forward", label="???", 
             confidence=0.62, uncertainty="Unclear relationship label"),
        Edge(id="e2", source="middle", target="back", direction="forward", label="API", confidence=0.88),
        Edge(id="e3", source="back", target="store", direction="forward", label="Query", confidence=0.95),
    ],
    warnings=["Low confidence node detected: 'Unknown Service'", "Uncertain edge: front -> middle"],
)

# Diagram 4: Complex with disconnected components
DIAGRAM_4_DISCONNECTED = GraphData(
    nodes=[
        # Main flow
        Node(id="web", label="Web App", group="frontend", confidence=0.94),
        Node(id="api", label="API Server", group="backend", confidence=0.92),
        Node(id="db", label="Database", group="data", confidence=0.97),
        # Disconnected monitoring
        Node(id="monitor", label="Monitoring", group="infra", confidence=0.85),
        Node(id="logs", label="Log Storage", group="infra", confidence=0.83),
    ],
    edges=[
        # Main flow edges
        Edge(id="e1", source="web", target="api", direction="forward", label="REST", confidence=0.93),
        Edge(id="e2", source="api", target="db", direction="forward", label="Query", confidence=0.96),
        # Disconnected edges (monitoring has no incoming)
        Edge(id="e3", source="monitor", target="logs", direction="forward", label="Store", confidence=0.84),
    ],
    warnings=["Disconnected component: Monitoring subsystem has no incoming edges"],
)

# Diagram 5: With bidirectional relationships
DIAGRAM_5_BIDIRECTIONAL = GraphData(
    nodes=[
        Node(id="svc_a", label="Service A", group="services", confidence=0.91),
        Node(id="svc_b", label="Service B", group="services", confidence=0.90),
        Node(id="svc_c", label="Service C", group="services", confidence=0.89),
        Node(id="cache", label="Shared Cache", group="data", confidence=0.94),
    ],
    edges=[
        Edge(id="e1", source="svc_a", target="svc_b", direction="forward", label="Request", confidence=0.88),
        Edge(id="e2", source="svc_b", target="svc_a", direction="forward", label="Response", confidence=0.87),
        Edge(id="e3", source="svc_a", target="cache", direction="bidirectional", label="Read/Write", confidence=0.92),
        Edge(id="e4", source="svc_b", target="cache", direction="bidirectional", label="Read/Write", confidence=0.91),
        Edge(id="e5", source="svc_c", target="cache", direction="undirected", label="Access", confidence=0.88),
    ],
    warnings=[],
)


class BenchmarkDataset:
    """Collection of labeled diagrams for evaluation."""

    diagrams = [
        {
            "id": "simple-3tier",
            "name": "Simple 3-Tier Architecture",
            "description": "Basic web app -> API -> database",
            "data": DIAGRAM_1_SIMPLE,
            "expected_nodes": 3,
            "expected_edges": 2,
            "expected_paths": [("frontend", "database")],
            "expected_groups": ["presentation", "application", "data"],
            "difficulty": "easy",
        },
        {
            "id": "microservices",
            "name": "Microservices with Shared Dependencies",
            "description": "Gateway routing to multiple services, shared cache and database",
            "data": DIAGRAM_2_MICROSERVICES,
            "expected_nodes": 8,
            "expected_edges": 9,
            "expected_paths": [("client", "db"), ("client", "cache"), ("client", "queue")],
            "expected_groups": ["frontend", "gateway", "services", "data", "infrastructure"],
            "difficulty": "medium",
        },
        {
            "id": "with-uncertainty",
            "name": "Diagram with Low-Confidence Elements",
            "description": "Contains uncertain nodes and edges for testing validation",
            "data": DIAGRAM_3_WITH_UNCERTAINTY,
            "expected_nodes": 4,
            "expected_edges": 3,
            "expected_uncertain_nodes": 1,
            "expected_uncertain_edges": 1,
            "expected_warnings": 2,
            "difficulty": "medium",
        },
        {
            "id": "disconnected",
            "name": "Disconnected Components",
            "description": "Main flow + separate monitoring subsystem",
            "data": DIAGRAM_4_DISCONNECTED,
            "expected_nodes": 5,
            "expected_edges": 3,
            "expected_components": 2,
            "expected_warnings": 1,
            "difficulty": "medium",
        },
        {
            "id": "bidirectional",
            "name": "Bidirectional and Undirected Edges",
            "description": "Tests direction handling and shared resource access",
            "data": DIAGRAM_5_BIDIRECTIONAL,
            "expected_nodes": 4,
            "expected_edges": 5,
            "expected_bidirectional": 2,
            "difficulty": "hard",
        },
    ]

    @staticmethod
    def get_diagram(diagram_id: str) -> GraphData | None:
        """Get a diagram by ID."""
        for d in BenchmarkDataset.diagrams:
            if d["id"] == diagram_id:
                return d["data"]
        return None

    @staticmethod
    def get_metadata(diagram_id: str):
        """Get metadata for a diagram."""
        for d in BenchmarkDataset.diagrams:
            if d["id"] == diagram_id:
                return d
        return None

    @staticmethod
    def list_all():
        """Get list of all benchmark diagrams."""
        return [
            {
                "id": d["id"],
                "name": d["name"],
                "difficulty": d["difficulty"],
                "nodes": d["expected_nodes"],
                "edges": d["expected_edges"],
            }
            for d in BenchmarkDataset.diagrams
        ]


def evaluate_extraction(extracted: GraphData, expected_data: dict) -> dict:
    """
    Evaluate extraction accuracy against expected results.
    Returns precision, recall, F1 for nodes and edges.
    """
    results = {
        "node_count_match": len(extracted.nodes) == expected_data.get("expected_nodes", 0),
        "edge_count_match": len(extracted.edges) == expected_data.get("expected_edges", 0),
        "actual_nodes": len(extracted.nodes),
        "expected_nodes": expected_data.get("expected_nodes", 0),
        "actual_edges": len(extracted.edges),
        "expected_edges": expected_data.get("expected_edges", 0),
    }

    # Count warnings
    if "expected_warnings" in expected_data:
        results["warning_count_match"] = len(extracted.warnings) >= expected_data["expected_warnings"]
        results["actual_warnings"] = len(extracted.warnings)
        results["expected_warnings"] = expected_data["expected_warnings"]

    # Calculate F1 if applicable
    if results["actual_nodes"] > 0 and results["expected_nodes"] > 0:
        precision = 1.0 if results["node_count_match"] else 0.0
        recall = 1.0 if results["node_count_match"] else 0.0
        results["node_f1"] = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    if results["actual_edges"] > 0 and results["expected_edges"] > 0:
        precision = 1.0 if results["edge_count_match"] else 0.0
        recall = 1.0 if results["edge_count_match"] else 0.0
        results["edge_f1"] = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    results["overall_pass"] = results.get("node_count_match", False) and results.get("edge_count_match", False)

    return results
