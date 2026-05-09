---
name: excalidraw
summary: Generate hand-drawn diagrams as Excalidraw JSON. Optional upload to excalidraw.com for shareable links.
---

# Excalidraw

Create architecture diagrams, flowcharts, sequence diagrams, and concept maps as `.excalidraw` JSON files. No accounts, no API keys, no rendering libraries — just JSON. Files drag-and-drop onto [excalidraw.com](https://excalidraw.com) for viewing and editing, or upload via the bundled script for a shareable URL.

## Capabilities

- Generate `.excalidraw` files (JSON) the user can open or share
- Compose diagrams from primitives: rectangles, ellipses, diamonds, lines, arrows, text
- Upload a generated file to excalidraw.com (encrypted client-side) and return a shareable URL — no account required

## Usage

### 1. Generate the JSON

Build an array of Excalidraw element objects, wrap in the standard envelope, save with `write_file` (or `tee`):

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "robomotion-hermes-agent",
  "elements": [
    {
      "type": "rectangle",
      "id": "node1", "x": 100, "y": 100, "width": 200, "height": 80,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "roughness": 1, "seed": 1
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff" }
}
```

Save to `/workspace/diagrams/<name>.excalidraw`. The user can open it directly at excalidraw.com.

### 2. (Optional) Upload for a shareable URL

```sh
python3 ${SKILL_DIR}/scripts/upload.py /workspace/diagrams/architecture.excalidraw
# → https://excalidraw.com/#json=abc123,encryptionKeyHere
```

The file is encrypted client-side (AES-GCM) before upload; the encryption key is embedded in the URL fragment, so excalidraw.com's server never sees plaintext.

## When to use

- "Draw the architecture of this microservice setup"
- "Make a flowchart of the user signup flow"
- "Sequence diagram for the OAuth handshake"
- "Sketch a concept map of these design tradeoffs"

## When NOT to use

- For pixel-perfect technical illustrations (use a vector editor — Figma, Illustrator)
- For UML with strict notation enforcement (use PlantUML or Mermaid)
- For data-driven charts (use matplotlib / Recharts / Vega-Lite)

## Operating notes

- Element IDs must be unique within a diagram. Use short stable IDs (`node1`, `arrow1`); the editor preserves them.
- Coordinates are in screen pixels; positive Y is downward. A 1200×800 canvas is a good default.
- Hand-drawn aesthetic comes from `roughness` (0=clean, 1=normal, 2=heavy). Keep it consistent within a diagram.
- For arrows between two nodes, set `startBinding` / `endBinding` to the node IDs so the arrow stays attached when nodes move in the editor.
- The upload script's only dependency is `cryptography` (installed by `post-install.sh`). Pure-stdlib alternatives don't exist for AES-GCM.

## Attribution

The bundled `upload.py` is adapted from the [Nous Hermes Agent](https://github.com/NousResearch/hermes-agent) skill of the same name (MIT).
