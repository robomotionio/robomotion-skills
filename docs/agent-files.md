# Agent context & memory files (Hermes Agent / OpenClaw model)

> Reference for skill authors: the durable, per-agent context/memory files the
> Robomotion **Hermes Agent** injects at runtime, and **where a skill should put
> durable output** instead of inventing filesystem paths.
>
> The Hermes Agent uses the **OpenClaw** memory convention (`SOUL.md`,
> `IDENTITY.md`, `USER.md`, `MEMORY.md`, `AGENT.md`). These are first-class,
> platform-managed, and injected into the system prompt — not ad-hoc files.

## The files (split by *subject*)

The model splits durable context by **what the file is about**:

| File | Subject | Holds | Who writes it | Size |
|---|---|---|---|---|
| `AGENT.md` | the **agent** | instructions / system prompt (the agent's job) | builder (Designer asset `assets/<node>/AGENT.md`); file wins | as needed |
| `SOUL.md` | the **agent** | personality / behavioral philosophy | builder | small |
| `IDENTITY.md` | the **agent** | identification / routing metadata | builder | small |
| `USER.md` | the **human** | who *the human user* is — name, timezone, language, expertise, communication prefs, things to avoid. Per-user in multi-user setups. | the human, or the agent over time | **concise** (~<500 words) |
| `MEMORY.md` | the **world / project** | **global project context + facts learned across sessions** | the agent (curated via the Memory tool/MemoryManager) | concise |

Key distinction authors get wrong: **`USER.md` is about the human, `MEMORY.md` is
about the world/project.** Facts about *a product, business, or domain* are
project context → **`MEMORY.md`**, never `USER.md`.

(OpenClaw defines more files, e.g. `HEARTBEAT.md`; Robomotion's Hermes Agent
bootstraps the five above.)

## How Robomotion wires them

- **Location:** under the per-agent `HERMES_HOME` =
  `~/.config/robomotion/agent/hermes/<workspace>/<robot>/<flow>/<agent-node>/`
  (`nodes/agent/_paths.py`). Persistent; in container mode it's bind-mounted **rw**
  at `/opt/robomotion/hermes-home` (`launcher/container.go`).
- **Sync:** the bootstrap files (`AGENT.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
  …) are copied from the flow repo's `assets/<node_guid>/` into `HERMES_HOME` on
  every message, so Designer edits take effect next run (`hermes_agent.py`).
- **Injection:** the Hermes `MemoryManager` surfaces `MEMORY.md` / `USER.md` into
  the agent's context each run — so anything stored there is **available to every
  active skill with no file read**.
- **Memory provider** (Designer → node `Memory` dropdown, `optMemoryProvider`):
  - `off` → no `MEMORY.md` / `USER.md`, no memory tool.
  - `builtin` (default) → always-on `MEMORY.md` + `USER.md` store under `HERMES_HOME`.
  - external (e.g. `supermemory`) → plugin on top of built-in (needs an API key).
- **Memory tool:** `_HERMES_INTERNAL_TOOLS` exposes `memory` — *"Read/write the
  agent's persistent memory store. Auto-enabled when Memory provider is on."*

## Two homes for what an agent produces

A skill that needs to persist something has exactly **two governed destinations** —
it must not invent a filesystem path:

| Output kind | Home | Why |
|---|---|---|
| **Durable cross-skill *context*** (facts other skills should know) | **Memory** (`MEMORY.md` via the memory tool) | auto-injected every run → consumers read it from context, **no path, no read step, no coupling**; persists per agent |
| **File *artifacts*** (generated CSV, image, code, reports) | the **agent workspace** `/workspace` | Robomotion designates it the cwd and *"where generated code, scratch files, and tool outputs land"*; sandboxed + persistent per agent |

Never: a hardcoded foreign path like `.agents/…` or `.claude/…` (those are other
tools' project-config conventions, not Robomotion's), and never a private
scratchpad file used as a side-channel between skills.

## Authoring rule

> **Durable cross-skill context → Memory (`MEMORY.md`). File artifacts → the agent
> workspace (`/workspace`). Skills never invent filesystem paths.**

Skills should also stay **self-contained**: if the context isn't present (Memory
off/empty), degrade gracefully — ask the user inline; don't hard-fail or assume
another skill ran first. (See the agentskills self-containment principle:
skills are independently useful, with no formal skill→skill dependencies.)

## Worked example: `product-marketing` (marketing-skills)

The upstream marketing collection has one *producer* skill, `product-marketing`,
that writes a foundational brief other skills read. Upstream stores it at
`.agents/product-marketing.md` (a Claude Code project-config convention) and 40
sibling skills read that path. In Robomotion that's the wrong layer **and** the
wrong location:

- It's **project context** (about the user's product), so it belongs in
  **`MEMORY.md`**, not a file — and certainly not in `USER.md` (that's the human).
- Storing it as an un-injected file forces every consumer to know a magic path and
  read it (tight coupling, invisible dependency).

**Correct shape in Robomotion:**
- `product-marketing` writes the brief to **Memory** (`MEMORY.md`) via the memory
  tool (or, for a large verbatim brief, a dedicated Designer-surfaced project-context
  doc injected like `AGENT.md`).
- Consumer skills **drop the file read** — the brief is already injected; they use
  it from context, and fall back to asking inline if it's absent.
- No producer→consumer filesystem edge remains.

## References

- Hermes/OpenClaw memory model: [LumaDock — Hermes memory architecture](https://lumadock.com/tutorials/hermes-memory-architecture-explained), [OpenClaw USER template](https://docs.openclaw.ai/reference/templates/USER), [OpenClaw workspace files](https://capodieci.medium.com/ai-agents-003-openclaw-workspace-files-explained-soul-md-agents-md-heartbeat-md-and-more-5bdfbee4827a)
- Self-containment / no formal skill deps: [agentskills best practices](https://agentskills.io/skill-creation/best-practices), [agentskills #100](https://github.com/agentskills/agentskills/issues/100), [#210](https://github.com/agentskills/agentskills/discussions/210)
- Robomotion code: `packages-main/src/hermes-agent/nodes/agent/hermes_agent.py` (bootstrap files, memory provider, `memory` tool), `nodes/agent/_paths.py` (`HERMES_HOME`, workspace), `launcher/container.go` (`/workspace` rw, cwd).
