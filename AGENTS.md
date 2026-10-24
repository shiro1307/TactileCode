# AGENTS.md — TactileCode

## 1. Project Overview

**TactileCode** converts architecture diagrams and flowcharts into structured, verified graphs that blind and low-vision developers can explore using a keyboard and screen reader.

### Core workflow

Diagram Image → Gemma 4 → Structured Graph → Verification → Accessible Navigation

### Primary objective

Build a functional, accessible MVP for a one-day hackathon. Prioritize correctness, accessibility, reliable graph extraction, and a smooth demonstration over unnecessary features.

### Target users

Blind and low-vision software developers who need to understand diagrams embedded in documentation, technical specifications, and engineering workflows.

---

## 2. Development Phases

Implement the project in four phases.

### Phase 1: Diagram Understanding and Graph Extraction

- Build an image-upload interface.
- Integrate Gemma 4 through a replaceable model-client interface.
- Use vision and structured function calling to extract nodes, edges, directions, labels, and confidence information.
- Store the extracted graph in a validated JSON representation.
- Convert the representation into a NetworkX graph.
- Handle malformed model responses and API errors gracefully.

**Acceptance criteria:**
- A user can upload a supported diagram image.
- The backend returns structured nodes and edges.
- The graph can be loaded into NetworkX.
- Missing, invalid, or ambiguous information is not silently invented.

### Phase 2: Graph Verification

- Validate node references and edge endpoints.
- Detect dangling edges, duplicate identifiers, and suspicious structural inconsistencies.
- Identify low-confidence elements.
- Support image cropping and targeted re-inspection by Gemma 4.
- Render the extracted graph with Graphviz for comparison against the original image.
- Preserve unresolved uncertainties in the graph and make them available to the frontend.

**Acceptance criteria:**
- Invalid graph references are detected.
- Uncertain connections are explicitly flagged.
- Verification does not automatically assume that every disconnected node or component is an error.
- The system can distinguish structural validation from visual correctness.
- Verification failures are reported without crashing the application.

### Phase 3: Accessible Navigation and Queries

- Build a simple React frontend.
- Display the graph as a keyboard-navigable semantic tree or equivalent accessible structure.
- Support keyboard-only interaction.
- Provide screen-reader announcements for focused nodes, connections, and uncertainty warnings.
- Implement graph-backed queries through deterministic tools.
- Support queries such as:
  - What connects to this node?
  - What depends on the database?
  - What path connects these two components?
  - Summarize this group of nodes.
- Never answer graph questions using unsupported assumptions about the original image.

**Acceptance criteria:**
- The main workflow works without a mouse.
- Focus movement and relationships are announced meaningfully.
- Queries operate on the extracted graph.
- Loading, error, empty, and uncertainty states are accessible.
- The interface does not depend on a canvas or visual positioning alone.

### Phase 4: Testing and Submission

- Test representative flowcharts, UML diagrams, and architecture diagrams.
- Test keyboard navigation and screen-reader behavior with NVDA when available.
- Build a small labeled benchmark if time permits.
- Compare baseline extraction with extraction plus verification.
- Include at least one failure case and explain how uncertainty handling responds.
- Cache a known-good response for the primary demo.
- Complete the README, setup instructions, environment template, and demo video.

**Acceptance criteria:**
- A fresh environment can run the project using the documented instructions.
- No API keys or secrets are committed.
- The primary demonstration works end to end.
- Known limitations and benchmark methodology are documented honestly.

---

## 3. Technology Stack

Use the following stack unless a technical constraint requires a change.

### Backend
- Python
- FastAPI
- NetworkX
- Graphviz
- Pydantic for request and response validation

### Model integration
- Gemma 4 through a model-client abstraction.
- Use the API or runtime supported by the actual model variant.
- Keep model-specific request formatting inside the model integration layer.
- Support structured tool calls when the selected model interface allows them.
- Never assume all Gemma 4 variants support identical vision or function-calling capabilities.

### Frontend
- React
- TypeScript
- Semantic HTML
- CSS
- Accessible keyboard interaction and ARIA where appropriate

### Testing
- pytest for backend tests
- Frontend testing tools where practical
- NVDA for manual screen-reader testing
- A small JSON-based labeled dataset for graph extraction evaluation

Avoid introducing additional frameworks unless they solve a concrete requirement.

---

## 4. Graph Data Contract

Use a consistent graph representation across the model client, backend, frontend, and tests.

A suggested JSON structure:

```json
{
  "nodes": [
    {
      "id": "api_gateway",
      "label": "API Gateway",
      "group": "infrastructure",
      "confidence": 0.96,
      "uncertainty": null
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "api_gateway",
      "target": "application_service",
      "direction": "forward",
      "label": "HTTP request",
      "confidence": 0.91,
      "uncertainty": null
    }
  ],
  "warnings": []
}
```

### Graph rules

- Every node must have a stable, unique identifier.
- Every edge must reference existing node identifiers.
- Represent direction explicitly.
- Preserve relationship labels when visible.
- Use normalized confidence values between 0 and 1 when confidence is available.
- Treat confidence as a model estimate, not a calibrated probability unless calibration has been evaluated.
- Represent uncertainty explicitly rather than converting unknown values into facts.
- Keep source image coordinates or crop metadata when available and useful for verification.
- Do not infer arrow direction solely from node order.
- Validate model-generated data before using it.

The schema may evolve, but changes must remain consistent across the backend, frontend, fixtures, and tests.

---

## 5. Model and Tool Design

Keep the model responsible for visual interpretation and ambiguous perception. Keep deterministic code responsible for graph integrity and graph operations.

### Suggested extraction tools

- `add_node(label, group, confidence)`
- `add_edge(source, target, direction, label, confidence)`
- `flag_uncertain(element_id, reason)`
- `crop_region(x, y, width, height)`

These names describe the intended application interface. Adapt their actual schemas to the selected model API.

### Suggested graph-query tools

- `get_node(node_id)`
- `get_neighbors(node_id)`
- `find_path(source_id, target_id)`
- `get_dependents(node_id)`
- `summarize_group(group_id)`
- `move_focus(node_id, direction)`

### Important rules

- Validate tool arguments before executing operations.
- Do not execute arbitrary code supplied by the model.
- Keep graph queries deterministic whenever possible.
- Distinguish missing relationships from confirmed negative relationships.
- Never fabricate a path when no path exists.
- Return a clear result when a requested node cannot be identified.
- Keep model retries bounded and handle API failures gracefully.
- Cache successful extraction results for the primary demonstration when appropriate.

---

## 6. Accessibility Requirements

Accessibility is a core product requirement, not a final polish task.

- Use semantic HTML elements.
- Ensure all essential functionality works with a keyboard.
- Maintain a visible keyboard focus indicator.
- Provide descriptive accessible names for controls.
- Announce important state changes through an appropriate live region.
- Avoid excessive or repetitive screen-reader announcements.
- Expose node labels, relationships, and uncertainty in understandable language.
- Do not communicate meaning through color alone.
- Provide accessible error messages and loading states.
- Ensure focus remains predictable after graph updates.
- Use a tree pattern only if its keyboard behavior and semantics are implemented correctly; otherwise, use a simpler accessible list or equivalent structure.
- Do not use `aria-activedescendant` without implementing the associated focus and active-item behavior correctly.

Test with a real screen reader when possible. Automated accessibility checks alone do not establish usability for blind users.

---

## 7. API and Error Handling

Keep the backend API small and predictable.

Suggested endpoints:

- `POST /api/diagrams` — upload and process a diagram.
- `GET /api/diagrams/{diagram_id}` — retrieve graph and processing status.
- `POST /api/diagrams/{diagram_id}/verify` — run verification.
- `POST /api/diagrams/{diagram_id}/query` — execute a graph-backed question.
- `GET /api/health` — check backend availability.

Adjust these endpoints to the chosen architecture; do not build unnecessary infrastructure for a one-day hackathon.

Requirements:

- Validate image type and size.
- Return structured error responses.
- Never expose API keys or internal stack traces to users.
- Set reasonable request and model-call timeouts.
- Prevent repeated retries from creating an endless processing loop.
- Keep temporary uploads under control and avoid retaining unnecessary user data.

---

## 8. Coding Standards

- Write readable, maintainable Python and TypeScript.
- Use type annotations and clear interfaces.
- Keep functions focused on one responsibility.
- Separate model integration, graph validation, graph queries, and API routing.
- Avoid giant components, monolithic route handlers, and duplicated logic.
- Use descriptive identifiers.
- Add comments for non-obvious decisions rather than narrating every line.
- Handle errors explicitly.
- Keep dependencies minimal.
- Do not replace working architecture with a new framework without a clear reason.
- Do not claim a feature works unless it has been implemented and tested.

---

## 9. Testing Strategy

### Backend tests

Cover:
- Valid graph creation.
- Duplicate node identifiers.
- Edges referencing nonexistent nodes.
- Missing or malformed model fields.
- Directed and undirected relationships where supported.
- Uncertain elements.
- Reachability and path queries.
- Missing-node queries.
- Model API failures.
- Invalid image uploads.

### Frontend tests

Cover:
- Image upload and processing states.
- Keyboard navigation.
- Focus management.
- Accessible announcements.
- Query results.
- Error and uncertainty states.

### Evaluation

Create a small hand-labeled dataset of diagrams and measure:
- Node precision, recall, and F1.
- Directed edge precision, recall, and F1.
- Verification outcomes and unresolved errors.
- Performance before and after targeted re-inspection.

Document the dataset size, annotation rules, and evaluation limitations. Never invent benchmark results.

---

## 10. Scope and Time Management

### P0 — Must ship
- Image upload.
- Gemma 4 integration.
- Structured graph extraction.
- NetworkX graph construction.
- Accessible keyboard navigation.
- One complete end-to-end workflow.

### P1 — Competitive differentiators
- Confidence and uncertainty flags.
- Targeted image cropping and re-inspection.
- Graph verification.
- Graph-backed natural-language queries.
- Small benchmark.

### P2 — Only if time remains
- Voice input.
- Mermaid export.
- Generated alt text.
- Browser extension.
- Synthetic-data fine-tuning.
- Large-scale benchmarking.

Do not start P2 work while a P0 requirement remains broken.

Reserve the final 25% of hackathon time for testing, README completion, and the demo video.

---

## 11. Security and Configuration

- Store credentials in environment variables.
- Include `.env.example` with placeholder values only.
- Add `.env` and other secret-bearing files to `.gitignore`.
- Validate uploaded files rather than trusting file extensions.
- Apply file-size limits.
- Avoid executing model-produced content as code.
- Keep logs free of API keys and unnecessary sensitive data.
- Do not commit real user diagrams or personal data without permission.

---

## 12. Instructions for AI Coding Agents

Before implementing a feature:

1. Inspect the existing repository and understand its structure.
2. Identify which development phase the task belongs to.
3. Reuse existing components and interfaces where appropriate.
4. Confirm actual Gemma 4 capabilities against the selected model documentation.
5. Define the expected inputs, outputs, and failure behavior.
6. Implement the smallest complete solution.
7. Add or update relevant tests.
8. Run available tests and report their actual results.
9. Update documentation when behavior or setup changes.

When a requirement is ambiguous, choose the simplest safe implementation consistent with this document. Ask for clarification when the ambiguity affects architecture, accessibility, data integrity, or external costs.

Do not rewrite unrelated files or add dependencies without justification. Do not claim tests passed when they were not run.

---

## 13. Definition of Done

The MVP is complete when a user can:

1. Upload an architecture diagram or flowchart.
2. Receive a structured graph extracted using Gemma 4.
3. Navigate nodes and relationships using only a keyboard and screen reader.
4. Ask a question whose answer is derived from the graph.
5. Hear when a connection is uncertain or could not be verified.
6. Complete the primary demo without relying on a live model call if the network fails.

**Product principle:** TactileCode must prefer an honest uncertainty statement over a confident but unsupported description of a diagram.
