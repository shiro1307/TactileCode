import React from "react";
import { NodeItem, EdgeItem } from "../types";

interface CanvasProps {
  nodes: NodeItem[];
  edges: EdgeItem[];
  selectedNodeId: string | null;
  onSelectNode: (node: NodeItem) => void;
}

export const AccessibleGraphCanvas: React.FC<CanvasProps> = ({
  nodes,
  edges,
  selectedNodeId,
  onSelectNode,
}) => {
  if (nodes.length === 0) {
    return (
      <div
        className="card-panel"
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "420px",
          color: "var(--text-muted)",
        }}
      >
        <p>No active diagram to display.</p>
        <p style={{ fontSize: "0.85rem", marginTop: "4px" }}>
          Upload an image or load the verified sample architecture.
        </p>
      </div>
    );
  }

  // Layout node positions in a neat grid or circular/layered arrangement
  const width = 640;
  const height = 440;
  const nodeCount = nodes.length;

  const nodePositions = React.useMemo(() => {
    const posMap: Record<string, { x: number; y: number }> = {};
    const cols = Math.min(3, Math.ceil(Math.sqrt(nodeCount)));
    const rows = Math.ceil(nodeCount / cols);
    const paddingX = 100;
    const paddingY = 80;
    const stepX = (width - paddingX * 2) / (cols > 1 ? cols - 1 : 1);
    const stepY = (height - paddingY * 2) / (rows > 1 ? rows - 1 : 1);

    nodes.forEach((node, idx) => {
      const col = idx % cols;
      const row = Math.floor(idx / cols);
      posMap[node.id] = {
        x: paddingX + col * stepX,
        y: paddingY + row * stepY,
      };
    });
    return posMap;
  }, [nodes, nodeCount]);

  return (
    <div
      className="card-panel"
      role="region"
      aria-label="Visual Graph Diagram Canvas (synchronized with keyboard navigation)"
      style={{ overflow: "hidden", position: "relative" }}
    >
      <div className="panel-header">
        <h2 className="panel-title">Visual Synchronizer</h2>
        <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
          Synchronized with keyboard focus
        </span>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: "100%", height: "420px", background: "#0d1322", borderRadius: "8px" }}
      >
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="26"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
          </marker>
          <marker
            id="arrow-uncertain"
            viewBox="0 0 10 10"
            refX="26"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b" />
          </marker>
        </defs>

        {/* Edges */}
        {edges.map((edge) => {
          const src = nodePositions[edge.source];
          const tgt = nodePositions[edge.target];
          if (!src || !tgt) return null;

          const isConnectedToSelected =
            edge.source === selectedNodeId || edge.target === selectedNodeId;
          const isUncertain = !!edge.uncertainty;

          return (
            <g key={edge.id}>
              <line
                x1={src.x}
                y1={src.y}
                x2={tgt.x}
                y2={tgt.y}
                stroke={
                  isUncertain
                    ? "#f59e0b"
                    : isConnectedToSelected
                    ? "#38bdf8"
                    : "#334155"
                }
                strokeWidth={isConnectedToSelected ? 3 : 1.5}
                strokeDasharray={isUncertain ? "4,4" : undefined}
                markerEnd={isUncertain ? "url(#arrow-uncertain)" : "url(#arrow)"}
              />
              {edge.label && (
                <text
                  x={(src.x + tgt.x) / 2}
                  y={(src.y + tgt.y) / 2 - 8}
                  fill={isConnectedToSelected ? "#e2e8f0" : "#64748b"}
                  fontSize="10"
                  textAnchor="middle"
                  fontFamily="sans-serif"
                >
                  {edge.label}
                </text>
              )}
            </g>
          );
        })}

        {/* Nodes */}
        {nodes.map((node) => {
          const pos = nodePositions[node.id];
          if (!pos) return null;

          const isSelected = node.id === selectedNodeId;
          const isUncertain = !!node.uncertainty;

          return (
            <g
              key={node.id}
              transform={`translate(${pos.x}, ${pos.y})`}
              style={{ cursor: "pointer" }}
              onClick={() => onSelectNode(node)}
            >
              <rect
                x="-70"
                y="-25"
                width="140"
                height="50"
                rx="8"
                fill={isSelected ? "#1e293b" : "#131b2e"}
                stroke={
                  isSelected
                    ? "#38bdf8"
                    : isUncertain
                    ? "#f59e0b"
                    : "#243250"
                }
                strokeWidth={isSelected ? 3 : 1.5}
                style={{
                  filter: isSelected ? "drop-shadow(0 0 8px rgba(56, 189, 248, 0.5))" : undefined,
                  transition: "all 0.2s ease",
                }}
              />
              <text
                x="0"
                y="-2"
                textAnchor="middle"
                fill={isSelected ? "#ffffff" : "#cbd5e1"}
                fontSize="12"
                fontWeight="700"
                fontFamily="sans-serif"
              >
                {node.label.length > 17 ? node.label.slice(0, 15) + "..." : node.label}
              </text>
              <text
                x="0"
                y="14"
                textAnchor="middle"
                fill={node.confidence >= 0.85 ? "#10b981" : "#f59e0b"}
                fontSize="10"
                fontFamily="monospace"
              >
                {(node.confidence * 100).toFixed(0)}% conf
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};
