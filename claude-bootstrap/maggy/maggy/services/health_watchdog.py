"""Server health watchdog.

Monitors processes, endpoints, and system memory.
Reports aggregate health status for the self-healing
triage engine.
"""
from __future__ import annotations

import os
import signal
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True)
class HealthCheck:
    name: str
    alive: bool
    detail: str = ""


@dataclass
class _ServiceEntry:
    name: str
    pid: int | None = None
    endpoint: str | None = None
    timeout: float = 2.0


class HealthWatchdog:
    """Lightweight health monitor for local services."""

    def __init__(self) -> None:
        self._services: dict[str, _ServiceEntry] = {}

    def register(
        self,
        name: str,
        *,
        pid: int | None = None,
        endpoint: str | None = None,
        timeout: float = 2.0,
    ) -> None:
        self._services[name] = _ServiceEntry(
            name=name,
            pid=pid,
            endpoint=endpoint,
            timeout=timeout,
        )

    def check_pid(self, pid: int) -> HealthCheck:
        try:
            os.kill(pid, signal.SIG_DFL)
            return HealthCheck(
                name=f"pid-{pid}", alive=True,
            )
        except ProcessLookupError:
            return HealthCheck(
                name=f"pid-{pid}",
                alive=False,
                detail="process not found",
            )
        except PermissionError:
            # Process exists but we lack permission
            return HealthCheck(
                name=f"pid-{pid}", alive=True,
                detail="permission denied",
            )

    def check_endpoint(
        self, url: str, *, timeout: float = 2.0,
    ) -> HealthCheck:
        try:
            resp = httpx.get(url, timeout=timeout)
            ok = resp.status_code < 500
            return HealthCheck(
                name=url, alive=ok,
                detail=f"status {resp.status_code}",
            )
        except Exception as exc:
            return HealthCheck(
                name=url, alive=False,
                detail=str(exc)[:120],
            )

    def system_memory(self) -> dict[str, Any]:
        try:
            import psutil
            vm = psutil.virtual_memory()
            return {
                "total_gb": round(vm.total / 1e9, 1),
                "used_gb": round(vm.used / 1e9, 1),
                "available_gb": round(
                    vm.available / 1e9, 1,
                ),
                "percent": vm.percent,
            }
        except ImportError:
            return _fallback_memory()

    def memory_pressure(
        self, *, threshold: float = 0.90,
    ) -> bool:
        mem = self.system_memory()
        pct = mem.get("percent", 0)
        return pct > threshold * 100

    def status(self) -> dict[str, HealthCheck]:
        results: dict[str, HealthCheck] = {}
        for name, svc in self._services.items():
            if svc.pid is not None:
                hc = self.check_pid(svc.pid)
            elif svc.endpoint is not None:
                hc = self.check_endpoint(
                    svc.endpoint, timeout=svc.timeout,
                )
            else:
                hc = HealthCheck(
                    name=name, alive=False,
                    detail="no check configured",
                )
            results[name] = HealthCheck(
                name=name,
                alive=hc.alive,
                detail=hc.detail,
            )
        return results

    def overall(self) -> HealthStatus:
        checks = self.status()
        if not checks:
            return HealthStatus.HEALTHY
        alive = sum(1 for c in checks.values() if c.alive)
        total = len(checks)
        if alive == total:
            return HealthStatus.HEALTHY
        if alive == 0:
            return HealthStatus.UNHEALTHY
        return HealthStatus.DEGRADED


def _fallback_memory() -> dict[str, Any]:
    """Parse sysctl on macOS when psutil is absent."""
    try:
        import subprocess
        out = subprocess.check_output(
            ["sysctl", "-n", "hw.memsize"],
            text=True, timeout=2,
        ).strip()
        total = int(out)
        return {
            "total_gb": round(total / 1e9, 1),
            "used_gb": 0.0,
            "available_gb": 0.0,
            "percent": 0.0,
        }
    except Exception:
        return {
            "total_gb": 0,
            "used_gb": 0,
            "available_gb": 0,
            "percent": 0,
        }
