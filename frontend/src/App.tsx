import React, { useState } from "react";
import { DiagramResponse, NodeItem } from "./types";
import { DiagramUploader } from "./components/DiagramUploader";
import { AccessibleGraphTree } from "./components/AccessibleGraphTree";
import { NodeDetailPanel } from "./components/NodeDetailPanel";
import { AccessibleGraphCanvas } from "./components/AccessibleGraphCanvas";
import { AccessibleLiveAnnouncer } from "./components/AccessibleLiveAnnouncer";
import { Network, Keyboard, AlertTriangle, CheckCircle2 } from "lucide-react";

export const App: React.FC = () => {
  const [diagram, setDiagram] = useState<DiagramResponse | null>(null);
  const [selectedNode, setSelectedNode] = useState<NodeItem | null>(null);
  const [announcement, setAnnouncement] = useState<string>(
    "Welcome to TactileCode. Use Tab to move to upload or load sample diagram."
  );

  const handleDiagramLoaded = (loadedDiagram: DiagramResponse) => {
    setDiagram(loadedDiagram);
    if (loadedDiagram.graph.nodes.length > 0) {
      setSelectedNode(loadedDiagram.graph.nodes[0]);
    } else {
      setSelectedNode(null);
    }
  };

  const handleSelectNodeById = (nodeId: string) => {
    if (!diagram) return;
    const found = diagram.graph.nodes.find((n) => n.id === nodeId);
    if (found) {
      setSelectedNode(found);
    }
  };

  return (
    <div className="app-container">
      {/* Skip Link for screen reader / keyboard users */}
      <a href="#main-graph-area" className="skip-link">
        Skip to Accessible Graph Structure
      </a>

      {/* Screen Reader Live Region */}
      <AccessibleLiveAnnouncer message={announcement} />

      {/* Header */}
      <header className="app-header" role="banner">
        <div className="brand-wrapper">
          <span className="brand-badge">NVDA / Screen Reader Verified</span>
          <div>
            <h1 className="brand-title">TactileCode</h1>
            <p className="brand-tagline">
              Non-visual architecture diagram and flowchart explorer
            </p>
          </div>
        </div>

        <div className="live-badge" role="status" aria-label="Screen reader status active">
          <div className="live-dot" aria-hidden="true" />
          <span>Screen Reader Live Region Active</span>
        </div>
      </header>

      {/* Main Grid Layout */}
      <main id="main-graph-area" className="main-grid" tabIndex={-1}>
        {/* Left Column: Uploader & Summary Stats */}
        <section aria-label="Ingestion and Diagram Stats" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <DiagramUploader
            onDiagramLoaded={handleDiagramLoaded}
            onAnnounce={setAnnouncement}
          />

          {diagram && (
            <div className="card-panel" role="region" aria-label="Diagram Summary">
              <div className="panel-header">
                <h3 className="panel-title">Diagram Overview</h3>
                <span className="panel-count">{diagram.metadata.status}</span>
              </div>
              <ul style={{ listStyle: "none", fontSize: "0.85rem", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "8px" }}>
                <li><strong>Filename:</strong> {diagram.metadata.filename}</li>
                <li><strong>Total Components:</strong> {diagram.metadata.node_count}</li>
                <li><strong>Total Relationships:</strong> {diagram.metadata.edge_count}</li>
                <li style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <strong>Uncertainty:</strong>{" "}
                  {diagram.metadata.has_uncertainty ? (
                    <span style={{ color: "var(--color-warning)", display: "inline-flex", alignItems: "center", gap: "4px" }}>
                      <AlertTriangle size={14} /> Explicit flags reported
                    </span>
                  ) : (
                    <span style={{ color: "var(--color-success)", display: "inline-flex", alignItems: "center", gap: "4px" }}>
                      <CheckCircle2 size={14} /> High confidence
                    </span>
                  )}
                </li>
              </ul>

              {diagram.graph.warnings.length > 0 && (
                <div style={{ marginTop: "14px" }}>
                  <h4 style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase" }}>
                    Pipeline Verification Flags ({diagram.graph.warnings.length})
                  </h4>
                  <ul style={{ marginTop: "6px", fontSize: "0.78rem", color: "var(--text-secondary)", paddingLeft: "16px" }}>
                    {diagram.graph.warnings.map((w, idx) => (
                      <li key={idx} style={{ marginTop: "3px" }}>{w}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Middle Column: Semantic Accessible Tree / List & Canvas */}
        <section aria-label="Graph Navigation & Visualization" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <AccessibleGraphTree
            nodes={diagram ? diagram.graph.nodes : []}
            edges={diagram ? diagram.graph.edges : []}
            selectedNodeId={selectedNode ? selectedNode.id : null}
            onSelectNode={setSelectedNode}
            onAnnounce={setAnnouncement}
          />

          <AccessibleGraphCanvas
            nodes={diagram ? diagram.graph.nodes : []}
            edges={diagram ? diagram.graph.edges : []}
            selectedNodeId={selectedNode ? selectedNode.id : null}
            onSelectNode={setSelectedNode}
          />
        </section>

        {/* Right Column: Component Inspector */}
        <section aria-label="Component Inspector">
          <NodeDetailPanel
            node={selectedNode}
            nodes={diagram ? diagram.graph.nodes : []}
            edges={diagram ? diagram.graph.edges : []}
            onSelectNodeById={handleSelectNodeById}
            onAnnounce={setAnnouncement}
          />
        </section>
      </main>

      {/* Accessible Keyboard Shortcut Reference Bar */}
      <footer className="keyboard-bar" role="contentinfo" aria-label="Keyboard Shortcuts">
        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontWeight: 700, color: "var(--text-primary)" }}>
          <Keyboard size={16} color="var(--color-primary)" />
          <span>Keyboard Navigation:</span>
        </div>
        <div><kbd>↑</kbd> <kbd>↓</kbd> Move focus between diagram components</div>
        <div><kbd>Enter</kbd> / <kbd>Space</kbd> Select component & announce connections</div>
        <div><kbd>Home</kbd> / <kbd>End</kbd> Jump to first / last node</div>
        <div><kbd>Tab</kbd> Move between action buttons and jump links</div>
      </footer>
    </div>
  );
};
