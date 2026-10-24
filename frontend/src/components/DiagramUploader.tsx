import React, { useRef, useState } from "react";
import { UploadCloud, FileImage, Sparkles, AlertCircle, Loader2 } from "lucide-react";
import { DiagramResponse } from "../types";
import API_ENDPOINTS from "../config";

interface UploaderProps {
  onDiagramLoaded: (diagram: DiagramResponse) => void;
  onAnnounce: (msg: string) => void;
}

export const DiagramUploader: React.FC<UploaderProps> = ({ onDiagramLoaded, onAnnounce }) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    setError(null);
    onAnnounce("Uploading diagram image for Gemma 4 vision extraction. Please wait.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(API_ENDPOINTS.UPLOAD_DIAGRAM, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed with HTTP ${response.status}`);
      }

      const data: DiagramResponse = await response.json();
      onDiagramLoaded(data);
      onAnnounce(
        `Extraction complete! Found ${data.graph.nodes.length} nodes and ${data.graph.edges.length} connections. ${
          data.metadata.has_uncertainty ? "Uncertainty detected in some elements." : "All elements verified."
        }`
      );
    } catch (err: any) {
      const msg = err.message || "Failed to process diagram.";
      setError(msg);
      onAnnounce(`Error processing diagram: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = async () => {
    setLoading(true);
    setError(null);
    onAnnounce("Loading sample architecture diagram for testing.");

    try {
      const response = await fetch(API_ENDPOINTS.GET_SAMPLE);
      if (!response.ok) {
        throw new Error(`Sample fetch failed with HTTP ${response.status}`);
      }
      const data: DiagramResponse = await response.json();
      onDiagramLoaded(data);
      onAnnounce(
        `Sample architecture loaded! ${data.graph.nodes.length} components, ${data.graph.edges.length} connections.`
      );
    } catch (err: any) {
      const msg = err.message || "Failed to load sample.";
      setError(msg);
      onAnnounce(`Error loading sample: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card-panel" role="region" aria-label="Diagram Ingestion">
      <div className="panel-header">
        <h2 className="panel-title">
          <UploadCloud size={20} color="var(--color-primary)" />
          Diagram Ingestion
        </h2>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        accept="image/png,image/jpeg,image/webp,image/svg+xml"
        style={{ display: "none" }}
        id="diagram-file-picker"
        aria-label="Upload diagram image file"
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            handleFileUpload(e.target.files[0]);
          }
        }}
      />

      <div
        className="uploader-box"
        role="button"
        tabIndex={0}
        aria-label="Upload diagram: click or press Enter to choose an image file"
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
      >
        <FileImage size={36} color="var(--color-primary)" style={{ margin: "0 auto 8px" }} />
        <p style={{ fontWeight: 600, color: "var(--text-primary)", fontSize: "0.95rem" }}>
          Drop diagram or click to upload
        </p>
        <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "4px" }}>
          PNG, JPEG, WebP, SVG (Max 10MB)
        </p>
      </div>

      {error && (
        <div
          role="alert"
          style={{
            marginTop: "12px",
            background: "rgba(239, 68, 68, 0.12)",
            border: "1px solid var(--color-danger)",
            color: "#fca5a5",
            padding: "8px 12px",
            borderRadius: "var(--radius-sm)",
            fontSize: "0.84rem",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      <div style={{ marginTop: "14px", display: "flex", flexDirection: "column", gap: "10px" }}>
        <button
          type="button"
          className="btn-secondary"
          onClick={handleLoadSample}
          disabled={loading}
          aria-label="Load pre-extracted sample architecture diagram for offline test"
          style={{ justifyContent: "center" }}
        >
          {loading ? (
            <>
              <Loader2 size={16} className="spin" />
              <span>Analyzing Diagram...</span>
            </>
          ) : (
            <>
              <Sparkles size={16} color="var(--color-primary)" />
              <span>Load Verified Architecture Sample</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
