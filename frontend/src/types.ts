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
  node_id: string;
  incoming: Array<{
    source: string;
    label?: string | null;
    direction: string;
    confidence: number;
    uncertainty?: string | null;
  }>;
  outgoing: Array<{
    target: string;
    label?: string | null;
    direction: string;
    confidence: number;
    uncertainty?: string | null;
  }>;
  total_connections: number;
}
