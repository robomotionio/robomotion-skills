---
name: arxiv
summary: Search and download academic papers from arXiv. Ships a stdlib Python CLI.
---

# arXiv

Search arXiv for academic papers, fetch metadata, and download PDFs. arXiv is open access — no API key, no login.

The skill ships `scripts/search_arxiv.py`, a stdlib-only CLI that wraps the arXiv API and prints clean Markdown-formatted results. Use it when the user asks for recent research on a topic, wants citation details, or needs PDFs to summarize.

## Capabilities

- Keyword search across title, abstract, author, category
- Author-scoped search (`--author "Yann LeCun"`)
- Category-scoped search (`--category cs.LG`)
- Fetch metadata for one or more paper IDs
- Sort by relevance, submission date, or last update

## Usage

```sh
python3 ${SKILL_DIR}/scripts/search_arxiv.py "GRPO reinforcement learning" --max 5
python3 ${SKILL_DIR}/scripts/search_arxiv.py --author "Yann LeCun" --max 5
python3 ${SKILL_DIR}/scripts/search_arxiv.py --category cs.AI --sort date --max 10
python3 ${SKILL_DIR}/scripts/search_arxiv.py --id 2402.03300
```

For PDF download, the URL pattern is `https://arxiv.org/pdf/<id>.pdf` — `curl -L -o /workspace/arxiv/<id>.pdf https://arxiv.org/pdf/<id>.pdf` so the agent persists files across iterations.

## When to use

- "Find recent papers on retrieval-augmented generation"
- "Get the abstract of arXiv:2401.12345"
- "Download the PDF for the latest survey on diffusion models"
- "Who is publishing on quantum error correction lately?"

## When NOT to use

- For non-arXiv venues (NeurIPS papers without a preprint, journal articles behind paywalls — try `crossref` or `semantic-scholar` first)
- For literature synthesis spanning hundreds of papers — query arXiv to get the candidate list, then summarize iteratively

## Operating notes

- IDs come in two forms: `2401.12345` (post-2007) and `cs.LG/0701001` (legacy). Both work.
- arXiv is unauthenticated and rate-limited per IP. Back off on 429. Don't issue more than one request every ~3 seconds in tight loops.
- Categories matter for filtering: `cs.LG` (machine learning), `cs.CL` (NLP), `stat.ML` (statistical ML), `cs.AI` (general AI). Use `--category` to avoid noise from unrelated fields.
- The `search_arxiv.py` CLI uses only Python's stdlib (`urllib`, `xml.etree`) — no `pip install` needed.

## Attribution

The bundled `search_arxiv.py` is adapted from the [Nous Hermes Agent](https://github.com/NousResearch/hermes-agent) skill of the same name (MIT).
