"""Vector-based duplicate detection for search_prior_work query.

Tiered fallback:
  1. chromadb + sentence-transformers (best quality)
  2. TF-IDF cosine similarity via scikit-learn (no GPU needed)
  3. Exact substring matching (zero deps)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .store import ICPGStore

VECTORS_DIR = '.icpg'
TFIDF_CACHE = '.icpg/tfidf_cache.json'


class VectorStore:
    """Tiered vector search for ReasonNode deduplication."""

    def __init__(self, project_dir: str = '.'):
        self.project_dir = Path(project_dir).resolve()
        self.icpg_dir = self.project_dir / VECTORS_DIR
        self._backend = _detect_backend()

    def add_reason(self, reason_id: str, goal: str, scope: list[str]) -> None:
        """Index a ReasonNode for similarity search."""
        text = f'{goal} | scope: {", ".join(scope)}'

        if self._backend == 'chromadb':
            _chromadb_add(self.icpg_dir, reason_id, text)
        elif self._backend == 'tfidf':
            _tfidf_add(self.icpg_dir, reason_id, text)
        else:
            _exact_add(self.icpg_dir, reason_id, text)

    def search_similar(
        self, goal_text: str, threshold: float = 0.75, top_k: int = 5
    ) -> list[tuple[str, float]]:
        """Find similar ReasonNodes. Returns [(id, score), ...]."""
        if self._backend == 'chromadb':
            return _chromadb_search(
                self.icpg_dir, goal_text, threshold, top_k
            )
        elif self._backend == 'tfidf':
            return _tfidf_search(
                self.icpg_dir, goal_text, threshold, top_k
            )
        else:
            return _exact_search(self.icpg_dir, goal_text, threshold)

    def remove_reason(self, reason_id: str) -> None:
        """Remove a ReasonNode from the vector index."""
        if self._backend == 'chromadb':
            _chromadb_remove(self.icpg_dir, reason_id)
        elif self._backend == 'tfidf':
            _tfidf_remove(self.icpg_dir, reason_id)
        else:
            _exact_remove(self.icpg_dir, reason_id)


def _detect_backend() -> str:
    """Detect best available vector search backend."""
    try:
        import chromadb
        import sentence_transformers
        return 'chromadb'
    except ImportError:
        pass

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        return 'tfidf'
    except ImportError:
        pass

    return 'exact'


# --- ChromaDB backend ---

def _get_chroma_collection(icpg_dir: Path):
    import chromadb
    client = chromadb.PersistentClient(path=str(icpg_dir / 'chroma'))
    return client.get_or_create_collection(
        name='reasons',
        metadata={'hnsw:space': 'cosine'}
    )


def _chromadb_add(icpg_dir: Path, reason_id: str, text: str) -> None:
    col = _get_chroma_collection(icpg_dir)
    col.upsert(ids=[reason_id], documents=[text])


def _chromadb_search(
    icpg_dir: Path, query: str, threshold: float, top_k: int
) -> list[tuple[str, float]]:
    col = _get_chroma_collection(icpg_dir)
    if col.count() == 0:
        return []
    results = col.query(
        query_texts=[query],
        n_results=min(top_k, col.count())
    )
    pairs = []
    if results['ids'] and results['distances']:
        for rid, dist in zip(results['ids'][0], results['distances'][0]):
            # chromadb cosine distance: 0 = identical, 2 = opposite
            score = 1.0 - (dist / 2.0)
            if score >= threshold:
                pairs.append((rid, round(score, 3)))
    return pairs


def _chromadb_remove(icpg_dir: Path, reason_id: str) -> None:
    col = _get_chroma_collection(icpg_dir)
    try:
        col.delete(ids=[reason_id])
    except Exception:
        pass


# --- TF-IDF backend ---

def _tfidf_load(icpg_dir: Path) -> dict[str, str]:
    cache_path = icpg_dir / 'tfidf_cache.json'
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    return {}


def _tfidf_save(icpg_dir: Path, data: dict[str, str]) -> None:
    cache_path = icpg_dir / 'tfidf_cache.json'
    cache_path.write_text(json.dumps(data))


def _tfidf_add(icpg_dir: Path, reason_id: str, text: str) -> None:
    data = _tfidf_load(icpg_dir)
    data[reason_id] = text
    _tfidf_save(icpg_dir, data)


def _tfidf_search(
    icpg_dir: Path, query: str, threshold: float, top_k: int
) -> list[tuple[str, float]]:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    data = _tfidf_load(icpg_dir)
    if not data:
        return []

    ids = list(data.keys())
    texts = list(data.values())
    texts.append(query)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)

    query_vec = tfidf_matrix[-1]
    doc_vecs = tfidf_matrix[:-1]
    scores = cosine_similarity(query_vec, doc_vecs).flatten()

    pairs = [
        (ids[i], round(float(scores[i]), 3))
        for i in range(len(ids))
        if scores[i] >= threshold
    ]
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs[:top_k]


def _tfidf_remove(icpg_dir: Path, reason_id: str) -> None:
    data = _tfidf_load(icpg_dir)
    data.pop(reason_id, None)
    _tfidf_save(icpg_dir, data)


# --- Exact match backend ---

def _exact_load(icpg_dir: Path) -> dict[str, str]:
    cache_path = icpg_dir / 'exact_cache.json'
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    return {}


def _exact_save(icpg_dir: Path, data: dict[str, str]) -> None:
    cache_path = icpg_dir / 'exact_cache.json'
    cache_path.write_text(json.dumps(data))


def _exact_add(icpg_dir: Path, reason_id: str, text: str) -> None:
    data = _exact_load(icpg_dir)
    data[reason_id] = text.lower()
    _exact_save(icpg_dir, data)


def _exact_search(
    icpg_dir: Path, query: str, threshold: float
) -> list[tuple[str, float]]:
    data = _exact_load(icpg_dir)
    query_words = set(query.lower().split())
    if not query_words:
        return []

    pairs = []
    for rid, text in data.items():
        text_words = set(text.split())
        if not text_words:
            continue
        overlap = len(query_words & text_words)
        score = overlap / max(len(query_words), len(text_words))
        if score >= threshold:
            pairs.append((rid, round(score, 3)))

    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs


def _exact_remove(icpg_dir: Path, reason_id: str) -> None:
    data = _exact_load(icpg_dir)
    data.pop(reason_id, None)
    _exact_save(icpg_dir, data)
