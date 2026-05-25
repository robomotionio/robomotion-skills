---
name: obsidian
version: 1.0.0
summary: Filesystem-first Obsidian vault work — read, list, search, create, append, and link notes.
tags: ["obsidian", "notes", "markdown", "note-taking"]
---

# Obsidian

Read and edit an Obsidian vault directly on the robot's filesystem using the agent's file tools (`read_file`, `write_file`, `patch`, `search_files`). A vault is just a folder of Markdown files, so no API and no token are involved.

## Capabilities

- Read a note with line numbers and pagination
- List notes (all, or within a subfolder)
- Search by filename or by note content (regex)
- Create notes and append to existing ones
- Make targeted, anchored edits
- Link related notes with `[[wikilinks]]`

## Resolving the vault path

Resolve a concrete absolute path before touching files:

1. If `OBSIDIAN_VAULT_PATH` is set, use it.
2. Otherwise fall back to `~/Documents/Obsidian Vault`.

File tools do **not** expand shell variables. Never pass `$OBSIDIAN_VAULT_PATH` to `read_file`/`write_file`/`patch`/`search_files` — resolve it first (via `terminal` if needed) and pass the literal absolute path. Vault paths often contain spaces, which is one more reason to use file tools over shell commands. Once the path is known, switch back to file tools.

## Usage

- **Read a note:** `read_file` with the absolute path. Prefer it over `cat` — you get line numbers and pagination.
- **List notes:** `search_files` with `target: "files"`, `pattern: "*.md"` under the vault path (or a subfolder path). Prefer it over `ls`/`find`.
- **Search filenames:** `search_files` with `target: "files"` and a filename `pattern`.
- **Search content:** `search_files` with `target: "content"`, the regex as `pattern`, and `file_glob: "*.md"` to restrict to notes.
- **Create a note:** `write_file` with the absolute path and full Markdown. Prefer it over shell heredocs/`echo` (avoids quoting issues, returns structured results).
- **Append:** read with `read_file`, then `patch` an anchored insert after a stable heading/block — or `write_file` the whole note when that's clearer than a fragile patch.
- **Targeted edits:** `patch` when current content gives stable context.
- **Wikilinks:** link related notes with `[[Note Name]]` when creating or editing.

## When to use

- "What's in my 'Daily/2026-05-25' note?"
- "Create a meeting note and link it to [[Project Apollo]]"
- "Search my vault for every note mentioning 'retro'"
- "Append today's decisions under the '## Decisions' heading"

## When NOT to use

- Anything requiring the Obsidian app's plugins, graph view, or sync — this is plain filesystem access, not the running app
- Non-Markdown knowledge bases or note systems behind an API (use the matching API skill)

## Operating notes

- **This is a host-mode / filesystem skill.** It needs the robot to have direct access to the vault folder. It ships no scripts and no `post-install.sh`, so on its own it runs the agent in host mode where the real vault is reachable. If another active skill forces container mode, the vault folder must be made available inside the container (bind-mounted) or these paths won't resolve.
- `OBSIDIAN_VAULT_PATH` is **optional** — there's a documented fallback — so it is declared in `env.optional`, not `env.required`. The Designer surfaces it as a non-mandatory binding and the launcher injects it when bound, but an empty value never blocks the run. Set it in the Designer's Environment tab only if your vault lives outside the default location.
- Prefer file tools over shell text rewriting throughout — they handle spaces in paths and return structured results.

## Attribution

Adapted from the [Nous Hermes Agent](https://github.com/NousResearch/hermes-agent) `obsidian` skill (MIT).
