import React, { useState } from "react";
import {
  NodeItem,
  PathQueryResult,
  DependentsQueryResult,
  GroupQueryResult,
} from "../types";
import {
  Search,
  ArrowRight,
  Zap,
  AlertTriangle,
  CheckCircle,
  Layers,
} from "lucide-react";

interface QueryBuilderProps {
  diagramId: string;
  nodes: NodeItem[];
  onSelectNode: (nodeId: string) => void;
  onAnnounce: (msg: string) => void;
}

type QueryType =
  | "path"
  | "dependents"
  | "dependencies"
  | "group"
  | "reachable"
  | "none";

export const GraphQueryBuilder: React.FC<QueryBuilderProps> = ({
  diagramId,
  nodes,
  onSelectNode,
  onAnnounce,
}) => {
  const [queryType, setQueryType] = useState<QueryType>("none");
  const [sourceNode, setSourceNode] = useState<string>("");
  const [targetNode, setTargetNode] = useState<string>("");
  const [groupName, setGroupName] = useState<string>("");
  const [result, setResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const groups = Array.from(new Set(nodes.map((n) => n.group).filter(Boolean)));

  const executeQuery = async () => {
    setError("");
    setResult(null);
    setIsLoading(true);

    try {
      let url = `http://localhost:8000/api/diagrams/${diagramId}/query/`;
      let resultMessage = "";

      switch (queryType) {
        case "path":
          if (!sourceNode || !targetNode) {
            throw new Error("Please select both source and target nodes.");
          }
          url += `path?source=${sourceNode}&target=${targetNode}`;
          const pathRes = await fetch(url);
          const pathData = (await pathRes.json()) as PathQueryResult;
          setResult(pathData);

          if (pathData.status === "found") {
            const nodeLabels = (pathData.path as any[])
              .filter((p: any) => p.node_label)
              .map((p: any) => p.node_label)
              .join(" → ");
            resultMessage = `Path found: ${nodeLabels}. ${pathData.path.length} steps total.`;
          } else if (pathData.status === "no_path") {
            resultMessage = `No direct path exists between these components.`;
          } else {
            resultMessage = `One or both nodes not found in the diagram.`;
          }
          break;

        case "dependents":
          if (!sourceNode) {
            throw new Error("Please select a node.");
          }
          url += `dependents?node_id=${sourceNode}`;
          const depRes = await fetch(url);
          const depData = (await depRes.json()) as DependentsQueryResult;
          setResult(depData);

          if (depData.status === "found") {
            const depCount = depData.dependent_count;
            resultMessage = `${depCount} component(s) depend on ${depData.node_label}.`;
            if (depCount > 0) {
              resultMessage += ` They are: ${depData.dependents
                .map((d: any) => d.node_label)
                .join(", ")}.`;
            }
          } else {
            resultMessage = `Node not found in the diagram.`;
          }
          break;

        case "dependencies":
          if (!sourceNode) {
            throw new Error("Please select a node.");
          }
          url += `dependencies?node_id=${sourceNode}`;
          const depsRes = await fetch(url);
          const depsData = (await depsRes.json()) as any;
          setResult(depsData);

          if (depsData.status === "found") {
            const depCount = depsData.dependency_count || 0;
            resultMessage = `${depCount} component(s) are required by ${depsData.node_label}.`;
            if (depCount > 0) {
              resultMessage += ` They are: ${(depsData.dependents || [])
                .map((d: any) => d.node_label)
                .join(", ")}.`;
            }
          } else {
            resultMessage = `Node not found in the diagram.`;
          }
          break;

        case "group":
          if (!groupName) {
            throw new Error("Please select a group.");
          }
          url += `group/${groupName}/summary`;
          const grpRes = await fetch(url);
          const grpData = (await grpRes.json()) as GroupQueryResult;
          setResult(grpData);

          if (grpData.status === "found") {
            resultMessage = grpData.summary_text || "Group found.";
          } else {
            resultMessage = `Group '${groupName}' not found in the diagram.`;
          }
          break;

        case "reachable":
          if (!sourceNode) {
            throw new Error("Please select a node.");
          }
          url += `reachable/${sourceNode}`;
          const reachRes = await fetch(url);
          const reachData = (await reachRes.json()) as any;
          setResult(reachData);

          if (reachData.status === "found") {
            const count = reachData.reachable_count;
            resultMessage = `${count} component(s) are reachable from ${reachData.node_label}.`;
          } else {
            resultMessage = `Node not found in the diagram.`;
          }
          break;

        default:
          throw new Error("No query type selected.");
      }

      onAnnounce(resultMessage);
    } catch (err: any) {
      const errorMsg = err.message || "Query failed. Please try again.";
      setError(errorMsg);
      onAnnounce(`Error: ${errorMsg}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearQuery = () => {
    setQueryType("none");
    setSourceNode("");
    setTargetNode("");
    setGroupName("");
    setResult(null);
    setError("");
  };

  return (
    <div className="card-panel" role="region" aria-label="Graph Query Builder">
      <div className="panel-header">
        <h2 className="panel-title" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Zap size={18} color="var(--color-primary)" />
          Query Builder
        </h2>
      </div>

      {/* Query Type Selector */}
      <div style={{ marginBottom: "16px" }}>
        <label htmlFor="query-type" style={{ display: "block", fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
          <strong>Query Type</strong>
        </label>
        <select
          id="query-type"
          value={queryType}
          onChange={(e) => {
            setQueryType(e.target.value as QueryType);
            setResult(null);
            setError("");
          }}
          style={{
            width: "100%",
            padding: "8px",
            backgroundColor: "var(--bg-input)",
            color: "var(--text-primary)",
            border: "1px solid var(--border-color)",
            borderRadius: "4px",
            fontSize: "0.9rem",
          }}
          aria-label="Choose a query type"
        >
          <option value="none">-- Select Query --</option>
          <option value="path">Find Path Between Nodes</option>
          <option value="dependents">Show Dependents</option>
          <option value="dependencies">Show Dependencies</option>
          <option value="group">Summarize Group</option>
          <option value="reachable">Find Reachable Nodes</option>
        </select>
      </div>

      {/* Query-Specific Inputs */}
      {(queryType === "path" || queryType === "dependents" || queryType === "dependencies" || queryType === "reachable") && (
        <div style={{ marginBottom: "16px" }}>
          <label htmlFor="source-node" style={{ display: "block", fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
            <strong>
              {queryType === "path" ? "Source Node" : "Select Node"}
            </strong>
          </label>
          <select
            id="source-node"
            value={sourceNode}
            onChange={(e) => setSourceNode(e.target.value)}
            style={{
              width: "100%",
              padding: "8px",
              backgroundColor: "var(--bg-input)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-color)",
              borderRadius: "4px",
              fontSize: "0.9rem",
            }}
            aria-label="Select source node"
          >
            <option value="">-- Choose Node --</option>
            {nodes.map((n) => (
              <option key={n.id} value={n.id}>
                {n.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {queryType === "path" && (
        <div style={{ marginBottom: "16px" }}>
          <label htmlFor="target-node" style={{ display: "block", fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
            <strong>Target Node</strong>
          </label>
          <select
            id="target-node"
            value={targetNode}
            onChange={(e) => setTargetNode(e.target.value)}
            style={{
              width: "100%",
              padding: "8px",
              backgroundColor: "var(--bg-input)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-color)",
              borderRadius: "4px",
              fontSize: "0.9rem",
            }}
            aria-label="Select target node"
          >
            <option value="">-- Choose Node --</option>
            {nodes.map((n) => (
              <option key={n.id} value={n.id}>
                {n.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {queryType === "group" && (
        <div style={{ marginBottom: "16px" }}>
          <label htmlFor="group-name" style={{ display: "block", fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
            <strong>Group</strong>
          </label>
          <select
            id="group-name"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            style={{
              width: "100%",
              padding: "8px",
              backgroundColor: "var(--bg-input)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-color)",
              borderRadius: "4px",
              fontSize: "0.9rem",
            }}
            aria-label="Select group"
          >
            <option value="">-- Choose Group --</option>
            {groups.map((g) => (
              <option key={g || "default"} value={g || "default"}>
                {g || "default"}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div
          className="uncertainty-alert"
          role="alert"
          style={{ marginBottom: "12px" }}
        >
          <AlertTriangle size={16} />
          <p>{error}</p>
        </div>
      )}

      {/* Query Buttons */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
        <button
          className="btn-primary"
          onClick={executeQuery}
          disabled={
            isLoading ||
            queryType === "none" ||
            (queryType === "path" && (!sourceNode || !targetNode)) ||
            ((queryType === "dependents" ||
              queryType === "dependencies" ||
              queryType === "reachable") &&
              !sourceNode) ||
            (queryType === "group" && !groupName)
          }
          aria-label="Execute query"
        >
          <Search size={14} />
          {isLoading ? "Querying..." : "Execute"}
        </button>
        {result && (
          <button
            className="btn-secondary"
            onClick={handleClearQuery}
            aria-label="Clear query"
          >
            Clear
          </button>
        )}
      </div>

      {/* Results Display */}
      {result && (
        <div
          style={{
            padding: "12px",
            backgroundColor: "rgba(59, 130, 246, 0.1)",
            borderRadius: "4px",
            marginBottom: "12px",
          }}
          role="region"
          aria-label="Query Results"
        >
          <h3 style={{ fontSize: "0.95rem", marginBottom: "10px", color: "var(--color-primary)" }}>
            <CheckCircle size={14} style={{ display: "inline", marginRight: "6px" }} />
            Results
          </h3>

          {result.status === "found" && (
            <div style={{ fontSize: "0.88rem", color: "var(--text-primary)", lineHeight: "1.5" }}>
              {queryType === "path" && result.path && (
                <div>
                  <p style={{ marginBottom: "8px" }}>
                    <strong>Path Length:</strong> {result.path_length || 0} step(s)
                  </p>
                  <ol style={{ paddingLeft: "16px", marginBottom: "8px" }}>
                    {(result.path as any[])
                      .filter((p: any) => p.node_label)
                      .map((p: any, i: number) => (
                        <li key={i}>
                          <strong>{p.node_label}</strong> ({p.node_group || "default"})
                        </li>
                      ))}
                  </ol>
                </div>
              )}

              {(queryType === "dependents" || queryType === "dependencies") && result.dependents && (
                <div>
                  <p style={{ marginBottom: "8px" }}>
                    <strong>Count:</strong> {result.dependent_count || 0}
                  </p>
                  {(result.dependent_count || 0) > 0 && (
                    <ul style={{ paddingLeft: "16px", marginBottom: "8px" }}>
                      {result.dependents.map((d: any) => (
                        <li key={d.node_id}>
                          <button
                            className="link-button"
                            onClick={() => {
                              onSelectNode(d.node_id);
                              onAnnounce(`Navigated to ${d.node_label}`);
                            }}
                            style={{ color: "var(--color-primary)", cursor: "pointer" }}
                          >
                            {d.node_label}
                          </button>
                          {d.node_group && <span> ({d.node_group})</span>}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              {queryType === "group" && result.nodes && (
                <div>
                  <p style={{ marginBottom: "8px" }}>
                    <strong>Components in group:</strong> {result.node_count}
                  </p>
                  {result.summary_text && (
                    <p style={{ marginBottom: "8px", fontStyle: "italic" }}>
                      {result.summary_text}
                    </p>
                  )}
                  <ul style={{ paddingLeft: "16px", marginBottom: "8px" }}>
                    {result.nodes.map((n: any) => (
                      <li key={n.node_id}>
                        <button
                          className="link-button"
                          onClick={() => {
                            onSelectNode(n.node_id);
                            onAnnounce(`Navigated to ${n.node_label}`);
                          }}
                          style={{ color: "var(--color-primary)", cursor: "pointer" }}
                        >
                          {n.node_label}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {queryType === "reachable" && result.reachable_nodes && (
                <div>
                  <p style={{ marginBottom: "8px" }}>
                    <strong>Reachable components:</strong> {result.reachable_count}
                  </p>
                  <ul style={{ paddingLeft: "16px", marginBottom: "8px" }}>
                    {result.reachable_nodes.map((n: any) => (
                      <li key={n.node_id}>
                        <button
                          className="link-button"
                          onClick={() => {
                            onSelectNode(n.node_id);
                            onAnnounce(`Navigated to ${n.node_label}`);
                          }}
                          style={{ color: "var(--color-primary)", cursor: "pointer" }}
                        >
                          {n.node_label}
                        </button>
                        {n.node_group && <span> ({n.node_group})</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {result.status === "no_path" && (
            <p style={{ fontSize: "0.88rem", color: "var(--text-primary)" }}>
              No path exists between the selected nodes.
            </p>
          )}

          {result.status === "not_found" && (
            <p style={{ fontSize: "0.88rem", color: "var(--color-warning)" }}>
              {result.message || "Resource not found."}
            </p>
          )}
        </div>
      )}

      {/* Help Text */}
      {queryType === "none" && !result && (
        <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontStyle: "italic" }}>
          Select a query type above to explore relationships, dependencies, and reachability in the diagram.
        </p>
      )}
    </div>
  );
};
