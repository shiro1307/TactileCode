# Keyboard Navigation Guide for TactileCode

Complete guide to using TactileCode without a mouse, with or without a screen reader.

## Quick Reference

| Action | Key(s) |
|--------|---------|
| Show this help | **?** |
| Move focus to upload area | **Alt+U** |
| Navigate components | **↑ ↓** |
| Jump to first/last component | **Home** / **End** |
| Select component | **Enter** / **Space** |
| Move between panels | **Tab** / **Shift+Tab** |
| Execute query | **Enter** (when focused on button) |

---

## Detailed Workflow

### 1. Upload a Diagram

**Goal:** Get a diagram into the system

**Steps:**
1. Press **Tab** repeatedly until you hear: "Upload diagram" or "Upload area"
2. Press **Enter** to open file picker
3. Select a PNG or JPG file
4. Press **Enter** to upload

**Announcements:**
- "Upload started..."
- "Diagram processing..."
- "[Filename], [node count] components, [edge count] relationships"

**Troubleshooting:**
- If file picker doesn't open, ensure JavaScript is enabled
- Supported formats: PNG, JPG (max 10MB)
- If diagram fails to process, check backend is running (port 8000)

---

### 2. View Diagram Summary

**Goal:** Understand what was extracted

**Status After Upload:**
The screen reader announces:
```
Diagram Overview
Filename: my-architecture.png
Total Components: 12
Total Relationships: 15
Uncertainty: [High confidence] or [Explicit flags reported]
```

**Components with Low Confidence:**
If any component has <70% confidence, you'll hear:
```
Warning: Component [name], low confidence [X%]
```

---

### 3. Navigate Diagram Components

**Goal:** Explore the nodes in the graph

**Navigation:**
1. Press **Tab** until you reach "Diagram Components" list
2. Press **↓** to move to first component
3. Press **↓** / **↑** to navigate between components
4. **Home** jumps to first, **End** jumps to last
5. As you navigate, hear: "[Component name], [group], [X] outgoing, [Y] incoming"

**Example Announcement:**
```
API Gateway, infrastructure. 3 outgoing, 1 incoming. Press Enter to select.
```

**Selection:**
1. Navigate to desired component
2. Press **Enter** or **Space**
3. Details panel on right announces: "Selected [name], group [group]"

---

### 4. Inspect Component Connections

**Goal:** Understand what connects to/from a node

**View Details:**
1. Select a component (see step 3)
2. Details panel shows:
   - Component name and group
   - Confidence score
   - Any uncertainty warnings
   - Incoming connections (what points to this)
   - Outgoing connections (what this points to)

**Connections Announcement:**
```
Outgoing Connections (2)
  1. → Target Node (via HTTP request)
  2. → Database (via Query)

Incoming Connections (1)
  ← Source Node (from Client)
```

**Jump to Connected Node:**
1. Tab to "Jump" button for a connection
2. Press **Enter**
3. Focus moves to that node
4. Details update automatically

---

### 5. Use Query Builder

**Goal:** Ask graph-backed questions

**Queries Available:**
- Find Path Between Nodes
- Show Dependents (what depends on this?)
- Show Dependencies (what does this depend on?)
- Summarize Group (analyze a tier)
- Find Reachable Nodes (what can fail?)

**Steps:**
1. Press **Tab** to reach "Query Builder" panel (left side)
2. Tab to "Query Type" dropdown
3. Press **↓** or **↑** to select query type, then **Enter**
4. Tab to node/group selector
5. Select source node or group
6. Tab to "Execute" button
7. Press **Enter** to run query

**For Path Finding Query:**
```
1. Select "Find Path Between Nodes"
2. Tab to "Source Node"
3. Press **↓** to list, select node, **Enter**
4. Tab to "Target Node"
5. Press **↓** to list, select node, **Enter**
6. Tab to "Execute", press **Enter**
```

**Results Announcement:**
```
Query Results
Path found: [Node A] → [Node B] → [Node C]. 2 steps total.
```

**Navigate Results:**
- Results appear in a panel below query controls
- Tab through result nodes
- Click (or press Enter on) linked node names to jump

---

### 6. Query Examples

### Query: "What connects to the API Gateway?"

```
1. Tab to "Query Builder"
2. Select query type: "Show Dependents"
3. Select node: "API Gateway"
4. Execute

Result:
"3 components depend on API Gateway.
They are: Frontend, Mobile App, Backup Service."
```

### Query: "Is there a path from Frontend to Database?"

```
1. Tab to "Query Builder"
2. Select query type: "Find Path Between Nodes"
3. Select source: "Frontend"
4. Select target: "Database"
5. Execute

Result:
"Path found: Frontend → API Gateway → Backend → Database. 3 steps total."
```

### Query: "What's in the 'backend' group?"

```
1. Tab to "Query Builder"
2. Select query type: "Summarize Group"
3. Select group: "backend"
4. Execute

Result:
"Group 'backend' contains 4 component(s). 
2 internal connection(s), 3 external connection(s).
Components: Auth Service, User Service, Order Service, Search Service"
```

---

## Tab Order

The application is navigable in this order:

1. **Skip link** — Jump to main content (press Enter)
2. **Upload diagram** — File input
3. **Sample diagram button** — Load demo (if available)
4. **Diagram summary** — Overview after upload
5. **Query builder** — Query controls (left panel)
6. **Component list** — Navigation tree (middle panel)
7. **Component details** — Inspector panel (right panel)

Press **Tab** repeatedly to cycle through. **Shift+Tab** goes backward.

---

## Screen Reader Announcements

TactileCode announces state changes via live regions. You'll hear:

### On Upload
```
Diagram loaded: [Filename]
Components extracted: [N]
Relationships extracted: [M]
Ready for navigation
```

### On Navigation
```
[Component name], [group]. [N] outgoing, [M] incoming.
Confidence [X]%.
```

### On Selection
```
Selected [Component name].
[N] outgoing connections: [list]
[M] incoming connections: [list]
Confidence [X]%.
[Warnings if any]
```

### On Query Execution
```
Executing [query type]...
Query complete: [Result summary]
[Details with clickable results]
```

### On Error
```
Error: [Description]
Please check your input and try again.
```

---

## Troubleshooting

### "I don't hear anything"

**Solution:**
1. Ensure screen reader is running
2. In NVDA: Press Ctrl+Alt+N
3. In JAWS: Press Insert+Space, then B
4. Refresh page (F5)
5. Click in page and press Tab

### "Component list doesn't respond to arrow keys"

**Solution:**
1. Click or Tab into the component list
2. Ensure you see a focus box around a component
3. Then use ↑ ↓

### "Query dropdown doesn't open"

**Solution:**
1. Tab to dropdown
2. Press **↓** arrow (not Enter)
3. Use ↑ ↓ to navigate options
4. Press Enter to select

### "Can't find Jump button"

**Solution:**
1. Expand connections in detail panel
2. Tab through connections
3. "Jump" link should be after each connection

### "Upload button grayed out"

**Solution:**
1. Ensure you've selected a file
2. Try a different file (PNG/JPG, <10MB)
3. Check browser console (F12) for errors
4. Restart backend server

---

## Testing Checklist

Use this to verify accessibility works:

- [ ] Can upload file without mouse
- [ ] Upload status announced via screen reader
- [ ] Can navigate components with arrow keys
- [ ] Component info announced on focus
- [ ] Can select component with Enter
- [ ] Details panel updates announcement
- [ ] Can use query builder without mouse
- [ ] Query results announced
- [ ] Can jump to result node
- [ ] Can press ? for help
- [ ] Focus always visible (blue outline)
- [ ] Tab order makes sense
- [ ] Errors announced clearly

---

## Keyboard Shortcuts (Advanced)

Faster navigation for power users:

| Shortcut | Action |
|----------|--------|
| **Home** | First component |
| **End** | Last component |
| **/**  (forward slash) | Search components by name* |
| **Escape** | Close any open modal |
| **?** | Show keyboard help |

*Not yet implemented

---

## Best Practices

1. **Upload first** — Always upload a diagram before querying
2. **Use arrow keys** — More efficient than Tab for component navigation
3. **Read help** — Press ? if unsure
4. **Inspect before querying** — Navigate components first to understand structure
5. **Ask specific questions** — Use queries for precise information

---

## Support

If you encounter accessibility issues:

1. Open browser console (F12)
2. Reproduce the issue
3. Note what key you pressed and what happened
4. Include error message from console
5. Report with your screen reader name and version

---

## Screen Reader Specific Tips

### NVDA Users
- Press Insert+N for menu
- Insert+V for virtual buffer mode
- Insert+A for focus mode

### JAWS Users
- Press Insert+B for browse mode
- Insert+Z for menu
- F11 for settings

### VoiceOver Users (macOS)
- Vo=Control+Option
- Vo+U for rotor
- Vo+Right arrow to move

### TalkBack Users (Android)
- Swipe right to navigate
- Swipe up then right to activate

---

Last updated: October 24, 2024

**Built for everyone. Use any way you want.**
