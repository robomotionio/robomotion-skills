"""Monday.com provider — IssueTrackerProvider implementation."""

from __future__ import annotations

import httpx

from .base import Comment, Task

MONDAY_API = "https://api.monday.com/v2"


class MondayProvider:
    """IssueTrackerProvider for Monday.com boards."""

    def __init__(self, api_token: str, board_id: str):
        self.api_token = api_token
        self.board_id = board_id

    def provider_name(self) -> str:
        return "monday"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
        }

    def _to_task(self, item: dict) -> Task:
        cols = item.get("column_values", [])
        status = _col_value(cols, "status")
        assignee = _col_value(cols, "person")
        return Task(
            id=item.get("id", ""),
            title=item.get("name", ""),
            description="",
            status=status,
            assignee=assignee,
            url=item.get("url", ""),
            created_at=item.get("created_at", ""),
            updated_at=item.get("updated_at", ""),
            raw=item,
        )

    async def _query(self, q: str) -> dict:
        async with httpx.AsyncClient(
            timeout=15, headers=self._headers(),
        ) as client:
            resp = await client.post(
                MONDAY_API, json={"query": q},
            )
            if resp.status_code != 200:
                return {}
            return resp.json().get("data", {})

    async def list_tasks(self, board=None, state="open", limit=50) -> list[Task]:
        bid = board or self.board_id
        q = _items_query(bid, limit)
        data = await self._query(q)
        boards = data.get("boards", [])
        if not boards:
            return []
        items = boards[0].get("items_page", {}).get("items", [])
        return [self._to_task(i) for i in items]

    async def get_task(self, task_id: str) -> Task | None:
        q = f'{{ items(ids: [{task_id}]) {{ id name column_values {{ id text }} url created_at updated_at }} }}'
        data = await self._query(q)
        items = data.get("items", [])
        if not items:
            return None
        return self._to_task(items[0])

    async def get_comments(self, task_id: str) -> list[Comment]:
        q = f'{{ items(ids: [{task_id}]) {{ updates {{ id body created_at creator {{ name }} }} }} }}'
        data = await self._query(q)
        items = data.get("items", [])
        if not items:
            return []
        updates = items[0].get("updates", [])
        return [
            Comment(
                id=u.get("id", ""),
                author=(u.get("creator") or {}).get("name", ""),
                text=u.get("body", ""),
                created_at=u.get("created_at", ""),
            )
            for u in updates
        ]

    async def add_comment(self, task_id: str, text: str) -> Comment | None:
        escaped = text.replace('"', '\\"')
        q = f'mutation {{ create_update(item_id: {task_id}, body: "{escaped}") {{ id body }} }}'
        data = await self._query(q)
        update = data.get("create_update", {})
        if not update:
            return None
        return Comment(
            id=update.get("id", ""),
            author="", text=update.get("body", text),
        )

    async def update_status(self, task_id: str, status: str) -> bool:
        return False  # Requires board-specific column ID

    async def list_followed(self, user_id=None, limit=50) -> list[Task]:
        return await self.list_tasks(limit=limit)

    async def search_tasks(self, query: str, limit=20) -> list[Task]:
        return await self.list_tasks(limit=limit)


def _col_value(cols: list[dict], col_id: str) -> str:
    for c in cols:
        if c.get("id") == col_id:
            return c.get("text", "")
    return ""


def _items_query(board_id: str, limit: int) -> str:
    return (
        f'{{ boards(ids: [{board_id}]) {{ items_page(limit: {limit}) '
        f'{{ items {{ id name column_values {{ id text }} url created_at updated_at }} }} }} }}'
    )
