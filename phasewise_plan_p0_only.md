TACTILECODE — FINAL SPRINT PLAN
Solo, Few Hours Remaining — P0 Only
Phase 1: Core Extraction Pipeline (1-1.5 hours)
Goal: Image → Structured Graph (no UI yet)

Set up minimal Python FastAPI backend
Integrate Gemma 4 vision + function calling for node/edge extraction
Validate extracted graph (no dangling edges, no invented relationships)
Return structured JSON with confidence scores
Deliverable: Working /api/diagrams endpoint that takes an image and returns a valid NetworkX-compatible graph
Success: Upload a sample diagram, get back clean JSON with nodes, edges, and confidence flags.

Phase 2: Accessible Navigation UI (1-1.5 hours)
Goal: Simple React app where keyboard + screen reader work end-to-end

Build minimal React frontend
Implement semantic HTML tree or list of nodes
Wire keyboard navigation (arrow keys, Enter to expand/collapse, Tab through nodes)
Add ARIA labels and live-region announcements for focus and relationships
Connect to backend /api/diagrams upload and query endpoints
Deliverable: You can upload an image, hear the graph structure via screen reader, navigate with keyboard only
Success: NVDA reads node labels and connections; you can explore the entire graph without touching the mouse.

Phase 3: Lightweight Verification (30 min)
Goal: Flag uncertainty without false confidence

Add basic validation: check for orphaned nodes, dangling edges, low-confidence elements
Display uncertainty flags in the UI ("This connection has low confidence")
Do not spend time on targeted re-inspection or Graphviz rendering
Deliverable: Graph is validated; uncertain elements are clearly marked
Success: When the model is unsure, you see a warning. No silent guesses.

Phase 4: Demo + Documentation (30 min - 1 hour)
Goal: Submission-ready artifact

Cache one successful end-to-end response (so demo works offline)
Write minimal README: setup, running the app, known limitations
Record or script a 3-minute demo: upload → navigate via keyboard/screen reader → show uncertainty handling
Confirm .env.example has no secrets; .gitignore includes .env
Deliverable: Everything needed for live demo + submission
Success: A fresh environment runs the app without errors; demo is cached and repeatable.

What to Skip (Save Serious Time)
❌ Image cropping / targeted re-inspection
❌ Graphviz rendering and visual comparison
❌ Graph-backed natural-language queries beyond "show me connected nodes"
❌ Benchmark dataset
❌ Voice input, Mermaid export, browser extension
❌ Complex error recovery
Critical Path to Shipping

Phase 1 (Backend extraction) → Phase 2 (Frontend + keyboard navigation) → Phase 3 (Light validation) → Phase 4 (Demo)
Parallel opportunity: While Phase 1 runs, start scaffolding Phase 2 React structure and API contracts.