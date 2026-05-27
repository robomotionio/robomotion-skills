"""
Tests for scripts/render_page.py.

Focus areas:
  - SPA heuristic (covers React/Next/Vue/Nuxt/Svelte/Astro shells + the
    thin-body fallback tuned against the example.com false-positive).
  - Mode dispatch (never / auto / always) without spinning up Chromium.
  - SSRF pre-flight delegation to url_safety.
  - Defensive returns for invalid mode / invalid viewport / raw-fetch
    failure / Playwright-missing.
  - Content extraction graceful degradation when trafilatura / htmldate
    aren't installed.

Tests that would launch Chromium are skipped automatically when
Playwright is not available in the test environment. The skip marker
documents the limitation so CI shows "skipped" rather than "failed".
"""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

_SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import render_page  # noqa: E402


# ---------------------------------------------------------------------------
# _is_spa: SPA shell detector
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "html",
    [
        # Empty input is treated as "render to be safe".
        "",
        # React CRA / Vite / Remix
        '<html><body><div id="root"></div></body></html>',
        # Next.js
        '<html><body><div id="__next"><div></div></div></body></html>',
        # Vue / Generic JS apps
        '<html><body><div id="app"></div></body></html>',
        # Nuxt
        '<html><body><div id="__nuxt"></div></body></html>',
        # Svelte
        '<html><body><div data-svelte-h="abc"></div></body></html>',
        # Astro islands
        '<html><body><astro-island uid="x"></astro-island></body></html>',
        # noscript banners
        '<html><body><noscript>You need to enable JavaScript to run this app.</noscript></body></html>',
        # Thin body (<100 chars text)
        "<html><body><h1>Hi</h1></body></html>",
    ],
)
def test_is_spa_positive(html: str) -> None:
    assert render_page._is_spa(html) is True


@pytest.mark.parametrize(
    "html",
    [
        # Rich content page.
        "<html><body><article>"
        + ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 5)
        + "</article></body></html>",
        # example.com-style minimal informational page (~125 chars body) —
        # the threshold was specifically tuned not to flag this.
        '<html><body><div><h1>Example Domain</h1>'
        '<p>This domain is for use in illustrative examples in documents. '
        'You may use this domain in literature without prior coordination '
        'or asking for permission.</p>'
        '<p><a href="https://www.iana.org/domains/example">More information...</a></p>'
        '</div></body></html>',
    ],
)
def test_is_spa_negative(html: str) -> None:
    assert render_page._is_spa(html) is False


# ---------------------------------------------------------------------------
# render_page — argument validation
# ---------------------------------------------------------------------------


def test_render_page_rejects_invalid_mode() -> None:
    result = render_page.render_page("https://example.com/", mode="banana")
    assert result["error"] and "Invalid mode" in result["error"]
    assert result["content"] is None


def test_render_page_rejects_invalid_viewport() -> None:
    result = render_page.render_page("https://example.com/", viewport="hologram")
    assert result["error"] and "Invalid viewport" in result["error"]


# ---------------------------------------------------------------------------
# render_page — SSRF pre-flight delegation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "http://10.0.0.7/",
        "http://169.254.169.254/latest/meta-data/",
        "http://2130706433/",          # obfuscated 127.0.0.1
        "https://metadata.google.internal./",  # FQDN bypass
    ],
)
def test_render_page_blocks_ssrf(url: str) -> None:
    result = render_page.render_page(url, mode="never")
    assert result["error"], f"expected error for {url}"
    assert result["error"].startswith("url_safety:")
    assert result["content"] is None


# ---------------------------------------------------------------------------
# render_page — raw mode (mode='never') is the cheap, network-touching path
# ---------------------------------------------------------------------------


def test_render_page_never_mode_against_example_com() -> None:
    """Single live-network check. example.com is the canonical IETF-reserved
    test target — stable, public, low-traffic, no auth required."""
    result = render_page.render_page("https://example.com/", mode="never")
    assert result["error"] is None
    assert result["status_code"] == 200
    assert result["mode_used"] == "raw"
    assert result["is_spa"] is False  # tuned threshold passes example.com
    assert result["render_engine"] is None
    assert result["content"] is not None
    assert "Example Domain" in result["content"]


# ---------------------------------------------------------------------------
# render_page — auto mode decision logic (mocked, no real network for SPA path)
# ---------------------------------------------------------------------------


def _fake_response(text: str, status: int = 200, url: str = "https://x.example/"):
    return SimpleNamespace(
        text=text, status_code=status, headers={"Content-Type": "text/html"},
        url=url, history=[],
    )


def _mock_validate_strict(url: str) -> tuple[str, str]:
    """Skip the real DNS resolution that validate_url_strict does."""
    return (url, "1.2.3.4")


def test_render_page_auto_stays_raw_for_static_html() -> None:
    """auto mode + non-SPA raw HTML → no Playwright invocation."""
    rich_html = "<html><body>" + ("hello world. " * 20) + "</body></html>"
    with patch.object(render_page, "validate_url_strict", side_effect=_mock_validate_strict), \
         patch.object(render_page, "safe_requests_get",
                      return_value=_fake_response(rich_html)):
        result = render_page.render_page("https://safe.example/", mode="auto")
    assert result["error"] is None
    assert result["mode_used"] == "raw"
    assert result["is_spa"] is False
    assert result["render_engine"] is None


def test_render_page_never_mode_skips_render_even_for_spa_shell() -> None:
    spa_html = '<html><body><div id="root"></div></body></html>'
    with patch.object(render_page, "validate_url_strict", side_effect=_mock_validate_strict), \
         patch.object(render_page, "safe_requests_get",
                      return_value=_fake_response(spa_html)):
        result = render_page.render_page("https://app.example/", mode="never")
    assert result["error"] is None
    assert result["mode_used"] == "raw"
    assert result["is_spa"] is True  # detected, but mode says don't render
    assert result["render_engine"] is None


def test_render_page_always_mode_errors_when_playwright_missing() -> None:
    """When Playwright is uninstalled, always-mode returns a clear error."""
    rich_html = "<html><body>" + ("a" * 1000) + "</body></html>"
    with patch.object(render_page, "validate_url_strict", side_effect=_mock_validate_strict), \
         patch.object(render_page, "safe_requests_get",
                      return_value=_fake_response(rich_html)), \
         patch.object(render_page, "sync_playwright", None):
        result = render_page.render_page("https://x.example/", mode="always")
    assert result["error"] is not None
    assert "playwright" in result["error"].lower()


def test_render_page_auto_errors_for_spa_when_playwright_missing() -> None:
    spa_html = '<html><body><div id="__next"></div></body></html>'
    with patch.object(render_page, "validate_url_strict", side_effect=_mock_validate_strict), \
         patch.object(render_page, "safe_requests_get",
                      return_value=_fake_response(spa_html)), \
         patch.object(render_page, "sync_playwright", None):
        result = render_page.render_page("https://app.example/", mode="auto")
    assert result["error"] is not None
    assert "playwright" in result["error"].lower()


def test_render_page_raw_fetch_failure_surfaces_clean_error() -> None:
    """When safe_requests_get raises, render_page returns an informative
    error rather than crashing."""
    import requests

    with patch.object(render_page, "validate_url_strict", side_effect=_mock_validate_strict), \
         patch.object(render_page, "safe_requests_get",
                      side_effect=requests.exceptions.ConnectionError("nope")):
        result = render_page.render_page("https://x.example/", mode="auto")
    assert result["error"] is not None
    assert "raw fetch failed" in result["error"]


# ---------------------------------------------------------------------------
# render_page — content-extraction graceful degradation
# ---------------------------------------------------------------------------


def test_render_page_extraction_skips_when_trafilatura_missing() -> None:
    rich_html = "<html><body>" + ("hello world. " * 20) + "</body></html>"
    with patch.object(render_page, "validate_url_strict", side_effect=_mock_validate_strict), \
         patch.object(render_page, "safe_requests_get",
                      return_value=_fake_response(rich_html)), \
         patch.object(render_page, "trafilatura", None), \
         patch.object(render_page, "find_date", None):
        result = render_page.render_page("https://x.example/", mode="never",
                                         extract_content=True)
    assert result["error"] is None
    assert result["extracted_text"] is None
    assert result["publication_date"] is None
    # Core fields still populated.
    assert result["content"] is not None


def test_render_page_extraction_disabled_by_flag() -> None:
    rich_html = "<html><body>" + ("hello world. " * 20) + "</body></html>"
    with patch.object(render_page, "validate_url_strict", side_effect=_mock_validate_strict), \
         patch.object(render_page, "safe_requests_get",
                      return_value=_fake_response(rich_html)):
        result = render_page.render_page("https://x.example/", mode="never",
                                         extract_content=False)
    assert result["error"] is None
    assert result["extracted_text"] is None
    assert result["publication_date"] is None


# ---------------------------------------------------------------------------
# render_page — result-shape contract
# ---------------------------------------------------------------------------


def test_render_page_result_dict_has_all_documented_fields() -> None:
    """Every caller (8 subagents) destructures this dict; the shape is the API."""
    rich_html = "<html><body>" + ("hello world. " * 20) + "</body></html>"
    with patch.object(render_page, "validate_url_strict", side_effect=_mock_validate_strict), \
         patch.object(render_page, "safe_requests_get",
                      return_value=_fake_response(rich_html)):
        result = render_page.render_page("https://x.example/", mode="never")
    expected_fields = {
        "url", "status_code", "content", "raw_content", "is_spa",
        "extracted_text", "publication_date", "accessibility_tree",
        "headers", "redirect_chain", "console_errors", "render_engine",
        "render_ms", "mode_used", "error",
    }
    assert set(result.keys()) == expected_fields
