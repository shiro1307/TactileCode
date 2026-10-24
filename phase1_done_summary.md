# Phase 1 Done

Pipeline built + verified.

## Built Components
- Data Models: `backend/app/models/graph.py` (`Node`, `Edge`, `GraphData`, `DiagramMetadata`, `DiagramResponse` per `AGENTS.md`)
- Model Client: `backend/app/services/model_client.py` (`BaseModelClient`, `GeminiGemmaClient` via `google.genai`, `MockGemmaClient` fallback)
- Validator: `backend/app/services/validator.py` (dedup nodes, flag dangling edges, flag confidence < 0.70, convert `networkx.DiGraph`)
- Pipeline + Store: `backend/app/services/extractor.py`, `backend/app/services/storage.py`
- Endpoints: `backend/app/routes/diagrams.py`, `backend/app/main.py`
  - `POST /api/diagrams`: upload image → return validated graph
  - `GET /api/diagrams/{diagram_id}`: get graph by ID
  - `GET /api/diagrams/sample/architecture`: cached demo graph
  - `GET /api/diagrams/{diagram_id}/nodes/{node_id}/neighbors`: query connections
  - `GET /api/health`: status
- Config: `.env.example`, `.gitignore`, `run_backend.py`
- Fixture: `backend/fixtures/sample_architecture_diagram.png`

## Tests
`python -m pytest backend/tests`: 15 passed in 2.10s. Ready Phase 2.