# References & Further Reading

This page lists primary sources, community resources, and evaluation frameworks relevant to building and testing Claude Code skills. Because URLs for documentation and blog posts change frequently, each entry describes where to find the resource rather than providing a direct link that may become stale.

---

## Anthropic Research & Documentation

### BrowseComp: Eval Awareness Research

**Anthropic — BrowseComp paper and associated blog post**

Covers the problem of eval awareness: when AI models appear to have been optimized for (or trained on) specific evaluation benchmarks, leading to inflated scores that do not reflect real-world capability. Directly relevant to the risk of over-fitting skill descriptions to eval case wording. The research also discusses strategies for constructing evaluation sets that are robust to this effect.

*To find:* Search for "Anthropic BrowseComp eval awareness" or look in Anthropic's research publications index at anthropic.com/research.

---

### Demystifying Evals for AI Agents

**Anthropic — "Demystifying Evals for AI Agents" research article**

The primary source for the 8-step roadmap described in the Best Practices guide. Covers how to design evaluation pipelines for agentic systems, with specific attention to the challenges of evaluating multi-step tool use, handling non-determinism, and choosing between automatic and human-in-the-loop grading. Highly recommended reading before designing any serious eval set.

*To find:* Search for "Anthropic demystifying evals AI agents" or browse Anthropic's research blog at anthropic.com/research. The article is sometimes referenced under the title "Evaluating AI Agents."

---

### Claude Code Skill Best Practices

**Anthropic — Claude Code official documentation**

The authoritative reference for the Claude Code skill system: skill file format, registration, description writing guidelines, and the Skill tool invocation protocol. The eval framework described in this documentation is designed to complement and validate the recommendations in the official skill docs.

*To find:* Search for "Claude Code skills documentation" in the Claude Code help system (`/help`) or at the Anthropic developer documentation site (docs.anthropic.com). Look for sections on custom skills or skill development.

---

## Community Resources

### The Eval Loop: Testing Claude Code Skills

**mager.co — Blog post on building and iterating on Claude Code skill evals**

A practitioner's walkthrough of the eval loop: writing an initial eval set, running it, interpreting failures, and iterating on skill descriptions. Covers the tooling choices (built-in runner vs. promptfoo), common failure patterns discovered in the field, and practical tips for writing criteria that produce consistent judge grades. A useful companion to the official Anthropic documentation because it focuses on the day-to-day workflow rather than theory.

*To find:* Search for "mager.co Claude Code eval loop" or "mager.co skill evaluation." The post may also be found by searching "Claude Code skill eval tutorial site:mager.co."

---

## Evaluation Frameworks

### promptfoo

**promptfoo — Open-source LLM evaluation framework**

An open-source tool for evaluating LLM outputs. Supports test case authoring in YAML or JSON, multiple grading strategies (exact match, regex, LLM-as-judge, custom scripts), and comparison across models or prompt variants. Integrates with most LLM APIs including Anthropic. Well-suited for graduating beyond the built-in runner when you need larger case sets, statistical comparison, or CI/CD integration.

*To find:* The project is hosted on GitHub. Search for "promptfoo GitHub" or "promptfoo LLM evaluation." The documentation site is at promptfoo.dev (search for latest URL, as it may change).

---

### Braintrust

**Braintrust — Eval and observability platform**

A managed platform for running, storing, and analyzing LLM evaluations. Provides a web UI for viewing eval results, tracking score trends over time, and comparing experiments. Supports LLM-as-judge grading, human annotation workflows, and integration with CI pipelines. Well-suited for teams that need persistent history, regression alerts, and collaborative review of eval results.

*To find:* Search for "Braintrust AI eval platform" or "braintrustdata.com." The platform has both a free tier and paid plans for higher volume.

---

### LangSmith

**LangSmith — LLM application monitoring and evaluation**

A product from LangChain focused on tracing, monitoring, and evaluating LLM applications in production and development. Provides tools for logging LLM calls, inspecting intermediate steps in agent chains, running dataset-based evaluations, and annotating results. Particularly useful if your skill invokes multi-step chains or if you want to trace exactly what happened inside a skill execution for debugging.

*To find:* Search for "LangSmith LangChain" or "smith.langchain.com." Documentation is available at docs.smith.langchain.com (search for latest URL).

---

### Harbor

**Harbor — Local AI testing toolkit**

A toolkit for running and testing AI models locally, including support for self-hosted model inference and local evaluation pipelines. Useful for teams that need to run evaluations in air-gapped environments, want to test against locally hosted models, or want to reduce API costs during heavy eval iteration cycles. Less feature-rich than cloud platforms but highly controllable.

*To find:* Search for "Harbor local AI testing toolkit" or "Harbor AI GitHub." The project is open-source; look for it in the GitHub ecosystem under AI developer tooling.

---

## How to Stay Current

The AI evaluation tooling landscape changes quickly. When the resources above seem outdated:

1. Check the official Anthropic changelog and blog (anthropic.com/news) for updates to Claude Code and eval guidance.
2. Search the Claude Code community forums or Discord for recent discussions on eval patterns.
3. Check the GitHub repositories of promptfoo, Braintrust, and LangSmith for release notes — these projects iterate frequently and new features often address common pain points described in older documentation.
4. The mager.co blog post may have follow-up posts as the tooling matures; search the site for the latest entries on skill development.
