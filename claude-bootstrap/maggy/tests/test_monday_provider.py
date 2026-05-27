"""Tests for Monday.com provider — IssueTrackerProvider impl."""

from __future__ import annotations

import pytest

from maggy.providers.monday import MondayProvider


@pytest.fixture()
def provider():
    return MondayProvider(
        api_token="test-token", board_id="18391076058",
    )


def test_provider_name(provider):
    assert provider.provider_name() == "monday"


def test_to_task_maps_fields(provider):
    """Monday item dict maps to Task dataclass."""
    item = {
        "id": "123", "name": "Fix login",
        "column_values": [
            {"id": "status", "text": "Working on it"},
            {"id": "person", "text": "Ali"},
        ],
        "url": "https://monday.com/123",
        "created_at": "2025-01-01",
        "updated_at": "2025-01-02",
    }
    task = provider._to_task(item)
    assert task.id == "123"
    assert task.title == "Fix login"
    assert task.status == "Working on it"
    assert task.assignee == "Ali"


@pytest.mark.asyncio()
async def test_list_tasks_parses_items(provider, monkeypatch):
    """list_tasks returns Task objects from API response."""
    import httpx

    class FakeResp:
        status_code = 200
        def json(self):
            return {"data": {"boards": [{"items_page": {
                "items": [
                    {"id": "1", "name": "Task A",
                     "column_values": [], "url": "",
                     "created_at": "", "updated_at": ""},
                ],
            }}]}}

    async def fake_post(self, url, **kw):
        return FakeResp()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    tasks = await provider.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Task A"


@pytest.mark.asyncio()
async def test_list_tasks_empty_board(provider, monkeypatch):
    """Empty board returns empty list."""
    import httpx

    class FakeResp:
        status_code = 200
        def json(self):
            return {"data": {"boards": [{"items_page": {
                "items": [],
            }}]}}

    async def fake_post(self, url, **kw):
        return FakeResp()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    tasks = await provider.list_tasks()
    assert tasks == []


@pytest.mark.asyncio()
async def test_get_task_by_id(provider, monkeypatch):
    """get_task fetches single item by ID."""
    import httpx

    class FakeResp:
        status_code = 200
        def json(self):
            return {"data": {"items": [
                {"id": "42", "name": "Deploy",
                 "column_values": [], "url": "",
                 "created_at": "", "updated_at": ""},
            ]}}

    async def fake_post(self, url, **kw):
        return FakeResp()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    task = await provider.get_task("42")
    assert task is not None
    assert task.id == "42"


@pytest.mark.asyncio()
async def test_get_task_not_found(provider, monkeypatch):
    """get_task returns None for missing item."""
    import httpx

    class FakeResp:
        status_code = 200
        def json(self):
            return {"data": {"items": []}}

    async def fake_post(self, url, **kw):
        return FakeResp()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    task = await provider.get_task("999")
    assert task is None
