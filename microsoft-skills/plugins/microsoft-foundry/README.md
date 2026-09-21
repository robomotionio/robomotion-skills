# Microsoft Foundry

**Foundry-platform fluency for any language.** Skills teach the model the mental model + non-obvious gotchas, then direct it to discover current API surface via Foundry MCP (`mcp.ai.azure.com`), Microsoft Docs MCP, and `azd ai agent`. No baked-in stale SDK syntax — concepts in, fresh code out.

## Install

```bash
# Copilot CLI
/plugin marketplace add microsoft/skills
/plugin install microsoft-foundry@skills
```

```bash
# npx
npx skills add microsoft/skills --skill microsoft-foundry
```

## What You Get

### MCP Servers

The plugin bundles three MCP servers that activate automatically on install:

| Server | Purpose |
|--------|---------|
| **Azure MCP** | Manage Azure resources, deployments, and infrastructure from your editor. 40+ services. |
| **Foundry MCP** | Foundry-native operations at `mcp.ai.azure.com` -- model catalog, agents, toolboxes, knowledge bases, evals. |
| **Microsoft Docs** | Search Microsoft Learn in real-time so the agent always uses current Foundry/SDK patterns. |

### Skills

One orchestrator routes intent to ten language-agnostic sub-skills. Each sub-skill teaches the platform mental model and gotchas, then directs to the appropriate discovery surface for current syntax.

| Skill | What It Covers |
|-------|---------------|
| `microsoft-foundry` | **Orchestrator.** Maps user intent (build a hosted agent, curate a toolbox, ground on docs, set up evals, govern tools, personalize, orchestrate) onto the right sub-skill and the right discovery surface (Microsoft Docs MCP, Foundry MCP, `azd ai agent`, `az`). |
| `foundry-projects-resources` | Provision Foundry resources and projects, configure project connections (key-auth, OAuth, managed identity, agent identity), standard vs private-network agent infrastructure, Azure auth via `DefaultAzureCredential` / `ManagedIdentityCredential`. |
| `foundry-models` | Discover, deploy, and manage models. Preset vs customized deployments, capacity discovery across regions, quota management, PTU vs pay-as-you-go, RAI policy on model deployments. |
| `foundry-hosted-agents` | Build, deploy, and manage hosted agents on the refreshed preview. Responses + Invocations protocols, `agent.yaml`, `azd ai agent`, ResponsesAgentServerHost / InvocationAgentServerHost, sessions, per-agent Microsoft Entra identity, dedicated endpoints. |
| `foundry-toolboxes` | Curate intent-based Toolboxes (preview) — a single MCP-compatible endpoint bundling 9 tool types: MCP, Web Search, Azure AI Search, Code Interpreter, File Search, OpenAPI, A2A, Browser Automation, Computer Use. Build once, consume everywhere. |
| `foundry-workflows` | Multi-agent orchestration. When to use a declarative workflow vs an A2A tool call vs the Connected Agents pattern, plus Microsoft Agent Framework workflow patterns. Author, visualize, and test. |
| `foundry-iq-knowledge-bases` | Foundry IQ knowledge bases (preview) — multi-source, permission-aware grounding. Connect Blob/SharePoint/OneLake/web sources, use the agentic retrieval pipeline (decomposition + parallel search + reranking), expose via MCP to agents. |
| `foundry-managed-skills` | SKILL.md as a Foundry-side resource (preview). Author behavioral guidelines once, store centrally via the Skills REST API, download into hosted agent containers as additional session instructions. Decouples policy from code. |
| `foundry-memory` | Long-term memory stores (preview) for personalized agents across sessions. User profile vs chat summary memory, memory search tool vs memory store APIs, scoping, prompt-injection / memory-corruption risks, retention. |
| `foundry-observability` | Trace, monitor, and evaluate hosted agents end-to-end. OpenTelemetry GenAI traces in App Insights via KQL, eval-trace correlation, `azd ai agent monitor`, dataset curation from production traces, built-in quality + safety/RAI evaluators, batch evals, regression detection. |
| `foundry-governance` | Govern agent fleets at scale via the Foundry Control Plane and AI Gateway. Tool catalog visibility, MCP routing/policy, RBAC and agent identity, third-party tool risk, RAI policies on model deployments, transparency notes for production rollout. |

### Companion Skills

Foundry agents commonly call into adjacent Azure SDKs. Those skills live in their **language plugins** — install the matching `azure-sdk-*` plugin for SDK-specific guidance:

| Capability | Skills | Plugin |
|------------|--------|--------|
| **AI Search** (vector, hybrid, agentic retrieval) | `azure-search-documents-py`, `azure-search-documents-dotnet`, `azure-search-documents-ts` | `azure-sdk-python` / `-dotnet` / `-typescript` |
| **VoiceLive** (real-time voice over WebSocket) | `azure-ai-voicelive-py`, `azure-ai-voicelive-dotnet`, `azure-ai-voicelive-ts`, `azure-ai-voicelive-java` | `azure-sdk-python` / `-dotnet` / `-typescript` / `-java` |
| **Content Safety** (harmful content detection) | `azure-ai-contentsafety-py`, `azure-ai-contentsafety-ts`, `azure-ai-contentsafety-java` | `azure-sdk-python` / `-typescript` / `-java` |
| **M365 Agents** (Teams / Copilot Studio) | `m365-agents-py`, `m365-agents-dotnet`, `m365-agents-ts` | `azure-sdk-python` / `-dotnet` / `-typescript` |
| **Azure AI Projects SDK** (project client + low-level CRUD) | `azure-ai-projects-py`, `azure-ai-projects-dotnet`, `azure-ai-projects-ts`, `azure-ai-projects-java` | `azure-sdk-python` / `-dotnet` / `-typescript` / `-java` |
| **Microsoft Agent Framework** (persistent Azure agents) | `agent-framework-azure-ai-py` | `azure-sdk-python` |

This plugin stays Foundry-platform focused; install language plugins alongside it for SDK depth.

## Prerequisites

- **Azure account** with an AI Foundry project ([create one](https://learn.microsoft.com/azure/ai-foundry/how-to/create-projects))
- **Azure CLI** authenticated (`az login`)
- **Node.js 18+** (for the Azure MCP server)
- **`azd` extension for hosted agents:** `azd ext install azure.ai.agents`

## Authentication

Foundry uses Microsoft Entra. Authenticate via Azure CLI:

```bash
az login                  # for az + Azure MCP + DefaultAzureCredential locally
azd auth login            # for hosted-agent deploys via `azd ai agent`
```

In code, prefer `DefaultAzureCredential` for local dev and `ManagedIdentityCredential` in production (hosted agents, App Service, Container Apps, AKS).

Set your Foundry project endpoint:

```bash
export AZURE_AI_PROJECT_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project>"
```

## Quick Start

After installing the plugin, your coding agent routes intent through the orchestrator to the right sub-skill:

```
"Provision a Foundry project and a model deployment"
  -> foundry-projects-resources + foundry-models

"Deploy a hosted agent with the Responses protocol"
  -> foundry-hosted-agents (azd ai agent + agent.yaml)

"Curate a toolbox with Web Search + AI Search + an MCP server"
  -> foundry-toolboxes (single MCP endpoint, versioned)

"Ground my agent on our SharePoint knowledge with permission trimming"
  -> foundry-iq-knowledge-bases (agentic retrieval + ACL-aware)

"Set up tracing, batch evals, and a regression alert"
  -> foundry-observability (App Insights KQL + evaluators)

"Centrally govern which MCP tools my agent fleet can call"
  -> foundry-governance (Foundry Control Plane + AI Gateway)
```

## Plugin Structure

```
microsoft-foundry/
  .claude-plugin/
    plugin.json                       # Plugin manifest
  .mcp.json                           # Azure MCP + Foundry MCP + Microsoft Docs MCP
  README.md
  skills/
    microsoft-foundry/                # Orchestrator — routes intent to sub-skills
    foundry-projects-resources/       # Resources, projects, connections, auth
    foundry-models/                   # Deploy, capacity, quota, RAI policy
    foundry-hosted-agents/            # Responses + Invocations, agent.yaml, azd
    foundry-toolboxes/                # Intent-based toolboxes (9 tool types)
    foundry-workflows/                # Workflow vs A2A vs Connected Agents
    foundry-iq-knowledge-bases/       # Foundry IQ + agentic retrieval
    foundry-managed-skills/           # SKILL.md as a Foundry resource
    foundry-memory/                   # Long-term memory stores
    foundry-observability/            # Tracing + KQL + evals + RAI evals
    foundry-governance/               # Control Plane + AI Gateway + RBAC
```

Skills are symlinked to canonical sources in the `azure-skills` plugin to maintain a single source of truth.

## Doctrine: Concepts → Discover

Foundry surfaces evolve fast. Skills that bake in SDK syntax go stale and produce broken code.

This plugin takes the opposite approach:

- **Concepts in skills.** Each sub-skill teaches the mental model (what a toolbox *is*, why memory has prompt-injection risk, how Responses differs from Invocations) and the non-obvious gotchas (preview header flags, capacity-region mismatches, ACL trimming caveats).
- **Discover for syntax.** Skills direct the model to the live surface for current API shape:
  - **Microsoft Docs MCP** — official Learn docs, always fresh
  - **Foundry MCP** (`mcp.ai.azure.com`) — Foundry-native operations
  - **`azd ai agent`** — hosted agent build/deploy/monitor
  - **`az` CLI** — Azure resource management

The result: stable skills + always-current code.

## License

MIT
