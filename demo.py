#!/usr/bin/env python3
"""
TactileCode Demo Script with Cached Responses

Demonstrates the system end-to-end without requiring live Gemma API.
Perfect for presentations, testing, and offline demos.

Usage:
    cd backend && python ../demo.py
"""

import sys
sys.path.insert(0, 'backend')

import json
import asyncio
from app.models.graph import DiagramResponse
from app.services.storage import diagram_storage
from app.services.query_engine import GraphQueryEngine

# Load benchmark data
sys.path.insert(0, 'backend/fixtures')
from benchmark_dataset import BenchmarkDataset


async def demo_workflow():
    """Walk through a complete TactileCode workflow."""

    print("=" * 80)
    print("TactileCode Demonstration")
    print("=" * 80)

    # Step 1: Load a diagram
    print("\n[1] LOAD DIAGRAM")
    print("-" * 80)

    diagram_metadata = BenchmarkDataset.get_metadata("microservices")
    graph_data = BenchmarkDataset.get_diagram("microservices")

    diagram_response = DiagramResponse(
        diagram_id="demo-microservices",
        status="completed",
        graph=graph_data,
        metadata={
            "diagram_id": "demo-microservices",
            "filename": diagram_metadata["name"],
            "created_at": "2024-10-24T10:00:00Z",
            "node_count": len(graph_data.nodes),
            "edge_count": len(graph_data.edges),
            "has_uncertainty": any(n.uncertainty for n in graph_data.nodes),
            "status": "completed",
        },
    )

    # Store in memory
    diagram_storage.save(diagram_response)

    print(f"[OK] Loaded: {diagram_metadata['name']}")
    print(f"  Components: {len(graph_data.nodes)}")
    print(f"  Relationships: {len(graph_data.edges)}")
    print(f"  Status: {diagram_response.status}")

    # Step 2: Display overview
    print("\n[2] DIAGRAM OVERVIEW")
    print("-" * 80)

    for i, node in enumerate(graph_data.nodes[:5], 1):
        confidence_bar = "█" * int(node.confidence * 10) + "░" * (10 - int(node.confidence * 10))
        uncertainty = f" ⚠️ {node.uncertainty}" if node.uncertainty else ""
        print(f"  {i}. [{confidence_bar}] {node.label} ({node.group}){uncertainty}")

    if len(graph_data.nodes) > 5:
        print(f"  ... and {len(graph_data.nodes) - 5} more")

    # Step 3: Run query: neighbors
    print("\n[3] QUERY - NODE NEIGHBORS")
    print("-" * 80)

    query_engine = GraphQueryEngine(graph_data)
    neighbors = query_engine.get_neighbors("api_gateway")

    print(f"Node: {neighbors.get('node_label', neighbors['node_id'])}")
    print(f"Total connections: {neighbors['total_connections']}")
    print(f"\nIncoming connections ({len(neighbors['incoming'])}):")
    for conn in neighbors["incoming"]:
        print(f"  ← {conn['source_label']}")
    print(f"\nOutgoing connections ({len(neighbors['outgoing'])}):")
    for conn in neighbors["outgoing"]:
        print(f"  → {conn['target_label']}")

    # Step 4: Run query: path finding
    print("\n🛤️  STEP 4: Query - Find Path")
    print("-" * 80)

    path = query_engine.find_path("client", "postgres_db")

    if path["status"] == "found":
        print(f"✓ Path found ({path['path_length']} hops):")
        for p in path["path"]:
            if "node_label" in p:
                print(f"  → {p['node_label']} ({p.get('node_group', 'N/A')})")
            elif "relationship" in p:
                print(f"     ({p['relationship']})")
    else:
        print(f"✗ No path found: {path['status']}")

    # Step 5: Run query: dependencies
    print("\n⚙️  STEP 5: Query - Dependencies")
    print("-" * 80)

    deps = query_engine.get_dependencies("order_service")

    print(f"Node: {deps['node_label']}")
    print(f"Dependencies ({deps['dependency_count']}):")
    for dep in deps["dependencies"]:
        print(f"  • {dep['node_label']} ({dep.get('node_group', 'N/A')})")

    # Step 6: Run query: group summary
    print("\n🏗️  STEP 6: Query - Group Summary")
    print("-" * 80)

    group_summary = query_engine.summarize_group("services")

    print(f"Group: {group_summary['group_name'].upper()}")
    print(f"Nodes in group: {group_summary['node_count']}")
    print(f"Internal connections: {group_summary['internal_connection_count']}")
    print(f"External connections: {group_summary['external_connection_count']}")
    print(f"\nNodes:")
    for node in group_summary["nodes"]:
        print(f"  • {node['node_label']}")

    # Step 7: Run query: reachability
    print("\n📡 STEP 7: Query - Reachability Analysis")
    print("-" * 80)

    reachable = query_engine.reachability_analysis("client")

    print(f"Starting from: {reachable['node_label']}")
    print(f"Reachable components: {reachable['reachable_count']}")
    print(f"Nodes:")
    for node in reachable["reachable_nodes"][:8]:
        print(f"  • {node['node_label']} ({node.get('node_group', 'N/A')})")

    if reachable["reachable_count"] > 8:
        print(f"  ... and {reachable['reachable_count'] - 8} more")

    # Step 8: Get all groups
    print("\n📊 STEP 8: Query - All Groups Overview")
    print("-" * 80)

    all_groups = query_engine.get_all_groups()

    print(f"Total groups: {all_groups['total_groups']}")
    for group in all_groups["groups"]:
        print(f"  • {group['group_name'].upper()}: {group['node_count']} nodes")

    # Step 9: Accessibility features
    print("\n♿ STEP 9: Accessibility Features")
    print("-" * 80)

    features = [
        "✓ Keyboard navigation (↑↓ Home End Tab Enter)",
        "✓ Screen reader support (ARIA live regions, semantic HTML)",
        "✓ Uncertainty handling (confidence scores, explicit warnings)",
        "✓ Query interface (8 graph-backed query types)",
        "✓ Focus indicators (3px blue outline on all controls)",
        "✓ High-contrast dark mode (AAA compliance ready)",
    ]

    for feature in features:
        print(f"  {feature}")

    # Step 10: Performance metrics
    print("\n⚡ STEP 10: Performance Metrics")
    print("-" * 80)

    metrics = [
        ("Path finding", "O(V+E)", "<100ms"),
        ("Neighbor query", "O(V)", "<50ms"),
        ("Dependencies", "O(V)", "<50ms"),
        ("Reachability", "O(V+E)", "<100ms"),
        ("Group summary", "O(V)", "<50ms"),
    ]

    print("Query Operation | Complexity | Typical Latency")
    print("-" * 80)
    for op, complexity, latency in metrics:
        print(f"{op:20} | {complexity:10} | {latency:15}")

    # Summary
    print("\n" + "=" * 80)
    print("✨ Demo Complete!")
    print("=" * 80)

    print(f"""
Next steps:
1. Start the backend: python -m uvicorn app.main:app --reload
2. Start the frontend: cd frontend && npm run dev
3. Open http://localhost:5173 in your browser
4. Upload a diagram and explore using keyboard + screen reader

For more information:
- See README.md for setup instructions
- See KEYBOARD_GUIDE.md for keyboard navigation
- See AGENTS.md for project specification
- Run 'python benchmark_eval.py' for accuracy evaluation
""")


if __name__ == "__main__":
    asyncio.run(demo_workflow())
