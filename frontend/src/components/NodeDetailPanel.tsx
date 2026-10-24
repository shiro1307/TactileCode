import React from "react";
import { NodeItem, EdgeItem } from "../types";
import { ArrowRight, ArrowLeft, AlertTriangle, ShieldCheck, CornerDownRight, ExternalLink } from "lucide-react";

interface NodeDetailProps {
  node: NodeItem | null;
  nodes: NodeItem[];
  edges: EdgeItem[];
  onSelectNodeById: (nodeId: string) => void;
  onAnnounce: (msg: string) => void;
}

export const NodeDetailPanel: React.FC<NodeDetailProps> = ({
  node,
  nodes,
  edges,
  onSelectNodeById,
  onAnnounce,
}) => {
  if (!node) {
    return (
      <div className="card-panel" role="region" aria-label="Component Details">
        <h2 className="panel-title">Component Inspector</h2>
        <p style={{ color: "var(--text-muted)", marginTop: "12px", fontStyle: "italic" }}>
          Select or navigate to any component using arrow keys to examine connections, dependencies, and confidence data.
        </p>
      </div>
    );
  }

  const outgoing = edges.filter((e) => e.source === node.id);
  const incoming = edges.filter((e) => e.target === node.id);

  const getNodeLabel = (id: string) => {
    const target = nodes.find((n) => n.id === id);
    return target ? target.label : id;
  };

  const handleJump = (targetId: string, direction: "source" | "target") => {
    onSelectNodeById(targetId);
    const targetNode = nodes.find((n) => n.id === targetId);
    if (targetNode) {
      onAnnounce(`Jumped to connected ${direction} node: ${targetNode.label}`);
    }
  };

  return (
    <div className="card-panel" role="region" aria-label={`Details for ${node.label}`}>
      <div className="panel-header">
        <h2 className="panel-title">Inspector</h2>
        {node.group && <span className="group-tag">{node.group}</span>}
      </div>

      <div style={{ marginBottom: "14px" }}>
        <h3 style={{ fontSize: "1.25rem", color: "#fff", fontWeight: 700 }}>{node.label}</h3>
        <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem", color: "var(--text-muted)" }}>
          ID: {node.id}
        </p>
      </div>

      {/* Uncertainty Notice */}
      {node.uncertainty && (
        <div className="uncertainty-alert" role="alert">
          <AlertTriangle size={18} style={{ flexShrink: 0, marginTop: "2px" }} />
          <div>
            <strong>Perceptual Uncertainty Flagged:</strong>
            <p>{node.uncertainty}</p>
          </div>
        </div>
      )}

      {/* Confidence status */}
      <div style={{ margin: "14px 0", display: "flex", alignItems: "center", gap: "10px", fontSize: "0.88rem" }}>
        <ShieldCheck size={16} color="var(--color-primary)" />
        <span>Detection Confidence:</span>
        <strong
          className={
            node.confidence >= 0.85
              ? "confidence-high"
              : node.confidence >= 0.7
              ? "confidence-mid"
              : "confidence-low"
          }
        >
          {(node.confidence * 100).toFixed(1)}%
        </strong>
      </div>

      <div className="details-section">
        {/* Outgoing edges */}
        <div>
          <h4 style={{ fontSize: "0.92rem", color: "var(--text-secondary)", marginBottom: "8px" }}>
            Outgoing Connections ({outgoing.length})
          </h4>
          {outgoing.length === 0 ? (
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>No outgoing connections.</p>
          ) : (
            <ul className="connection-list" role="list">
              {outgoing.map((edge) => (
                <li key={edge.id} className="connection-item">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <span className="conn-direction-badge">→ Out</span>
                      <strong style={{ color: "#fff" }}>{getNodeLabel(edge.target)}</strong>
                    </div>
                    <button
                      className="btn-secondary"
                      style={{ padding: "4px 8px", fontSize: "0.75rem" }}
                      aria-label={`Jump to target node ${getNodeLabel(edge.target)}`}
                      onClick={() => handleJump(edge.target, "target")}
                    >
                      Jump <CornerDownRight size={12} />
                    </button>
                  </div>
                  {edge.label && (
                    <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "4px" }}>
                      Label: <em>"{edge.label}"</em> ({edge.direction})
                    </div>
                  )}
                  {edge.uncertainty && (
                    <div style={{ fontSize: "0.78rem", color: "var(--color-warning)", marginTop: "4px" }}>
                      ⚠️ {edge.uncertainty}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Incoming edges */}
        <div style={{ marginTop: "12px" }}>
          <h4 style={{ fontSize: "0.92rem", color: "var(--text-secondary)", marginBottom: "8px" }}>
            Incoming Connections ({incoming.length})
          </h4>
          {incoming.length === 0 ? (
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>No incoming connections.</p>
          ) : (
            <ul className="connection-list" role="list">
              {incoming.map((edge) => (
                <li key={edge.id} className="connection-item">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <span className="conn-direction-badge" style={{ color: "#a855f7" }}>← In</span>
                      <strong style={{ color: "#fff" }}>{getNodeLabel(edge.source)}</strong>
                    </div>
                    <button
                      className="btn-secondary"
                      style={{ padding: "4px 8px", fontSize: "0.75rem" }}
                      aria-label={`Jump to source node ${getNodeLabel(edge.source)}`}
                      onClick={() => handleJump(edge.source, "source")}
                    >
                      Jump <CornerDownRight size={12} />
                    </button>
                  </div>
                  {edge.label && (
                    <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "4px" }}>
                      Label: <em>"{edge.label}"</em>
                    </div>
                  )}
                  {edge.uncertainty && (
                    <div style={{ fontSize: "0.78rem", color: "var(--color-warning)", marginTop: "4px" }}>
                      ⚠️ {edge.uncertainty}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};
