"""Async wrappers around sync Docker runtime calls.

Polyphony's runtime.py uses subprocess.run (blocking). These
wrappers use asyncio.to_thread so the event loop stays free
while Docker containers are created/started/waited.
"""

from __future__ import annotations

import asyncio

from .models import RunSpec
from .runtime import (
    container_logs,
    create_container,
    remove_container,
    start_container,
    stop_container,
    wait_container,
)


async def async_create_container(run_spec: RunSpec) -> str:
    """Create a Docker container. Returns container ID."""
    return await asyncio.to_thread(create_container, run_spec)


async def async_start_container(container_id: str) -> None:
    """Start a created container."""
    await asyncio.to_thread(start_container, container_id)


async def async_wait_container(container_id: str) -> int:
    """Wait for container exit. Returns exit code."""
    return await asyncio.to_thread(wait_container, container_id)


async def async_stop_container(
    container_id: str, timeout: int | None = None,
) -> None:
    """Stop a running container."""
    await asyncio.to_thread(stop_container, container_id, timeout)


async def async_remove_container(container_id: str) -> None:
    """Remove a container."""
    await asyncio.to_thread(remove_container, container_id)


__all__ = [
    "async_create_container",
    "async_start_container",
    "async_wait_container",
    "async_stop_container",
    "async_remove_container",
    "container_logs",
]
