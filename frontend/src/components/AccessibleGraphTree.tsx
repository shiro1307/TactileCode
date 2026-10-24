import React, { useRef, useEffect } from "react";
import { NodeItem, EdgeItem } from "../types";
import { AlertTriangle, CheckCircle, ShieldAlert, ArrowRight, ArrowLeft } from "lucide-react";

interface GraphTreeProps {
  nodes: NodeItem[];
  edges: EdgeItem[];
  selectedNodeId: string | null;
  onSelectNode: (node: NodeItem) => void;
  onAnnounce: (msg: string) => void;
}

export const AccessibleGraphTree: React.FC<GraphTreeProps> = ({
  nodes,
  edges,
  selectedNodeId,
  onSelectNode,
  onAnnounce,
}) => {
  const [focusedIndex, setFocusedIndex] = React.useState<number>(0);
  const itemRefs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    if (selectedNodeId) {
      const idx = nodes.findIndex((n) => n.id === selectedNodeId);
      if (idx !== -1) {
        setFocusedIndex(idx);
      }
    }
  }, [selectedNodeId, nodes]);

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    let nextIndex = index;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      nextIndex = (index + 1) % nodes.length;
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      nextIndex = (index - 1 + nodes.length) % nodes.length;
    } else if (e.key === "Home") {
      e.preventDefault();
      nextIndex = 0;
    } else if (e.key === "End") {
      e.preventDefault();
      nextIndex = nodes.length - 1;
    } else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      selectNodeByIndex(index);
      return;
    } else {
      return;
    }

    setFocusedIndex(nextIndex);
    itemRefs.current[nextIndex]?.focus();
    announceNodeBrief(nodes[nextIndex]);
  };

  const selectNodeByIndex = (index: number) => {
    const node = nodes[index];
    if (!node) return;
    onSelectNode(node);

    const outgoing = edges.filter((e) => e.source === node.id);
    const incoming = edges.filter((e) => e.target === node.id);

    let speech = `Selected ${node.label}, group ${node.group || "none"}. `;
    speech += `${outgoing.length} outgoing connections, ${incoming.length} incoming connections. `;
    if (node.uncertainty) {
      speech += `Warning: ${node.uncertainty}. `;
    }
    speech += `Confidence ${(node.confidence * 100).toFixed(0)} percent.`;
    onAnnounce(speech);
  };

  const announceNodeBrief = (node: NodeItem) => {
    const outgoingCount = edges.filter((e) => e.source === node.id).length;
    const incomingCount = edges.filter((e) => e.target === node.id).length;
    const warn = node.uncertainty ? ", has uncertainty warning" : "";
    onAnnounce(
      `${node.label}, ${node.group || "component"}. ${outgoingCount} out, ${incomingCount} in${warn}.`
    );
  };

  if (nodes.length === 0) {
    return (
      <div className="card-panel" role="region" aria-label="Diagram Nodes">
        <p style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
          No components loaded. Upload a diagram to explore graph nodes.
        </p>
      </div>
    );
  }

  return (
    <div className="card-panel" role="region" aria-label="Graph Nodes List">
      <div className="panel-header">
        <h2 className="panel-title" id="nodes-list-title">
          Diagram Components
        </h2>
        <span className="panel-count">{nodes.length} nodes</span>
      </div>

      <p className="sr-only">
        Use Up and Down Arrow keys to navigate components. Press Enter or Space to inspect details and connections.
      </p>

      <div
        role="listbox"
        aria-labelledby="nodes-list-title"
        aria-activedescendant={nodes[focusedIndex] ? `node-item-${nodes[focusedIndex].id}` : undefined}
        className="tree-container"
        tabIndex={0}
        onFocus={() => itemRefs.current[focusedIndex]?.focus()}
      >
        {nodes.map((node, idx) => {
          const isSelected = node.id === selectedNodeId;
          const isFocused = idx === focusedIndex;
          const outgoing = edges.filter((e) => e.source === node.id).length;
          const incoming = edges.filter((e) => e.target === node.id).length;

          return (
            <div
              key={node.id}
              id={`node-item-${node.id}`}
              ref={(el) => (itemRefs.current[idx] = el)}
              role="option"
              aria-selected={isSelected}
              tabIndex={isFocused ? 0 : -1}
              className={`tree-node-item ${isSelected ? "selected" : ""}`}
              onClick={() => {
                setFocusedIndex(idx);
                selectNodeByIndex(idx);
              }}
              onKeyDown={(e) => handleKeyDown(e, idx)}
            >
              <div className="node-title-row">
                <span className="node-label">{node.label}</span>
                {node.group && <span className="group-tag">{node.group}</span>}
              </div>

              <div className="node-meta-row">
                <span title="Connections" style={{ display: "flex", gap: "8px" }}>
                  <span>{outgoing} out</span>
                  <span>•</span>
                  <span>{incoming} in</span>
                </span>

                <span
                  className={`badge-confidence ${
                    node.confidence >= 0.85
                      ? "confidence-high"
                      : node.confidence >= 0.7
                      ? "confidence-mid"
                      : "confidence-low"
                  }`}
                >
                  <CheckCircle size={12} />
                  {(node.confidence * 100).toFixed(0)}%
                </span>

                {node.uncertainty && (
                  <span
                    style={{ color: "var(--color-warning)", display: "flex", alignItems: "center", gap: 3 }}
                    title={node.uncertainty}
                  >
                    <AlertTriangle size={13} />
                    <span className="sr-only">Uncertainty detected</span>
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
