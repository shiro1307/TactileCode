export interface NodeItem {
  id: string;
  label: string;
  group?: string | null;
  confidence: number;
  uncertainty?: string | null;
}

export interface EdgeItem {
  id: string;
  source: string;
  target: string;
  direction: "forward" | "backward" | "bidirectional" | "undirected";
  label?: string | null;
  confidence: number;
  uncertainty?: string | null;
}

export interface GraphData {
  nodes: NodeItem[];
  edges: EdgeItem[];
  warnings: string[];
}

export interface DiagramMetadata {
  diagram_id: string;
  filename: string;
  created_at: string;
  node_count: number;
  edge_count: number;
  has_uncertainty: boolean;
  status: "processing" | "completed" | "failed";
}

export interface DiagramResponse {
  diagram_id: string;
  status: string;
  graph: GraphData;
  metadata: DiagramMetadata;
}

export interface NodeConnectionQuery {
  status: "found" | "not_found";
  node_id: string;
  node_label?: string;
  incoming: Array<{
    source_id: string;
    source_label: string;
    relationship: string;
    direction: string;
    confidence: number;
    uncertainty?: string | null;
  }>;
  outgoing: Array<{
    target_id: string;
    target_label: string;
    relationship: string;
    direction: string;
    confidence: number;
    uncertainty?: string | null;
  }>;
  total_connections: number;
  node_uncertainty?: string | null;
}

export interface PathQueryResult {
  status: "found" | "no_path" | "source_not_found" | "target_not_found";
  source_id: string;
  target_id: string;
  path_length?: number;
  path: Array<{
    step: number;
    node_id?: string;
    node_label?: string;
    node_group?: string;
    type?: string;
    relationship?: string;
    direction?: string;
    confidence?: number;
  }>;
}

export interface DependentsQueryResult {
  status: "found" | "not_found";
  node_id: string;
  node_label: string;
  dependents: Array<{
    node_id: string;
    node_label: string;
    node_group?: string;
  }>;
  dependent_count: number;
}

export interface GroupQueryResult {
  status: "found" | "not_found";
  group_name: string;
  nodes: Array<{
    node_id: string;
    node_label: string;
    confidence: number;
    uncertainty?: string | null;
  }>;
  node_count: number;
  internal_connection_count?: number;
  external_connection_count?: number;
  summary_text?: string;
}
