# TactileCode — Project Summary

## What It Is
TactileCode converts architecture diagrams and flowcharts into interactive, keyboard-navigable graphs for blind and low-vision developers. Upload a PNG/JPG diagram → AI extracts nodes and edges → Navigate with arrow keys → Hear connections → Ask graph-backed questions.

## Problem Solved
Blind developers can't explore architecture diagrams in documentation, PRs, or technical specs. Screenshots are inaccessible. They're locked out of understanding system design and have to ask sighted colleagues for descriptions.

## Solution
- **AI Vision Extraction**: Gemma 4 vision model analyzes diagram images and extracts components (nodes), relationships (edges), labels, and directions as structured JSON
- **Accessible Navigation**: 100% keyboard-navigable React UI with screen reader support (ARIA labels, live regions, semantic HTML)
- **Graph-Backed Queries**: Ask questions like "What connects to the database?" or "Show me a path from client to backend" — answers come from the extracted graph, not guesses
- **Uncertainty Handling**: When the AI is unsure, it says so explicitly. No fabricated connections
- **Timeout Fallback**: If Gemma 4 takes >60 seconds, automatically falls back to demo data so you never get stuck waiting

## Technical Stack
**Backend**: Python, FastAPI, NetworkX, Pydantic, google-genai SDK, Graphviz for verification
**Frontend**: React, TypeScript, semantic HTML, CSS, ARIA for accessibility
**Model**: Gemma 4 vision model via official Google AI Studio (free tier)
**Testing**: pytest, manual NVDA screen reader testing

## Architecture
1. **Diagram Uploader** → Image validation → File storage
2. **Model Client Factory** → Tries Gemma 4 API first (with 60s timeout) → Falls back to Ollama → Falls back to Gemini → Falls back to mock
3. **Graph Extraction** → Gemma 4 analyzes image → Returns structured JSON (nodes, edges, confidence, uncertainty)
4. **Validation Pipeline** → Detects dangling edges, duplicate IDs, ambiguous connections
5. **NetworkX Conversion** → Builds queryable graph
6. **Frontend Graph UI** → Keyboard navigation tree → Query engine → Live announcements
7. **Query Engine** → Deterministic operations: neighbors, paths, dependencies, group summaries

## Key Features
✅ Real vision AI (Gemma 4) extracts diagrams
✅ 100% keyboard accessible (Tab, Arrow keys, Enter)
✅ Screen reader compatible (NVDA tested)
✅ Graph-backed queries (not hallucinated answers)
✅ Confidence scores and explicit uncertainty flags
✅ Smart timeout + fallback (60s limit with mock recovery)
✅ One-click diagram summary (component breakdown by group)
✅ NetworkX verification ensures graph integrity
✅ No API keys or secrets in repo (.env.example provided)

## User Journey
1. Open http://localhost:5173
2. Upload PNG/JPG architecture or flowchart diagram
3. Gemma 4 extracts components and connections (10-30 sec, or instant mock if timeout)
4. Navigate diagram using arrow keys and Tab
5. Screen reader announces focused node and its connections
6. Click "Generate Summary" → see component breakdown by group
7. Ask questions: "What connects to database?" → get instant answers
8. Export or share the extracted graph

## Real-World Impact
- **Documentation**: Embedded diagrams in tech specs become accessible immediately
- **Pull Reviews**: Blind engineers can review architecture changes independently
- **Meeting Access**: System design discussions don't require real-time descriptions
- **Onboarding**: New blind team members can explore codebase architecture at their own pace
- **Inclusion**: Removes the barrier that locked blind developers out of visual technical communication

## What's Working
✅ Backend API fully functional (upload, extract, query)
✅ Gemma 4 integration working with real vision AI
✅ Frontend UI keyboard navigable
✅ Graph extraction accurate (5 nodes, 4 edges from sample diagram)
✅ Query engine deterministic and correct
✅ Fallback mechanisms prevent timeouts
✅ Screen reader compatibility verified

## Build & Run
```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Then go to http://localhost:5173, upload a diagram, and navigate with keyboard + screen reader.

## Demo (15 minutes)
1. Upload diagram → show extraction
2. Navigate with arrow keys → show keyboard accessibility
3. Click "Generate Summary" → show instant text breakdown
4. Ask a query → show graph-backed answer
5. Explain impact for blind developers

## Next Steps (If Time Permits)
- Export as Mermaid diagram syntax
- Group-based summaries (show "Backend Tier" with 3 services, 5 edges)
- Caching for repeated diagrams
- Multi-diagram navigation (compare two architectures)
- Voice input for queries
- Browser extension for embedded diagrams

## Why This Matters
Accessibility isn't a feature. It's inclusion. Blind developers shouldn't have to ask "Can someone describe this diagram?" They should be able to explore it independently, understand it completely, and contribute to system design decisions with full agency.

TactileCode does that.

---

**Built for**: Hacktoberfest 2026 Hackathon
**Duration**: 1 day
**Team**: Solo build, open to collaboration
**License**: Open source (ready for contribution)
