---
name: "figma-implement-design"
description: "Translate Figma nodes into production-ready code with 1:1 visual fidelity using the Figma MCP workflow (design context, screenshots, assets, and project-convention translation)."
---

# Implement Design

## Overview
Structured workflow for translating Figma designs into production-ready code with pixel-perfect accuracy. Ensures consistent integration with the Figma MCP server, proper use of design tokens, and 1:1 visual parity.

## Required Workflow
1. **Get Node ID** - Parse from Figma URL to extract fileKey and nodeId.
2. **Fetch Design Context** - Run `get_design_context` for layout, typography, colors, components.
3. **Capture Visual Reference** - Run `get_screenshot` as source of truth.
4. **Download Assets** - Download images, icons, SVGs from Figma MCP.
5. **Translate to Project Conventions** - Map Figma output to your framework, design tokens, and components.
6. **Achieve 1:1 Visual Parity** - Use design tokens, avoid hardcoded values, follow WCAG.
7. **Validate Against Figma** - Compare layout, typography, colors, interactive states, responsive behavior.

## Key Principles
- Treat Figma MCP output as a representation of design, not final code style.
- Reuse existing components instead of duplicating functionality.
- When conflicts arise between design system tokens and Figma specs, prefer design system tokens.
- Always start with context - never implement based on assumptions.
