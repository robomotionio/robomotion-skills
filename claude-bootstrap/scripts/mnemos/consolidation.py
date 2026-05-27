"""Micro-consolidation -- rule-based, in-context, Tier 0 only.

Triggered when fatigue >= 0.40 (COMPRESS state). No LLM calls.
Target: <100ms execution time.

Actions:
    1. Compress 3 oldest ResultNodes (status=COMPRESSED, summary kept)
    2. Evict 1 cold ContextNode (weight < 0.2, no scope overlap)
    3. Decay weights on all evictable active nodes
"""

from __future__ import annotations

from .models import MnemoNode
from .store import MnemosStore


def micro_consolidate(
    store: MnemosStore,
    current_scope: str = '',
    max_compress: int = 3,
    max_evict: int = 1
) -> dict:
    """Run micro-consolidation pass. Rule-based, no LLM.

    Args:
        store: MnemosStore instance.
        current_scope: Current scope tag for eviction decisions.
        max_compress: Max ResultNodes to compress per pass.
        max_evict: Max ContextNodes to evict per pass.

    Returns:
        Stats: {compressed, evicted, decayed}.
    """
    stats = {'compressed': 0, 'evicted': 0, 'decayed': 0}

    # 1. Compress oldest active ResultNodes
    result_nodes = store.get_by_type('result', status='active')
    # Sort by created_at ascending (oldest first)
    result_nodes.sort(key=lambda n: n.created_at)

    compressed = 0
    for node in result_nodes:
        if compressed >= max_compress:
            break
        summary = _compress_result_node(node)
        store.compress_node(node.id, summary)
        compressed += 1
    stats['compressed'] = compressed

    # 2. Evict cold ContextNodes
    context_nodes = store.get_by_type('context', status='active')
    evicted = 0
    for node in context_nodes:
        if evicted >= max_evict:
            break
        if _should_evict(node, current_scope):
            store.evict_node(node.id)
            evicted += 1
    stats['evicted'] = evicted

    # 3. Decay weights on all evictable nodes
    decayed = store.decay_weights(factor=0.95)
    stats['decayed'] = decayed

    return stats


def _compress_result_node(node: MnemoNode) -> str:
    """Produce a summary from a ResultNode.

    Rule-based: first 200 chars of content as summary.
    """
    content = node.content.strip()
    if not content:
        return node.summary or '(empty result)'

    if len(content) <= 200:
        return content

    # Truncate at word boundary
    truncated = content[:200]
    last_space = truncated.rfind(' ')
    if last_space > 150:
        truncated = truncated[:last_space]
    return truncated + '...'


def _should_evict(node: MnemoNode, current_scope: str) -> bool:
    """Determine if a ContextNode should be evicted.

    Evict when:
        - activation_weight < 0.2
        - No scope_tag overlap with current scope
        - Access count is low (< 3)
    """
    if node.activation_weight >= 0.2:
        return False

    if node.access_count >= 3:
        return False

    if not current_scope:
        return True

    # Check scope overlap
    if node.scope_tags:
        for tag in node.scope_tags:
            if current_scope.startswith(tag) or tag.startswith(current_scope):
                return False

    return True
