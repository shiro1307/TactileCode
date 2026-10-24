"""
Deterministic graph query engine for accessible navigation.

Implements queries such as:
- What connects to this node?
- What depends on the database?
- What path connects these two components?
- Summarize this group of nodes.

All queries operate on the extracted graph, never fabricating relationships.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
import networkx as nx
from app.models.graph import GraphData, Node, Edge


class GraphQueryEngine:
    """Deterministic query interface for graph exploration."""

    def __init__(self, graph_data: GraphData):
        self.graph_data = graph_data
        self.nx_graph = self._build_networkx(graph_data)
        self.node_map = {n.id: n for n in graph_data.nodes}
        self.edge_map = {e.id: e for e in graph_data.edges}

    def _build_networkx(self, graph_data: GraphData) -> nx.DiGraph:
        """Build NetworkX graph from GraphData."""
        g = nx.DiGraph()

        for node in graph_data.nodes:
            g.add_node(
                node.id,
                label=node.label,
                group=node.group or "default",
                confidence=node.confidence,
                uncertainty=node.uncertainty,
            )

        for edge in graph_data.edges:
            g.add_edge(
                edge.source,
                edge.target,
                edge_id=edge.id,
                label=edge.label or "",
                direction=edge.direction,
                confidence=edge.confidence,
                uncertainty=edge.uncertainty,
            )

        return g

    def get_neighbors(self, node_id: str) -> Dict[str, Any]:
        """Get all incoming and outgoing connections for a node."""
        if node_id not in self.nx_graph:
            return {
                "status": "not_found",
                "message": f"Node '{node_id}' not found in graph.",
                "node_id": node_id,
                "incoming": [],
                "outgoing": [],
                "total_connections": 0,
            }

        node = self.node_map.get(node_id)
        incoming = []
        outgoing = []

        # Predecessors (incoming)
        for pred_id in self.nx_graph.predecessors(node_id):
            pred_node = self.node_map.get(pred_id)
            edge_data = self.nx_graph.get_edge_data(pred_id, node_id)
            incoming.append({
                "source_id": pred_id,
                "source_label": pred_node.label if pred_node else pred_id,
                "relationship": edge_data.get("label", ""),
                "direction": edge_data.get("direction", "forward"),
                "confidence": edge_data.get("confidence", 1.0),
                "uncertainty": edge_data.get("uncertainty"),
            })

        # Successors (outgoing)
        for succ_id in self.nx_graph.successors(node_id):
            succ_node = self.node_map.get(succ_id)
            edge_data = self.nx_graph.get_edge_data(node_id, succ_id)
            outgoing.append({
                "target_id": succ_id,
                "target_label": succ_node.label if succ_node else succ_id,
                "relationship": edge_data.get("label", ""),
                "direction": edge_data.get("direction", "forward"),
                "confidence": edge_data.get("confidence", 1.0),
                "uncertainty": edge_data.get("uncertainty"),
            })

        return {
            "status": "found",
            "node_id": node_id,
            "node_label": node.label if node else node_id,
            "incoming": incoming,
            "outgoing": outgoing,
            "total_connections": len(incoming) + len(outgoing),
            "node_uncertainty": node.uncertainty if node else None,
        }

    def find_path(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """Find a path between two nodes, if one exists."""
        if source_id not in self.nx_graph:
            return {
                "status": "source_not_found",
                "message": f"Source node '{source_id}' not found.",
                "source_id": source_id,
                "target_id": target_id,
                "path": [],
            }

        if target_id not in self.nx_graph:
            return {
                "status": "target_not_found",
                "message": f"Target node '{target_id}' not found.",
                "source_id": source_id,
                "target_id": target_id,
                "path": [],
            }

        try:
            path = nx.shortest_path(self.nx_graph, source_id, target_id)
        except nx.NetworkXNoPath:
            return {
                "status": "no_path",
                "message": f"No path exists from '{source_id}' to '{target_id}'.",
                "source_id": source_id,
                "target_id": target_id,
                "path": [],
            }

        path_details = []
        for i, node_id in enumerate(path):
            node = self.node_map.get(node_id)
            path_details.append({
                "step": i,
                "node_id": node_id,
                "node_label": node.label if node else node_id,
                "node_group": node.group if node else None,
            })

            if i < len(path) - 1:
                next_node_id = path[i + 1]
                edge_data = self.nx_graph.get_edge_data(node_id, next_node_id)
                path_details.append({
                    "step": i + 0.5,
                    "type": "edge",
                    "relationship": edge_data.get("label", ""),
                    "direction": edge_data.get("direction", "forward"),
                    "confidence": edge_data.get("confidence", 1.0),
                })

        return {
            "status": "found",
            "source_id": source_id,
            "target_id": target_id,
            "path_length": len(path) - 1,
            "path": path_details,
        }

    def get_dependents(self, node_id: str) -> Dict[str, Any]:
        """Get all nodes that depend on (point to) the given node."""
        if node_id not in self.nx_graph:
            return {
                "status": "not_found",
                "message": f"Node '{node_id}' not found in graph.",
                "node_id": node_id,
                "dependents": [],
            }

        node = self.node_map.get(node_id)
        dependents = []

        for pred_id in self.nx_graph.predecessors(node_id):
            pred_node = self.node_map.get(pred_id)
            dependents.append({
                "node_id": pred_id,
                "node_label": pred_node.label if pred_node else pred_id,
                "node_group": pred_node.group if pred_node else None,
            })

        return {
            "status": "found",
            "node_id": node_id,
            "node_label": node.label if node else node_id,
            "dependents": dependents,
            "dependent_count": len(dependents),
        }

    def get_dependencies(self, node_id: str) -> Dict[str, Any]:
        """Get all nodes that the given node depends on (points to)."""
        if node_id not in self.nx_graph:
            return {
                "status": "not_found",
                "message": f"Node '{node_id}' not found in graph.",
                "node_id": node_id,
                "dependencies": [],
            }

        node = self.node_map.get(node_id)
        dependencies = []

        for succ_id in self.nx_graph.successors(node_id):
            succ_node = self.node_map.get(succ_id)
            dependencies.append({
                "node_id": succ_id,
                "node_label": succ_node.label if succ_node else succ_id,
                "node_group": succ_node.group if succ_node else None,
            })

        return {
            "status": "found",
            "node_id": node_id,
            "node_label": node.label if node else node_id,
            "dependencies": dependencies,
            "dependency_count": len(dependencies),
        }

    def find_nodes_by_group(self, group_name: str) -> Dict[str, Any]:
        """Find all nodes belonging to a specific group."""
        matching_nodes = [n for n in self.graph_data.nodes if n.group == group_name]

        return {
            "status": "found",
            "group_name": group_name,
            "nodes": [
                {
                    "node_id": n.id,
                    "node_label": n.label,
                    "confidence": n.confidence,
                    "uncertainty": n.uncertainty,
                }
                for n in matching_nodes
            ],
            "node_count": len(matching_nodes),
        }

    def summarize_group(self, group_name: str) -> Dict[str, Any]:
        """Summarize nodes and connections within a group."""
        group_nodes = [n for n in self.graph_data.nodes if n.group == group_name]
        if not group_nodes:
            return {
                "status": "not_found",
                "message": f"No nodes found in group '{group_name}'.",
                "group_name": group_name,
            }

        group_ids = {n.id for n in group_nodes}
        internal_edges = []
        external_edges = []

        for edge in self.graph_data.edges:
            source_in_group = edge.source in group_ids
            target_in_group = edge.target in group_ids

            if source_in_group and target_in_group:
                internal_edges.append(edge)
            elif source_in_group or target_in_group:
                external_edges.append(edge)

        return {
            "status": "found",
            "group_name": group_name,
            "nodes": [
                {
                    "node_id": n.id,
                    "node_label": n.label,
                    "confidence": n.confidence,
                }
                for n in group_nodes
            ],
            "node_count": len(group_nodes),
            "internal_connection_count": len(internal_edges),
            "external_connection_count": len(external_edges),
            "summary_text": (
                f"Group '{group_name}' contains {len(group_nodes)} component(s). "
                f"{len(internal_edges)} internal connection(s), "
                f"{len(external_edges)} external connection(s)."
            ),
        }

    def get_all_groups(self) -> Dict[str, Any]:
        """Get a summary of all groups in the graph."""
        groups: Dict[str, List[Node]] = {}
        for node in self.graph_data.nodes:
            group_name = node.group or "default"
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(node)

        group_summaries = []
        for group_name, nodes in sorted(groups.items()):
            group_summaries.append({
                "group_name": group_name,
                "node_count": len(nodes),
                "nodes": [{"node_id": n.id, "node_label": n.label} for n in nodes],
            })

        return {
            "status": "found",
            "total_groups": len(groups),
            "groups": group_summaries,
        }

    def reachability_analysis(self, node_id: str) -> Dict[str, Any]:
        """Analyze which nodes are reachable from the given node."""
        if node_id not in self.nx_graph:
            return {
                "status": "not_found",
                "message": f"Node '{node_id}' not found in graph.",
                "node_id": node_id,
                "reachable": [],
            }

        node = self.node_map.get(node_id)
        reachable = set()

        # BFS to find all reachable nodes
        queue = [node_id]
        visited = {node_id}

        while queue:
            current = queue.pop(0)
            for successor in self.nx_graph.successors(current):
                if successor not in visited:
                    visited.add(successor)
                    queue.append(successor)
                    reachable.add(successor)

        reachable_nodes = []
        for reachable_id in sorted(reachable):
            reachable_node = self.node_map.get(reachable_id)
            reachable_nodes.append({
                "node_id": reachable_id,
                "node_label": reachable_node.label if reachable_node else reachable_id,
                "node_group": reachable_node.group if reachable_node else None,
            })

        return {
            "status": "found",
            "node_id": node_id,
            "node_label": node.label if node else node_id,
            "reachable_count": len(reachable_nodes),
            "reachable_nodes": reachable_nodes,
        }
